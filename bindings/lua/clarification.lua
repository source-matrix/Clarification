-- Clarification Lua binding.
-- Requires the `clarification` binary to be available on PATH.
local M = {}

local function shell_quote(value)
  return "'" .. tostring(value):gsub("'", "'\\''") .. "'"
end

local function command(binary, args)
  local pieces = { shell_quote(binary) }
  for _, value in ipairs(args) do
    table.insert(pieces, shell_quote(value))
  end
  local process = table.concat(pieces, " ")
  local handle = io.popen(process .. " 2>&1")
  if not handle then return nil, "unable to start clarification" end
  local output = handle:read("*a")
  local ok, _, code = handle:close()
  if not ok then return nil, output ~= "" and output or ("process exited with code " .. tostring(code)) end
  return output
end

function M.defaults()
  return {
    radius = 1.2,
    amount = 1.35,
    contrast = 8.0,
    threshold = 2,
    scale = 1.0,
    denoise = 0.12,
    skin_protection = 0.25,
  }
end

function M.portrait()
  return {
    radius = 0.15,
    amount = 6.0,
    contrast = 10.0,
    threshold = 1,
    scale = 4.0,
    denoise = 0.02,
    skin_protection = 0.72,
  }
end

function M.enhance(binary, input, output, options)
  options = options or M.defaults()
  return command(binary or "clarification", {
    "clarify", input, output,
    "--radius", options.radius,
    "--amount", options.amount,
    "--contrast", options.contrast,
    "--threshold", options.threshold,
    "--scale", options.scale or 1.0,
    "--denoise", options.denoise or 0.12,
    "--skin-protection", options.skin_protection or 0.25,
  })
end

function M.enhance_ai(command_name, input, output, realesrgan_weights, gfpgan_weights, options)
  options = options or {}
  return command(command_name or "clarification-ai", {
    input,
    output,
    "--realesrgan-weights", realesrgan_weights,
    "--gfpgan-weights", gfpgan_weights,
    "--face-weight", options.face_weight or 0.50,
    "--eye-blend", options.eye_blend or 0.65,
    "--tile", options.tile or 128,
  })
end

function M.score(binary, input)
  local output, err = command(binary or "clarification", { "score", input })
  if not output then return nil, err end
  return tonumber(output:match("[%d%.]+")), nil
end

return M
