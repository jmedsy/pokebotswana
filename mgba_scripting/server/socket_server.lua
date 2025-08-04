--[[
	Input instructions are sent from the client as serialized bitmasks. This is the decimal equivalent
	of a binary string in which the state of each key is represented by its associated bit (1 or 0, pressed or released).
	Passing instructions in this way is efficient, and also allows for multiple keys to be changed with a single bitmask.
	These are distinguished from other messages by also being prefixed with a specific control character.

	Basic host/client communication (see functions ST_*) is based loosely on mGBA test script(s) from official repo.
]]

--[[ begin section Bitmask Utilities ]]
local PK_KEY_STATE_CTRL_CHAR = "\x01"

function PK_is_valid_key_state_bitmask_str(ks_str)
	-- Check if string starts with control character. Otherwise,
	-- it is assumed to be a general message and not a key state.
	if string.sub(ks_str, 1, 1) == PK_KEY_STATE_CTRL_CHAR then
		return true
	else
		return false
	end
end

function PK_handle_key_state_bitmask(ks_bitmask)
	-- Remove control character and convert to number
    local bitmask = tonumber(string.sub(ks_bitmask, 2))
    -- console:log("Received bitmask: " .. bitmask)
    emu:setKeys(bitmask)
end
--[[ end section Bitmask Utilities ]]

--[[ begin section Repurposed mGBA Example Scripts Code ]]
server = nil
ST_sockets = {}
nextID = 1

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

			-- Added to mGBA official socket communication example to handle bitmask messages.
			local messages = p:gmatch("[^\n]+")
			for message in messages do
				if PK_is_valid_key_state_bitmask_str(message) then
					PK_handle_key_state_bitmask(message)
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

--[[ begin Main loop ]]
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
--[[ end Main loop ]]
--[[ end section Repurposed mGBA Example Scripts Code ]]