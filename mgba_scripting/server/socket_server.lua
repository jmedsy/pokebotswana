--[[ Usage Notes:

	Instructions are sent from the client as a bitmask string, which is prefixed with
	a control character to distinguish it from other messages. For clarity/debugging,
	you can alternatively use the key state factory to see a human-readable key state,
	and its binary equivalent, for a clearer (and less efficient) look at what's going on.

	This alternative path is noted in ST_received().
]]

--[[ begin Key Management Definitions ]]

local PK_KEY_STATE_CTRL_CHAR = "\x01"

function pk_is_valid_key_state_bitmask_str(ks_str)
	-- Check if string starts with control character. Otherwise,
	-- it is assumed to be a general message and not a key state.
	if string.sub(ks_str, 1, 1) == PK_KEY_STATE_CTRL_CHAR then
		return true
	else
		return false
	end
end

function pk_handle_key_state_bitmask(ks_bitmask)
	-- Remove control character and convert to number
    local bitmask = tonumber(string.sub(ks_bitmask, 2))
    -- console:log("Received bitmask: " .. bitmask)
    emu:setKeys(bitmask)
end

-- Optional, alternative path for clarity/debugging

-- Make sure order and number of keys matches that specified in client code
local PK_KEY_NAMES = { "A", "B", "SELECT", "START", "RIGHT", "LEFT", "UP", "DOWN", "R", "L" }
local PK_KEY_NAMES_LEN = #PK_KEY_NAMES

function pk_create_inert_key_state()
	local iks = {}
	for _, v in ipairs(PK_KEY_NAMES) do
		iks[v] = false
	end
	return iks
end

function pk_key_state_factory(ks_string)
	if ks_string == nil then
		return pk_create_inert_key_state()
	else
		local manufactured_ks = pk_create_inert_key_state()
		local binary_bitmask_str = to_binary_string(tonumber(string.sub(ks_string, 2)))
		-- Each bit in the binary string represents a key in the PK_KEY_NAMES array.
		-- The binary string is read right to left, so the first bit represents the last key in the PK_KEY_NAMES array.
		-- The last bit represents the first key in the PK_KEY_NAMES array.
		console:log("Binary bitmask: " .. binary_bitmask_str)
		for i = #binary_bitmask_str, 1, -1 do  -- Right to left
			local key_switch = string.sub(binary_bitmask_str, i, i)
			local key_index = #binary_bitmask_str - i + 1  -- Convert position
			manufactured_ks[PK_KEY_NAMES[key_index]] = key_switch == "1"
		end
		return manufactured_ks
	end
end

function to_binary_string(decimal)
    local result = ""
    local num = decimal
    while num > 0 do
        result = (num % 2) .. result
        num = math.floor(num / 2)
    end
    -- Pad with leading zeros to however many bits are needed
    while #result < #PK_KEY_NAMES do
        result = "0" .. result
    end
    return result
end

function pk_handle_key_state(ks)

	-- If you want to see the human-readable key state,
	-- you can toss some debug code in here.

	if ks["A"] then
		emu:addKey(C.GBA_KEY.A)
	else
		emu:clearKey(C.GBA_KEY.A)
	end
	if ks["B"] then
		emu:addKey(C.GBA_KEY.B)
	else
		emu:clearKey(C.GBA_KEY.B)
	end
	if ks["SELECT"] then
		emu:addKey(C.GBA_KEY.SELECT)
	else
		emu:clearKey(C.GBA_KEY.SELECT)
	end
	if ks["START"] then
		emu:addKey(C.GBA_KEY.START)
	else
		emu:clearKey(C.GBA_KEY.START)
	end
	if ks["LEFT"] then
		emu:addKey(C.GBA_KEY.LEFT)
	else
		emu:clearKey(C.GBA_KEY.LEFT)
	end
	if ks["RIGHT"] then
		emu:addKey(C.GBA_KEY.RIGHT)
	else
		emu:clearKey(C.GBA_KEY.RIGHT)
	end
	if ks["UP"] then
		emu:addKey(C.GBA_KEY.UP)
	else
		emu:clearKey(C.GBA_KEY.UP)
	end
	if ks["DOWN"] then
		emu:addKey(C.GBA_KEY.DOWN)
	else
		emu:clearKey(C.GBA_KEY.DOWN)
	end
	if ks["R"] then
		emu:addKey(C.GBA_KEY.R)
	else
		emu:clearKey(C.GBA_KEY.R)
	end
	if ks["L"] then
		emu:addKey(C.GBA_KEY.L)
	else
		emu:clearKey(C.GBA_KEY.L)
	end
end

--[[ end section Key Management Definitions ]]

lastkeys = nil
server = nil
ST_sockets = {}
nextID = 1

local KEY_NAMES = { "A", "B", "s", "S", ">", "<", "^", "v", "R", "L" }

function ST_stop(id)
	local sock = ST_sockets[id]
	ST_sockets[id] = nil
	sock:close()
end

function ST_format(id, msg, isError)
	local prefix = "Socket " .. id
	if isError then
		prefix = prefix .. " Error: "
	else
		prefix = prefix .. " Received: "
	end
	return prefix .. msg
end

function ST_error(id, err)
	console:error(ST_format(id, err, true))
	ST_stop(id)
end

function ST_received(id)
	local sock = ST_sockets[id]
	if not sock then return end
	while true do
		local p, err = sock:receive(1024)
		if p then
			console:log(ST_format(id, p:match("^(.-)%s*$")))
			local messages = p:gmatch("[^\n]+")
			for message in messages do

				-- Option 1: Use the bitmask string directly for efficiency
				-- if pk_is_valid_key_state_bitmask_str(message) then
				-- 	pk_handle_key_state_bitmask(message)
				-- end

				-- Option 2:
				--	Comment out Option 1 and use the following instead to deserialize
				--	the key state for a clearer (and less efficient) look at what's going on

				if pk_is_valid_key_state_bitmask_str(message) then
				    pk_handle_key_state(pk_key_state_factory(message))
				end
			end
		else
			if err ~= socket.ERRORS.AGAIN then
				console:error(ST_format(id, err, true))
				ST_stop(id)
			end
			return
		end
	end
end

function ST_scankeys()
	local keys = emu:getKeys()
	if keys ~= lastkeys then
		lastkeys = keys
		local msg = "["
		for i, k in ipairs(KEY_NAMES) do
			if (keys & (1 << (i - 1))) == 0 then
				msg = msg .. " "
			else
				msg = msg .. k;
			end
		end
		msg = msg .. "]\n"
		for id, sock in pairs(ST_sockets) do
			if sock then sock:send(msg) end
		end
	end
end

function ST_accept()
	local sock, err = server:accept()
	if err then
		console:error(ST_format("Accept", err, true))
		return
	end
	local id = nextID
	nextID = id + 1
	ST_sockets[id] = sock
	sock:add("received", function() ST_received(id) end)
	sock:add("error", function() ST_error(id) end)
	console:log(ST_format(id, "Connected"))
end

callbacks:add("keysRead", ST_scankeys)

local port = 8888
server = nil
while not server do
	server, err = socket.bind(nil, port)
	if err then
		if err == socket.ERRORS.ADDRESS_IN_USE then
			port = port + 1
		else
			console:error(ST_format("Bind", err, true))
			break
		end
	else
		local ok
		ok, err = server:listen()
		if err then
			server:close()
			console:error(ST_format("Listen", err, true))
		else
			console:log("Socket Server Test: Listening on port " .. port)
			server:add("received", ST_accept)
		end
	end
end
