AddEventHandler('onResourceStart', function(resourceName)
    if resourceName ~= GetCurrentResourceName() then
        return
    end

    local profile = GetConvar('fgm_profile', 'quality')
    print(('[fivem-graphics-mod] iniciado. Perfil padrão do servidor: %s'):format(profile))
end)
