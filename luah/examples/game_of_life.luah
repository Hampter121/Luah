local W, H   = 800, 600
local CELL   = 10
local COLS   = W / CELL
local ROWS   = H / CELL
local win    = graphix.newWindow(W, H, "Game of Life")
win:setBackground(10, 10, 20)

local grid = {}
local next = {}

local function makeGrid()
    local g = {}
    for r = 1, ROWS do
        g[r] = {}
        for c = 1, COLS do
            g[r][c] = 0
        end
    end
    return g
end

local function randomize()
    for r = 1, ROWS do
        for c = 1, COLS do
            grid[r][c] = math.random() < 0.3 and 1 or 0
        end
    end
end

grid = makeGrid()
next = makeGrid()
randomize()

local generation = 0
local stepTimer  = 0
local stepRate   = 0.08
local paused     = false
local population = 0

local function countNeighbors(r, c)
    local count = 0
    for dr = -1, 1 do
        for dc = -1, 1 do
            if not (dr == 0 and dc == 0) then
                local nr = ((r - 1 + dr) % ROWS) + 1
                local nc = ((c - 1 + dc) % COLS) + 1
                count = count + grid[nr][nc]
            end
        end
    end
    return count
end

win:onUpdate(function(dt)
    if win:isKeyDown("space") and dt > 0 then
        paused = not paused
        wait(0.2)
    end
    if win:isKeyDown("r") then
        randomize()
        generation = 0
        wait(0.2)
    end

    if paused then return end

    stepTimer = stepTimer + dt
    if stepTimer < stepRate then return end
    stepTimer = 0

    population = 0
    for r = 1, ROWS do
        for c = 1, COLS do
            local alive     = grid[r][c]
            local neighbors = countNeighbors(r, c)
            if alive == 1 then
                next[r][c] = (neighbors == 2 or neighbors == 3) and 1 or 0
            else
                next[r][c] = neighbors == 3 and 1 or 0
            end
            population = population + next[r][c]
        end
    end

    local tmp = grid
    grid = next
    next = tmp
    generation = generation + 1
end)

win:onDraw(function()
    for r = 1, ROWS do
        for c = 1, COLS do
            if grid[r][c] == 1 then
                local rr = math.floor(80 + (r / ROWS) * 100)
                local gg = math.floor(180 + (c / COLS) * 75)
                local bb = math.floor(100 + (r + c) / (ROWS + COLS) * 155)
                win:fillRect((c-1)*CELL+1, (r-1)*CELL+1, CELL-2, CELL-2, rr, gg, bb)
            end
        end
    end

    win:drawText(8, 8,  "Generation: " .. generation, 200, 255, 200, 12)
    win:drawText(8, 24, "Population: " .. population, 200, 255, 200, 12)
    win:drawText(8, 40, "FPS: " .. math.round(win:getFPS()), 150, 200, 150, 12)
    if paused then
        win:drawText(8, 56, "PAUSED", 255, 200, 50, 12)
    end
    win:drawText(W-240, H-18, "Space=pause  R=randomize", 80, 120, 80, 11)
end)

win:run(60)
