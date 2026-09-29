Config = {
    -- Limiar do GetRainLevel / clima úmido para puddles, trilha e gotas na tela.
    rainThreshold = 0.15,

    -- Força do timecycle por período. golden cobre nascer (5h–8h) e pôr (17h–20h).
    strength = {
        quality = { day = 0.84, golden = 0.88, night = 0.90, rain = 0.76 },
        performance = { day = 0.50, golden = 0.52, night = 0.56, rain = 0.38 },
    },

    -- Em interior o grau fica mais baixo para não escurecer apartamentos e lojas.
    interiorStrengthScale = 0.45,

    engine = {
        quality = {
            shadowScale = 1.00,
            lightCutoff = 1.12,
            rainFx = 0.58,
            tracks = true,
            screenDrops = 22,
        },
        performance = {
            shadowScale = 0.60,
            lightCutoff = 0.70,
            rainFx = 0.28,
            tracks = false,
            screenDrops = 9,
        },
    },

    screen = {
        rain = true,
        blood = true,
        -- Dano menor que isto (pontos de vida) não desenha sangue.
        minDamage = 3,
    },
}
