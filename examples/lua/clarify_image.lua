local clarification = require("clarification")

local options = clarification.defaults()
options.amount = 1.5
options.contrast = 10.0

local output, err = clarification.enhance("clarification", "input.png", "clarified.png", options)
assert(output, err)
print("saved clarified.png")
