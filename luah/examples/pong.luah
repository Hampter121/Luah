-- LuaForge Example: Simple Pong Game
-- Uses graphix for rendering and keyboard input

local win = graphix.newWindow(600, 400, "Pong - LuaForge")
win:setBackground(10, 10, 20)

-- Ball
local bx, by   = 300, 200
local bvx, bvy = 220, 160
local bsize    = 8

-- Paddles
local p1y = 180  -- left  (W/S keys)
local p2y = 180  -- right (Up/Down keys)
local pw, ph = 12, 70
local pspeed = 280

-- Scores
local s1, s2 = 0, 0

local function resetBall()
    bx, by   = 300, 200
    bvx, bvy = 220 * math.sign(bvx), 160
end

win:onUpdate(function(dt)
    -- Move paddles
    if win:isKeyDown("w")    then p1y = p1y - pspeed * dt end
    if win:isKeyDown("s")    then p1y = p1y + pspeed * dt end
    if win:isKeyDown("up")   then p2y = p2y - pspeed * dt end
    if win:isKeyDown("down") then p2y = p2y + pspeed * dt end

    p1y = math.clamp(p1y, 0, 400 - ph)
    p2y = math.clamp(p2y, 0, 400 - ph)

    -- Move ball
    bx = bx + bvx * dt
    by = by + bvy * dt

    -- Wall bounce (top/bottom)
    if by - bsize < 0   then by = bsize;        bvy = math.abs(bvy) end
    if by + bsize > 400 then by = 400 - bsize;  bvy = -math.abs(bvy) end

    -- Paddle collision (left)
    if bx - bsize < 20 + pw and by > p1y and by < p1y + ph then
        bx = 20 + pw + bsize
        bvx = math.abs(bvx) * 1.05
        bvy = bvy + (by - (p1y + ph/2)) * 2
    end

    -- Paddle collision (right)
    if bx + bsize > 600 - 20 - pw and by > p2y and by < p2y + ph then
        bx = 600 - 20 - pw - bsize
        bvx = -math.abs(bvx) * 1.05
        bvy = bvy + (by - (p2y + ph/2)) * 2
    end

    -- Score
    if bx < 0   then s2 = s2 + 1; resetBall() end
    if bx > 600 then s1 = s1 + 1; resetBall() end

    -- Clamp speed
    local spd = math.sqrt(bvx*bvx + bvy*bvy)
    if spd > 500 then
        bvx = bvx / spd * 500
        bvy = bvy / spd * 500
    end
end)

win:onDraw(function()
    -- Centre line
    for y = 0, 400, 20 do
        win:fillRect(298, y, 4, 10, 50, 50, 70)
    end

    -- Paddles
    win:fillRect(20,       p1y, pw, ph, 100, 200, 255)
    win:fillRect(600-20-pw, p2y, pw, ph, 255, 120, 100)

    -- Ball
    win:fillCircle(bx, by, bsize, 255, 255, 255)

    -- Scores
    win:drawText(220, 20, tostring(s1), 100, 200, 255, 36)
    win:drawText(320, 20, tostring(s2), 255, 120, 100, 36)

    -- Controls help
    win:drawText(10, 375, "W/S", 100, 200, 255, 11)
    win:drawText(550, 375, "↑/↓", 255, 120, 100, 11)
    win:drawText(240, 375, "FPS: " .. math.round(win:getFPS()), 80, 80, 100, 11)
end)

win:run(60)
