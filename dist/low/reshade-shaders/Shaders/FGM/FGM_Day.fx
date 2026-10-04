// Calma do dia. Verde, amarelo e azul cedem um pouco quando a cena está clara.
// À noite este passo sai cedo. Custo: 5 amostras só de dia. Baixo.
#include "FGM.fxh"

uniform float DayCalm <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.40;
    ui_step = 0.01;
    ui_label = "Calma do dia";
> = 0.24;

float4 FGM_DayPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (DayCalm <= 0.001)
        return float4(color, 1.0);
    float day = FGM_DayFactor(uv);
    if (day <= 0.001)
        return float4(color, 1.0);
    float luma = FGM_Luma(color);
    float sat = FGM_Sat(color);
    float open = smoothstep(0.16, 0.34, luma) * (1.0 - smoothstep(0.90, 0.98, luma));
    float green = saturate((color.g - max(color.r, color.b)) / 0.08);
    float warm = saturate((min(color.r, color.g) - color.b - 0.02) / 0.10);
    float sky = saturate((color.b - max(color.r, color.g)) / 0.06);
    float pull = DayCalm * day * open * (0.70 + green + 0.55 * warm + 0.35 * sky);
    pull *= lerp(1.0, 0.35, FGM_Skin(color, luma, sat));
    pull = min(pull, 0.32);
    float3 calmed = lerp(color, luma.xxx, pull);
    float hot = smoothstep(0.86, 0.98, luma) * day;
    calmed = lerp(calmed, calmed * 0.97 + 0.01, hot);
    return float4(FGM_Guard(color, saturate(calmed)), 1.0);
}

technique FGM_Day
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_DayPS;
    }
}
