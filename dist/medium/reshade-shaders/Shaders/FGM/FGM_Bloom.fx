// Bloom curto, limiar alto. Superfície clara (camisa, nuvem, parede, asfalto) não ganha halo.
// Luz saturada, como farol e poste, ainda espalha. Custo: Ultra 13, High 9, Medium 5. Médio.
#include "FGM.fxh"

#ifndef BLOOM_TAPS
#define BLOOM_TAPS 13
#endif

uniform float BloomThreshold <
    ui_type = "slider";
    ui_min = 0.50;
    ui_max = 1.00;
    ui_step = 0.01;
    ui_label = "Limiar do bloom";
> = 0.94;

uniform float BloomAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.40;
    ui_step = 0.005;
    ui_label = "Quantidade do bloom";
> = 0.04;

float3 FGM_BloomSample(float2 uv, float2 offset)
{
    float3 color = tex2D(ReShade::BackBuffer, uv + offset).rgb;
    float weight = saturate((FGM_Luma(color) - BloomThreshold) / max(1.0 - BloomThreshold, 0.001));
    return color * weight;
}

float4 FGM_BloomPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 base = tex2D(ReShade::BackBuffer, uv).rgb;
    if (BloomAmount <= 0.0001)
        return float4(base, 1.0);
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT);
    float3 glow = FGM_BloomSample(uv, float2(0.0, 0.0)) * 1.4;
    float weight = 1.4;
    float2 near = px * 2.5;
    glow += FGM_BloomSample(uv, float2(near.x, 0.0));
    glow += FGM_BloomSample(uv, float2(-near.x, 0.0));
    glow += FGM_BloomSample(uv, float2(0.0, near.y));
    glow += FGM_BloomSample(uv, float2(0.0, -near.y));
    weight += 4.0;
#if BLOOM_TAPS > 5
    glow += FGM_BloomSample(uv, near);
    glow += FGM_BloomSample(uv, -near);
    glow += FGM_BloomSample(uv, float2(near.x, -near.y));
    glow += FGM_BloomSample(uv, float2(-near.x, near.y));
    weight += 4.0;
#endif
#if BLOOM_TAPS > 9
    float2 far = px * 6.0;
    glow += FGM_BloomSample(uv, float2(far.x, 0.0)) * 0.45;
    glow += FGM_BloomSample(uv, float2(-far.x, 0.0)) * 0.45;
    glow += FGM_BloomSample(uv, float2(0.0, far.y)) * 0.45;
    glow += FGM_BloomSample(uv, float2(0.0, -far.y)) * 0.45;
    weight += 1.8;
#endif
    glow /= weight;
    float3 result = saturate(base + glow * BloomAmount);
    float tone = FGM_Luma(base);
    float surface = 1.0 - smoothstep(0.04, 0.18, FGM_Sat(base));
    float capLuma = min(0.948, max(tone, BloomThreshold) + 0.008);
    float outLuma = FGM_Luma(result);
    if (surface > 0.001 && outLuma > capLuma)
        result = lerp(result, result * (capLuma / max(outLuma, 0.001)), surface);
    return float4(saturate(result), 1.0);
}

technique FGM_Bloom
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_BloomPS;
    }
}
