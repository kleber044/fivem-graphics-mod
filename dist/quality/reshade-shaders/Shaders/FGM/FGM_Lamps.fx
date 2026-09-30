// Iluminação urbana. O ReShade não sabe o que é poste.
// Branco neutro no pico, no fio, no halo e no reflexo claro.
// Parede, rua, fachada e janela plana conservam a cor.
// Farol branco, freio, semáforo e neon ficam de fora.
#include "FGM.fxh"

#ifndef LAMP_TAPS
#define LAMP_TAPS 8
#endif

uniform int LampLevel <
    ui_type = "slider";
    ui_min = 1;
    ui_max = 3;
    ui_step = 1;
    ui_label = "Postes (1 Soft, 2 Neutral, 3 White LED)";
> = 3;

static const float3 FGM_LumaWeights = float3(0.2126, 0.7152, 0.0722);

float FGM_LampStrength(int level)
{
    if (level <= 1)
        return 0.78;
    if (level == 2)
        return 0.98;
    return 1.0;
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

void FGM_Add(float value, float cut, inout float brightSum, inout float brightCount, inout float darkSum, inout float darkCount)
{
    float keep = step(cut, value);
    brightSum += value * keep;
    brightCount += keep;
    darkSum += value * (1.0 - keep);
    darkCount += 1.0 - keep;
}

void FGM_Ring(float2 uv, float radius, out float spread, out float brightSupport, out float darkSupport, out float darkFraction)
{
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT) * radius;
    float s0 = dot(tex2D(ReShade::BackBuffer, uv + float2(px.x, 0.0)).rgb, FGM_LumaWeights);
    float s1 = dot(tex2D(ReShade::BackBuffer, uv - float2(px.x, 0.0)).rgb, FGM_LumaWeights);
    float s2 = dot(tex2D(ReShade::BackBuffer, uv + float2(0.0, px.y)).rgb, FGM_LumaWeights);
    float s3 = dot(tex2D(ReShade::BackBuffer, uv - float2(0.0, px.y)).rgb, FGM_LumaWeights);
    float lo = min(min(s0, s1), min(s2, s3));
    float hi = max(max(s0, s1), max(s2, s3));
    float brightSum = 0.0;
    float brightCount = 0.0;
    float darkSum = 0.0;
    float darkCount = 0.0;
    float taps = 4.0;
#if LAMP_TAPS > 4
    float2 diagonal = px * 0.7071;
    float s4 = dot(tex2D(ReShade::BackBuffer, uv + float2(diagonal.x, diagonal.y)).rgb, FGM_LumaWeights);
    float s5 = dot(tex2D(ReShade::BackBuffer, uv + float2(-diagonal.x, diagonal.y)).rgb, FGM_LumaWeights);
    float s6 = dot(tex2D(ReShade::BackBuffer, uv + float2(diagonal.x, -diagonal.y)).rgb, FGM_LumaWeights);
    float s7 = dot(tex2D(ReShade::BackBuffer, uv + float2(-diagonal.x, -diagonal.y)).rgb, FGM_LumaWeights);
    lo = min(lo, min(min(s4, s5), min(s6, s7)));
    hi = max(hi, max(max(s4, s5), max(s6, s7)));
    taps = 8.0;
#endif
    float cut = (lo + hi) * 0.5;
    FGM_Add(s0, cut, brightSum, brightCount, darkSum, darkCount);
    FGM_Add(s1, cut, brightSum, brightCount, darkSum, darkCount);
    FGM_Add(s2, cut, brightSum, brightCount, darkSum, darkCount);
    FGM_Add(s3, cut, brightSum, brightCount, darkSum, darkCount);
#if LAMP_TAPS > 4
    FGM_Add(s4, cut, brightSum, brightCount, darkSum, darkCount);
    FGM_Add(s5, cut, brightSum, brightCount, darkSum, darkCount);
    FGM_Add(s6, cut, brightSum, brightCount, darkSum, darkCount);
    FGM_Add(s7, cut, brightSum, brightCount, darkSum, darkCount);
#endif
    spread = hi - lo;
    brightSupport = brightSum / max(brightCount, 1.0);
    darkSupport = darkCount > 0.0 ? darkSum / darkCount : brightSupport;
    darkFraction = darkCount / taps;
}

float4 FGM_LampsPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    float sodium = FGM_Sodium(color);
    if (sodium <= 0.001)
        return float4(color, 1.0);

    float nearSpread, nearBright, nearDark, nearFraction;
    FGM_Ring(uv, 56.0, nearSpread, nearBright, nearDark, nearFraction);
    float farSpread, farBright, farDark, farFraction;
    FGM_Ring(uv, 140.0, farSpread, farBright, farDark, farFraction);

    float luma = dot(color, FGM_LumaWeights);
    float peak = smoothstep(0.012, 0.045, luma - nearBright);
    float thin = smoothstep(0.34, 0.52, nearFraction) * smoothstep(0.05, 0.12, luma - nearDark);
    float spill = smoothstep(0.05, 0.12, luma - nearDark) * smoothstep(0.08, 0.18, nearBright - luma);
    float gradient = smoothstep(0.025, 0.07, nearSpread) * (1.0 - smoothstep(0.16, 0.30, nearSpread));
    float wide = smoothstep(0.40, 0.65, farFraction) * smoothstep(0.08, 0.16, luma - farDark) * gradient;
    float onSurface = (1.0 - smoothstep(0.02, 0.28, nearFraction)) * (1.0 - smoothstep(0.03, 0.09, abs(luma - nearBright)));
    float dayBlock = smoothstep(0.30, 0.40, farDark);
    float light = sodium * max(peak, max(thin, max(spill, wide))) * (1.0 - onSurface) * (1.0 - dayBlock);
    float shade = 1.0 - smoothstep(0.10, 0.18, luma);
    light *= 1.0 - shade * (1.0 - saturate(peak + thin + spill));
    float amount = saturate(light) * FGM_LampStrength(LampLevel);
    if (amount <= 0.001)
        return float4(color, 1.0);

    return float4(saturate(lerp(color, luma.xxx, amount)), 1.0);
}

technique FGM_Lamps
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_LampsPS;
    }
}
