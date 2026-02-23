print("=== Luah SQLite Demo ===")
print("")

local conn = db.sqlite("school.db")

conn:exec([[
    CREATE TABLE IF NOT EXISTS students (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT NOT NULL,
        grade   INTEGER,
        score   REAL
    )
]])

conn:exec([[
    CREATE TABLE IF NOT EXISTS courses (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        title   TEXT NOT NULL,
        teacher TEXT
    )
]])

conn:exec("DELETE FROM students")
conn:exec("DELETE FROM courses")

conn:begin()
local students = {
    {"Alice",   10, 95.5},
    {"Bob",     11, 82.0},
    {"Carol",   10, 91.2},
    {"David",   12, 76.8},
    {"Eve",     11, 88.4},
    {"Frank",   12, 99.1},
    {"Grace",   10, 67.3},
}
for _, s in ipairs(students) do
    conn:exec("INSERT INTO students (name, grade, score) VALUES (?, ?, ?)", s)
end
conn:commit()

print("All students:")
local rows = conn:query("SELECT * FROM students ORDER BY score DESC")
for i, row in ipairs(rows) do
    print(string.format("  [%d] %-8s  Grade %d  Score %.1f",
        row.id, row.name, row.grade, row.score))
end

print("")
print("Grade 10 students:")
rows = conn:query("SELECT * FROM students WHERE grade = 10 ORDER BY name")
for i, row in ipairs(rows) do
    print(string.format("  %s (%.1f)", row.name, row.score))
end

print("")
local avg = conn:queryOne("SELECT AVG(score) as avg FROM students")
print(string.format("Class average: %.2f", avg.avg))

local top = conn:queryOne("SELECT * FROM students ORDER BY score DESC LIMIT 1")
print("Top student: " .. top.name .. " with " .. top.score)

print("")
print("Updating Bob's score...")
conn:exec("UPDATE students SET score = 90.0 WHERE name = 'Bob'")
local bob = conn:queryOne("SELECT * FROM students WHERE name = 'Bob'")
print("Bob's new score: " .. bob.score)

print("")
print("Tables in DB:")
local tables = conn:tables()
for i, t in ipairs(tables) do
    print("  " .. t)
end

conn:close()
fs.delete("school.db")
print("")
print("Done! Database cleaned up.")
