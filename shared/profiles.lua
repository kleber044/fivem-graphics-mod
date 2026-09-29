GraphicsProfiles = {}

local aliases = {
    quality = 'quality',
    qualidade = 'quality',
    cinematico = 'quality',
    cinematic = 'quality',
    cine = 'quality',
    principal = 'quality',
    performance = 'performance',
    perf = 'performance',
    fps = 'performance',
    leve = 'performance',
    off = 'off',
    desligar = 'off',
    ['0'] = 'off',
    parar = 'off',
}

function GraphicsProfiles.normalize(name)
    if type(name) ~= 'string' then
        return nil
    end
    return aliases[string.lower(name)]
end

function GraphicsProfiles.periodForHour(hour)
    hour = tonumber(hour) or 0
    hour = hour % 24
    if hour >= 5 and hour < 8 then
        return 'sunrise'
    end
    if hour >= 17 and hour < 20 then
        return 'sunset'
    end
    if hour >= 20 or hour < 5 then
        return 'night'
    end
    return 'day'
end

function GraphicsProfiles.strengthKey(period)
    if period == 'sunrise' or period == 'sunset' then
        return 'golden'
    end
    return period
end

function GraphicsProfiles.modifierName(profile, period)
    local key = GraphicsProfiles.strengthKey(period)
    if profile == 'performance' then
        return 'fgm_perf_' .. key
    end
    return 'fgm_quality_' .. key
end

function GraphicsProfiles.rainExtra(profile)
    if profile == 'performance' then
        return 'fgm_perf_rain'
    end
    return 'fgm_quality_rain'
end

function GraphicsProfiles.label(profile)
    if profile == 'performance' then
        return 'Performance'
    end
    if profile == 'off' then
        return 'desligado'
    end
    return 'Quality'
end
