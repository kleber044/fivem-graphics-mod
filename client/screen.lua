GraphicsScreen = {}

local lastHealth = nil
local lastArmour = nil

local function maxHealthOf(ped)
    local value = GetEntityMaxHealth(ped)
    if not value or value < 100 then
        return 200
    end
    return value
end

local function lowHealthAmount(health, maximum)
    local span = math.max(maximum - 100, 1)
    local alive = math.max(health - 100, 0) / span
    if alive > 0.45 then
        return 0.0
    end
    return math.min(0.55, ((0.45 - alive) / 0.45) * 0.55)
end

function GraphicsScreen.resetVitals(ped)
    ped = ped or PlayerPedId()
    lastHealth = GetEntityHealth(ped)
    lastArmour = GetPedArmour(ped)
end

function GraphicsScreen.pushRain(active, level, drops)
    SendNUIMessage({
        action = 'rain',
        active = active and Config.screen.rain or false,
        level = level or 0.0,
        drops = drops or 0,
    })
end

function GraphicsScreen.pushVitals(ped)
    if not Config.screen.blood then
        SendNUIMessage({ action = 'lowhealth', amount = 0.0 })
        return
    end

    local health = GetEntityHealth(ped)
    local armour = GetPedArmour(ped)
    local maximum = maxHealthOf(ped)

    if lastHealth == nil then
        lastHealth = health
        lastArmour = armour
    end

    local healthLoss = lastHealth - health
    local armourLoss = (lastArmour or armour) - armour
    local dealt = 0
    if healthLoss >= Config.screen.minDamage then
        dealt = healthLoss
    elseif armourLoss >= Config.screen.minDamage and healthLoss >= 0 then
        dealt = armourLoss * 0.65
    end

    if dealt > 0 and not IsEntityDead(ped) then
        local intensity = math.min(1.0, 0.22 + (dealt / math.max(maximum, 1)) * 2.4)
        SendNUIMessage({
            action = 'damage',
            intensity = intensity,
        })
    end

    lastHealth = health
    lastArmour = armour

    SendNUIMessage({
        action = 'lowhealth',
        amount = lowHealthAmount(health, maximum),
    })
end

function GraphicsScreen.hide()
    SendNUIMessage({ action = 'hide' })
    lastHealth = nil
    lastArmour = nil
end
