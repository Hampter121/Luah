print("=== Luah Config Manager Demo ===")
print("")

local CONFIG_FILE = "settings.json"

local function loadConfig(path, defaults)
    if fs.exists(path) then
        local ok, data = pcall(function()
            return json.decode(fs.read(path))
        end)
        if ok and data then
            for k, v in pairs(defaults) do
                if data[k] == nil then
                    data[k] = v
                end
            end
            return data
        end
    end
    return defaults
end

local function saveConfig(path, config)
    fs.write(path, json.pretty(config))
end

local function getNestedKey(tbl, keypath)
    local keys = {}
    for k in string.gmatch(keypath, "[^.]+") do
        table.insert(keys, k)
    end
    local current = tbl
    for _, k in ipairs(keys) do
        if type(current) ~= "table" then return nil end
        current = current[k]
    end
    return current
end

local defaults = {
    app = {
        name    = "MyApp",
        version = "1.0.0",
        debug   = false,
    },
    display = {
        width   = 1280,
        height  = 720,
        fps     = 60,
        vsync   = true,
    },
    audio = {
        volume  = 0.8,
        music   = true,
        sfx     = true,
    },
    database = {
        path    = "data.db",
        maxConn = 5,
    },
}

print("Loading config (using defaults since file doesn't exist)...")
local config = loadConfig(CONFIG_FILE, defaults)

print("App name:    " .. config.app.name)
print("Resolution:  " .. config.display.width .. "x" .. config.display.height)
print("Volume:      " .. config.audio.volume)

print("")
print("Modifying settings...")
config.display.fps = 144
config.audio.volume = 0.5
config.app.debug = true

saveConfig(CONFIG_FILE, config)
print("Saved to " .. CONFIG_FILE)

print("")
print("Reloading from disk...")
local reloaded = loadConfig(CONFIG_FILE, defaults)
print("FPS is now:    " .. reloaded.display.fps)
print("Volume is now: " .. reloaded.audio.volume)
print("Debug is now:  " .. tostring(reloaded.app.debug))

print("")
print("Raw JSON file:")
print(fs.read(CONFIG_FILE))

fs.delete(CONFIG_FILE)
print("Cleaned up.")
