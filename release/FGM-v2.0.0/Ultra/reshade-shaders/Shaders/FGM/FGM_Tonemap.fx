// Joelha do topo, depois da cor. Segura o que a vivacidade empurrou para cima.
// Custo: 1 amostra. Baixo.
#include "FGM.fxh"

uniform float TonemapAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 1.00;
    ui_step = 0.01;
    ui_label = "Joelha do branco";
> = 0.40;

float FGM_Shoulder(float channel)
{
    const float knee = 0.78;
    if (channel <= knee)
        return saturate(channel);
    float t = (channel - knee) / (1.0 - knee);
    float curved = t / (1.0 + 0.35 * t);
    float full = 1.0 / 1.35;
    return saturate(knee + 0.16 * (curved / full));
}

float4 FGM_TonemapPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (TonemapAmount <= 0.0001)
        return float4(color, 1.0);
    float3 mapped = float3(
        color.r + (FGM_Shoulder(color.r) - color.r) * TonemapAmount,
        color.g + (FGM_Shoulder(color.g) - color.g) * TonemapAmount,
        color.b + (FGM_Shoulder(color.b) - color.b) * TonemapAmount);
    return float4(FGM_Guard(color, saturate(mapped)), 1.0);
}

technique FGM_Tonemap
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_TonemapPS;
    }
}
