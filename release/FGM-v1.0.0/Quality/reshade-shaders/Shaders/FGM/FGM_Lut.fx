// Grade cinematográfica original. A LUT faz contraste e split. A vivacidade é seletiva.
#include "FGM.fxh"

uniform float ColorVibrance <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.60;
    ui_step = 0.01;
    ui_label = "Vivacidade";
> = 0.14;

uniform float PlantExtra <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.60;
    ui_step = 0.01;
    ui_label = "Verde da vegetação";
> = 0.04;

float3 FGM_Vibrant(float3 color)
{
    float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
    float peak = max(color.r, max(color.g, color.b));
    float floorc = min(color.r, min(color.g, color.b));
    float sat = (peak - floorc) / max(peak, 0.001);
    float shadow = smoothstep(0.08, 0.22, luma);
    float notWhite = 1.0 - smoothstep(0.72, 0.90, luma);
    float headroom = 1.0 - smoothstep(0.28, 0.50, sat);
    float rg = color.r - color.g;
    float gb = color.g - color.b;
    float skin = smoothstep(0.04, 0.12, rg) * (1.0 - smoothstep(0.18, 0.32, rg));
    skin *= smoothstep(0.03, 0.10, gb);
    skin *= smoothstep(0.20, 0.40, luma) * (1.0 - smoothstep(0.62, 0.82, luma));
    skin *= smoothstep(0.10, 0.22, sat) * (1.0 - smoothstep(0.45, 0.65, sat));
    float protect = 1.0 - 0.80 * saturate(skin);
    float green = smoothstep(0.03, 0.14, color.g - max(color.r, color.b));
    green *= 1.0 - smoothstep(0.55, 0.80, sat);
    float hueBias = 1.0;
    float greenDom = saturate((color.g - max(color.r, color.b)) / 0.12);
    hueBias *= lerp(1.0, 0.35, greenDom);
    float blueDom = saturate((color.b - max(color.r, color.g)) / 0.10);
    hueBias *= lerp(1.0, 0.45, blueDom);
    float warmDom = saturate((color.r - max(color.g, color.b) - 0.05) / 0.14);
    hueBias *= lerp(1.0, 0.60, warmDom);
    float gain = ColorVibrance * shadow * notWhite * headroom * protect * hueBias * (1.0 + PlantExtra * green);
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

texture2D FGM_LutTex < source = "fgm_quality_lut.png"; >
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
    return float4(FGM_Vibrant(FGM_SampleLut(color)), 1.0);
}

technique FGM_Lut
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_LutPS;
    }
}
