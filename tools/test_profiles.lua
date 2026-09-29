dofile('shared/config.lua')
dofile('shared/profiles.lua')
dofile('shared/timecycle.lua')
dofile('shared/visual_settings.lua')

local function assert_eq(actual, expected, label)
    if actual ~= expected then
        error(label .. ': esperado ' .. tostring(expected) .. ', obteve ' .. tostring(actual))
    end
end

assert_eq(GraphicsProfiles.periodForHour(6), 'sunrise', 'nascer')
assert_eq(GraphicsProfiles.periodForHour(12), 'day', 'dia')
assert_eq(GraphicsProfiles.periodForHour(18), 'sunset', 'por do sol')
assert_eq(GraphicsProfiles.periodForHour(23), 'night', 'noite')
assert_eq(GraphicsProfiles.periodForHour(2), 'night', 'madrugada')
assert_eq(GraphicsProfiles.periodForHour(8), 'day', 'manha')
assert_eq(GraphicsProfiles.periodForHour(20), 'night', 'vira a noite')

assert_eq(GraphicsProfiles.normalize('quality'), 'quality', 'quality')
assert_eq(GraphicsProfiles.normalize('cinematico'), 'quality', 'alias cine')
assert_eq(GraphicsProfiles.normalize('Performance'), 'performance', 'alias perf')
assert_eq(GraphicsProfiles.normalize('desligar'), 'off', 'alias off')
assert_eq(GraphicsProfiles.normalize('nao-existe'), nil, 'alias invalido')

assert_eq(GraphicsProfiles.modifierName('quality', 'sunset'), 'fgm_quality_golden', 'mod por do sol')
assert_eq(GraphicsProfiles.modifierName('performance', 'night'), 'fgm_perf_night', 'mod noite leve')
assert_eq(GraphicsProfiles.rainExtra('quality'), 'fgm_quality_rain', 'chuva quality')
assert_eq(GraphicsProfiles.rainExtra('performance'), 'fgm_perf_rain', 'chuva perf')

local required = {
    'fgm_quality_day', 'fgm_quality_golden', 'fgm_quality_night', 'fgm_quality_rain',
    'fgm_perf_day', 'fgm_perf_golden', 'fgm_perf_night', 'fgm_perf_rain',
}

for _, name in ipairs(required) do
    if GraphicsTimecycle[name] == nil then
        error('modifier ausente: ' .. name)
    end
    local count = 0
    for _, pair in pairs(GraphicsTimecycle[name]) do
        count = count + 1
        if type(pair[1]) ~= 'number' or type(pair[2]) ~= 'number' then
            error(name .. ' tem par invalido')
        end
    end
    if count < 4 then
        error(name .. ' está curto demais')
    end
end

for profile, pack in pairs(GraphicsVisualSettings.profiles) do
    if Config.engine[profile] == nil or Config.strength[profile] == nil then
        error('perfil sem engine ou força: ' .. profile)
    end
    for _, group in pairs({ pack.base, pack.rain }) do
        for key, value in pairs(group) do
            if GraphicsVisualSettings.restore[key] == nil then
                error('chave sem restauração: ' .. key)
            end
            if type(value) ~= 'number' then
                error(profile .. ' valor invalido em ' .. key)
            end
        end
    end
end

if GraphicsTimecycle.fgm_perf_day.postfx_intensity_bloom[1]
    >= GraphicsTimecycle.fgm_quality_day.postfx_intensity_bloom[1] then
    error('Performance deveria usar menos bloom que Quality')
end

if GraphicsTimecycle.fgm_perf_night.dir_shadow_distance_multiplier[1]
    >= GraphicsTimecycle.fgm_quality_night.dir_shadow_distance_multiplier[1] then
    error('Performance deveria encurtar a sombra noturna')
end

if GraphicsVisualSettings.profiles.quality.rain['rain.NumberParticles']
    <= GraphicsVisualSettings.profiles.performance.rain['rain.NumberParticles'] then
    error('Quality na chuva deveria ter mais partículas que Performance')
end

print('perfis ok')
