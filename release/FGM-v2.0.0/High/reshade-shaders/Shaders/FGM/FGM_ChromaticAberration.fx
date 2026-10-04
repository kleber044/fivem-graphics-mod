// Aberração cromática opcional, só na borda. O preset deixa desligada e a força em zero.
// Custo, se ligada: 3 amostras. Baixo.
#include "FGM.fxh"

uniform float AberrationAmount <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 1.00;
    ui_step = 0.01;
    ui_label = "Aberração na borda";
> = 0.00;

float4 FGM_AberrationPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float3 color = tex2D(ReShade::BackBuffer, uv).rgb;
    if (AberrationAmount <= 0.001)
        return float4(color, 1.0);
    float2 fromCenter = uv - 0.5;
    float edge = smoothstep(0.25, 0.70, length(fromCenter));
    if (edge <= 0.001)
        return float4(color, 1.0);
    float2 shift = fromCenter * edge * AberrationAmount * 0.004;
    float red = tex2D(ReShade::BackBuffer, uv + shift).r;
    float blue = tex2D(ReShade::BackBuffer, uv - shift).b;
    return float4(saturate(float3(red, color.g, blue)), 1.0);
}

technique FGM_ChromaticAberration
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_AberrationPS;
    }
}
