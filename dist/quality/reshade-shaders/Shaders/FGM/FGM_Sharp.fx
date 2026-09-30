// Nitidez por máscara de contraste. Não copia o shader CAS da AMD.
// Até 0,14 o ganho é o do Performance, em todo pixel. O extra do Quality sai nos picos de luz.
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
    float baseGain = min(SharpStrength, 0.14);
    float extra = max(SharpStrength - 0.14, 0.0);
    float luma = dot(center, float3(0.2126, 0.7152, 0.0722));
    float detailLuma = dot(abs(detail), float3(0.2126, 0.7152, 0.0722));
    float spike = smoothstep(0.08, 0.18, detailLuma);
    float hot = smoothstep(0.28, 0.48, luma);
    float calm = 1.0 - spike * max(hot, 0.50);
    float gain = baseGain + extra * calm;
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
