// De dia, só o leite alto e quase sem cor. Montanha, mata distante e céu com tom ficam quietos.
// A noite continua no leite baixo. Não lê profundidade nem o clima.
// Custo: 1 amostra. Baixo.
#include "FGM.fxh"

uniform float ClearDay <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.80;
    ui_step = 0.01;
    ui_label = "Véu do dia";
> = 0.18;

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
    float nightGray = 1.0 - smoothstep(0.02, 0.10, sat);
    float nightBand = smoothstep(0.12, 0.20, luma) * (1.0 - smoothstep(0.32, 0.46, luma));
    float veilNight = nightGray * nightBand * ClearNight;
    float dayGray = 1.0 - smoothstep(0.012, 0.07, sat);
    float dayBand = smoothstep(0.64, 0.76, luma) * (1.0 - smoothstep(0.90, 0.97, luma));
    float green = saturate((color.g - max(color.r, color.b)) / 0.04);
    float blue = saturate((color.b - max(color.r, color.g)) / 0.04);
    float warm = saturate((color.r - max(color.g, color.b)) / 0.04);
    float hue = max(green, max(blue, warm));
    dayGray *= 1.0 - smoothstep(0.02, 0.10, hue);
    float veilDay = min(dayGray * dayBand * ClearDay, luma * 0.16);
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
