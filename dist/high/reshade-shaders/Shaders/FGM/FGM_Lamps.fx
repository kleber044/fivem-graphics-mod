// Poste, halo, reflexo claro e rastro de movimento. Branco neutro, mesma luminância.
// Parede, fachada, rua contínua, farol branco, neon e semáforo ficam de fora.
// Custo: sai cedo sem amarelo. Ultra/High 20 amostras no pixel amarelo. Médio.
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

float FGM_LampStrength(int level)
{
    if (level <= 1)
        return 0.78;
    if (level == 2)
        return 0.98;
    return 1.0;
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
    float s0 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(px.x, 0.0)).rgb);
    float s1 = FGM_Luma(tex2D(ReShade::BackBuffer, uv - float2(px.x, 0.0)).rgb);
    float s2 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(0.0, px.y)).rgb);
    float s3 = FGM_Luma(tex2D(ReShade::BackBuffer, uv - float2(0.0, px.y)).rgb);
    float lo = min(min(s0, s1), min(s2, s3));
    float hi = max(max(s0, s1), max(s2, s3));
    float brightSum = 0.0;
    float brightCount = 0.0;
    float darkSum = 0.0;
    float darkCount = 0.0;
    float taps = 4.0;
#if LAMP_TAPS > 4
    float2 diagonal = px * 0.7071;
    float s4 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(diagonal.x, diagonal.y)).rgb);
    float s5 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(-diagonal.x, diagonal.y)).rgb);
    float s6 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(diagonal.x, -diagonal.y)).rgb);
    float s7 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(-diagonal.x, -diagonal.y)).rgb);
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

float FGM_Streak(float2 uv, float tone)
{
    // Rastro fino em alta velocidade: um eixo acompanha a luz e o outro cai.
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT) * 18.0;
    float left = FGM_Luma(tex2D(ReShade::BackBuffer, uv - float2(px.x, 0.0)).rgb);
    float right = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(px.x, 0.0)).rgb);
    float up = FGM_Luma(tex2D(ReShade::BackBuffer, uv - float2(0.0, px.y)).rgb);
    float down = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(0.0, px.y)).rgb);
    float horizontal = (left + right) * 0.5;
    float vertical = (up + down) * 0.5;
    float elongated = smoothstep(0.06, 0.14, abs(horizontal - vertical));
    float darker = min(horizontal, vertical);
    float brighter = max(horizontal, vertical);
    float aligned = smoothstep(0.04, 0.10, tone - darker);
    float along = 1.0 - smoothstep(0.02, 0.08, abs(tone - brighter));
    return elongated * aligned * along;
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

    float luma = FGM_Luma(color);
    float peak = smoothstep(0.012, 0.045, luma - nearBright);
    float thin = smoothstep(0.34, 0.52, nearFraction) * smoothstep(0.05, 0.12, luma - nearDark);
    float spill = smoothstep(0.05, 0.12, luma - nearDark) * smoothstep(0.08, 0.18, nearBright - luma);
    float gradient = smoothstep(0.025, 0.07, nearSpread) * (1.0 - smoothstep(0.16, 0.30, nearSpread));
    float wide = smoothstep(0.40, 0.65, farFraction) * smoothstep(0.08, 0.16, luma - farDark) * gradient;
    float onSurface = (1.0 - smoothstep(0.02, 0.28, nearFraction)) * (1.0 - smoothstep(0.03, 0.09, abs(luma - nearBright)));
    float dayBlock = smoothstep(0.30, 0.40, farDark);
    float motion = FGM_Streak(uv, luma) * (1.0 - onSurface) * (1.0 - dayBlock);
    float light = sodium * max(peak, max(thin, max(spill, max(wide, motion)))) * (1.0 - onSurface) * (1.0 - dayBlock);
    float shade = 1.0 - smoothstep(0.10, 0.18, luma);
    light *= 1.0 - shade * (1.0 - saturate(peak + thin + spill + motion));
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
