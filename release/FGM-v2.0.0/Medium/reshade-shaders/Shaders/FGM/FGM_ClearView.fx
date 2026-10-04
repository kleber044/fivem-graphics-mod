// Véu do horizonte de dia e leite da noite. Não lê profundidade nem o clima.
// Cor de pele, roupa, planta e céu saturado fica de fora. O dia desce mais que a noite.
// Custo: 1 amostra. Baixo.
#include "FGM.fxh"

uniform float ClearDay <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.80;
    ui_step = 0.01;
    ui_label = "Véu do dia";
> = 0.50;

uniform float ClearNight <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.40;
    ui_step = 0.01;
    ui_label = "Véu da noite";
> = 0.12;

float4 FGM_ClearPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (ClearDay <= 0.001 && ClearNight <= 0.001)
        return float4(color, 1.0);
    float luma = FGM_Luma(color);
    float sat = FGM_Sat(color);
    float dayGray = 1.0 - smoothstep(0.03, 0.16, sat);
    float nightGray = 1.0 - smoothstep(0.02, 0.10, sat);
    float dayBand = smoothstep(0.30, 0.44, luma) * (1.0 - smoothstep(0.78, 0.90, luma));
    float nightBand = smoothstep(0.12, 0.20, luma) * (1.0 - smoothstep(0.32, 0.46, luma));
    float veilDay = min(dayGray * dayBand * ClearDay, luma * 0.52);
    float veilNight = nightGray * nightBand * ClearNight;
    float veil = max(veilDay, veilNight);
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
