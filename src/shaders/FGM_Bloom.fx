// Bloom curto e alto limiar. Não pinta chão escuro, folha nem reflexo que já está no topo.
#include "FGM.fxh"

uniform float BloomThreshold <
    ui_type = "slider";
    ui_min = 0.50;
    ui_max = 1.00;
    ui_step = 0.01;
    ui_label = "Limiar do bloom";
> = 0.93;

uniform float BloomAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.50;
    ui_step = 0.01;
    ui_label = "Quantidade do bloom";
> = 0.05;

float3 FGM_BloomSample(float2 uv, float2 offset)
{
    float3 color = tex2D(ReShade::BackBuffer, uv + offset).rgb;
    float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
    float weight = saturate((luma - BloomThreshold) / max(1.0 - BloomThreshold, 0.001));
    return color * weight;
}

float4 FGM_BloomPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 base = tex2D(ReShade::BackBuffer, uv).rgb;
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT);
    float3 glow = FGM_BloomSample(uv, float2(0.0, 0.0)) * 1.4;
    float weight = 1.4;
    float2 near = px * 2.5;
    float2 far = px * 6.0;
    glow += FGM_BloomSample(uv, float2(near.x, 0.0));
    glow += FGM_BloomSample(uv, float2(-near.x, 0.0));
    glow += FGM_BloomSample(uv, float2(0.0, near.y));
    glow += FGM_BloomSample(uv, float2(0.0, -near.y));
    glow += FGM_BloomSample(uv, near);
    glow += FGM_BloomSample(uv, -near);
    glow += FGM_BloomSample(uv, float2(near.x, -near.y));
    glow += FGM_BloomSample(uv, float2(-near.x, near.y));
    weight += 8.0;
    glow += FGM_BloomSample(uv, float2(far.x, 0.0)) * 0.45;
    glow += FGM_BloomSample(uv, float2(-far.x, 0.0)) * 0.45;
    glow += FGM_BloomSample(uv, float2(0.0, far.y)) * 0.45;
    glow += FGM_BloomSample(uv, float2(0.0, -far.y)) * 0.45;
    weight += 1.8;
    glow /= weight;
    float baseLuma = dot(base, float3(0.2126, 0.7152, 0.0722));
    float glowLuma = dot(glow, float3(0.2126, 0.7152, 0.0722));
    // Ombro da luz, não o asfalto e não o núcleo que já estourou.
    float receive = smoothstep(0.70, 0.84, baseLuma) * (1.0 - smoothstep(0.84, 0.94, baseLuma));
    float presence = smoothstep(0.02, 0.12, glowLuma);
    return float4(saturate(base + glow * BloomAmount * receive * presence), 1.0);
}

technique FGM_Bloom
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_BloomPS;
    }
}
