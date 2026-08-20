local clarification = require("clarification")

local output, err = clarification.enhance("target/release/clarification", "tests/fixtures/input.png", "/tmp/clarification-lua.png", clarification.defaults())
assert(output, err)
local score, score_err = clarification.score("target/release/clarification", "/tmp/clarification-lua.png")
assert(score, score_err)
assert(score > 0, "expected a positive detail score")
print(string.format("lua score=%.4f", score))
