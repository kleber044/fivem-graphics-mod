// Realce curto do brilho que já existe no asfalto. Não cria espelho nem bloom.
// Custo: Ultra 9 amostras, High e Medium 5. Médio. Low não carrega este arquivo.
#include "FGM.fxh"

#ifndef REFLECT_TAPS
#define REFLECT_TAPS 8
#endif

uniform float ReflectAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.50;
    ui_step = 0.01;
    ui_label = "Reflexo do asfalto";
> = 0.20;

float4 FGM_ReflectPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (ReflectAmount <= 0.001)
        return float4(color, 1.0);
    float mask = FGM_Asphalt(color);
    if (mask <= 0.001)
        return float4(color, 1.0);
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT) * 6.0;
    float s0 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(px.x, 0.0)).rgb);
    float s1 = FGM_Luma(tex2D(ReShade::BackBuffer, uv - float2(px.x, 0.0)).rgb);
    float s2 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(0.0, px.y)).rgb);
    float s3 = FGM_Luma(tex2D(ReShade::BackBuffer, uv - float2(0.0, px.y)).rgb);
    float lo = min(min(s0, s1), min(s2, s3));
    float hi = max(max(s0, s1), max(s2, s3));
#if REFLECT_TAPS > 4
    float2 diagonal = px * 0.7071;
    float s4 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + diagonal).rgb);
    float s5 = FGM_Luma(tex2D(ReShade::BackBuffer, uv - diagonal).rgb);
    float s6 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(diagonal.x, -diagonal.y)).rgb);
    float s7 = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(-diagonal.x, diagonal.y)).rgb);
    lo = min(lo, min(min(s4, s5), min(s6, s7)));
    hi = max(hi, max(max(s4, s5), max(s6, s7)));
#endif
    float tone = FGM_Luma(color);
    float spread = hi - lo;
    float glint = smoothstep(0.03, 0.10, tone - lo) * (1.0 - smoothstep(0.22, 0.40, spread));
    float amount = mask * glint * ReflectAmount;
    if (amount <= 0.001)
        return float4(color, 1.0);
    float3 neutral = lerp(color, tone.xxx, 0.35);
    float3 lifted = neutral * (1.0 + 0.12 * amount);
    return float4(saturate(lerp(color, lifted, amount)), 1.0);
}

technique FGM_ReflectionsEnhance
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_ReflectPS;
    }
}
