local win = graphix.newWindow(600, 600, "Snake")
win:setBackground(10, 20, 10)

local GRID   = 20
local COLS   = 30
local ROWS   = 30
local snake  = {{x=15, y=15}}
local dir    = {x=1, y=0}
local nextDir = {x=1, y=0}
local food   = {x=math.random(0, COLS-1), y=math.random(0, ROWS-1)}
local score  = 0
local dead   = false
local timer  = 0
local speed  = 0.12

local function placeFood()
    food.x = math.random(0, COLS-1)
    food.y = math.random(0, ROWS-1)
end

win:onUpdate(function(dt)
    if dead then return end

    if win:isKeyDown("left")  and dir.x == 0 then nextDir = {x=-1, y=0} end
    if win:isKeyDown("right") and dir.x == 0 then nextDir = {x=1,  y=0} end
    if win:isKeyDown("up")    and dir.y == 0 then nextDir = {x=0,  y=-1} end
    if win:isKeyDown("down")  and dir.y == 0 then nextDir = {x=0,  y=1}  end

    timer = timer + dt
    if timer < speed then return end
    timer = 0

    dir = nextDir
    local head = snake[1]
    local newHead = {x = head.x + dir.x, y = head.y + dir.y}

    if newHead.x < 0 or newHead.x >= COLS or newHead.y < 0 or newHead.y >= ROWS then
        dead = true
        return
    end

    for _, seg in ipairs(snake) do
        if seg.x == newHead.x and seg.y == newHead.y then
            dead = true
            return
        end
    end

    table.insert(snake, 1, newHead)

    if newHead.x == food.x and newHead.y == food.y then
        score = score + 10
        speed = math.max(0.05, speed - 0.002)
        placeFood()
    else
        table.remove(snake)
    end
end)

win:onDraw(function()
    for col = 0, COLS-1 do
        for row = 0, ROWS-1 do
            local shade = (col + row) % 2 == 0 and 18 or 22
            win:fillRect(col*GRID, row*GRID, GRID, GRID, shade, shade+5, shade)
        end
    end

    win:fillRect(food.x*GRID+2, food.y*GRID+2, GRID-4, GRID-4, 255, 80, 80)

    for i, seg in ipairs(snake) do
        local g = math.floor(200 - (i / #snake) * 100)
        win:fillRect(seg.x*GRID+1, seg.y*GRID+1, GRID-2, GRID-2, 50, g, 50)
    end

    win:drawText(10, 10, "Score: " .. score, 200, 255, 200, 14)
    win:drawText(10, 28, "FPS: " .. math.round(win:getFPS()), 100, 180, 100, 12)

    if dead then
        win:fillRect(150, 250, 300, 80, 20, 10, 10)
        win:drawText(170, 265, "GAME OVER!", 255, 80, 80, 24)
        win:drawText(190, 300, "Score: " .. score, 255, 200, 200, 16)
    end
end)

win:run(60)
