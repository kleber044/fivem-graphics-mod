// A sombra perde um fio de dominante quente. Vegetação, pele e meio-tom ficam.
// Custo: 1 amostra. Baixo.
#include "FGM.fxh"

uniform float AmbientAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.20;
    ui_step = 0.005;
    ui_label = "Tom da sombra";
> = 0.000;

float4 FGM_AmbientPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (AmbientAmount <= 0.0001)
        return float4(color, 1.0);
    float tone = FGM_Luma(color);
    float shadow = smoothstep(0.42, 0.06, tone);
    if (shadow <= 0.001)
        return float4(color, 1.0);
    float sat = FGM_Sat(color);
    float weight = AmbientAmount * shadow * (1.0 - smoothstep(0.20, 0.45, sat)) * (1.0 - FGM_Foliage(color));
    weight *= 1.0 - FGM_Skin(color, tone, sat);
    float3 cooled = saturate(float3(color.r - 0.012, color.g - 0.002, color.b + 0.008));
    return float4(FGM_Guard(color, lerp(color, cooled, saturate(weight))), 1.0);
}

technique FGM_AmbientTone
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_AmbientPS;
    }
}
