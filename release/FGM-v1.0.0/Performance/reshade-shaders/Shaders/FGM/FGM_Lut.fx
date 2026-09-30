// Grade cinematográfica. A LUT faz contraste e split. A vivacidade é seletiva.
// Em cena clara, a calma do dia reduz verde, amarelo e azul. Cena escura não entra nessa conta.
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

uniform float DayCalm <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.40;
    ui_step = 0.01;
    ui_label = "Calma do dia";
> = 0.22;

float FGM_SceneLuma(float2 uv)
{
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT) * 160.0;
    float3 w = float3(0.2126, 0.7152, 0.0722);
    float scene = dot(tex2D(ReShade::BackBuffer, uv + float2(px.x, 0.0)).rgb, w);
    scene += dot(tex2D(ReShade::BackBuffer, uv - float2(px.x, 0.0)).rgb, w);
    scene += dot(tex2D(ReShade::BackBuffer, uv + float2(0.0, px.y)).rgb, w);
    scene += dot(tex2D(ReShade::BackBuffer, uv - float2(0.0, px.y)).rgb, w);
    return scene * 0.25;
}

float FGM_Skin(float3 color, float luma, float sat)
{
    float rg = color.r - color.g;
    float gb = color.g - color.b;
    float skin = smoothstep(0.04, 0.12, rg) * (1.0 - smoothstep(0.18, 0.32, rg));
    skin *= smoothstep(0.03, 0.10, gb);
    skin *= smoothstep(0.20, 0.40, luma) * (1.0 - smoothstep(0.62, 0.82, luma));
    skin *= smoothstep(0.10, 0.22, sat) * (1.0 - smoothstep(0.45, 0.65, sat));
    return saturate(skin);
}

float3 FGM_Vibrant(float3 color, float day)
{
    float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
    float peak = max(color.r, max(color.g, color.b));
    float floorc = min(color.r, min(color.g, color.b));
    float sat = (peak - floorc) / max(peak, 0.001);
    float shadow = smoothstep(0.08, 0.22, luma);
    float notWhite = 1.0 - smoothstep(0.72, 0.90, luma);
    float headroom = 1.0 - smoothstep(0.28, 0.50, sat);
    float protect = 1.0 - 0.80 * FGM_Skin(color, luma, sat);
    float green = smoothstep(0.03, 0.14, color.g - max(color.r, color.b));
    green *= 1.0 - smoothstep(0.55, 0.80, sat);
    float hueBias = 1.0;
    float greenDom = saturate((color.g - max(color.r, color.b)) / 0.12);
    hueBias *= lerp(1.0, 0.35, greenDom);
    float blueDom = saturate((color.b - max(color.r, color.g)) / 0.10);
    hueBias *= lerp(1.0, 0.45, blueDom);
    float warmDom = saturate((color.r - max(color.g, color.b) - 0.05) / 0.14);
    hueBias *= lerp(1.0, 0.60, warmDom);
    float amount = ColorVibrance * (1.0 - 0.75 * day);
    float plant = PlantExtra * (1.0 - day);
    float gain = amount * shadow * notWhite * headroom * protect * hueBias * (1.0 + plant * green);
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

float3 FGM_DayCalm(float3 color, float day)
{
    if (day <= 0.001 || DayCalm <= 0.001)
        return color;

    float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
    float peak = max(color.r, max(color.g, color.b));
    float floorc = min(color.r, min(color.g, color.b));
    float sat = (peak - floorc) / max(peak, 0.001);
    float open = smoothstep(0.16, 0.34, luma) * (1.0 - smoothstep(0.90, 0.98, luma));
    float green = saturate((color.g - max(color.r, color.b)) / 0.08);
    float warm = saturate((min(color.r, color.g) - color.b - 0.02) / 0.10);
    float sky = saturate((color.b - max(color.r, color.g)) / 0.06);
    float pull = DayCalm * day * open * (0.70 + 1.00 * green + 0.55 * warm + 0.35 * sky);
    pull *= lerp(1.0, 0.35, FGM_Skin(color, luma, sat));
    pull = min(pull, 0.32);
    float3 calmed = lerp(color, luma.xxx, pull);
    float hot = smoothstep(0.86, 0.98, luma) * day;
    calmed = lerp(calmed, calmed * 0.97 + 0.01, hot);
    return saturate(calmed);
}

texture2D FGM_LutTex < source = "fgm_performance_lut.png"; >
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
    float day = smoothstep(0.26, 0.46, FGM_SceneLuma(uv));
    return float4(FGM_DayCalm(FGM_Vibrant(FGM_SampleLut(color), day), day), 1.0);
}

technique FGM_Lut
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_LutPS;
    }
}
