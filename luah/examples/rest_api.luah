print("=== Luah REST API Demo ===")
print("")

print("1. GET public posts...")
local resp = net.get("https://jsonplaceholder.typicode.com/posts/1")
if resp.ok then
    local post = json.decode(resp.body)
    print("   Title: " .. post.title)
    print("   Body:  " .. string.sub(post.body, 1, 60) .. "...")
else
    print("   Failed: " .. resp.status)
end

print("")
print("2. GET list of users...")
resp = net.get("https://jsonplaceholder.typicode.com/users")
if resp.ok then
    local users = json.decode(resp.body)
    for i = 1, math.min(3, #users) do
        local u = users[i]
        print(string.format("   [%d] %s <%s>", u.id, u.name, u.email))
    end
end

print("")
print("3. POST a new item...")
local newPost = json.encode({
    title  = "My Luah Post",
    body   = "Posted from Luah!",
    userId = 1,
})
resp = net.post("https://jsonplaceholder.typicode.com/posts", newPost)
if resp.ok then
    local created = json.decode(resp.body)
    print("   Created with id: " .. tostring(created.id))
    print("   Title: " .. created.title)
end

print("")
print("4. Download and inspect headers...")
resp = net.get("https://httpbin.org/headers")
if resp.ok then
    local data = json.decode(resp.body)
    print("   User-Agent: " .. tostring(data.headers["User-Agent"]))
end

print("")
print("Done!")
