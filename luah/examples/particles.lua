local win = graphix.newWindow(700, 500, "Particles - LuaForge")
win:setBackground(5, 5, 15)

local particles = {}
local MAX = 500

local function spawnParticle(x, y)
    if #particles >= MAX then table.remove(particles, 1) end
    local angle = math.random() * math.pi * 2
    local speed = math.random(80, 250)
    table.insert(particles, {
        x=x, y=y,
        vx = math.cos(angle) * speed,
        vy = math.sin(angle) * speed - 100,
        life = 1.0,
        maxlife = 0.8 + math.random() * 1.2,
        r = math.random(150, 255),
        g = math.random(50, 200),
        b = math.random(50, 255),
        size = math.random(3, 8),
    })
end

win:onUpdate(function(dt)
    local mx, my = win:getMousePos()

    if win:isMouseDown(1) then
        for i = 1, 5 do spawnParticle(mx, my) end
    end

    -- Auto-spawn from center when idle
    if not win:isMouseDown(1) then
        spawnParticle(350, 250)
    end

    local alive = {}
    for _, p in ipairs(particles) do
        p.x    = p.x + p.vx * dt
        p.y    = p.y + p.vy * dt
        p.vy   = p.vy + 150 * dt   -- gravity
        p.vx   = p.vx * (1 - dt * 0.8) -- drag
        p.life = p.life - dt / p.maxlife
        if p.life > 0 then table.insert(alive, p) end
    end
    particles = alive
end)

win:onDraw(function()
    for _, p in ipairs(particles) do
        local a   = p.life
        local sz  = math.floor(p.size * a)
        if sz < 1 then sz = 1 end
        local r = math.floor(p.r * a)
        local g = math.floor(p.g * a)
        local b = math.floor(p.b * a)
        win:fillCircle(p.x, p.y, sz, r, g, b)
    end

    win:drawText(10, 10, "Particles: " .. #particles, 150, 150, 200, 13)
    win:drawText(10, 28, "FPS: " .. math.round(win:getFPS()), 150, 150, 200, 13)
    win:drawText(10, 460, "Click to spawn particles!", 100, 100, 150, 12)
end)

win:run(60)
