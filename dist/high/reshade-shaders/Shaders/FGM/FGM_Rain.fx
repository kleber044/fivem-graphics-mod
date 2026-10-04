// Gotas na lente. Não lê clima, menu nem memória. O preset deixa a técnica desligada.
// A gota fica na borda, com tamanho variado, e não cobre o centro da visão.
// Custo, se ligada: cerca de 20 amostras no Ultra. Médio.
#include "FGM.fxh"

uniform float RainStrength <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 1.00;
    ui_step = 0.01;
    ui_label = "Força das gotas";
> = 0.70;

uniform int RainLayers <
    ui_type = "slider";
    ui_min = 1;
    ui_max = 2;
    ui_label = "Camadas de chuva";
> = 2;

uniform float RainDistort <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 1.50;
    ui_step = 0.01;
    ui_label = "Distorção das gotas";
> = 0.85;

float FGM_Hash(float2 p)
{
    float3 v = frac(float3(p.xyx) * 0.1031);
    v += dot(v, v.yzx + 33.33);
    return frac((v.x + v.y) * v.z);
}

void FGM_Layer(float2 uv, float scale, float speed, float time, out float drop, out float2 warp)
{
    float2 grid = uv * scale;
    float2 cell = floor(grid);
    drop = 0.0;
    warp = float2(0.0, 0.0);
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
            float2 head = float2(n * 0.62 + 0.19, fall);
            float2 delta = local - head;
            float wide = lerp(2.2, 5.2, n);
            delta.x *= wide;
            float size = lerp(8.0, 18.0, frac(n * 7.13));
            float bead = saturate(1.0 - length(delta) * size);
            bead = smoothstep(0.15, 0.85, bead);
            float streak = saturate(1.0 - abs(delta.x) * 14.0) * saturate(1.0 - abs(delta.y + 0.12) * 2.6) * 0.40;
            float here = max(bead, streak);
            if (here > drop)
            {
                drop = here;
                warp = delta / scale * bead;
            }
        }
    }
}

float4 FGM_RainPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (RainStrength <= 0.001)
        return float4(color, 1.0);

    float2 fromCenter = uv - float2(0.5, 0.46);
    float edge = smoothstep(0.28, 0.62, length(fromCenter * float2(1.15, 1.0)));
    if (edge <= 0.001)
        return float4(color, 1.0);

    float time = frac(timer / 9000.0);
    float drops = 0.0;
    float2 warp = float2(0.0, 0.0);
    float layerDrop = 0.0;
    float2 layerWarp = float2(0.0, 0.0);
    FGM_Layer(uv, 22.0, 0.85, time, layerDrop, layerWarp);
    drops = layerDrop;
    warp = layerWarp;
    if (RainLayers > 1)
    {
        FGM_Layer(uv + float2(0.17, 0.04), 38.0, 1.35, time, layerDrop, layerWarp);
        if (layerDrop > drops)
            warp = layerWarp;
        drops = max(drops, layerDrop * 0.65);
    }

    float amount = drops * edge * RainStrength;
    if (amount <= 0.02)
        return float4(color, 1.0);
    float2 sampleUv = uv + warp * edge * RainDistort * RainStrength * 0.012;
    color = tex2D(ReShade::BackBuffer, sampleUv).rgb;
    float3 highlight = float3(0.78, 0.84, 0.90);
    color = lerp(color, highlight, saturate(amount) * 0.28);
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
