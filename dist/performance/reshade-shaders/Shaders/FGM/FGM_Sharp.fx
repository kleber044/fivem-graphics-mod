// Nitidez por máscara de contraste. Não copia o shader CAS da AMD.
#include "FGM.fxh"

uniform float SharpStrength <
    ui_type = "slider";
    ui_min = 0.00;
    ui_max = 1.00;
    ui_step = 0.01;
    ui_label = "Nitidez";
> = 0.35;

float4 FGM_SharpPS(float4 pos : SV_Position, float2 uv : TEXCOORD) : SV_Target
{
    float2 px = float2(BUFFER_RCP_WIDTH, BUFFER_RCP_HEIGHT);
    float3 center = tex2D(ReShade::BackBuffer, uv).rgb;
    float3 north = tex2D(ReShade::BackBuffer, uv + float2(0.0, -px.y)).rgb;
    float3 south = tex2D(ReShade::BackBuffer, uv + float2(0.0, px.y)).rgb;
    float3 east = tex2D(ReShade::BackBuffer, uv + float2(px.x, 0.0)).rgb;
    float3 west = tex2D(ReShade::BackBuffer, uv + float2(-px.x, 0.0)).rgb;
    float3 blur = (north + south + east + west) * 0.25;
    float3 detail = center - blur;
    return float4(saturate(center + detail * SharpStrength), 1.0);
}

technique FGM_Sharp
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = FGM_SharpPS;
    }
}
