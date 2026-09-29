// Núcleo de poste. O ReShade não sabe o tipo da luz.
// White LED leva o núcleo quente e pequeno até o branco da própria luminância.
// O halo mais fraco fica de fora. Farol branco, neon, semáforo e janela grande também.
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
        return 0.62;
    if (level == 2)
        return 0.82;
    return 1.0;
}

float FGM_LampChroma(float3 color)
{
    float peak = max(color.r, max(color.g, color.b));
    float floorc = min(color.r, min(color.g, color.b));
    float sat = (peak - floorc) / max(peak, 0.001);
    float luma = dot(color, FGM_LumaWeights);
    float bright = smoothstep(0.58, 0.68, luma);
    float ratio = color.g / max(color.r, 0.001);
    float sodium = smoothstep(0.42, 0.56, ratio) * (1.0 - smoothstep(0.90, 0.98, ratio));
    float blueDef = smoothstep(0.10, 0.22, min(color.r, color.g) - color.b);
    float satOk = smoothstep(0.10, 0.20, sat) * (1.0 - smoothstep(0.78, 0.92, sat));
    return bright * sodium * blueDef * satOk;
}

float FGM_AverageAround(float2 uv)
{
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT) * 32.0;
    float around = 0.0;
    float weight = 0.0;
    around += dot(tex2D(ReShade::BackBuffer, uv + float2(px.x, 0.0)).rgb, FGM_LumaWeights);
    around += dot(tex2D(ReShade::BackBuffer, uv - float2(px.x, 0.0)).rgb, FGM_LumaWeights);
    around += dot(tex2D(ReShade::BackBuffer, uv + float2(0.0, px.y)).rgb, FGM_LumaWeights);
    around += dot(tex2D(ReShade::BackBuffer, uv - float2(0.0, px.y)).rgb, FGM_LumaWeights);
    weight += 4.0;
#if LAMP_TAPS > 4
    float2 diagonal = px * 0.7071;
    around += dot(tex2D(ReShade::BackBuffer, uv + float2(diagonal.x, diagonal.y)).rgb, FGM_LumaWeights);
    around += dot(tex2D(ReShade::BackBuffer, uv + float2(-diagonal.x, diagonal.y)).rgb, FGM_LumaWeights);
    around += dot(tex2D(ReShade::BackBuffer, uv + float2(diagonal.x, -diagonal.y)).rgb, FGM_LumaWeights);
    around += dot(tex2D(ReShade::BackBuffer, uv + float2(-diagonal.x, -diagonal.y)).rgb, FGM_LumaWeights);
    weight += 4.0;
#endif
    return around / weight;
}

float4 FGM_LampsPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    float chroma = FGM_LampChroma(color);
    if (chroma <= 0.001)
        return float4(color, 1.0);

    float luma = dot(color, FGM_LumaWeights);
    float isolated = smoothstep(0.06, 0.18, luma - FGM_AverageAround(uv));
    float amount = chroma * isolated * FGM_LampStrength(LampLevel);
    float3 neutral = float3(luma, luma, luma);
    return float4(saturate(lerp(color, neutral, amount)), 1.0);
}

technique FGM_Lamps
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_LampsPS;
    }
}
