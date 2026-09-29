local state = {
    enabled = true,
    profile = 'quality',
    modifier = nil,
    rainExtra = nil,
    interior = false,
}

local rainHashes

local function notify(message)
    TriggerEvent('chat:addMessage', {
        color = { 186, 196, 206 },
        multiline = false,
        args = { 'Gráficos', message },
    })
end

local function defaultProfile()
    local fromKvp = GetResourceKvpString('fgm_profile')
    local normalized = GraphicsProfiles.normalize(fromKvp or '')
    if normalized and normalized ~= 'off' then
        return normalized
    end
    if normalized == 'off' then
        return 'off'
    end
    normalized = GraphicsProfiles.normalize(GetConvar('fgm_profile', 'quality'))
    if normalized == 'off' then
        return 'off'
    end
    return normalized or 'quality'
end

local function rainLevel()
    local level = GetRainLevel() or 0.0
    local weather = GetPrevWeatherTypeHashName()
    if weather == rainHashes.thunder then
        level = math.max(level, 0.75)
    elseif weather == rainHashes.rain then
        level = math.max(level, 0.55)
    elseif weather == rainHashes.clearing then
        level = math.max(level, 0.22)
    end
    return level
end

local function applyLook()
    if not state.enabled then
        return
    end

    local ped = PlayerPedId()
    local hour = GetClockHours()
    local period = GraphicsProfiles.periodForHour(hour)
    local level = rainLevel()
    local raining = level >= Config.rainThreshold
    local interior = GetInteriorFromEntity(ped) ~= 0
    state.interior = interior

    local name = GraphicsProfiles.modifierName(state.profile, period)
    local strengthKey = GraphicsProfiles.strengthKey(period)
    local strength = Config.strength[state.profile][strengthKey] or 0.7
    if interior then
        strength = strength * Config.interiorStrengthScale
    end

    if name ~= state.modifier then
        SetTransitionTimecycleModifier(name, 2.8)
        state.modifier = name
    end
    SetTimecycleModifierStrength(strength + 0.0)

    if raining and not interior then
        local extra = GraphicsProfiles.rainExtra(state.profile)
        local extraStrength = (Config.strength[state.profile].rain or 0.5) * math.min(level + 0.2, 1.0)
        if extra ~= state.rainExtra then
            SetExtraTimecycleModifier(extra)
            state.rainExtra = extra
        end
        SetExtraTimecycleModifierStrength(extraStrength + 0.0)
    elseif state.rainExtra then
        ClearExtraTimecycleModifier()
        state.rainExtra = nil
    end

    GraphicsVisuals.apply(state.profile, raining and not interior)
    local drops = Config.engine[state.profile].screenDrops
    if IsPedInAnyVehicle(ped, false) then
        drops = math.floor(drops * 0.55)
        level = level * 0.75
    end
    GraphicsScreen.pushRain(raining and not interior, level, drops)
end

local function setProfile(profile, persist)
    if profile == 'off' then
        state.enabled = false
        state.profile = 'off'
        state.modifier = nil
        state.rainExtra = nil
        GraphicsVisuals.clear()
        GraphicsScreen.hide()
    else
        local wasOff = not state.enabled
        state.enabled = true
        state.profile = profile
        state.modifier = nil
        state.rainExtra = nil
        if wasOff then
            GraphicsVisuals.installTimecycles()
        end
        applyLook()
    end

    if persist then
        SetResourceKvp('fgm_profile', profile == 'off' and 'off' or profile)
    end
end

local function statusText()
    if not state.enabled then
        return 'Pacote desligado. O visual do jogo volta ao conjunto de restauração.'
    end
    local period = GraphicsProfiles.periodForHour(GetClockHours())
    local wet = (GetRainLevel() or 0.0) >= Config.rainThreshold
    return ('Perfil %s, período %s%s.'):format(
        GraphicsProfiles.label(state.profile),
        period,
        wet and ', chuva ativa' or ''
    )
end

RegisterCommand('grafico', function(_, args)
    local raw = args[1]
    if raw == nil or raw == 'status' then
        notify(statusText())
        return
    end

    local profile = GraphicsProfiles.normalize(raw)
    if not profile then
        notify('Use /grafico quality, /grafico performance, /grafico desligar ou /grafico status.')
        return
    end

    setProfile(profile, true)
    notify('Perfil ' .. GraphicsProfiles.label(profile) .. ' aplicado.')
end, false)

CreateThread(function()
    rainHashes = {
        rain = GetHashKey('RAIN'),
        thunder = GetHashKey('THUNDER'),
        clearing = GetHashKey('CLEARING'),
    }

    TriggerEvent('chat:addSuggestion', '/grafico', 'Controla o pacote gráfico', {
        { name = 'perfil', help = 'quality | performance | desligar | status' },
    })

    local initial = defaultProfile()
    if initial == 'off' then
        state.enabled = false
        state.profile = 'off'
        return
    end

    GraphicsVisuals.installTimecycles()
    setProfile(initial, false)
    GraphicsScreen.resetVitals()

    while true do
        if state.enabled then
            applyLook()
            Wait(700)
        else
            Wait(1000)
        end
    end
end)

CreateThread(function()
    while true do
        if state.enabled and Config.screen.blood then
            GraphicsScreen.pushVitals(PlayerPedId())
            Wait(150)
        else
            Wait(500)
        end
    end
end)

AddEventHandler('onClientResourceStop', function(resourceName)
    if resourceName ~= GetCurrentResourceName() then
        return
    end
    GraphicsVisuals.clear()
    GraphicsScreen.hide()
end)

exports('setProfile', function(name)
    local profile = GraphicsProfiles.normalize(name or '')
    if not profile then
        return false
    end
    setProfile(profile, true)
    return true
end)

exports('getProfile', function()
    if not state.enabled then
        return 'off'
    end
    return state.profile
end)
