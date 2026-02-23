local win = graphix.newWindow(700, 500, "Asteroids")
win:setBackground(5, 5, 15)

local W, H = 700, 500
local ship  = {x=350, y=250, angle=0, vx=0, vy=0}
local bullets = {}
local asteroids = {}
local particles = {}
local score = 0
local lives = 3
local shootTimer = 0

math.randomseed(os.time())

local function spawnAsteroid(size)
    local side = math.random(1, 4)
    local x, y
    if side == 1 then x, y = math.random(0, W), 0
    elseif side == 2 then x, y = W, math.random(0, H)
    elseif side == 3 then x, y = math.random(0, W), H
    else x, y = 0, math.random(0, H) end
    local angle = math.random() * math.pi * 2
    local spd   = math.random(40, 100) / (size or 3)
    table.insert(asteroids, {
        x=x, y=y, size=size or 3,
        vx=math.cos(angle)*spd, vy=math.sin(angle)*spd,
        rot=math.random()*math.pi*2, rotspd=math.random()-0.5,
    })
end

for i = 1, 5 do spawnAsteroid(3) end

local function spawnParticle(x, y, r, g, b)
    for i = 1, 8 do
        local angle = math.random() * math.pi * 2
        local spd   = math.random(30, 150)
        table.insert(particles, {
            x=x, y=y, vx=math.cos(angle)*spd, vy=math.sin(angle)*spd,
            life=1, r=r, g=g, b=b,
        })
    end
end

win:onUpdate(function(dt)
    local turnSpd = 3.5
    if win:isKeyDown("left")  then ship.angle = ship.angle - turnSpd * dt end
    if win:isKeyDown("right") then ship.angle = ship.angle + turnSpd * dt end
    if win:isKeyDown("up") then
        ship.vx = ship.vx + math.cos(ship.angle) * 200 * dt
        ship.vy = ship.vy + math.sin(ship.angle) * 200 * dt
    end
    local maxSpd = 300
    local spd = math.sqrt(ship.vx*ship.vx + ship.vy*ship.vy)
    if spd > maxSpd then
        ship.vx = ship.vx / spd * maxSpd
        ship.vy = ship.vy / spd * maxSpd
    end
    ship.vx = ship.vx * (1 - 0.5 * dt)
    ship.vy = ship.vy * (1 - 0.5 * dt)
    ship.x = (ship.x + ship.vx * dt) % W
    ship.y = (ship.y + ship.vy * dt) % H

    shootTimer = shootTimer - dt
    if win:isKeyDown("space") and shootTimer <= 0 then
        shootTimer = 0.2
        table.insert(bullets, {
            x = ship.x + math.cos(ship.angle) * 14,
            y = ship.y + math.sin(ship.angle) * 14,
            vx = math.cos(ship.angle) * 450,
            vy = math.sin(ship.angle) * 450,
            life = 1.2,
        })
    end

    local aliveBullets = {}
    for _, b in ipairs(bullets) do
        b.x = (b.x + b.vx * dt) % W
        b.y = (b.y + b.vy * dt) % H
        b.life = b.life - dt
        if b.life > 0 then table.insert(aliveBullets, b) end
    end
    bullets = aliveBullets

    local aliveAsteroids = {}
    for _, a in ipairs(asteroids) do
        a.x = (a.x + a.vx * dt) % W
        a.y = (a.y + a.vy * dt) % H
        a.rot = a.rot + a.rotspd * dt
        local aradius = a.size * 12
        local hit = false
        local aliveBullets2 = {}
        for _, b in ipairs(bullets) do
            local dx, dy = b.x - a.x, b.y - a.y
            if math.sqrt(dx*dx + dy*dy) < aradius then
                hit = true
                spawnParticle(a.x, a.y, 200, 150, 80)
                score = score + (4 - a.size) * 10
                if a.size > 1 then
                    spawnAsteroid(a.size - 1)
                    spawnAsteroid(a.size - 1)
                end
            else
                table.insert(aliveBullets2, b)
            end
        end
        bullets = aliveBullets2
        if not hit then table.insert(aliveAsteroids, a) end
    end
    asteroids = aliveAsteroids

    local aliveParticles = {}
    for _, p in ipairs(particles) do
        p.x = p.x + p.vx * dt
        p.y = p.y + p.vy * dt
        p.vx = p.vx * (1 - 2*dt)
        p.vy = p.vy * (1 - 2*dt)
        p.life = p.life - dt
        if p.life > 0 then table.insert(aliveParticles, p) end
    end
    particles = aliveParticles

    if #asteroids == 0 then
        for i = 1, 6 do spawnAsteroid(3) end
    end
end)

win:onDraw(function()
    for _, p in ipairs(particles) do
        local a = p.life
        win:fillCircle(p.x, p.y, 2, math.floor(p.r*a), math.floor(p.g*a), math.floor(p.b*a))
    end

    for _, a in ipairs(asteroids) do
        local rad = a.size * 12
        win:drawCircle(a.x, a.y, rad, 160, 120, 80, 2)
        win:drawCircle(a.x, a.y, rad-4, 120, 90, 60, 1)
    end

    for _, b in ipairs(bullets) do
        win:fillCircle(b.x, b.y, 3, 255, 255, 100)
    end

    local nx = ship.x + math.cos(ship.angle) * 14
    local ny = ship.y + math.sin(ship.angle) * 14
    local lx = ship.x + math.cos(ship.angle + 2.4) * 10
    local ly = ship.y + math.sin(ship.angle + 2.4) * 10
    local rx = ship.x + math.cos(ship.angle - 2.4) * 10
    local ry = ship.y + math.sin(ship.angle - 2.4) * 10
    win:drawLine(nx, ny, lx, ly, 100, 200, 255, 2)
    win:drawLine(nx, ny, rx, ry, 100, 200, 255, 2)
    win:drawLine(lx, ly, rx, ry, 80, 160, 200, 2)

    win:drawText(10, 10, "Score: " .. score, 200, 200, 255, 14)
    win:drawText(10, 28, "Lives: " .. lives, 200, 255, 200, 14)
    win:drawText(10, 46, "FPS: " .. math.round(win:getFPS()), 120, 120, 180, 12)
    win:drawText(W-200, H-20, "Arrows=turn/thrust  Space=shoot", 80, 80, 120, 11)
end)

win:run(60)
