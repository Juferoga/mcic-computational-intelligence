-- Code with me: datos para el overlay HTML de OBS.
-- Cada segundo escribe overlay/estado.json (tiempo grabado y uso de Claude);
-- el overlay lo lee junto con tareas.md. Claude cuenta como "en uso" solo si es
-- la app al frente (app de escritorio o pestaña de claude.ai en el navegador).
-- Cada intervalo de uso queda en registro_claude.csv.

obs = obslua

local cfg = { tareas = "", registro = "", estado = "" }
local hk = {}

-- grabación
local rec_acc, rec_last = 0, nil

-- Claude
local CLAUDE_APP = "com.anthropic.claudefordesktop"
local NAVEGADORES = {
  ["com.google.Chrome"] = 'tell application "Google Chrome" to get URL of active tab of front window',
  ["com.brave.Browser"] = 'tell application "Brave Browser" to get URL of active tab of front window',
  ["company.thebrowser.Browser"] = 'tell application "Arc" to get URL of active tab of front window',
  ["com.apple.Safari"] = 'tell application "Safari" to get URL of front document',
}
local ESPERA = 3 -- revisiones inactivas seguidas antes de dar Claude por cerrado

local claude_on, claude_fuente = false, ""
local claude_desde = nil   -- inicio del intervalo actual (para el CSV)
local claude_cuenta = nil  -- desde cuándo suma el intervalo al día de hoy
local claude_fin = nil     -- primera revisión inactiva del intervalo actual
local inactivas = 0
local hoy_acc, hoy = 0, os.date("%Y-%m-%d")

-- utilidades ----------------------------------------------------------------

local function leer_cmd(cmd)
  local h = io.popen(cmd .. " 2>/dev/null")
  if h == nil then return "" end
  local out = h:read("*a") or ""
  h:close()
  return out
end

-- tareas.md -----------------------------------------------------------------

local function marcar(hecha)
  local f = io.open(cfg.tareas, "r")
  if f == nil then return end
  local lineas = {}
  for l in f:lines() do table.insert(lineas, l) end
  f:close()
  if hecha then
    for i = 1, #lineas do
      if lineas[i]:match("^%s*[-*]%s+%[ %]") then
        lineas[i] = lineas[i]:gsub("%[ %]", "[x]", 1); break
      end
    end
  else
    for i = #lineas, 1, -1 do
      if lineas[i]:match("^%s*[-*]%s+%[[xX]%]") then
        lineas[i] = lineas[i]:gsub("%[[xX]%]", "[ ]", 1); break
      end
    end
  end
  f = io.open(cfg.tareas, "w")
  if f == nil then return end
  f:write(table.concat(lineas, "\n") .. "\n")
  f:close()
end

-- Claude --------------------------------------------------------------------

local LINUX = jit ~= nil and jit.os == "Linux"

-- Devuelve la fuente ("app" o "web") si Claude está al frente, o nil.
local function claude_al_frente()
  if LINUX then
    -- X11: clase y título de la ventana activa
    local id = leer_cmd("xprop -root _NET_ACTIVE_WINDOW"):match("(0x%x+)")
    if id == nil then return nil end
    local out = leer_cmd("xprop -id " .. id .. " WM_CLASS _NET_WM_NAME"):lower()
    local clase = out:match('wm_class[^=]*= ([^\n]*)') or ""
    if clase:find("claude", 1, true) then return "app" end
    if out:find("claude", 1, true) then return "web" end
    return nil
  end
  local out = leer_cmd('lsappinfo info -only bundleid "$(lsappinfo front)"')
  local bundle = out:match('bundleID="([^"]+)"')
  if bundle == nil then return nil end
  if bundle == CLAUDE_APP then return "app" end
  local script = NAVEGADORES[bundle]
  if script == nil then return nil end
  -- solo se pregunta al navegador cuando está al frente; sin permiso, la salida queda vacía
  local url = leer_cmd("osascript -e '" .. script .. "'")
  if url:find("claude.ai", 1, true) then return "web" end
  return nil
end

local function registrar(inicio, fin, fuente)
  if cfg.registro == "" or inicio == nil then return end
  local f = io.open(cfg.registro, "r")
  local nuevo = f == nil
  if f then f:close() end
  f = io.open(cfg.registro, "a")
  if f == nil then return end
  if nuevo then f:write("inicio,fin,duracion_s,fuente\n") end
  f:write(string.format("%s,%s,%d,%s\n", os.date("%Y-%m-%d %H:%M:%S", inicio),
    os.date("%Y-%m-%d %H:%M:%S", fin), fin - inicio, fuente))
  f:close()
end

local function abrir(ahora, fuente)
  claude_on, claude_fuente = true, fuente
  claude_desde, claude_cuenta, claude_fin = ahora, ahora, nil
  inactivas = 0
end

local function cerrar(fin)
  if not claude_on then return end
  hoy_acc = hoy_acc + math.max(0, fin - claude_cuenta)
  registrar(claude_desde, fin, claude_fuente)
  claude_on, claude_fuente = false, ""
  claude_desde, claude_cuenta, claude_fin = nil, nil, nil
  inactivas = 0
end

