-- related server url
-- @see server.py
local host = "http://192.168.1.14:8000"

local function live(project)
    -- liveCodea V 0.1
    -- TODO: documentation ?
    ------------------------

    local project = project
    local project_host = string.gsub(host.."/"..project.."/", "% ", "%%20")
    local connected, watches, handle_response, handle_fail, start_polling, stop_polling, poll, connect, eval, log, live_id
 
    local function add_liveswitch()
        -- TODO: think how to deal with polling and that parameter
        local enabled = connected
        parameter.boolean("liveEnabled", enabled,
                function(flag)
                    if flag ~= connected then
                        if flag then start_polling() else stop_polling() end
                    end
                end)
    end

    -- Overrides
    -- hooks into base object(s) and function(s)
    -------------

    -- @class function
    -- In order to return a custom metatable applied to 'new object'
    -- this metatable is intended to serve the base referenced before the incoming eval    
    local o_class = class
    local mt = {
        __call = function(class_tbl, ...)
            local info = debug.getinfo(1, "n")
            local name = info.name obj = {} prp = {}
            local mtf = {
                    __index = function (t,k)
                        if prp[k] then return prp[k] end
                        return _G[name][k]
                    end,
                    __newindex = function (t,k,v)
                        prp[k] = v
                    end
                }
            setmetatable(obj,mtf)
            if class_tbl.init then
                class_tbl.init(obj,...)
            else 
                -- make sure that any stuff from the base class is initialized!
                if base and base.init then
                    base.init(obj, ...)
                end
            end

            return obj
        end
    }
    function class(base)
        c = o_class(base)
        setmetatable(c, mt)
        return c
    end

    -- @parameter methods
    local p_clear = parameter.clear
    parameter.clear = function()
        -- Inject additional start/stop polling parameter.
        -- Until opened http requests would crash Codea, we must have this ro stop
        -- polling before return to the ide
        p_clear()        
        watches = nil -- maybe bad choice
        add_liveswitch()        
    end
    local p_watch = parameter.watch
    parameter.watch = function(exp)
        -- Catch watched properties to send to the server
        p_watch(exp)
        if not watches then watches = {} end
        table.insert(watches, loadstring("return "..exp))
    end

    -- @print function
    local o_print = print
    function print(...)
        -- copy to log
        o_print(unpack(arg))
        local log = log
        log(unpack(arg))
    end
    -------------------

    -------------------
    -- Core methods

    function log(...)
        -- For now send output to remote
        -- TODO: buffer, correct serialization

        local parg = {}
        for _,v in ipairs(arg) do
            table.insert(parg, tostring(v))
        end
        local str_log = table.concat(parg, " ")        
        local params = { method = "POST", data = str_log }
        local function fn() end
        http.request(project_host.."log", fn, fn, params)
    end

    function eval(data)
        -- Eval string code
        -- TODO return state / error        
         local s, f = pcall(assert, loadstring(data))
         if s then        
            f = setfenv(f, _G)
            return pcall(f)
         else
            print(f)
         end
    end

    function handle_response(data, status, headers)
        -- Handle requests and continue polling        
        -- TODO: implements dedicated method based on the status
        -- (do_200, do_304..) or headers ?

        if status == 200 then
            local key = headers["Content-Tab"]
            if key then
                if headers["Content-Update"] == "save" then
                    saveProjectTab(key, data)
                    log("Tab saved", key)
                elseif headers["Content-Update"] == "doc-save" then
                    saveImage(key, data)
                    log("Doc saved > ", key)
                end
            end
            if headers["Content-Eval"] == "eval" then
                local s,f = eval(data)
                if not s then
                    log(f)
                end
            end
        elseif status ~= 304 then
            -- TODO
        end
        return true
    end

    function handle_fail(msg)
        -- Handle fail response        
        print(msg)
        return true
    end

    function poll()
        -- TODO: implements "talk" with server

        if readGlobalData("live_id") ~= live_id then
            log("Stop live", live_id)
            connected = false
        end
        if connected then
            local function fnS(d, s, h)
                if handle_response(d,s,h) then poll() end
            end
            local function fnF(msg)
                if handle_fail(msg) then poll() end
            end
            http.request(project_host.."changes", fnS, nfF)
        end
    end

    function start_polling()
        connected = true
        liveEnabled = true
        poll()
    end

    function stop_polling()
        connected = false
        liveEnabled = false
    end

    function connect(callback)
        -- Send project with it's dependencies to remote

        local tabs = {} tabs_content = {}
        local function send_tab(ind)
            local ind = ind or 1 tabs = listProjectTabs(project) tab = tabs[ind]
            if tab then                
                local function onF(msg)
                    print(msg)
                end
                local function onC(d,s,h)
                    if s == 200 or s == 201 or s == 301 then
                        if s == 301 then
                            -- Todo resource moved
                        end
                        ind = ind + 1
                        send_tab(ind)
                    else onF("Unable to send "..tab) end
                end
                local d = readProjectTab(project..":"..tab)
                table.insert(tabs_content,d)
                local p = { method = "PUT", data = d }
                -- local project_host = string.gsub(host.."/"..project.."/", "% ", "%%20")
                http.request(project_host..tab, onC, onF, p)
            else
                -- For now we assume that all tabs are up to date
                -- TODO handle diffs files
                callback(table.concat(tabs_content,"\n"))
            end
        end

        send_tab()

        -- local headers = { session = live_id }
        -- local p = { method = "HEADER", headers = headers }
        -- http.request(project_host..tab, onC, onF, p)
    end    

    --  TODO: Expose api ?
    --[[
    _G.livecodea = {
        connect = connect
        stop_polling = stop_polling,
        response_hook...
    }
    --]]

    -- Here we go! 
    connect(function(tabs_content)
        -- We must rely on this in order to stop "old" runing instance(s)
        -- @bug http request polling stay alive
        local d = os.date("*t")
        live_id = tostring(d.yday..":"..d.hour..d.min..d.sec)
        log("Run live", live_id)
        saveGlobalData("live_id", live_id) 
        start_polling()
        add_liveswitch()
        eval(tabs_content)
        -- for _,v in pairs(success) do
        --     eval(v)
        -- end
        setup()
    end)

end



-- App start hook
-----------------
local o_setup
debug.sethook(function(e)
    -- TODO: dig into the startup process
    -- why when new tab created in 'live mode' delay the read
    -- of the Main tab ?
    if not o_setup and setup then
        o_setup = setup
        setup = function() end
        draw = function() end
            -- background(0)
            -- local lw = 10 msg = "loading project"
            -- local x = WIDTH/2-(#msg*lw/2) y = HEIGHT/2
            -- fill(255)
            -- fontSize(20)        
            -- for i=1,#msg do
            --     local freq = math.sin(ElapsedTime * (i+10%20))
            --     text(string.sub(msg,i,i), x+(lw*i), y+freq)
            -- end
    end

    local status, tab = pcall(readProjectTab, "Main")
    if o_setup and status then
        debug.sethook()
        local project = string.match(tab, "^%--%s(.-)\n")
        if project and string.len(project) > 1 then
            live(project)
        else
            print("You must set a the project name as a comment on top of the Main tab in order to run live")
            print("ex: -- MyProjectName")
        end
    end
end, "r")