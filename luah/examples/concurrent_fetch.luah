print("=== Luah Concurrent Fetcher ===")
print("")

local endpoints = {
    {name="UUID",       url="https://httpbin.org/uuid"},
    {name="IP Address", url="https://httpbin.org/ip"},
    {name="User Agent", url="https://httpbin.org/user-agent"},
    {name="Headers",    url="https://httpbin.org/headers"},
}

print("Fetching " .. #endpoints .. " endpoints concurrently...")
print("")

local threads = {}
for i, ep in ipairs(endpoints) do
    threads[i] = concurrent.thread(function()
        local start = time.now()
        local resp  = net.get(ep.url)
        local elapsed = time.now() - start
        return {
            name    = ep.name,
            status  = resp.status,
            ok      = resp.ok,
            elapsed = elapsed,
            body    = resp.body,
        }
    end)
end

local results = {}
for i, t in ipairs(threads) do
    local ok, result = t:join(15)
    if ok then
        table.insert(results, result)
    else
        table.insert(results, {name=endpoints[i].name, ok=false, status=0, elapsed=0, body=""})
    end
end

for _, r in ipairs(results) do
    local status = r.ok and "OK" or "FAIL"
    print(string.format("[%s] %s — HTTP %d — %.2fs",
        status, r.name, r.status, r.elapsed))
    if r.ok and #r.body > 0 then
        local preview = json.decode(r.body)
        if preview then
            print("     " .. string.sub(json.encode(preview), 1, 80))
        end
    end
    print("")
end

print("All requests complete.")
