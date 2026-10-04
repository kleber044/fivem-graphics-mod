// Abre só o preto esmagado. O meio-tom não sobe e a noite não vira leite.
// Custo: 1 amostra. Baixo.
#include "FGM.fxh"

uniform float ShadowOpen <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.20;
    ui_step = 0.005;
    ui_label = "Abertura da sombra";
> = 0.045;

float4 FGM_ShadowsPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (ShadowOpen <= 0.0001)
        return float4(color, 1.0);
    float tone = FGM_Luma(color);
    float crushed = smoothstep(0.16, 0.02, tone);
    if (crushed <= 0.001)
        return float4(color, 1.0);
    float lift = ShadowOpen * crushed * 0.55;
    float3 opened = saturate(color + lift * (0.08 - color));
    return float4(FGM_Guard(color, opened), 1.0);
}

technique FGM_Shadows
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_ShadowsPS;
    }
}
