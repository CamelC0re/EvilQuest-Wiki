local p = {}

local rareDropTables = mw.loadJsonData('Module:RareDropData/json')
local itemsData = mw.loadJsonData('Module:ItemData/json')

-- Helper to quickly find an item's name by its ID
local function getItemName(itemId)
    for _, item in ipairs(itemsData) do
        if item.id == itemId then
            return item.name
        end
    end
    return "Unknown Item (" .. tostring(itemId) .. ")"
end

-- Helper to find a rare drop table's name by its ID
local function getTableName(tableId)
    for _, t in ipairs(rareDropTables) do
        if t.id == tableId then
            return t.name
        end
    end
    return "Unknown Table (" .. tostring(tableId) .. ")"
end

-- Helper to find a rare drop table by its ID
local function getTable(tableId)
    for _, t in ipairs(rareDropTables) do
        if t.id == tableId then
            return t
        end
    end
    return nil
end

function p.renderTable(frame)
    local targetTableId = frame.args[1] or frame:getParent().args[1]
    if not targetTableId then return "Error: Missing table ID" end

    local out = '{| class="wikitable sortable"\n! Item\n! Amount\n! Rate\n'
    local t = getTable(targetTableId)
    
    if t and t.entries then
        for _, entry in ipairs(t.entries) do
            if entry.type == "item" then
                local itemName = getItemName(entry.itemId)
                local amount = entry.amount or 1
                local rate = entry.rate or "Rare"

                -- Build the raw wikitext table row
                out = out .. "|-\n"
                out = out .. "| [[" .. itemName .. "]]\n"
                out = out .. "| " .. amount .. "\n"
                if tonumber(rate) then
                    out = out .. "| " .. rate .. "%\n"
                else
                    out = out .. "| " .. rate .. "\n"
                end
            end
        end
    end
    
    out = out .. "|}"
    return out
end

return p
