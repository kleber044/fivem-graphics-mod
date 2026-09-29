// Gotas procedurais. Não leem o clima do GTA: em cena escura e pouco saturada
// (rua molhada, noite nublada) elas aparecem. Cena clara fica limpa.
// O centro da tela é mascarado de propósito.
#include "FGM.fxh"

uniform float RainStrength <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 1.00;
    ui_step = 0.01;
    ui_label = "Força das gotas";
> = 0.75;

uniform int RainLayers <
    ui_type = "slider";
    ui_min = 1;
    ui_max = 2;
    ui_label = "Camadas de chuva";
> = 2;

float FGM_Hash(float2 p)
{
    float3 v = frac(float3(p.xyx) * 0.1031);
    v += dot(v, v.yzx + 33.33);
    return frac((v.x + v.y) * v.z);
}

float FGM_Layer(float2 uv, float scale, float speed, float time)
{
    float2 grid = uv * scale;
    float2 cell = floor(grid);
    float drop = 0.0;
    [unroll]
    for (int y = -1; y <= 1; y++)
    {
        [unroll]
        for (int x = -1; x <= 1; x++)
        {
            float2 id = cell + float2(x, y);
            float n = FGM_Hash(id);
            float2 local = grid - id;
            float fall = frac(time * speed + n);
            float2 head = float2(n * 0.65 + 0.18, fall);
            float2 delta = local - head;
            delta.x *= 3.2;
            float bead = saturate(1.0 - length(delta) * 9.0);
            float streak = saturate(1.0 - abs(delta.x) * 14.0) * saturate(1.0 - abs(delta.y + 0.18) * 2.4);
            drop = max(drop, bead * 0.85 + streak * 0.45);
        }
    }
    return drop;
}

float4 FGM_RainPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
    float peak = max(color.r, max(color.g, color.b));
    float floorc = min(color.r, min(color.g, color.b));
    float saturation = (peak - floorc) / max(peak, 0.001);
    float dark = saturate((0.46 - luma) / 0.46);
    float dull = saturate((0.42 - saturation) / 0.42);
    float weather = dark * lerp(0.45, 1.0, dull);

    float2 fromCenter = uv - float2(0.5, 0.46);
    float edge = smoothstep(0.15, 0.48, length(fromCenter * float2(1.05, 1.0)));

    float time = frac(timer / 8000.0);
    float drops = FGM_Layer(uv, 28.0, 1.15, time);
    if (RainLayers > 1)
        drops = max(drops, FGM_Layer(uv + 0.17, 46.0, 1.7, time) * 0.75);

    float mask = drops * weather * edge * RainStrength;
    float3 wet = lerp(color, float3(0.78, 0.84, 0.90), 0.55);
    color = lerp(color, wet, saturate(mask));
    return float4(saturate(color), 1.0);
}

technique FGM_Rain
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_RainPS;
    }
}
