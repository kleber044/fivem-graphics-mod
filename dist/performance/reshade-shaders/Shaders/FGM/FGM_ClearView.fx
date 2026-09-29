// Reduz véu branco de baixa saturação. Não lê profundidade nem o clima.
// Sombras, luzes estouradas e cores já vivas ficam de fora. Neblina real só perde o leite.
#include "FGM.fxh"

uniform int ClearLevel <
    ui_type = "slider";
    ui_min = 0;
    ui_max = 3;
    ui_step = 1;
    ui_label = "Horizonte (0 off, 1 leve, 2 médio, 3 forte)";
> = 3;

float FGM_ClearStrength(int level)
{
    if (level <= 0)
        return 0.0;
    if (level == 1)
        return 0.12;
    if (level == 2)
        return 0.22;
    return 0.34;
}

float4 FGM_ClearPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    float strength = FGM_ClearStrength(ClearLevel);
    if (strength <= 0.001)
        return float4(color, 1.0);

    float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
    float peak = max(color.r, max(color.g, color.b));
    float floorc = min(color.r, min(color.g, color.b));
    float sat = (peak - floorc) / max(peak, 0.001);
    float gray = 1.0 - smoothstep(0.06, 0.22, sat);
    float band = smoothstep(0.40, 0.55, luma) * (1.0 - smoothstep(0.76, 0.88, luma));
    float veil = gray * band * strength;
    if (veil <= 0.001)
        return float4(color, 1.0);

    float3 recovered = (color - veil) / max(1.0 - veil, 0.001);
    return float4(saturate(recovered), 1.0);
}

technique FGM_ClearView
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_ClearPS;
    }
}
