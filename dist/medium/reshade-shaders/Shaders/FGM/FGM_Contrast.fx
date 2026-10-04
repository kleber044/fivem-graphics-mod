// Contraste só no meio-tom. Sombra e branco não entram na curva.
// Custo: 1 amostra. Baixo. O Low deixa este passo de fora.
#include "FGM.fxh"

uniform float ContrastAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.20;
    ui_step = 0.005;
    ui_label = "Contraste do meio";
> = 0.04;

float4 FGM_ContrastPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (ContrastAmount <= 0.0001)
        return float4(color, 1.0);
    float tone = FGM_Luma(color);
    float weight = smoothstep(0.12, 0.28, tone) * (1.0 - smoothstep(0.72, 0.90, tone));
    if (weight <= 0.001)
        return float4(color, 1.0);
    float3 curved = saturate((color - 0.5) * (1.0 + ContrastAmount) + 0.5);
    return float4(FGM_Guard(color, lerp(color, curved, weight)), 1.0);
}

technique FGM_Contrast
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_ContrastPS;
    }
}
