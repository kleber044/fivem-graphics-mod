// Véu do horizonte e leite da noite. Não lê profundidade nem o clima.
// O leite noturno é o cinza baixo, de 0.10 a 0.50 de luminância.
// Sombras reais, cores vivas e o núcleo das luzes ficam de fora.
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
        return 0.07;
    if (level == 2)
        return 0.13;
    return 0.20;
}

float FGM_NightStrength(int level)
{
    if (level <= 0)
        return 0.0;
    if (level == 1)
        return 0.06;
    if (level == 2)
        return 0.11;
    return 0.18;
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
    float dayGray = 1.0 - smoothstep(0.05, 0.24, sat);
    float nightGray = 1.0 - smoothstep(0.08, 0.42, sat);
    float dayBand = smoothstep(0.40, 0.55, luma) * (1.0 - smoothstep(0.76, 0.88, luma));
    float nightBand = smoothstep(0.10, 0.18, luma) * (1.0 - smoothstep(0.34, 0.50, luma));
    float warm = smoothstep(0.0, 0.08, (color.r + color.g) * 0.5 - color.b);
    float veil = max(dayGray * dayBand * dayStrength, nightGray * nightBand * nightStrength * (0.55 + 0.45 * warm));
    if (veil <= 0.001 && nightBand <= 0.001)
        return float4(color, 1.0);

    float3 recovered = (color - veil) / max(1.0 - veil, 0.001);
    float recLuma = dot(recovered, float3(0.2126, 0.7152, 0.0722));
    float neutralNight = saturate(nightStrength / 0.18) * nightGray * nightBand * (0.55 + 0.45 * warm);
    recovered = lerp(recovered, recLuma.xxx, neutralNight);
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