local function revisar_claude(ahora)
  -- cambio de día: el contador de hoy vuelve a cero
  local dia = os.date("%Y-%m-%d", ahora)
  if dia ~= hoy then
    hoy, hoy_acc = dia, 0
    if claude_on then claude_cuenta = ahora end
  end
  local fuente = claude_al_frente()
  if fuente then
    if claude_on and fuente ~= claude_fuente then cerrar(ahora) end
    if not claude_on then abrir(ahora, fuente) end
    inactivas, claude_fin = 0, nil
  elseif claude_on then
    inactivas = inactivas + 1
    if inactivas == 1 then claude_fin = ahora end
    if inactivas >= ESPERA then cerrar(claude_fin) end
  end
end

local function claude_segundos(ahora)
  if not claude_on then return hoy_acc end
  return hoy_acc + math.max(0, (claude_fin or ahora) - claude_cuenta)
end

-- estado.json ---------------------------------------------------------------

local function escribir_estado(ahora, rec)
  if cfg.estado == "" then return end
  local json = string.format(
    '{"rec": %s, "rec_s": %d, "claude": %s, "claude_s": %d, "claude_fuente": "%s", "ts": %d}\n',
    tostring(rec), math.floor(rec_acc), tostring(claude_on), math.floor(claude_segundos(ahora)),
    claude_fuente, ahora)
  -- escritura atómica: el overlay nunca lee un archivo a medias
  local tmp = cfg.estado .. ".tmp"
  local f = io.open(tmp, "w")
  if f == nil then return end
  f:write(json)
  f:close()
  os.rename(tmp, cfg.estado)
end

-- ciclo principal -------------------------------------------------------------

local function tick()
  local ahora = os.time()
  local rec = obs.obs_frontend_recording_active()
  if rec and not obs.obs_frontend_recording_paused() then
    if rec_last then rec_acc = rec_acc + (ahora - rec_last) end
    rec_last = ahora
  else
    rec_last = nil
  end
  -- Claude solo cuenta mientras se graba (sin pausas)
  if rec and not obs.obs_frontend_recording_paused() then
    revisar_claude(ahora)
  elseif claude_on then
    cerrar(ahora)
  end
  escribir_estado(ahora, rec)
end

local function al_evento(ev)
  if ev == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED then
    rec_acc, rec_last = 0, os.time()
    hoy_acc = 0  -- el uso de IA se cuenta por grabación
  end
end

-- interfaz de script ----------------------------------------------------------

function script_description()
  return "Code with me: escribe overlay/estado.json (tiempo grabado y uso de Claude al frente) "
    .. "para el overlay HTML, registra el uso de Claude en CSV y da atajos para marcar tareas."
end

function script_properties()
  local p = obs.obs_properties_create()
  obs.obs_properties_add_path(p, "tareas", "Archivo de tareas (.md)", obs.OBS_PATH_FILE, "Markdown (*.md)", nil)
  obs.obs_properties_add_path(p, "registro", "Registro de uso de Claude (.csv)", obs.OBS_PATH_FILE_SAVE, "CSV (*.csv)", nil)
  obs.obs_properties_add_path(p, "estado", "Estado para el overlay (.json)", obs.OBS_PATH_FILE_SAVE, "JSON (*.json)", nil)
  return p
end

function script_update(s)
  cfg.tareas = obs.obs_data_get_string(s, "tareas")
  cfg.registro = obs.obs_data_get_string(s, "registro")
  cfg.estado = obs.obs_data_get_string(s, "estado")
end

-- Pide el texto con un cuadro de diálogo (macOS o zenity en Linux) y lo agrega con el CLI `tarea`
-- (en segundo plano, para no bloquear OBS mientras se escribe).
local function agregar()
  local cli = cfg.tareas:gsub("[^/]+$", "") .. "tarea"
  local dialogo = [[osascript -e 'activate' -e 'text returned of (display dialog "Nueva tarea para el bloque actual" default answer "" with title "Code with me")']]
  if LINUX then
    dialogo = [[zenity --entry --title "Code with me" --text "Nueva tarea para el bloque actual"]]
  end
  os.execute(string.format([[(t=$(%s) && [ -n "$t" ] && TAREAS_MD='%s' '%s' add "$t") >/dev/null 2>&1 &]],
    dialogo, cfg.tareas, cli))
end

local HOTKEYS = {
  { "cwm_hecha", "Code with me: marcar siguiente tarea como hecha", function() marcar(true) end },
  { "cwm_deshacer", "Code with me: desmarcar la última tarea", function() marcar(false) end },
  { "cwm_agregar", "Code with me: agregar tarea", agregar },
}

function script_load(s)
  for _, h in ipairs(HOTKEYS) do
    local id = h[1]
    hk[id] = obs.obs_hotkey_register_frontend(id, h[2], function(pressed) if pressed then h[3]() end end)
    local arr = obs.obs_data_get_array(s, id)
    obs.obs_hotkey_load(hk[id], arr)
    obs.obs_data_array_release(arr)
  end
  obs.obs_frontend_add_event_callback(al_evento)
  obs.timer_add(tick, 1000)
end

function script_save(s)
  for id, h in pairs(hk) do
    local arr = obs.obs_hotkey_save(h)
    obs.obs_data_set_array(s, id, arr)
    obs.obs_data_array_release(arr)
  end
end

function script_unload()
  obs.timer_remove(tick)
  if claude_on then cerrar(claude_fin or os.time()) end
end
