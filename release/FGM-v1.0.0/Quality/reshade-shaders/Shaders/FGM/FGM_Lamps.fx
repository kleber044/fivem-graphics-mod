// Aproxima lâmpadas de poste. O ReShade não sabe qual luz é um poste.
// Só entra um núcleo pequeno, brilhante e âmbar, cercado de noite.
// A luminância fica igual, então o bloom não ganha energia. O azul não passa do branco neutro.
#include "FGM.fxh"

#ifndef LAMP_TAPS
#define LAMP_TAPS 8
#endif

uniform float LampWhite <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 1.00;
    ui_step = 0.01;
    ui_label = "Branco dos postes";
> = 0.88;

static const float3 FGM_LumaWeights = float3(0.2126, 0.7152, 0.0722);

float FGM_LampChroma(float3 color)
{
    float peak = max(color.r, max(color.g, color.b));
    float floorc = min(color.r, min(color.g, color.b));
    float sat = (peak - floorc) / max(peak, 0.001);
    float luma = dot(color, FGM_LumaWeights);
    float bright = smoothstep(0.55, 0.75, luma);
    float ratio = color.g / max(color.r, 0.001);
    float sodium = smoothstep(0.55, 0.64, ratio) * (1.0 - smoothstep(0.84, 0.93, ratio));
    float blueDef = smoothstep(0.16, 0.30, min(color.r, color.g) - color.b);
    float satOk = smoothstep(0.18, 0.32, sat) * (1.0 - smoothstep(0.70, 0.88, sat));
    return bright * sodium * blueDef * satOk;
}

float FGM_MaxAround(float2 uv)
{
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT) * 18.0;
    float around = 0.0;
    around = max(around, dot(tex2D(ReShade::BackBuffer, uv + float2(px.x, 0.0)).rgb, FGM_LumaWeights));
    around = max(around, dot(tex2D(ReShade::BackBuffer, uv - float2(px.x, 0.0)).rgb, FGM_LumaWeights));
    around = max(around, dot(tex2D(ReShade::BackBuffer, uv + float2(0.0, px.y)).rgb, FGM_LumaWeights));
    around = max(around, dot(tex2D(ReShade::BackBuffer, uv - float2(0.0, px.y)).rgb, FGM_LumaWeights));
#if LAMP_TAPS > 4
    float2 diagonal = px * 0.7071;
    around = max(around, dot(tex2D(ReShade::BackBuffer, uv + float2(diagonal.x, diagonal.y)).rgb, FGM_LumaWeights));
    around = max(around, dot(tex2D(ReShade::BackBuffer, uv + float2(-diagonal.x, diagonal.y)).rgb, FGM_LumaWeights));
    around = max(around, dot(tex2D(ReShade::BackBuffer, uv + float2(diagonal.x, -diagonal.y)).rgb, FGM_LumaWeights));
    around = max(around, dot(tex2D(ReShade::BackBuffer, uv + float2(-diagonal.x, -diagonal.y)).rgb, FGM_LumaWeights));
#endif
    return around;
}

float4 FGM_LampsPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    float chroma = FGM_LampChroma(color);
    if (LampWhite <= 0.001 || chroma <= 0.001)
        return float4(color, 1.0);

    float luma = dot(color, FGM_LumaWeights);
    float isolated = smoothstep(0.22, 0.42, luma - FGM_MaxAround(uv));
    float amount = chroma * isolated * LampWhite;
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
