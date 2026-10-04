// Vivacidade seletiva. Verde, azul e laranja forte recebem menos ganho.
// Pele fica quase parada. De dia a força cai. Custo: 5 amostras. Baixo.
#include "FGM.fxh"

uniform float ColorVibrance <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.60;
    ui_step = 0.01;
    ui_label = "Vivacidade";
> = 0.12;

uniform float PlantExtra <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.40;
    ui_step = 0.01;
    ui_label = "Verde da vegetação";
> = 0.03;

float3 FGM_Vibrant(float3 color, float day)
{
    float luma = FGM_Luma(color);
    float sat = FGM_Sat(color);
    float shadow = smoothstep(0.08, 0.22, luma);
    float notWhite = 1.0 - smoothstep(0.72, 0.90, luma);
    float headroom = 1.0 - smoothstep(0.28, 0.50, sat);
    float protect = 1.0 - 0.80 * FGM_Skin(color, luma, sat);
    float green = smoothstep(0.03, 0.14, color.g - max(color.r, color.b));
    green *= 1.0 - smoothstep(0.55, 0.80, sat);
    float hueBias = 1.0;
    float greenDom = saturate((color.g - max(color.r, color.b)) / 0.12);
    hueBias *= lerp(1.0, 0.35, greenDom);
    float blueDom = saturate((color.b - max(color.r, color.g)) / 0.10);
    hueBias *= lerp(1.0, 0.45, blueDom);
    float warmDom = saturate((color.r - max(color.g, color.b) - 0.05) / 0.14);
    hueBias *= lerp(1.0, 0.60, warmDom);
    float amount = ColorVibrance * (1.0 - 0.75 * day);
    float plant = PlantExtra * (1.0 - day);
    float gain = amount * shadow * notWhite * headroom * protect * hueBias * (1.0 + plant * green);
    float3 outColor = luma + (color - luma) * (1.0 + gain);
    float outPeak = max(outColor.r, max(outColor.g, outColor.b));
    if (outPeak > 1.0)
    {
        float head = max(outPeak - luma, 0.001);
        float room = max(1.0 - luma, 0.0);
        outColor = luma + (outColor - luma) * (room / head);
    }
    return saturate(outColor);
}

float4 FGM_ColorPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (ColorVibrance <= 0.001 && PlantExtra <= 0.001)
        return float4(color, 1.0);
    float day = FGM_DayFactor(uv);
    return float4(FGM_Guard(color, FGM_Vibrant(color, day)), 1.0);
}

technique FGM_Color
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_ColorPS;
    }
}
