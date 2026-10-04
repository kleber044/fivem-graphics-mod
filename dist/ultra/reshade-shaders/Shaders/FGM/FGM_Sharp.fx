// Nitidez curta. Borda forte, folha e pele perdem força para não criar halo.
// Custo: 5 amostras. Baixo.
#include "FGM.fxh"

uniform float SharpStrength <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 1.00;
    ui_step = 0.01;
    ui_label = "Nitidez";
> = 0.26;

float4 FGM_SharpPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 center = tex2D(ReShade::BackBuffer, uv).rgb;
    if (SharpStrength <= 0.001)
        return float4(center, 1.0);
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT);
    float north = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(0.0, -px.y)).rgb);
    float south = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(0.0, px.y)).rgb);
    float east = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(px.x, 0.0)).rgb);
    float west = FGM_Luma(tex2D(ReShade::BackBuffer, uv + float2(-px.x, 0.0)).rgb);
    float detail = FGM_Luma(center) - (north + south + east + west) * 0.25;
    float edge = smoothstep(0.05, 0.16, abs(detail));
    float tone = FGM_Luma(center);
    float sat = FGM_Sat(center);
    float gain = SharpStrength * (1.0 - 0.70 * edge) * (1.0 - 0.50 * FGM_Foliage(center)) * (1.0 - 0.85 * FGM_Skin(center, tone, sat));
    return float4(saturate(center + detail * gain), 1.0);
}

technique FGM_Sharp
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_SharpPS;
    }
}
