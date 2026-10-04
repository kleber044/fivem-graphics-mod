// Véu azul do céu noturno. Não é o ClearView e não mexe em poste, neon nem planta.
// De dia sai cedo. Custo: 5 amostras só à noite. Baixo.
#include "FGM.fxh"

uniform float NightAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.30;
    ui_step = 0.005;
    ui_label = "Céu da noite";
> = 0.08;

float4 FGM_NightPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (NightAmount <= 0.0001)
        return float4(color, 1.0);
    float night = 1.0 - FGM_DayFactor(uv);
    if (night <= 0.001)
        return float4(color, 1.0);
    float tone = FGM_Luma(color);
    float blueDom = saturate((color.b - max(color.r, color.g)) / 0.08);
    if (blueDom <= 0.001)
        return float4(color, 1.0);
    float band = smoothstep(0.05, 0.14, tone) * (1.0 - smoothstep(0.30, 0.46, tone));
    float gray = 1.0 - smoothstep(0.04, 0.18, FGM_Sat(color));
    float pull = NightAmount * night * blueDom * band * gray;
    float3 neutral = float3(tone, tone * 0.98, tone * 0.96);
    return float4(FGM_Guard(color, lerp(color, neutral, saturate(pull))), 1.0);
}

technique FGM_Night
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_NightPS;
    }
}
