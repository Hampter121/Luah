import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time as _time
import re
import os

from runtime.executor import LuaForgeRuntime

yuricolors = {
    "bg":          "#0d0f14",
    "surface":     "#13161e",
    "surface2":    "#1a1e2a",
    "border":      "#252a38",
    "accent":      "#e8c547",
    "accent2":     "#47c5e8",
    "accent3":     "#e847a8",
    "green":       "#50fa7b",
    "red":         "#ff5555",
    "orange":      "#ffb86c",
    "purple":      "#bd93f9",
    "text":        "#f8f8f2",
    "muted":       "#6272a4",
    "toolbar":     "#0a0c10",
}

def _yuripick_font(yuricandidates, yurisize):
    try:
        import tkinter.font as _tkfont
        import tkinter as _tk2
        _tk2.Tk().destroy()
        yuriavail = set(_tkfont.families())
        for yuriname in yuricandidates:
            if yuriname in yuriavail:
                return (yuriname, yurisize)
    except Exception:
        pass
    return (yuricandidates[-1], yurisize)

yurifontmono  = _yuripick_font(["JetBrains Mono","Cascadia Code","Fira Code","Consolas","Courier New","Courier"], 12)
yurifontmonos = _yuripick_font(["JetBrains Mono","Cascadia Code","Fira Code","Consolas","Courier New","Courier"], 10)
yurifontui    = _yuripick_font(["Segoe UI","SF Pro Text","Ubuntu","Helvetica","TkDefaultFont"], 10)

