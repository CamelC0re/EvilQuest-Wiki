local p = {}

-- Natively load and decode the NPC JSON subpage
local npcs = mw.loadJsonData('Module:NPCData/json')

function p.fetchNpcData(frame)
    local rawTitle = frame.args[1] or frame:getParent().args['name'] or mw.title.getCurrentTitle().text
    local targetField = frame.args['field']

    if not targetField then
        return "Error: Missing 'field' parameter."
    end

    -- Use Lua Pattern Matching to extract "Skeleton Warrior" and "28" from "Skeleton Warrior (Lvl 28)"
    local baseName, targetLevel = string.match(rawTitle, "^(.-)%s*%(Lvl (.-)%)$")
    
    -- If the pattern didn't match (e.g. standard "Chicken"), fallback to the full title
    if not baseName then
        baseName = rawTitle
    end

    for _, npc in ipairs(npcs) do
        if npc.name == baseName then
            -- If a specific level was requested in the URL, verify it matches the JSON entry
            if targetLevel then
                if tostring(npc.combatLevel or "??") == targetLevel then
                    return p.formatValue(npc[targetField])
                end
            else
                -- If no level was requested in the URL, return the first match we find
                return p.formatValue(npc[targetField])
            end
        end
    end
    
    return "" 
end

-- Helper function to sanitize types for MediaWiki templates
function p.formatValue(value)
    if value == nil then
        return "" 
    elseif type(value) == "boolean" then
        return value and "Yes" or "No" 
    else
        return tostring(value)
    end
end

-- Master Index Table (Automatically handles Disambiguation Links!)
function p.renderNPCTable(frame)
    -- Pre-scan array to find duplicates so we generate correct wiki links
    local nameCounts = {}
    for _, npc in ipairs(npcs) do
        nameCounts[npc.name] = (nameCounts[npc.name] or 0) + 1
    end

    local html = '<table class="wikitable sortable" style="width: 100%; border-collapse: collapse; margin-top: 1em;">\n'
    html = html .. '<tr style="background-color: #5c1d1d; color: white;">'
    html = html .. '<th style="width: 80px;">ID</th>'
    html = html .. '<th>Name</th>'
    html = html .. '<th>Examine</th>'
    html = html .. '<th style="width: 100px;">Combat Lvl</th>'
    html = html .. '</tr>\n'
    
    for _, npc in ipairs(npcs) do
        -- Dynamically route the link: [[Skeleton Warrior (Lvl 28)|Skeleton Warrior]]
        local linkTitle = npc.name
        if nameCounts[npc.name] > 1 then
            linkTitle = npc.name .. " (Lvl " .. tostring(npc.combatLevel or '??') .. ")"
        end
        
        html = html .. '<tr>'
        html = html .. '<td>' .. npc.id .. '</td>'
        html = html .. '<td style="font-weight: bold;">[[' .. linkTitle .. '|' .. npc.name .. ']]</td>'
        html = html .. '<td style="font-style: italic; color: #555;">"' .. (npc.examineText or "") .. '"</td>'
        html = html .. '<td data-sort-value="' .. (npc.combatLevel or 0) .. '">' .. (npc.combatLevel or '—') .. '</td>'
        html = html .. '</tr>\n'
    end
    
    html = html .. '</table>'
    return html
end

return p
