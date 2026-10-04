// Só canal já estourado, acima de 0,94. Céu e montanha clara não são highlight.
// Branco neutro encosta em 0,945. Custo: 1 amostra. Baixo.
#include "FGM.fxh"

uniform float HighlightAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 1.00;
    ui_step = 0.01;
    ui_label = "Recuperar luz alta";
> = 0.22;

float4 FGM_HighlightPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (HighlightAmount <= 0.0001)
        return float4(color, 1.0);
    float peak = max(color.r, max(color.g, color.b));
    if (peak < 0.94)
        return float4(color, 1.0);
    float floorc = min(color.r, min(color.g, color.b));
    float hot = smoothstep(0.94, 0.995, peak);
    float sat = (peak - floorc) / max(peak, 0.001);
    float colored = smoothstep(0.08, 0.22, sat);
    float3 pulled = color + (min(color, peak * 0.92 + floorc * 0.08) - color) * hot * colored * HighlightAmount;
    float white = smoothstep(0.945, 0.962, peak) * (1.0 - smoothstep(0.015, 0.06, sat));
    float3 knee = min(pulled, 0.945);
    return float4(FGM_Guard(color, saturate(lerp(pulled, knee, white))), 1.0);
}

technique FGM_HighlightRecovery
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_HighlightPS;
    }
}