yurisnippets = {

    # -- BASICS --
    "Hello World": """\
print("Hello from Luah!")
print("Lua version: " .. _VERSION)
print("Time: " .. string.format("%.3f", time.now()))
""",

    "variables & types": """\
local name    = "Luah"
local version = 1.0
local active  = true
local nothing = nil

print("Name:    " .. name)
print("Version: " .. version)
print("Active:  " .. tostring(active))
print("Type:    " .. type(name))
""",

    "loops": """\
for i = 1, 5 do
    print("for loop: " .. i)
end

local i = 0
while i < 3 do
    i = i + 1
    print("while: " .. i)
end

local n = 1
repeat
    print("repeat: " .. n)
    n = n + 1
until n > 3
""",

    "functions": """\
local function greet(name, loud)
    local msg = "Hello, " .. name .. "!"
    if loud then
        return string.upper(msg)
    end
    return msg
end

print(greet("world", false))
print(greet("LUAH", true))

local square = function(x) return x * x end
print("5 squared = " .. square(5))
""",

    "tables": """\
local fruits = {"apple", "banana", "cherry"}
table.insert(fruits, "date")
print("Fruits: " .. #fruits)
for i, v in ipairs(fruits) do
    print(i .. ": " .. v)
end

local person = {name="Alice", age=30, active=true}
for k, v in pairs(person) do
    print(k .. " = " .. tostring(v))
end
""",

    "string ops": """\
local s = "Hello, Luah!"
print(string.upper(s))
print(string.lower(s))
print(string.len(s))
print(string.sub(s, 1, 5))
print(string.rep("ab", 3))
print(string.reverse(s))
print(string.format("Pi = %.4f", math.pi))

local found, pos = string.find(s, "Luah")
print("Found 'Luah' at: " .. pos)

local result = string.gsub(s, "Luah", "World")
print(result)
""",

    "math utils": """\
print(math.clamp(150, 0, 100))
print(math.lerp(0, 100, 0.75))
print(math.sign(-42))
print(math.round(3.7))
print(math.floor(3.9))
print(math.ceil(3.1))
print(math.sqrt(144))
print(math.abs(-99))
math.randomseed(42)
print(math.random(1, 10))
""",

    "wait & time": """\
print("start: " .. string.format("%.3f", time.now()))
wait(1)
print("after 1s: " .. string.format("%.3f", time.now()))
wait(0.5)
print("after 0.5s: " .. string.format("%.3f", time.now()))
print("clock: " .. string.format("%.6f", time.clock()))
""",

    "error handling": """\
local ok, err = pcall(function()
    error("something went wrong!")
end)
print("ok: " .. tostring(ok))
print("err: " .. err)

local function safeDivide(a, b)
    if b == 0 then
        return nil, "division by zero"
    end
    return a / b, nil
end

local result, errmsg = safeDivide(10, 0)
if errmsg then
    print("Error: " .. errmsg)
else
    print("Result: " .. result)
end
""",

    "coroutines": """\
local function producer()
    for i = 1, 5 do
        print("producing: " .. i)
        coroutine.yield(i)
    end
end

local co = coroutine.create(producer)
for i = 1, 6 do
    local ok, val = coroutine.resume(co)
    if ok and val then
        print("consumed: " .. val)
    end
end
""",

    # -- GRAPHIX --
    "graphix window": """\
local win = graphix.newWindow(400, 300, "My Window")
win:setBackground(20, 20, 40)
win:clear()
win:drawText(120, 130, "Hello graphix!", 255, 200, 50, 24)
win:present()
wait(3)
win:close()
""",

    "draw shapes": """\
local win = graphix.newWindow(500, 400, "Shapes Demo")
win:setBackground(15, 15, 30)

win:onDraw(function()
    win:fillRect(50, 50, 120, 80, 255, 80, 80)
    win:fillCircle(300, 120, 60, 80, 200, 255)
    win:drawRect(200, 200, 150, 100, 255, 200, 50, 2)
    win:drawCircle(100, 280, 50, 150, 255, 150, 2)
    win:drawLine(0, 0, 500, 400, 200, 100, 255, 1)
    win:drawText(150, 360, "Luah graphix!", 255, 255, 255, 16)
end)

win:run(60)
""",

    "game loop": """\
local win = graphix.newWindow(600, 400, "Game Loop")
win:setBackground(10, 10, 20)
local x, y  = 300, 200
local speed = 150

win:onUpdate(function(dt)
    if win:isKeyDown("left")  then x = x - speed * dt end
    if win:isKeyDown("right") then x = x + speed * dt end
    if win:isKeyDown("up")    then y = y - speed * dt end
    if win:isKeyDown("down")  then y = y + speed * dt end
    x = math.clamp(x, 0, 600)
    y = math.clamp(y, 0, 400)
end)

win:onDraw(function()
    win:fillCircle(x, y, 20, 100, 200, 255)
    win:drawText(10, 10, "Arrow keys to move", 180, 180, 180, 13)
    win:drawText(10, 28, "FPS: " .. math.round(win:getFPS()), 100, 255, 100, 13)
end)

win:run(60)
""",

    "bouncing ball": """\
local win = graphix.newWindow(600, 400, "Bouncing Ball")
win:setBackground(10, 10, 20)
local bx, by = 300, 200
local vx, vy = 220, 160
local radius = 18
local trail  = {}

win:onUpdate(function(dt)
    vy = vy + 200 * dt
    bx = bx + vx * dt
    by = by + vy * dt
    if bx - radius < 0   then bx = radius;       vx =  math.abs(vx) end
    if bx + radius > 600 then bx = 600 - radius; vx = -math.abs(vx) end
    if by - radius < 0   then by = radius;       vy =  math.abs(vy) end
    if by + radius > 400 then
        by = 400 - radius
        vy = -math.abs(vy) * 0.85
        vx = vx * 0.99
    end
    table.insert(trail, {x=bx, y=by})
    if #trail > 30 then table.remove(trail, 1) end
end)

win:onDraw(function()
    for i, p in ipairs(trail) do
        local a = i / #trail
        win:fillCircle(p.x, p.y, math.floor(radius * a * 0.7),
            math.floor(50*a), math.floor(100*a), math.floor(255*a))
    end
    win:fillCircle(bx, by, radius, 100, 180, 255)
    win:drawText(10, 10, "FPS: " .. math.round(win:getFPS()), 150, 150, 150, 12)
end)

win:run(60)
""",

    "draw text sizes": """\
local win = graphix.newWindow(500, 350, "Text Sizes")
win:setBackground(10, 10, 25)

win:onDraw(function()
    win:drawText(30, 20,  "Size 10", 200, 200, 200, 10)
    win:drawText(30, 45,  "Size 14", 255, 200, 100, 14)
    win:drawText(30, 80,  "Size 20", 100, 255, 180, 20)
    win:drawText(30, 120, "Size 28", 255, 100, 150, 28)
    win:drawText(30, 175, "Size 36", 200, 100, 255, 36)
    win:drawText(30, 270, "t=" .. string.format("%.2f", time.now()), 180, 220, 255, 14)
end)

win:run(60)
""",

    "mouse input": """\
local win = graphix.newWindow(500, 400, "Mouse Demo")
win:setBackground(15, 15, 30)
local mx, my = 0, 0
local clicks = {}

win:onUpdate(function(dt)
    mx, my = win:getMousePos()
    if win:isMouseDown(1) then
        table.insert(clicks, {x=mx, y=my, t=time.now()})
    end
    local now = time.now()
    local keep = {}
    for _, c in ipairs(clicks) do
        if now - c.t < 2 then table.insert(keep, c) end
    end
    clicks = keep
end)

win:onDraw(function()
    for _, c in ipairs(clicks) do
        win:fillCircle(c.x, c.y, 8, 255, 100, 150)
    end
    win:fillCircle(mx, my, 6, 255, 220, 80)
    win:drawText(10, 10, "Mouse: " .. mx .. ", " .. my, 200, 200, 200, 13)
    win:drawText(10, 28, "Click to paint!", 150, 150, 150, 12)
end)

win:run(60)
""",

    "keyboard input": """\
local win = graphix.newWindow(400, 200, "Keyboard")
win:setBackground(10, 20, 10)
local lastKey = "none"

win:onUpdate(function(dt)
    local keys = {"a","b","c","space","left","right","up","down","escape"}
    for _, k in ipairs(keys) do
        if win:isKeyDown(k) then lastKey = k end
    end
end)

win:onDraw(function()
    win:drawText(80, 70,  "Press any key!", 200, 255, 200, 20)
    win:drawText(110, 110, "Last: " .. lastKey, 255, 255, 100, 18)
end)

win:run(60)
""",

    "color grid": """\
local win = graphix.newWindow(512, 256, "Color Grid")
win:setBackground(0, 0, 0)

win:onDraw(function()
    for row = 0, 15 do
        for col = 0, 31 do
            local r = math.floor((col / 31) * 255)
            local g = math.floor((row / 15) * 255)
            local b = 128
            win:fillRect(col * 16, row * 16, 16, 16, r, g, b)
        end
    end
    win:drawText(10, 8, "Color Grid", 255, 255, 255, 13)
end)

win:run(60)
""",

    "starfield": """\
local win = graphix.newWindow(700, 500, "Starfield")
win:setBackground(0, 0, 10)
local stars = {}
for i = 1, 200 do
    table.insert(stars, {
        x = math.random(0, 700),
        y = math.random(0, 500),
        speed = math.random(1, 5) * 20,
        size  = math.random(1, 3),
    })
end

win:onUpdate(function(dt)
    for _, s in ipairs(stars) do
        s.x = s.x - s.speed * dt
        if s.x < 0 then
            s.x = 700
            s.y = math.random(0, 500)
        end
    end
end)

win:onDraw(function()
    for _, s in ipairs(stars) do
        local bright = math.floor(100 + s.speed * 20)
        win:fillCircle(s.x, s.y, s.size, bright, bright, 255)
    end
    win:drawText(10, 10, "Starfield - " .. math.round(win:getFPS()) .. " FPS", 100, 100, 200, 12)
end)

win:run(60)
""",

    # -- FILESYSTEM --
    "fs write & read": """\
fs.write("hello.txt", "Hello from Luah!\\nLine 2\\nLine 3")
print("Written!")

local content = fs.read("hello.txt")
print("Content:\\n" .. content)

print("Exists: " .. tostring(fs.exists("hello.txt")))
print("Size: " .. fs.size("hello.txt") .. " bytes")
""",

    "fs list files": """\
local files = fs.list(".")
print("Files in current dir:")
for i, name in ipairs(files) do
    local path = fs.join(".", name)
    local kind = fs.isDir(path) and "[DIR]" or "[FILE]"
    print(kind .. " " .. name)
end
print("CWD: " .. fs.cwd())
""",

    "fs read lines": """\
fs.write("data.txt", "apple\\nbanana\\ncherry\\ndate")

local lines = fs.lines("data.txt")
for i, line in ipairs(lines) do
    print(i .. ": " .. line)
end

fs.delete("data.txt")
print("Cleaned up.")
""",

    "fs paths": """\
local p = fs.join("folder", "sub", "file.txt")
print("Joined:   " .. p)
print("Basename: " .. fs.basename(p))
print("Dirname:  " .. fs.dirname(p))
local info = fs.ext(p)
print("Root: " .. info.root)
print("Ext:  " .. info.ext)
print("Abspath: " .. fs.abspath("hello.txt"))
""",

    # -- JSON --
    "json encode": """\
local data = {
    name    = "Alice",
    age     = 30,
    hobbies = {"coding", "reading", "gaming"},
    address = {city = "Tokyo", zip = "100-0001"},
}

local encoded = json.encode(data)
print("Encoded: " .. encoded)

local pretty = json.pretty(data)
print("Pretty:\\n" .. pretty)
""",

    "json decode": """\
local raw = '{"name":"Bob","score":9001,"tags":["lua","cool"]}'

local data = json.decode(raw)
print("Name:  " .. data.name)
print("Score: " .. data.score)

for i, tag in ipairs(data.tags) do
    print("Tag " .. i .. ": " .. tag)
end
""",

    "json roundtrip": """\
local original = {items = {}}
for i = 1, 5 do
    table.insert(original.items, {id=i, value=i*i})
end

local encoded = json.encode(original)
fs.write("data.json", encoded)

local loaded   = json.decode(fs.read("data.json"))
for i, item in ipairs(loaded.items) do
    print("id=" .. item.id .. " value=" .. item.value)
end

fs.delete("data.json")
""",

    # -- XML --
    "xml parse": """\
local xmlstr = [[
<library>
    <book id="1">
        <title>Programming in Lua</title>
        <author>Roberto Ierusalimschy</author>
    </book>
    <book id="2">
        <title>The C Programming Language</title>
        <author>Kernighan and Ritchie</author>
    </book>
</library>
]]

local root = xml.parse(xmlstr)
print("Tag: " .. root.tag)
print("Children: " .. root.numChildren)

for i = 1, root.numChildren do
    local book = root.children[i]
    local title = book.children[1].text
    local author = book.children[2].text
    print("Book: " .. title .. " by " .. author)
end
""",

    "xml encode text": """\
local dangerous = '<script>alert("xss")</script> & "quotes"'
local safe = xml.encode(dangerous)
print("Original: " .. dangerous)
print("Encoded:  " .. safe)
""",

    # -- NETWORKING --
    "net GET request": """\
print("Fetching public API...")
local resp = net.get("https://httpbin.org/get")
print("Status: " .. resp.status)
print("OK: " .. tostring(resp.ok))
if resp.ok then
    print("Body preview: " .. string.sub(resp.body, 1, 200))
end
""",

    "net POST JSON": """\
local payload = json.encode({
    username = "luahuser",
    message  = "Hello from Luah!",
})

local resp = net.post("https://httpbin.org/post", payload)
print("Status: " .. resp.status)
if resp.ok then
    local data = json.decode(resp.body)
    print("Sent data: " .. data.data)
end
""",

    "net download file": """\
print("Downloading file...")
net.download("https://httpbin.org/image/png", "downloaded.png")
print("Saved!")
print("Size: " .. fs.size("downloaded.png") .. " bytes")
fs.delete("downloaded.png")
print("Cleaned up.")
""",

    "net urlencode": """\
local params = {
    q      = "luah programming language",
    page   = "1",
    format = "json",
}
local encoded = net.urlencode(params)
print("Encoded params: " .. encoded)

local decoded = net.urldecode("hello%20world%21")
print("Decoded: " .. decoded)
""",

    # -- TCP --
    "tcp connect": """\
print("Connecting to example server...")
local ok, err = pcall(function()
    local conn = tcp.connect("httpbin.org", 80)
    conn:sendLine("GET /get HTTP/1.0")
    conn:sendLine("Host: httpbin.org")
    conn:sendLine("")
    local line = conn:recvLine()
    print("Response: " .. line)
    conn:close()
end)
if not ok then
    print("Error: " .. err)
end
""",

    "tcp server": """\
print("Starting TCP server on port 9000...")
print("(Connect with: telnet localhost 9000)")
local server = tcp.listen(9000)
print("Listening...")
local client = server:accept()
if client then
    print("Client connected from " .. client.address)
    client:sendLine("Welcome to Luah TCP server!")
    local msg = client:recvLine()
    print("Got: " .. msg)
    client:sendLine("Echo: " .. msg)
    client:close()
end
server:close()
""",

    # -- WEBSOCKETS --
    "ws connect": """\
print("Connecting to WebSocket echo server...")
local conn = ws.connect("wss://echo.websocket.events")

local deadline = time.now() + 3
while not conn:isConnected() and time.now() < deadline do
    wait(0.1)
end

if conn:isConnected() then
    print("Connected!")
    conn:send("Hello from Luah WebSocket!")
    wait(1)
    local msg = conn:recv(2)
    if msg then
        print("Echo received: " .. msg)
    end
    conn:close()
else
    print("Could not connect: " .. tostring(conn:error()))
end
""",

    # -- CONCURRENCY --
    "concurrent threads": """\
print("Spawning threads...")

local function worker(id, delay)
    wait(delay)
    return "worker " .. id .. " done after " .. delay .. "s"
end

local t1 = concurrent.thread(worker, 1, 0.5)
local t2 = concurrent.thread(worker, 2, 1.0)
local t3 = concurrent.thread(worker, 3, 0.2)

local ok1, r1 = t1:join(3)
local ok2, r2 = t2:join(3)
local ok3, r3 = t3:join(3)

print(r1)
print(r2)
print(r3)
""",

    "concurrent channel": """\
local ch = concurrent.channel(10)

local producer = concurrent.thread(function()
    for i = 1, 5 do
        ch:send(i)
        wait(0.1)
    end
    ch:send(nil)
end)

while true do
    local val = ch:recv(2)
    if val == nil then break end
    print("Received: " .. val)
end

producer:join(5)
print("Done.")
""",

    "concurrent mutex": """\
local lock    = concurrent.mutex()
local counter = 0

local function increment(n)
    for i = 1, n do
        lock:lock()
        counter = counter + 1
        lock:unlock()
    end
end

local t1 = concurrent.thread(increment, 100)
local t2 = concurrent.thread(increment, 100)
local t3 = concurrent.thread(increment, 100)
t1:join(5)
t2:join(5)
t3:join(5)

print("Counter: " .. counter .. " (expected 300)")
""",

    "concurrent event": """\
local ready = concurrent.event()

local worker = concurrent.thread(function()
    print("Worker: waiting for signal...")
    ready:wait(5)
    print("Worker: got signal, doing work!")
    wait(0.5)
    return "work complete"
end)

wait(1)
print("Main: sending signal!")
ready:set()

local ok, result = worker:join(5)
print("Result: " .. result)
""",

    # -- CLI --
    "cli exec": """\
local result = cli.exec("echo Hello from shell!")
print("stdout: " .. result.stdout)
print("code:   " .. result.code)
print("ok:     " .. tostring(result.ok))
""",

    "cli environment": """\
local path = cli.getEnv("PATH", "not set")
print("PATH starts with: " .. string.sub(path, 1, 50))

cli.setEnv("LUAH_TEST", "hello from lua")
print("LUAH_TEST: " .. cli.getEnv("LUAH_TEST"))
print("Platform: " .. cli.platform())
""",

    "cli colors": """\
print(cli.color("This is red",     "red"))
print(cli.color("This is green",   "green"))
print(cli.color("This is cyan",    "cyan"))
print(cli.color("This is yellow",  "yellow"))
print(cli.color("This is magenta", "magenta"))
print(cli.color("Bold text",       "bold"))
print(cli.color("Red on white",    "red", "bgWhite"))
""",

    "cli args": """\
local args = cli.args()
print("Script args:")
for i, v in ipairs(args) do
    print("  [" .. i .. "] = " .. v)
end
""",

    # -- DATABASE --
    "db in-memory": """\
local conn = db.sqlite()

conn:exec("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
conn:exec("INSERT INTO users (name, age) VALUES ('Alice', 30)")
conn:exec("INSERT INTO users (name, age) VALUES ('Bob', 25)")
conn:exec("INSERT INTO users (name, age) VALUES ('Carol', 35)")

local rows = conn:query("SELECT * FROM users ORDER BY age")
for i, row in ipairs(rows) do
    print(row.id .. ": " .. row.name .. " (age " .. row.age .. ")")
end

local one = conn:queryOne("SELECT * FROM users WHERE name = 'Bob'")
print("Found: " .. one.name .. ", age " .. one.age)

conn:close()
""",

    "db file": """\
local path = "mydata.db"
local conn = db.sqlite(path)

conn:exec("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, content TEXT, ts REAL)")

conn:begin()
for i = 1, 5 do
    conn:exec("INSERT INTO notes (content, ts) VALUES (?, ?)",
        {"Note number " .. i, time.now()})
end
conn:commit()

local rows = conn:query("SELECT * FROM notes")
print("Total notes: " .. #rows)
for i, row in ipairs(rows) do
    print("[" .. row.id .. "] " .. row.content)
end

conn:close()
fs.delete(path)
print("Done.")
""",

    "db transactions": """\
local conn = db.sqlite()
conn:exec("CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT, balance REAL)")
conn:exec("INSERT INTO accounts (name, balance) VALUES ('Alice', 1000)")
conn:exec("INSERT INTO accounts (name, balance) VALUES ('Bob', 500)")

local function transfer(from, to, amount)
    conn:begin()
    local ok, err = pcall(function()
        conn:exec("UPDATE accounts SET balance = balance - ? WHERE name = ?", {amount, from})
        conn:exec("UPDATE accounts SET balance = balance + ? WHERE name = ?", {amount, to})
    end)
    if ok then
        conn:commit()
        return true
    else
        conn:rollback()
        return false, err
    end
end

transfer("Alice", "Bob", 200)

local rows = conn:query("SELECT * FROM accounts")
for i, row in ipairs(rows) do
    print(row.name .. ": $" .. row.balance)
end
conn:close()
""",

    # -- COMBINED --
    "fetch & save JSON": """\
print("Fetching data from API...")
local resp = net.get("https://httpbin.org/uuid")
if resp.ok then
    local data = json.decode(resp.body)
    print("UUID: " .. data.uuid)
    fs.write("uuid.json", json.pretty(data))
    print("Saved to uuid.json")
    fs.delete("uuid.json")
else
    print("Request failed: " .. resp.status)
end
""",

    "config file": """\
local configPath = "config.json"

local defaults = {
    width  = 800,
    height = 600,
    title  = "My App",
    debug  = false,
}

if not fs.exists(configPath) then
    fs.write(configPath, json.pretty(defaults))
    print("Created default config.")
end

local config = json.decode(fs.read(configPath))
print("Title:  " .. config.title)
print("Width:  " .. config.width)
print("Height: " .. config.height)
print("Debug:  " .. tostring(config.debug))

fs.delete(configPath)
""",

    "log to file": """\
local logPath = "app.log"

local function log(level, msg)
    local line = string.format("[%s] [%s] %s\\n",
        os.date("%Y-%m-%d %H:%M:%S"), level, msg)
    fs.append(logPath, line)
    print(line)
end

log("INFO",  "Application started")
wait(0.1)
log("WARN",  "Low memory warning")
wait(0.1)
log("ERROR", "Something failed")
wait(0.1)
log("INFO",  "Application shutting down")

print("\\nLog file contents:")
print(fs.read(logPath))
fs.delete(logPath)
""",

    "concurrent download": """\
local urls = {
    "https://httpbin.org/uuid",
    "https://httpbin.org/ip",
    "https://httpbin.org/user-agent",
}

local results = {}
local threads = {}

for i, url in ipairs(urls) do
    threads[i] = concurrent.thread(function()
        local resp = net.get(url)
        return {url=url, status=resp.status, body=resp.body}
    end)
end

for i, t in ipairs(threads) do
    local ok, result = t:join(10)
    if ok then
        print("URL: " .. result.url)
        print("Status: " .. result.status)
        print("Body: " .. string.sub(result.body, 1, 80))
        print("---")
    end
end
""",
}


class LuahApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Luah IDE")
        self.root.geometry("1380x860")
        self.root.configure(bg=yuricolors["bg"])
        self._yuriconfigure_styles()

        self._yuriruntime    = None
        self._yuriterminal   = None
        self._yuritabbar     = None
        self._yurishowterm   = tk.BooleanVar(value=False)

        self._yuribuild_ui()
        self._yuribind_keys()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._yuriclose)
        self.root.mainloop()

    def _yuriclose(self):
        if self._yuriruntime:
            self._yuriruntime.stop()
        if self._yuriterminal:
            self._yuriterminal.destroy()
        self.root.destroy()

    def _yuriconfigure_styles(self):
        yuristyle = ttk.Style()
        yuristyle.theme_use("clam")
        yuristyle.configure("TFrame",         background=yuricolors["bg"])
        yuristyle.configure("Surface.TFrame", background=yuricolors["surface"])
        yuristyle.configure("TLabel",         background=yuricolors["bg"], foreground=yuricolors["text"], font=yurifontui)
        yuristyle.configure("TButton",        background=yuricolors["surface2"], foreground=yuricolors["text"],
                            relief="flat", borderwidth=0, font=yurifontui, padding=(12, 6))
        yuristyle.map("TButton",
                      background=[("active", yuricolors["border"]), ("pressed", yuricolors["border"])],
                      foreground=[("active", yuricolors["text"])])
        yuristyle.configure("Vertical.TScrollbar",   background=yuricolors["surface2"],
                            troughcolor=yuricolors["bg"], borderwidth=0, arrowsize=12)
        yuristyle.configure("Horizontal.TScrollbar", background=yuricolors["surface2"],
                            troughcolor=yuricolors["bg"], borderwidth=0, arrowsize=12)
        yuristyle.configure("TPanedwindow", background=yuricolors["border"])

    def _yuribuild_ui(self):
        self._yuribuild_toolbar()
        self._yuribuild_statusbar()

        yurimainpane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        yurimainpane.pack(fill=tk.BOTH, expand=True)

        yurisidebar = self._yuribuild_sidebar(yurimainpane)
        yurimainpane.add(yurisidebar, weight=0)

        yuriright = tk.Frame(yurimainpane, bg=yuricolors["bg"])
        yurimainpane.add(yuriright, weight=1)

        yurivertpane = ttk.PanedWindow(yuriright, orient=tk.VERTICAL)
        yurivertpane.pack(fill=tk.BOTH, expand=True)

        yurieditorarea = tk.Frame(yurivertpane, bg=yuricolors["bg"])
        yurivertpane.add(yurieditorarea, weight=3)

        self._yuribottompane = ttk.PanedWindow(yurivertpane, orient=tk.HORIZONTAL)
        yurivertpane.add(self._yuribottompane, weight=1)

        yuriconsframe = self._yuribuild_console(self._yuribottompane)
        self._yuribottompane.add(yuriconsframe, weight=1)

        self._yuritermframe = tk.Frame(self._yuribottompane, bg=yuricolors["surface"])

        from ide.tabs import LuahTabBar
        self._yuritabbar = LuahTabBar(
            yurieditorarea,
            yuricolors, yurifontmono, yurifontmonos, yurifontui,
            self._yurionactivetab,
            self._yuriontabclosed,
        )

        yuridefault = (
            "-- Welcome to Luah!\n"
            "-- Press F5 to run  |  Ctrl+T = new tab  |  Ctrl+` = toggle terminal\n"
            "\n"
            'print("Hello from Luah!")\n'
            'print("Lua version: " .. _VERSION)\n'
            'print("Libraries: fs, json, xml, net, ws, tcp, concurrent, cli, db")\n'
            'print("Time: " .. string.format("%.3f", time.now()))\n'
        )
        self._yuritabbar.new_tab(yuricode=yuridefault)

    def _yuribuild_toolbar(self):
        yuritb = tk.Frame(self.root, bg=yuricolors["toolbar"], height=48)
        yuritb.pack(fill=tk.X, side=tk.TOP)
        yuritb.pack_propagate(False)

        tk.Label(yuritb, text="⬡ Luah", bg=yuricolors["toolbar"],
                 fg=yuricolors["accent"], font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT, padx=(14, 4))

        tk.Label(yuritb, text="Lua 5.4+", bg=yuricolors["surface"],
                 fg=yuricolors["muted"], font=yurifontmonos, padx=8, pady=2).pack(side=tk.LEFT, padx=6)

        tk.Button(yuritb, text="＋ Tab",   command=self._yurinew_tab,     **self._yuribtn()).pack(side=tk.LEFT, padx=2, pady=8)
        tk.Button(yuritb, text="Open",     command=self._yuriopen_file,   **self._yuribtn()).pack(side=tk.LEFT, padx=2, pady=8)
        tk.Button(yuritb, text="Save",     command=self._yurisave_file,   **self._yuribtn()).pack(side=tk.LEFT, padx=2, pady=8)
        tk.Button(yuritb, text="Save As",  command=self._yurisave_file_as,**self._yuribtn()).pack(side=tk.LEFT, padx=2, pady=8)

        self._yuritermtoggle = tk.Button(
            yuritb, text="⬛ Terminal", command=self._yuritoggle_terminal,
            bg=yuricolors["surface2"], fg=yuricolors["muted"],
            font=yurifontui, relief="flat", padx=10, pady=5, cursor="hand2",
            activebackground=yuricolors["border"],
        )
        self._yuritermtoggle.pack(side=tk.LEFT, padx=2, pady=8)

        self._yuristopbtn = tk.Button(yuritb, text="■  Stop", command=self._yuristop_script,
                                      bg=yuricolors["red"], fg="#ffffff",
                                      font=("Segoe UI", 10, "bold"),
                                      relief="flat", padx=14, pady=6, cursor="hand2")
        self._yuristopbtn.pack(side=tk.RIGHT, padx=(4, 14), pady=8)
        self._yuristopbtn.config(state=tk.DISABLED)

        self._yurirunbtn = tk.Button(yuritb, text="▶  Run", command=self._yurirun_script,
                                     bg=yuricolors["green"], fg="#000000",
                                     font=("Segoe UI", 10, "bold"),
                                     relief="flat", padx=14, pady=6, cursor="hand2")
        self._yurirunbtn.pack(side=tk.RIGHT, padx=4, pady=8)

        tk.Button(yuritb, text="Clear", command=self._yuriclear_console,
                  **self._yuribtn()).pack(side=tk.RIGHT, padx=4, pady=8)

    def _yuribtn(self):
        return dict(bg=yuricolors["surface2"], fg=yuricolors["text"], font=yurifontui,
                    relief="flat", padx=10, pady=5, cursor="hand2",
                    activebackground=yuricolors["border"], activeforeground=yuricolors["text"])

    def _yuribuild_sidebar(self, yuriparent):
        yuriframe = tk.Frame(yuriparent, bg=yuricolors["surface"], width=210)
        yuriframe.pack_propagate(False)

        tk.Label(yuriframe, text="SNIPPETS", bg=yuricolors["surface"],
                 fg=yuricolors["muted"], font=("Segoe UI", 8, "bold")).pack(padx=10, pady=(10, 4), anchor="w")
        tk.Frame(yuriframe, bg=yuricolors["border"], height=1).pack(fill=tk.X, padx=10)

        yuricanvas = tk.Canvas(yuriframe, bg=yuricolors["surface"], highlightthickness=0, bd=0)
        yurisb2 = ttk.Scrollbar(yuriframe, orient=tk.VERTICAL, command=yuricanvas.yview)
        yurisb2.pack(side=tk.RIGHT, fill=tk.Y)
        yuricanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yuricanvas.configure(yscrollcommand=yurisb2.set)

        yurisf = tk.Frame(yuricanvas, bg=yuricolors["surface"])
        yuricanvaswin = yuricanvas.create_window((0, 0), window=yurisf, anchor="nw")

        yurisf.bind("<Configure>", lambda yurie: (
            yuricanvas.configure(scrollregion=yuricanvas.bbox("all")),
            yuricanvas.itemconfig(yuricanvaswin, width=yuricanvas.winfo_width()),
        ))
        yuricanvas.bind("<Configure>", lambda yurie: yuricanvas.itemconfig(yuricanvaswin, width=yurie.width))

        def yuriwheel(yurie):
            yuricanvas.yview_scroll(int(-1 * (yurie.delta / 120)), "units")

        yuricanvas.bind("<MouseWheel>", yuriwheel)
        yurisf.bind("<MouseWheel>", yuriwheel)

        for yurisnipname in yurisnippets:
            yuribtn = tk.Button(
                yurisf, text=yurisnipname, anchor="w",
                command=lambda yurin=yurisnipname: self._yuriinsert_snippet(yurin),
                bg=yuricolors["surface2"], fg=yuricolors["accent2"],
                font=yurifontmonos, relief="flat",
                padx=8, pady=4, cursor="hand2",
                activebackground=yuricolors["border"], activeforeground=yuricolors["text"]
            )
            yuribtn.pack(fill=tk.X, pady=1, padx=4)
            yuribtn.bind("<MouseWheel>", yuriwheel)

        return yuriframe

    def _yuribuild_console(self, yuriparent):
        yuriframe = tk.Frame(yuriparent, bg=yuricolors["surface"])

        yuriheader = tk.Frame(yuriframe, bg=yuricolors["surface"], height=28)
        yuriheader.pack(fill=tk.X)
        yuriheader.pack_propagate(False)

        self._yuriconsoledot = tk.Label(yuriheader, text="●", bg=yuricolors["surface"],
                                        fg=yuricolors["green"], font=("Segoe UI", 10))
        self._yuriconsoledot.pack(side=tk.LEFT, padx=(10, 4), pady=4)
        tk.Label(yuriheader, text="OUTPUT", bg=yuricolors["surface"],
                 fg=yuricolors["muted"], font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, pady=4)

        tk.Frame(yuriframe, bg=yuricolors["border"], height=1).pack(fill=tk.X)

        yuriconsrow = tk.Frame(yuriframe, bg="#09090d")
        yuriconsrow.pack(fill=tk.BOTH, expand=True)

        self._yuriconsole = tk.Text(
            yuriconsrow, bg="#09090d", fg=yuricolors["text"],
            font=yurifontmonos, relief="flat", padx=10, pady=8,
            state=tk.DISABLED, wrap=tk.WORD,
        )
        self._yuriconsole.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        yuriconssb = ttk.Scrollbar(yuriconsrow, orient=tk.VERTICAL, command=self._yuriconsole.yview)
        yuriconssb.pack(side=tk.RIGHT, fill=tk.Y)
        self._yuriconsole.config(yscrollcommand=yuriconssb.set)

        for yuritag, yuriclr in [
            ("normal", yuricolors["text"]), ("error", yuricolors["red"]),
            ("info", yuricolors["accent2"]), ("success", yuricolors["green"]),
            ("warn", yuricolors["accent"]), ("time", yuricolors["muted"]),
            ("dim", yuricolors["muted"]),
        ]:
            self._yuriconsole.tag_config(yuritag, foreground=yuriclr)

        return yuriframe

    def _yuribuild_statusbar(self):
        yurisb = tk.Frame(self.root, bg=yuricolors["surface"], height=22)
        yurisb.pack(fill=tk.X, side=tk.BOTTOM)
        yurisb.pack_propagate(False)

        self._yuristatusdot = tk.Label(yurisb, text="●", bg=yuricolors["surface"],
                                       fg=yuricolors["green"], font=("Segoe UI", 8))
        self._yuristatusdot.pack(side=tk.LEFT, padx=(8, 2))
        self._yuristatustxt = tk.Label(yurisb, text="Ready", bg=yuricolors["surface"],
                                       fg=yuricolors["muted"], font=yurifontmonos)
        self._yuristatustxt.pack(side=tk.LEFT)

        self._yuricursorpos = tk.Label(yurisb, text="Ln 1, Col 1", bg=yuricolors["surface"],
                                       fg=yuricolors["muted"], font=yurifontmonos)
        self._yuricursorpos.pack(side=tk.RIGHT, padx=10)

        self._yuritabnametxt = tk.Label(yurisb, text="untitled.luah", bg=yuricolors["surface"],
                                        fg=yuricolors["muted"], font=yurifontmonos)
        self._yuritabnametxt.pack(side=tk.RIGHT, padx=10)

        tk.Label(yurisb, text="Lua 5.1+", bg=yuricolors["surface"],
                 fg=yuricolors["muted"], font=yurifontmonos).pack(side=tk.RIGHT, padx=10)

    def _yuribind_keys(self):
        self.root.bind("<F5>",             lambda yurie: self._yurirun_script())
        self.root.bind("<F6>",             lambda yurie: self._yuristop_script())
        self.root.bind("<Control-Return>", lambda yurie: self._yurirun_script())
        self.root.bind("<Control-s>",      lambda yurie: self._yurisave_file())
        self.root.bind("<Control-t>",      lambda yurie: self._yurinew_tab())
        self.root.bind("<Control-o>",      lambda yurie: self._yuriopen_file())
        self.root.bind("<Control-grave>",  lambda yurie: self._yuritoggle_terminal())

    def _yurionactivetab(self, yurittab):
        yuriname = os.path.basename(yurittab.yuripath) if yurittab.yuripath else "untitled.luah"
        self._yuritabnametxt.config(text=yuriname)
        self.root.title(f"Luah IDE — {yuriname}")

    def _yuriontabclosed(self, yurittab):
        pass

    def _yurinew_tab(self):
        if self._yuritabbar:
            self._yuritabbar.new_tab()

    def _yuriopen_file(self):
        if self._yuritabbar:
            self._yuritabbar.open_file()

    def _yurisave_file(self):
        if self._yuritabbar:
            yuriok = self._yuritabbar.save_tab()
            if yuriok:
                yurittab = self._yuritabbar.active_tab()
                if yurittab and yurittab.yuripath:
                    self._yurilog("Saved: " + yurittab.yuripath, "info")

    def _yurisave_file_as(self):
        if self._yuritabbar:
            self._yuritabbar.save_tab_as()

    def _yuriinsert_snippet(self, yuriname: str):
        yuricode = yurisnippets.get(yuriname, "")
        if self._yuritabbar:
            self._yuritabbar.insert_snippet(yuricode)

    def _yuritoggle_terminal(self):
        from ide.terminal import LuahTerminal
        if self._yurishowterm.get():
            self._yurishowterm.set(False)
            self._yuritermframe.pack_forget()
            self._yuribottompane.forget(self._yuritermframe)
            self._yuritermtoggle.config(fg=yuricolors["muted"], bg=yuricolors["surface2"])
        else:
            self._yurishowterm.set(True)
            if self._yuriterminal is None:
                self._yuriterminal = LuahTerminal(
                    self._yuritermframe, yuricolors, yurifontmono
                )
            self._yuribottompane.add(self._yuritermframe, weight=1)
            self._yuritermtoggle.config(fg=yuricolors["bg"], bg=yuricolors["accent2"])
            self._yuriterminal.focus_input()

    def _yurirun_script(self):
        if self._yuriruntime and self._yuriruntime.is_running():
            self._yurilog("Already running. Stop it first.", "warn")
            return
        if not self._yuritabbar:
            return

        yuricode = self._yuritabbar.get_code()
        self._yuritabbar.clear_error_line()
        self._yurilog("─" * 40, "dim")
        self._yurilog("Running script...", "info")
        self._yuriset_running(True)

        self._yuriruntime = LuaForgeRuntime(
            output_callback=lambda yurimsg: self._yurilog(yurimsg, "normal"),
            error_callback=self._yurihandle_error,
        )

        def yurifinish_check():
            if self._yuriruntime and self._yuriruntime.is_running():
                self.root.after(100, yurifinish_check)
            else:
                self._yuriset_running(False)
                self._yurilog("Script finished.", "success")

        self._yuriruntime.execute(yuricode)
        yurifinish_check()

    def _yuristop_script(self):
        if self._yuriruntime:
            self._yuriruntime.stop()
            self._yurilog("Script stopped by user.", "warn")
        self._yuriset_running(False)

    def _yuriset_running(self, yurirunning: bool):
        if yurirunning:
            self._yurirunbtn.config(state=tk.DISABLED, bg="#2a4a2a")
            self._yuristopbtn.config(state=tk.NORMAL)
            self._yuristatusdot.config(fg=yuricolors["accent"])
            self._yuristatustxt.config(text="Running...")
            self._yuriconsoledot.config(fg=yuricolors["accent"])
        else:
            self._yurirunbtn.config(state=tk.NORMAL, bg=yuricolors["green"])
            self._yuristopbtn.config(state=tk.DISABLED)
            self._yuristatusdot.config(fg=yuricolors["green"])
            self._yuristatustxt.config(text="Ready")
            self._yuriconsoledot.config(fg=yuricolors["green"])

    def _yurihandle_error(self, yurimsg: str):
        yurimatch = re.search(r':(\d+):', yurimsg)
        if yurimatch:
            yurilinenum = int(yurimatch.group(1))
            self.root.after(0, lambda: self._yuritabbar.mark_error_line(yurilinenum))
        self.root.after(0, lambda: self._yurilog(f"ERROR: {yurimsg}", "error"))
        self.root.after(0, lambda: self._yuriset_running(False))

    def _yurilog(self, yurimsg: str, yuritag: str = "normal"):
        def yuridolog():
            yuric = self._yuriconsole
            yuric.config(state=tk.NORMAL)
            yuripts = _time.strftime("%H:%M:%S")
            yuric.insert("end", f"[{yuripts}] ", "time")
            yuric.insert("end", str(yurimsg) + "\n", yuritag)
            yuric.see("end")
            yuric.config(state=tk.DISABLED)
        self.root.after(0, yuridolog)

    def _yuriclear_console(self):
        self._yuriconsole.config(state=tk.NORMAL)
        self._yuriconsole.delete("1.0", "end")
        self._yuriconsole.config(state=tk.DISABLED)
