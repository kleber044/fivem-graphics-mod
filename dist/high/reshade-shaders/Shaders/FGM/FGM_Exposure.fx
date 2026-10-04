// Viés curto de exposição. O ganho some no branco para não estourar camisa e nuvem.
// Custo: 1 amostra. Baixo.
#include "FGM.fxh"

uniform float ExposureBias <
    ui_type = "slider";
    ui_min = -0.10;
    ui_max = 0.10;
    ui_step = 0.005;
    ui_label = "Exposição";
> = 0.012;

float4 FGM_ExposurePS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (abs(ExposureBias) <= 0.0001)
        return float4(color, 1.0);
    float tone = FGM_Luma(color);
    float gain = ExposureBias * (1.0 - smoothstep(0.72, 0.94, tone));
    float3 lifted = saturate(color * (1.0 + gain));
    return float4(FGM_Guard(color, lifted), 1.0);
}

technique FGM_Exposure
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_ExposurePS;
    }
}
