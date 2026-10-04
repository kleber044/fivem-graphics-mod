// Cabeçalho deste produto. Não copia o repositório reshade-shaders e não lê profundidade.
#pragma once

namespace ReShade
{
    texture BackBufferTex : COLOR;
    sampler BackBuffer
    {
        Texture = BackBufferTex;
    };
}

uniform float timer < source = "timer"; >;

static const float3 FGM_LumaW = float3(0.2126, 0.7152, 0.0722);

void PostProcessVS(in uint id : SV_VertexID, out float4 position : SV_Position, out float2 texcoord : TEXCOORD)
{
    texcoord.x = (id == 2) ? 2.0 : 0.0;
    texcoord.y = (id == 1) ? 2.0 : 0.0;
    position = float4(texcoord * float2(2.0, -2.0) + float2(-1.0, 1.0), 0.0, 1.0);
}

float FGM_Luma(float3 color)
{
    return dot(color, FGM_LumaW);
}

float FGM_Sat(float3 color)
{
    float peak = max(color.r, max(color.g, color.b));
    float floorc = min(color.r, min(color.g, color.b));
    return (peak - floorc) / max(peak, 0.001);
}

float FGM_Skin(float3 color, float luma, float sat)
{
    float rg = color.r - color.g;
    float gb = color.g - color.b;
    float skin = smoothstep(0.04, 0.12, rg) * (1.0 - smoothstep(0.18, 0.32, rg));
    skin *= smoothstep(0.03, 0.10, gb);
    skin *= smoothstep(0.20, 0.40, luma) * (1.0 - smoothstep(0.62, 0.82, luma));
    skin *= smoothstep(0.10, 0.22, sat) * (1.0 - smoothstep(0.45, 0.65, sat));
    return saturate(skin);
}

float FGM_Foliage(float3 color)
{
    return smoothstep(0.02, 0.08, color.g - max(color.r, color.b));
}

float FGM_Skyish(float3 color, float luma, float sat)
{
    float sky = smoothstep(0.04, 0.12, color.b - max(color.r, color.g));
    sky *= smoothstep(0.35, 0.52, luma);
    sky *= 1.0 - smoothstep(0.58, 0.78, sat);
    return saturate(sky);
}

float3 FGM_KeepPerson(float3 original, float3 graded)
{
    float luma = FGM_Luma(original);
    float sat = FGM_Sat(original);
    float foliage = FGM_Foliage(original);
    float skyish = FGM_Skyish(original, luma, sat);
    float rg = original.r - original.g;
    float gb = original.g - original.b;
    float skin = FGM_Skin(original, luma, sat);
    float broad = smoothstep(0.015, 0.06, rg) * (1.0 - smoothstep(0.28, 0.48, rg));
    broad *= smoothstep(0.008, 0.045, gb);
    broad *= smoothstep(0.08, 0.20, luma) * (1.0 - smoothstep(0.86, 0.97, luma));
    broad *= smoothstep(0.05, 0.14, sat) * (1.0 - smoothstep(0.62, 0.82, sat));
    broad *= 1.0 - foliage;
    skin = max(skin, broad);
    float garment = smoothstep(0.10, 0.20, sat) * (1.0 - foliage) * (1.0 - skyish);
    float keep = saturate(max(skin, garment * 0.92));
    return lerp(graded, original, keep);
}

float3 FGM_Guard(float3 before, float3 after)
{
    float3 kept = FGM_KeepPerson(before, after);
    float tone = FGM_Luma(before);
    float sat = FGM_Sat(before);
    float hot = smoothstep(0.82, 0.94, tone) * (1.0 - smoothstep(0.02, 0.12, sat));
    if (hot <= 0.001)
        return kept;
    float cap = FGM_Luma(kept);
    float limit = FGM_Luma(before);
    if (cap <= limit)
        return kept;
    float3 capped = kept * (limit / max(cap, 0.001));
    return lerp(kept, capped, hot);
}

float FGM_SceneLuma(float2 uv)
{
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT) * 160.0;
    float scene = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(px.x, 0.0)).rgb);
    scene += FGM_Luma(tex2D(ReShade::BackBuffer, uv - float2(px.x, 0.0)).rgb);
    scene += FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(0.0, px.y)).rgb);
    scene += FGM_Luma(tex2D(ReShade::BackBuffer, uv - float2(0.0, px.y)).rgb);
    return scene * 0.25;
}

float FGM_DayFactor(float2 uv)
{
    return smoothstep(0.26, 0.46, FGM_SceneLuma(uv));
}

float FGM_Sodium(float3 color)
{
    float peak = max(color.r, max(color.g, color.b));
    float floorc = min(color.r, min(color.g, color.b));
    float sat = (peak - floorc) / max(peak, 0.001);
    float excess = min(color.r, color.g) - color.b;
    float yellow = smoothstep(0.035, 0.10, excess);
    float ratio = color.g / max(color.r, 0.001);
    float notRed = smoothstep(0.40, 0.55, ratio);
    float notGreen = 1.0 - smoothstep(0.0, 0.08, color.g - color.r);
    float notNeon = 1.0 - smoothstep(0.86, 0.96, sat);
    float hasCast = smoothstep(0.15, 0.28, sat);
    return yellow * notRed * notGreen * notNeon * hasCast;
}

float FGM_Asphalt(float3 color)
{
    float tone = FGM_Luma(color);
    float sat = FGM_Sat(color);
    float gray = 1.0 - smoothstep(0.05, 0.16, sat);
    float band = smoothstep(0.05, 0.12, tone) * (1.0 - smoothstep(0.42, 0.62, tone));
    float notSkin = 1.0 - FGM_Skin(color, tone, sat);
    float notPlant = 1.0 - FGM_Foliage(color);
    float notLamp = 1.0 - FGM_Sodium(color);
    float blue = smoothstep(0.04, 0.12, color.b - max(color.r, color.g));
    return saturate(gray * band * notSkin * notPlant * notLamp * (1.0 - blue));
}
