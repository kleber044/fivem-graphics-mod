// Vinheta curta nas bordas. O centro permanece aberto.
// Custo: 1 amostra. Baixo.
#include "FGM.fxh"

uniform float VignetteAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.50;
    ui_step = 0.01;
    ui_label = "Vinheta";
> = 0.14;

float4 FGM_VignettePS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (VignetteAmount <= 0.001)
        return float4(color, 1.0);
    float edge = smoothstep(0.35, 0.92, length((uv - float2(0.5, 0.48)) * float2(1.15, 1.0)));
    color *= 1.0 - edge * VignetteAmount;
    return float4(saturate(color), 1.0);
}

technique FGM_Vignette
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_VignettePS;
    }
}
