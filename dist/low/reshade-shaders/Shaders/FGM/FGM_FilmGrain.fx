// Grão fino opcional. O preset deixa a técnica desligada e a força em zero.
// Custo, se ligada: 1 amostra. Baixo.
#include "FGM.fxh"

uniform float GrainAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 0.08;
    ui_step = 0.005;
    ui_label = "Grão";
> = 0.00;

float FGM_GrainHash(float2 p)
{
    float3 v = frac(float3(p.xyx) * 0.1031);
    v += dot(v, v.yzx + 33.33);
    return frac((v.x + v.y) * v.z);
}

float4 FGM_GrainPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (GrainAmount <= 0.0001)
        return float4(color, 1.0);
    float2 pixel = floor(uv * float2(BUFFER_WIDTH, BUFFER_HEIGHT));
    float n = FGM_GrainHash(pixel + float2(timer * 0.01, 0.0));
    float tone = FGM_Luma(color);
    float mid = smoothstep(0.08, 0.20, tone) * (1.0 - smoothstep(0.80, 0.95, tone));
    color += (n - 0.5) * GrainAmount * mid;
    return float4(saturate(color), 1.0);
}

technique FGM_FilmGrain
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_GrainPS;
    }
}
