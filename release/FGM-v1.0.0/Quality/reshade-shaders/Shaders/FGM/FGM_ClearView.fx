// Véu do horizonte e leite cinza da noite. Não lê profundidade nem o clima.
// De dia o cinza claro desce mais. Cor de pele, roupa, planta e céu saturado fica de fora.
#include "FGM.fxh"

uniform int ClearLevel <
    ui_type = "slider";
    ui_min = 0;
    ui_max = 3;
    ui_step = 1;
    ui_label = "Horizonte (0 off, 1 leve, 2 médio, 3 forte)";
> = 3;

float FGM_DayStrength(int level)
{
    if (level <= 0)
        return 0.0;
    if (level == 1)
        return 0.16;
    if (level == 2)
        return 0.34;
    return 0.50;
}

float FGM_NightStrength(int level)
{
    if (level <= 0)
        return 0.0;
    if (level == 1)
        return 0.05;
    if (level == 2)
        return 0.09;
    return 0.14;
}

float4 FGM_ClearPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    int level = ClearLevel;
    float dayStrength = FGM_DayStrength(level);
    float nightStrength = FGM_NightStrength(level);
    if (dayStrength <= 0.001 && nightStrength <= 0.001)
        return float4(color, 1.0);

    float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
    float peak = max(color.r, max(color.g, color.b));
    float floorc = min(color.r, min(color.g, color.b));
    float sat = (peak - floorc) / max(peak, 0.001);
    float dayGray = 1.0 - smoothstep(0.03, 0.16, sat);
    float nightGray = 1.0 - smoothstep(0.02, 0.10, sat);
    float dayBand = smoothstep(0.30, 0.44, luma) * (1.0 - smoothstep(0.78, 0.90, luma));
    float nightBand = smoothstep(0.12, 0.20, luma) * (1.0 - smoothstep(0.32, 0.46, luma));
    float veilDay = min(dayGray * dayBand * dayStrength, luma * 0.52);
    float veilNight = nightGray * nightBand * nightStrength;
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
