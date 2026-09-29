(function () {
    var rainLayer = document.getElementById('rain');
    var bloodLayer = document.getElementById('blood');
    var lowHealth = document.getElementById('low-health');
    var hitVignette = document.getElementById('hit-vignette');
    var builtDrops = -1;

    function rng(seed) {
        var value = seed >>> 0;
        return function () {
            value = (value + 0x6d2b79f5) >>> 0;
            var t = Math.imul(value ^ (value >>> 15), 1 | value);
            t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    }

    function buildRain(drops) {
        var count = Math.max(0, drops | 0);
        if (count === builtDrops) {
            return;
        }
        builtDrops = count;
        rainLayer.textContent = '';
        var random = rng(0x51a7);
        var beads = Math.max(3, Math.round(count * 0.45));
        var i;
        var node;
        var left;
        var size;

        for (i = 0; i < count; i += 1) {
            node = document.createElement('span');
            node.className = 'drop';
            left = random() * 100;
            size = 10 + random() * 22;
            node.style.left = left.toFixed(2) + '%';
            node.style.height = size.toFixed(1) + 'px';
            node.style.animationDuration = (0.85 + random() * 1.15).toFixed(2) + 's';
            node.style.animationDelay = (-random() * 2.2).toFixed(2) + 's';
            node.style.opacity = String(0.35 + random() * 0.45);
            rainLayer.appendChild(node);
        }

        for (i = 0; i < beads; i += 1) {
            node = document.createElement('span');
            node.className = 'bead';
            size = 5 + random() * 11;
            node.style.left = (random() * 100).toFixed(2) + '%';
            node.style.top = (random() * 100).toFixed(2) + '%';
            node.style.width = size.toFixed(1) + 'px';
            node.style.height = (size * (1.15 + random() * 0.45)).toFixed(1) + 'px';
            node.style.animationDelay = (-random() * 7).toFixed(2) + 's';
            rainLayer.appendChild(node);
        }
    }

    function placeOnEdge(random) {
        var edge = Math.floor(random() * 4);
        if (edge === 0) {
            return { x: random() * 100, y: random() * 18 };
        }
        if (edge === 1) {
            return { x: random() * 100, y: 82 + random() * 18 };
        }
        if (edge === 2) {
            return { x: random() * 16, y: random() * 100 };
        }
        return { x: 84 + random() * 16, y: random() * 100 };
    }

    function showDamage(intensity) {
        var amount = Math.max(0.15, Math.min(1, Number(intensity) || 0.4));
        var count = 2 + Math.round(amount * 4);
        var random = rng((Date.now() & 0xffff) ^ Math.floor(amount * 1000));
        var i;
        var spot;
        var pos;
        var size;

        while (bloodLayer.children.length > 8) {
            bloodLayer.removeChild(bloodLayer.firstChild);
        }

        for (i = 0; i < count; i += 1) {
            spot = document.createElement('span');
            spot.className = 'splat';
            pos = placeOnEdge(random);
            size = 28 + amount * 70 + random() * 36;
            spot.style.left = pos.x.toFixed(2) + '%';
            spot.style.top = pos.y.toFixed(2) + '%';
            spot.style.width = size.toFixed(1) + 'px';
            spot.style.height = (size * (0.55 + random() * 0.7)).toFixed(1) + 'px';
            spot.style.transform = 'translate(-50%, -50%) rotate(' + Math.floor(random() * 180) + 'deg)';
            spot.style.opacity = String(0.35 + amount * 0.4);
            bloodLayer.appendChild(spot);
            window.setTimeout(function (node) {
                if (node.parentNode) {
                    node.parentNode.removeChild(node);
                }
            }, 2400, spot);
        }

        hitVignette.classList.remove('flash');
        void hitVignette.offsetWidth;
        hitVignette.style.setProperty('--hit', String(0.25 + amount * 0.45));
        hitVignette.classList.add('flash');
    }

    function onMessage(data) {
        if (!data || !data.action) {
            return;
        }
        if (data.action === 'rain') {
            var level = Math.max(0, Math.min(1, Number(data.level) || 0));
            rainLayer.style.setProperty('--rain', level.toFixed(3));
            if (data.active && level > 0.02) {
                buildRain(data.drops || 12);
                rainLayer.classList.add('on');
            } else {
                rainLayer.classList.remove('on');
            }
            return;
        }
        if (data.action === 'damage') {
            showDamage(data.intensity);
            return;
        }
        if (data.action === 'lowhealth') {
            lowHealth.style.opacity = String(Math.max(0, Math.min(0.55, Number(data.amount) || 0)));
            return;
        }
        if (data.action === 'hide') {
            rainLayer.classList.remove('on');
            lowHealth.style.opacity = '0';
            hitVignette.classList.remove('flash');
            bloodLayer.textContent = '';
        }
    }

    window.addEventListener('message', function (event) {
        onMessage(event.data);
    });

    var params = new URLSearchParams(window.location.search);
    if (params.get('preview') === '1') {
        document.body.classList.add('preview');
        var bar = document.getElementById('preview');
        bar.hidden = false;
        var slider = document.getElementById('rain-level');
        var drops = 22;

        function pushRain() {
            onMessage({
                action: 'rain',
                active: Number(slider.value) > 2,
                level: Number(slider.value) / 100,
                drops: drops,
            });
        }

        slider.addEventListener('input', pushRain);
        document.getElementById('btn-cine').addEventListener('click', function () {
            drops = 22;
            if (Number(slider.value) < 40) {
                slider.value = '70';
            }
            pushRain();
        });
        document.getElementById('btn-perf').addEventListener('click', function () {
            drops = 9;
            builtDrops = -1;
            if (Number(slider.value) < 40) {
                slider.value = '70';
            }
            pushRain();
        });
        document.getElementById('btn-hit').addEventListener('click', function () {
            onMessage({ action: 'damage', intensity: 0.35 });
            onMessage({ action: 'lowhealth', amount: 0.18 });
        });
        document.getElementById('btn-hit-hard').addEventListener('click', function () {
            onMessage({ action: 'damage', intensity: 0.85 });
            onMessage({ action: 'lowhealth', amount: 0.42 });
        });
        document.getElementById('btn-clear').addEventListener('click', function () {
            slider.value = '0';
            onMessage({ action: 'hide' });
        });
    }
}());
