// Consulta a LUT 32³. Contraste, céu e pôr do sol estão na textura.
// Vivacidade, dia e noite ficam nos shaders seguintes. Custo: 3 amostras. Baixo.
#include "FGM.fxh"

texture2D FGM_LutTex < source = "fgm_high_lut.png"; >
{
    Width = 1024;
    Height = 32;
    Format = RGBA8;
};

sampler2D FGM_LutSamp
{
    Texture = FGM_LutTex;
    AddressU = CLAMP;
    AddressV = CLAMP;
    MinFilter = LINEAR;
    MagFilter = LINEAR;
    MipFilter = POINT;
};

float3 FGM_SampleLut(float3 color)
{
    const float size = 32.0;
    color = saturate(color);
    float blue = color.b * (size - 1.0);
    float slice0 = floor(blue);
    float slice1 = min(slice0 + 1.0, size - 1.0);
    float blend = blue - slice0;
    float x0 = (slice0 * size + color.r * (size - 1.0) + 0.5) / (size * size);
    float x1 = (slice1 * size + color.r * (size - 1.0) + 0.5) / (size * size);
    float y = (color.g * (size - 1.0) + 0.5) / size;
    float3 a = tex2D(FGM_LutSamp, float2(x0, y)).rgb;
    float3 b = tex2D(FGM_LutSamp, float2(x1, y)).rgb;
    return lerp(a, b, blend);
}

float4 FGM_LutPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    return float4(FGM_Guard(color, FGM_SampleLut(color)), 1.0);
}

technique FGM_Lut
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_LutPS;
    }
}
