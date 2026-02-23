print("=== Luah Filesystem Demo ===")
print("")

local base = "luah_test_dir"
fs.mkdir(base)
fs.mkdir(fs.join(base, "subdir"))
fs.mkdir(fs.join(base, "logs"))

fs.write(fs.join(base, "readme.txt"), "This is a test directory created by Luah.")
fs.write(fs.join(base, "config.json"), json.pretty({version=1, debug=true, name="test"}))
fs.write(fs.join(base, "subdir", "data.txt"), "Some data in a subdirectory.")

for i = 1, 5 do
    fs.append(fs.join(base, "logs", "app.log"),
        string.format("[%s] Log entry #%d\n", os.date("%H:%M:%S"), i))
    wait(0.05)
end

print("Directory structure:")
local function listDir(path, indent)
    indent = indent or 0
    local prefix = string.rep("  ", indent)
    local items = fs.list(path)
    for i, name in ipairs(items) do
        local fullpath = fs.join(path, name)
        if fs.isDir(fullpath) then
            print(prefix .. "[DIR]  " .. name)
            listDir(fullpath, indent + 1)
        else
            print(prefix .. "[FILE] " .. name .. " (" .. fs.size(fullpath) .. " bytes)")
        end
    end
end
listDir(base)

print("")
print("Reading config.json:")
local cfg = json.decode(fs.read(fs.join(base, "config.json")))
print("  version: " .. cfg.version)
print("  debug:   " .. tostring(cfg.debug))

print("")
print("Reading log file:")
local loglines = fs.lines(fs.join(base, "logs", "app.log"))
for i, line in ipairs(loglines) do
    print("  " .. line)
end

print("")
print("Copying config to subdir...")
fs.copy(fs.join(base, "config.json"), fs.join(base, "subdir", "config_backup.json"))
print("Done. subdir now has:")
local subfiles = fs.list(fs.join(base, "subdir"))
for i, f in ipairs(subfiles) do
    print("  " .. f)
end

print("")
print("Cleaning up...")
fs.delete(base)
print("Deleted: " .. base)
print("Exists: " .. tostring(fs.exists(base)))
