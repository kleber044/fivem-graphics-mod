GraphicsVisuals = {}

local appliedSignature = nil

local function signature(profile, raining)
    return profile .. (raining and ':rain' or ':dry')
end

local function applyFloats(values)
    for key, value in pairs(values) do
        SetVisualSettingFloat(key, value + 0.0)
    end
end

function GraphicsVisuals.installTimecycles()
    for name, vars in pairs(GraphicsTimecycle) do
        if GetTimecycleModifierIndexByName(name) == -1 then
            CreateTimecycleModifier(name)
        end
        for varName, pair in pairs(vars) do
            SetTimecycleModifierVar(name, varName, pair[1] + 0.0, pair[2] + 0.0)
        end
    end
end

function GraphicsVisuals.apply(profile, raining)
    local pack = GraphicsVisualSettings.profiles[profile]
    local engine = Config.engine[profile]
    if not pack or not engine then
        return
    end

    local sign = signature(profile, raining)
    if sign ~= appliedSignature then
        applyFloats(pack.base)
        if raining then
            applyFloats(pack.rain)
        end
        CascadeShadowsSetCascadeBoundsScale(engine.shadowScale + 0.0)
        SetLightsCutoffDistanceTweak(engine.lightCutoff + 0.0)
        appliedSignature = sign
    end

    SetRainFxIntensity(raining and (engine.rainFx + 0.0) or 0.0)
    local tracks = raining and engine.tracks or false
    SetForceVehicleTrails(tracks)
    SetForcePedFootstepsTracks(tracks)
end

function GraphicsVisuals.clear()
    ClearTimecycleModifier()
    ClearExtraTimecycleModifier()
    SetRainFxIntensity(0.0)
    SetForceVehicleTrails(false)
    SetForcePedFootstepsTracks(false)
    CascadeShadowsSetCascadeBoundsScale(1.0)
    SetLightsCutoffDistanceTweak(1.0)
    applyFloats(GraphicsVisualSettings.restore)
    appliedSignature = nil
end
