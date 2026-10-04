// Detalhe de asfalto em espaço de tela. A textura é gerada por este projeto.
// Não substitui o YTD do GTA. Sai cedo fora do asfalto. Custo: 2 amostras. Baixo.
#include "FGM.fxh"

uniform float RoadStrength <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.40;
    ui_step = 0.01;
    ui_label = "Detalhe do asfalto";
> = 0.12;

uniform float RoadScale <
    ui_type = "slider";
    ui_min = 2.00;
    ui_max = 16.00;
    ui_step = 0.50;
    ui_label = "Escala do asfalto";
> = 7.0;

texture2D FGM_RoadTex < source = "fgm_road.png"; >
{
    Format = RGBA8;
};

sampler2D FGM_RoadSamp
{
    Texture = FGM_RoadTex;
    AddressU = WRAP;
    AddressV = WRAP;
    MinFilter = LINEAR;
    MagFilter = LINEAR;
    MipFilter = LINEAR;
};

float4 FGM_RoadsPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (RoadStrength <= 0.001)
        return float4(color, 1.0);
    float mask = FGM_Asphalt(color) * RoadStrength;
    if (mask <= 0.001)
        return float4(color, 1.0);
    float detail = tex2D(FGM_RoadSamp, uv * RoadScale).r;
    float gain = 1.0 + (detail - 0.5) * 0.55;
    float3 textured = saturate(color * gain);
    return float4(lerp(color, textured, mask), 1.0);
}

technique FGM_Roads
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_RoadsPS;
    }
}
