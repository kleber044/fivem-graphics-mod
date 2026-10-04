// Trava final de pele, branco e verde. Não devolve o quadro original: cada passo anterior já devolveu pele e roupa.
// Aqui o laranja residual desce, o branco neutro não passa de 0,955 e o verde neon cede.
// Custo: 1 amostra. Baixo.
#include "FGM.fxh"

float4 FGM_ProtectPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    float tone = FGM_Luma(color);
    float sat = FGM_Sat(color);
    float skin = FGM_Skin(color, tone, sat);
    float orange = smoothstep(0.16, 0.28, color.r - color.g) * skin;
    float3 cooled = saturate(float3(color.r - 0.06 * orange, color.g, color.b));
    float3 outColor = lerp(color, cooled, saturate(orange));
    float peak = max(outColor.r, max(outColor.g, outColor.b));
    if (peak > 0.96 && sat < 0.08)
        outColor *= 0.955 / peak;
    float foliage = FGM_Foliage(color);
    if (foliage > 0.4 && sat > 0.62)
    {
        float pull = smoothstep(0.62, 0.80, sat) * foliage;
        float3 calmer = tone + (outColor - tone) * 0.72;
        outColor = lerp(outColor, calmer, pull);
    }
    return float4(saturate(outColor), 1.0);
}

technique FGM_ColorProtection
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_ProtectPS;
    }
}
