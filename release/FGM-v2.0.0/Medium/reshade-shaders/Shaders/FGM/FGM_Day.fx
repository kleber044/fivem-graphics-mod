// Calma só do verde, amarelo e azul que já estão saturados.
// Montanha, árvore distante e céu lavado ficam de fora: puxar isso para o luma vira véu cinza.
// À noite este passo sai cedo. Custo: 5 amostras só de dia. Baixo.
#include "FGM.fxh"

uniform float DayCalm <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.40;
    ui_step = 0.01;
    ui_label = "Calma do dia";
> = 0.10;

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
    float open = smoothstep(0.18, 0.36, luma) * (1.0 - smoothstep(0.92, 0.98, luma));
    float satGate = smoothstep(0.28, 0.48, sat);
    float green = saturate((color.g - max(color.r, color.b)) / 0.08);
    float yellow = saturate((min(color.r, color.g) - color.b - 0.04) / 0.12);
    float notSunset = 1.0 - saturate((color.r - color.g - 0.08) / 0.20);
    float sky = saturate((color.b - max(color.r, color.g) - 0.04) / 0.10);
    float hue = max(green, max(yellow * notSunset, sky * 0.55));
    float pull = DayCalm * day * open * satGate * hue;
    pull *= 1.0 - FGM_Skin(color, luma, sat);
    pull = min(pull, 0.16);
    float3 calmed = lerp(color, luma.xxx, pull);
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
