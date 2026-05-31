
        // ─── PROFESSIONAL AUDIO ENGINE (Fieldrunners 2 Style) ───
        class SoundFX {
            constructor() {
                this.ctx = null;
                this.master = null;
                this.compressor = null;
                this.musicPlaying = false;
                this.musicGain = null;
                this.musicNodes = [];
            }

            init() {
                try {
                    if (!this.ctx) {
                        this.ctx = new (window.AudioContext || window.webkitAudioContext)();
                        // Master dynamics compressor for consistent volume
                        this.compressor = this.ctx.createDynamicsCompressor();
                        this.compressor.threshold.value = -24;
                        this.compressor.knee.value = 30;
                        this.compressor.ratio.value = 12;
                        this.compressor.attack.value = 0.003;
                        this.compressor.release.value = 0.25;
                        this.compressor.connect(this.ctx.destination);
                        // Master gain
                        this.master = this.ctx.createGain();
                        this.master.gain.value = 0.7;
                        this.master.connect(this.compressor);
                    }
                    if (this.ctx.state === 'suspended') this.ctx.resume();
                } catch (e) {
                    console.warn("AudioContext init failed:", e);
                    this.ctx = null;
                }
            }

            // Create white noise buffer utility
            _noiseBuffer(duration) {
                const len = this.ctx.sampleRate * duration;
                const buf = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
                const data = buf.getChannelData(0);
                for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
                return buf;
            }

            // ── SHOOT SOUNDS (per tower type) ──
            playShoot(type) {
                try {
                    this.init();
                    if (!this.ctx) return;
                    const now = this.ctx.currentTime;

                    if (type === 'arrow') {
                        // Crossbow twang: fast plucked string + air whoosh
                        const osc1 = this.ctx.createOscillator();
                        const g1 = this.ctx.createGain();
                        osc1.type = 'triangle';
                        osc1.frequency.setValueAtTime(1800, now);
                        osc1.frequency.exponentialRampToValueAtTime(200, now + 0.12);
                        g1.gain.setValueAtTime(0.18, now);
                        g1.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
                        osc1.connect(g1); g1.connect(this.master);
                        osc1.start(now); osc1.stop(now + 0.12);

                        // Subtle string body resonance
                        const osc2 = this.ctx.createOscillator();
                        const g2 = this.ctx.createGain();
                        osc2.type = 'sine';
                        osc2.frequency.setValueAtTime(440, now);
                        osc2.frequency.exponentialRampToValueAtTime(110, now + 0.15);
                        g2.gain.setValueAtTime(0.06, now);
                        g2.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
                        osc2.connect(g2); g2.connect(this.master);
                        osc2.start(now); osc2.stop(now + 0.15);

                        // Air whoosh noise
                        const ns = this.ctx.createBufferSource();
                        ns.buffer = this._noiseBuffer(0.08);
                        const nf = this.ctx.createBiquadFilter();
                        nf.type = 'bandpass'; nf.frequency.value = 4000; nf.Q.value = 2;
                        const ng = this.ctx.createGain();
                        ng.gain.setValueAtTime(0.04, now);
                        ng.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
                        ns.connect(nf); nf.connect(ng); ng.connect(this.master);
                        ns.start(now); ns.stop(now + 0.08);

                    } else if (type === 'slow') {
                        // Goo splat: wet bubbly sound
                        const osc = this.ctx.createOscillator();
                        const g = this.ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(600, now);
                        osc.frequency.exponentialRampToValueAtTime(80, now + 0.18);
                        g.gain.setValueAtTime(0.1, now);
                        g.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
                        osc.connect(g); g.connect(this.master);
                        osc.start(now); osc.stop(now + 0.18);

                        // Bubble pop overtone
                        const osc2 = this.ctx.createOscillator();
                        const g2 = this.ctx.createGain();
                        osc2.type = 'triangle';
                        osc2.frequency.setValueAtTime(1200, now);
                        osc2.frequency.exponentialRampToValueAtTime(200, now + 0.06);
                        g2.gain.setValueAtTime(0.05, now);
                        g2.gain.exponentialRampToValueAtTime(0.001, now + 0.06);
                        osc2.connect(g2); g2.connect(this.master);
                        osc2.start(now); osc2.stop(now + 0.06);

                    } else if (type === 'bomb') {
                        // Mortar launch: deep thump + metal clank
                        const osc = this.ctx.createOscillator();
                        const g = this.ctx.createGain();
                        osc.type = 'sawtooth';
                        osc.frequency.setValueAtTime(220, now);
                        osc.frequency.exponentialRampToValueAtTime(35, now + 0.3);
                        g.gain.setValueAtTime(0.2, now);
                        g.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
                        osc.connect(g); g.connect(this.master);
                        osc.start(now); osc.stop(now + 0.3);

                        // Metal tube resonance
                        const osc2 = this.ctx.createOscillator();
                        const g2 = this.ctx.createGain();
                        osc2.type = 'square';
                        osc2.frequency.setValueAtTime(800, now);
                        osc2.frequency.exponentialRampToValueAtTime(100, now + 0.05);
                        g2.gain.setValueAtTime(0.08, now);
                        g2.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
                        osc2.connect(g2); g2.connect(this.master);
                        osc2.start(now); osc2.stop(now + 0.05);

                    } else if (type === 'flame') {
                        // Flamethrower whoosh: filtered noise burst
                        const ns = this.ctx.createBufferSource();
                        ns.buffer = this._noiseBuffer(0.15);
                        const bp = this.ctx.createBiquadFilter();
                        bp.type = 'bandpass'; bp.frequency.value = 1500; bp.Q.value = 0.8;
                        bp.frequency.setValueAtTime(2000, now);
                        bp.frequency.exponentialRampToValueAtTime(500, now + 0.15);
                        const g = this.ctx.createGain();
                        g.gain.setValueAtTime(0.12, now);
                        g.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
                        ns.connect(bp); bp.connect(g); g.connect(this.master);
                        ns.start(now); ns.stop(now + 0.15);

                        // Low roar undertone
                        const osc = this.ctx.createOscillator();
                        const g2 = this.ctx.createGain();
                        osc.type = 'sawtooth';
                        osc.frequency.setValueAtTime(120, now);
                        osc.frequency.linearRampToValueAtTime(60, now + 0.12);
                        g2.gain.setValueAtTime(0.06, now);
                        g2.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
                        osc.connect(g2); g2.connect(this.master);
                        osc.start(now); osc.stop(now + 0.12);

                    } else if (type === 'tesla') {
                        // Tesla electric zap: harsh buzzy snap + sparkle
                        const osc = this.ctx.createOscillator();
                        const g = this.ctx.createGain();
                        osc.type = 'sawtooth';
                        osc.frequency.setValueAtTime(3000, now);
                        osc.frequency.exponentialRampToValueAtTime(150, now + 0.1);
                        g.gain.setValueAtTime(0.15, now);
                        g.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
                        osc.connect(g); g.connect(this.master);
                        osc.start(now); osc.stop(now + 0.1);

                        // Electric crackle noise burst
                        const ns = this.ctx.createBufferSource();
                        ns.buffer = this._noiseBuffer(0.08);
                        const hp = this.ctx.createBiquadFilter();
                        hp.type = 'highpass'; hp.frequency.value = 5000;
                        const ng = this.ctx.createGain();
                        ng.gain.setValueAtTime(0.08, now);
                        ng.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
                        ns.connect(hp); hp.connect(ng); ng.connect(this.master);
                        ns.start(now); ns.stop(now + 0.08);

                        // Sub hum body
                        const osc2 = this.ctx.createOscillator();
                        const g2 = this.ctx.createGain();
                        osc2.type = 'sine';
                        osc2.frequency.value = 60;
                        g2.gain.setValueAtTime(0.1, now);
                        g2.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
                        osc2.connect(g2); g2.connect(this.master);
                        osc2.start(now); osc2.stop(now + 0.15);

                    } else {
                        // Generic fallback
                        const osc = this.ctx.createOscillator();
                        const g = this.ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(1200, now);
                        osc.frequency.exponentialRampToValueAtTime(400, now + 0.08);
                        g.gain.setValueAtTime(0.12, now);
                        g.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
                        osc.connect(g); g.connect(this.master);
                        osc.start(now); osc.stop(now + 0.08);
                    }
                } catch (e) { /* silent */ }
            }

            // ── HIT IMPACT ──
            playHit() {
                try {
                    this.init();
                    if (!this.ctx) return;
                    const now = this.ctx.currentTime;
                    // Meaty impact thud
                    const osc = this.ctx.createOscillator();
                    const g = this.ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(200, now);
                    osc.frequency.exponentialRampToValueAtTime(40, now + 0.08);
                    g.gain.setValueAtTime(0.1, now);
                    g.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
                    osc.connect(g); g.connect(this.master);
                    osc.start(now); osc.stop(now + 0.08);

                    // Snap noise layer
                    const ns = this.ctx.createBufferSource();
                    ns.buffer = this._noiseBuffer(0.03);
                    const ng = this.ctx.createGain();
                    ng.gain.setValueAtTime(0.04, now);
                    ng.gain.exponentialRampToValueAtTime(0.001, now + 0.03);
                    ns.connect(ng); ng.connect(this.master);
                    ns.start(now); ns.stop(now + 0.03);
                } catch (e) { /* silent */ }
            }

            // ── EXPLOSION (multi-layered) ──
            playExplode() {
                try {
                    this.init();
                    if (!this.ctx) return;
                    const now = this.ctx.currentTime;
                    
                    // Layer 1: Sub-bass thump
                    const sub = this.ctx.createOscillator();
                    const sg = this.ctx.createGain();
                    sub.type = 'sine';
                    sub.frequency.setValueAtTime(80, now);
                    sub.frequency.exponentialRampToValueAtTime(20, now + 0.5);
                    sg.gain.setValueAtTime(0.35, now);
                    sg.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
                    sub.connect(sg); sg.connect(this.master);
                    sub.start(now); sub.stop(now + 0.5);

                    // Layer 2: Noise burst with lowpass sweep
                    const ns = this.ctx.createBufferSource();
                    ns.buffer = this._noiseBuffer(0.6);
                    const lp = this.ctx.createBiquadFilter();
                    lp.type = 'lowpass';
                    lp.frequency.setValueAtTime(3000, now);
                    lp.frequency.exponentialRampToValueAtTime(40, now + 0.6);
                    const ng = this.ctx.createGain();
                    ng.gain.setValueAtTime(0.3, now);
                    ng.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
                    ns.connect(lp); lp.connect(ng); ng.connect(this.master);
                    ns.start(now); ns.stop(now + 0.6);

                    // Layer 3: Metal debris clang
                    const clang = this.ctx.createOscillator();
                    const cg = this.ctx.createGain();
                    clang.type = 'square';
                    clang.frequency.setValueAtTime(600, now + 0.02);
                    clang.frequency.exponentialRampToValueAtTime(80, now + 0.15);
                    cg.gain.setValueAtTime(0.08, now + 0.02);
                    cg.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
                    clang.connect(cg); cg.connect(this.master);
                    clang.start(now + 0.02); clang.stop(now + 0.15);

                    // Layer 4: Distant rumble tail
                    const rum = this.ctx.createOscillator();
                    const rg = this.ctx.createGain();
                    rum.type = 'sawtooth';
                    rum.frequency.setValueAtTime(50, now + 0.1);
                    rum.frequency.linearRampToValueAtTime(25, now + 0.8);
                    rg.gain.setValueAtTime(0.06, now + 0.1);
                    rg.gain.exponentialRampToValueAtTime(0.001, now + 0.8);
                    rum.connect(rg); rg.connect(this.master);
                    rum.start(now + 0.1); rum.stop(now + 0.8);
                } catch (e) { /* silent */ }
            }

            // ── BUY / UPGRADE: satisfying coin chime ──
            playBuy() {
                try {
                    this.init();
                    if (!this.ctx) return;
                    const now = this.ctx.currentTime;
                    // Ascending chime arpeggio (coin collect feel)
                    const notes = [523.25, 659.25, 783.99, 1046.50]; // C5-E5-G5-C6
                    notes.forEach((f, i) => {
                        const o = this.ctx.createOscillator();
                        const g = this.ctx.createGain();
                        o.type = 'sine';
                        o.frequency.value = f;
                        g.gain.setValueAtTime(0.001, now + i * 0.05);
                        g.gain.linearRampToValueAtTime(0.12, now + i * 0.05 + 0.015);
                        g.gain.exponentialRampToValueAtTime(0.001, now + i * 0.05 + 0.25);
                        o.connect(g); g.connect(this.master);
                        o.start(now + i * 0.05);
                        o.stop(now + i * 0.05 + 0.25);
                    });
                    // Sparkle shimmer
                    const sh = this.ctx.createOscillator();
                    const sg = this.ctx.createGain();
                    sh.type = 'triangle';
                    sh.frequency.value = 2093;
                    sg.gain.setValueAtTime(0.03, now + 0.15);
                    sg.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
                    sh.connect(sg); sg.connect(this.master);
                    sh.start(now + 0.15); sh.stop(now + 0.4);
                } catch (e) { /* silent */ }
            }

            // ── DENY: buzzer ──
            playDeny() {
                try {
                    this.init();
                    if (!this.ctx) return;
                    const now = this.ctx.currentTime;
                    // Low harsh buzz
                    const o1 = this.ctx.createOscillator();
                    const g1 = this.ctx.createGain();
                    o1.type = 'sawtooth';
                    o1.frequency.setValueAtTime(110, now);
                    o1.frequency.linearRampToValueAtTime(80, now + 0.2);
                    g1.gain.setValueAtTime(0.15, now);
                    g1.gain.linearRampToValueAtTime(0.001, now + 0.2);
                    o1.connect(g1); g1.connect(this.master);
                    o1.start(now); o1.stop(now + 0.2);
                    // Dissonant overtone
                    const o2 = this.ctx.createOscillator();
                    const g2 = this.ctx.createGain();
                    o2.type = 'square';
                    o2.frequency.value = 165;
                    g2.gain.setValueAtTime(0.05, now);
                    g2.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
                    o2.connect(g2); g2.connect(this.master);
                    o2.start(now); o2.stop(now + 0.15);
                } catch (e) { /* silent */ }
            }

            // ── WAVE START FANFARE ──
            playWaveStart() {
                try {
                    this.init();
                    if (!this.ctx) return;
                    const now = this.ctx.currentTime;
                    // Brass fanfare: short ascending power chord
                    const chord = [196.00, 246.94, 293.66, 392.00]; // G3-B3-D4-G4
                    chord.forEach((f, i) => {
                        const o = this.ctx.createOscillator();
                        const g = this.ctx.createGain();
                        o.type = 'sawtooth';
                        o.frequency.value = f;
                        g.gain.setValueAtTime(0.001, now + i * 0.04);
                        g.gain.linearRampToValueAtTime(0.08, now + i * 0.04 + 0.05);
                        g.gain.exponentialRampToValueAtTime(0.001, now + i * 0.04 + 0.6);
                        o.connect(g); g.connect(this.master);
                        o.start(now + i * 0.04);
                        o.stop(now + i * 0.04 + 0.6);
                    });
                    // Snare hit accent
                    const ns = this.ctx.createBufferSource();
                    ns.buffer = this._noiseBuffer(0.1);
                    const hp = this.ctx.createBiquadFilter();
                    hp.type = 'highpass'; hp.frequency.value = 3000;
                    const ng = this.ctx.createGain();
                    ng.gain.setValueAtTime(0.12, now + 0.12);
                    ng.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
                    ns.connect(hp); hp.connect(ng); ng.connect(this.master);
                    ns.start(now + 0.12); ns.stop(now + 0.22);
                } catch (e) { /* silent */ }
            }

            // ── ENEMY LEAK (life lost) ──
            playLeak() {
                try {
                    this.init();
                    if (!this.ctx) return;
                    const now = this.ctx.currentTime;
                    // Warning descending tone
                    const o = this.ctx.createOscillator();
                    const g = this.ctx.createGain();
                    o.type = 'triangle';
                    o.frequency.setValueAtTime(880, now);
                    o.frequency.exponentialRampToValueAtTime(220, now + 0.3);
                    g.gain.setValueAtTime(0.18, now);
                    g.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
                    o.connect(g); g.connect(this.master);
                    o.start(now); o.stop(now + 0.3);
                    // Alarm beep
                    const o2 = this.ctx.createOscillator();
                    const g2 = this.ctx.createGain();
                    o2.type = 'square';
                    o2.frequency.value = 440;
                    g2.gain.setValueAtTime(0.06, now + 0.05);
                    g2.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
                    o2.connect(g2); g2.connect(this.master);
                    o2.start(now + 0.05); o2.stop(now + 0.2);
                } catch (e) { /* silent */ }
            }

            // ── VICTORY JINGLE: triumphant fanfare ──
            playWin() {
                try {
                    this.init();
                    if (!this.ctx) return;
                    const now = this.ctx.currentTime;
                    // Heroic ascending melody (C-E-G-C-E-G-C)
                    const melody = [
                        { f: 261.63, t: 0, d: 0.3 },    // C4
                        { f: 329.63, t: 0.12, d: 0.3 },  // E4
                        { f: 392.00, t: 0.24, d: 0.3 },  // G4
                        { f: 523.25, t: 0.36, d: 0.35 },  // C5
                        { f: 659.25, t: 0.5, d: 0.35 },  // E5
                        { f: 783.99, t: 0.65, d: 0.5 },   // G5
                        { f: 1046.50, t: 0.85, d: 0.8 },  // C6 sustained
                    ];
                    melody.forEach(n => {
                        // Main voice
                        const o = this.ctx.createOscillator();
                        const g = this.ctx.createGain();
                        o.type = 'triangle';
                        o.frequency.value = n.f;
                        g.gain.setValueAtTime(0.001, now + n.t);
                        g.gain.linearRampToValueAtTime(0.13, now + n.t + 0.03);
                        g.gain.exponentialRampToValueAtTime(0.001, now + n.t + n.d);
                        o.connect(g); g.connect(this.master);
                        o.start(now + n.t); o.stop(now + n.t + n.d);
                        // Octave shimmer
                        const o2 = this.ctx.createOscillator();
                        const g2 = this.ctx.createGain();
                        o2.type = 'sine';
                        o2.frequency.value = n.f * 2;
                        g2.gain.setValueAtTime(0.001, now + n.t);
                        g2.gain.linearRampToValueAtTime(0.04, now + n.t + 0.03);
                        g2.gain.exponentialRampToValueAtTime(0.001, now + n.t + n.d * 0.7);
                        o2.connect(g2); g2.connect(this.master);
                        o2.start(now + n.t); o2.stop(now + n.t + n.d);
                    });
                    // Victory drum roll accent
                    for (let i = 0; i < 4; i++) {
                        const ns = this.ctx.createBufferSource();
                        ns.buffer = this._noiseBuffer(0.05);
                        const hp = this.ctx.createBiquadFilter();
                        hp.type = 'highpass'; hp.frequency.value = 4000;
                        const ng = this.ctx.createGain();
                        ng.gain.setValueAtTime(0.06, now + 0.85 + i * 0.06);
                        ng.gain.exponentialRampToValueAtTime(0.001, now + 0.9 + i * 0.06);
                        ns.connect(hp); hp.connect(ng); ng.connect(this.master);
                        ns.start(now + 0.85 + i * 0.06); ns.stop(now + 0.95 + i * 0.06);
                    }
                } catch (e) { /* silent */ }
            }

            // ── DEFEAT JINGLE: somber descending ──
            playLose() {
                try {
                    this.init();
                    if (!this.ctx) return;
                    const now = this.ctx.currentTime;
                    // Sad descending minor melody
                    const melody = [
                        { f: 392.00, t: 0 },      // G4
                        { f: 349.23, t: 0.2 },     // F4
                        { f: 311.13, t: 0.4 },     // Eb4
                        { f: 261.63, t: 0.6 },     // C4
                        { f: 196.00, t: 0.85 },    // G3 sustained
                    ];
                    melody.forEach((n, i) => {
                        const dur = i === melody.length - 1 ? 1.0 : 0.4;
                        const o = this.ctx.createOscillator();
                        const g = this.ctx.createGain();
                        o.type = 'triangle';
                        o.frequency.value = n.f;
                        g.gain.setValueAtTime(0.001, now + n.t);
                        g.gain.linearRampToValueAtTime(0.12, now + n.t + 0.04);
                        g.gain.exponentialRampToValueAtTime(0.001, now + n.t + dur);
                        o.connect(g); g.connect(this.master);
                        o.start(now + n.t); o.stop(now + n.t + dur);
                        // Detuned unison for melancholy
                        const o2 = this.ctx.createOscillator();
                        const g2 = this.ctx.createGain();
                        o2.type = 'sine';
                        o2.frequency.value = n.f * 0.998; // slightly flat
                        g2.gain.setValueAtTime(0.001, now + n.t);
                        g2.gain.linearRampToValueAtTime(0.06, now + n.t + 0.04);
                        g2.gain.exponentialRampToValueAtTime(0.001, now + n.t + dur);
                        o2.connect(g2); g2.connect(this.master);
                        o2.start(now + n.t); o2.stop(now + n.t + dur);
                    });
                } catch (e) { /* silent */ }
            }

            // ── AMBIENT BACKGROUND MUSIC LOOP ──
            startMusic() {
                try {
                    this.init();
                    if (!this.ctx || this.musicPlaying) return;
                    this.musicPlaying = true;

                    this.musicGain = this.ctx.createGain();
                    this.musicGain.gain.value = 0.0;
                    this.musicGain.gain.linearRampToValueAtTime(0.06, this.ctx.currentTime + 2);
                    this.musicGain.connect(this.master);

                    // Warm pad drone: root + fifth, gently oscillating
                    const padFreqs = [65.41, 98.00]; // C2 + G2
                    padFreqs.forEach(f => {
                        const o = this.ctx.createOscillator();
                        o.type = 'triangle';
                        o.frequency.value = f;
                        // Gentle vibrato via LFO
                        const lfo = this.ctx.createOscillator();
                        const lfoGain = this.ctx.createGain();
                        lfo.frequency.value = 0.3 + Math.random() * 0.2;
                        lfoGain.gain.value = 1.5;
                        lfo.connect(lfoGain);
                        lfoGain.connect(o.frequency);
                        lfo.start();
                        o.connect(this.musicGain);
                        o.start();
                        this.musicNodes.push(o, lfo);
                    });

                    // Subtle high shimmer pad
                    const shimmer = this.ctx.createOscillator();
                    shimmer.type = 'sine';
                    shimmer.frequency.value = 523.25; // C5
                    const shimGain = this.ctx.createGain();
                    shimGain.gain.value = 0.012;
                    // Tremolo on shimmer
                    const trem = this.ctx.createOscillator();
                    const tremG = this.ctx.createGain();
                    trem.frequency.value = 0.5;
                    tremG.gain.value = 0.008;
                    trem.connect(tremG);
                    tremG.connect(shimGain.gain);
                    trem.start();
                    shimmer.connect(shimGain);
                    shimGain.connect(this.musicGain);
                    shimmer.start();
                    this.musicNodes.push(shimmer, trem);
                } catch (e) { /* silent */ }
            }

            stopMusic() {
                try {
                    if (!this.musicPlaying) return;
                    this.musicPlaying = false;
                    if (this.musicGain) {
                        this.musicGain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 1);
                    }
                    setTimeout(() => {
                        this.musicNodes.forEach(n => { try { n.stop(); } catch(e){} });
                        this.musicNodes = [];
                    }, 1200);
                } catch (e) { /* silent */ }
            }
        }
        const sfx = new SoundFX();

        const assets = {
            arrow_tower: new Image(),
            bomb_tower: new Image(),
            flame_tower: new Image(),
            tesla_tower: new Image(),
            slow_tower: new Image(),
            enemy_soldier: new Image(),
            enemy_scout: new Image(),
            enemy_heavy: new Image(),
            enemy_air: new Image(),
            map_tile: new Image()
        };

        let imagesLoaded = 0;
        const totalImages = Object.keys(assets).length;

        function initAssets(callback) {
            let loaded = 0;
            const btn = document.querySelector('.start-btn');
            if (btn) btn.disabled = true;

            for (let key in assets) {
                assets[key].onload = () => {
                    loaded++;
                    if (btn) btn.innerText = `Đang tải ảnh... (${Math.round((loaded/totalImages)*100)}%)`;
                    if (loaded === totalImages) {
                        if (btn) {
                            btn.disabled = false;
                            btn.innerText = 'XUẤT QUÂN TRẬN ĐỒ';
                        }
                        callback();
                    }
                };
                assets[key].onerror = () => {
                    console.log('Failed to load asset: ' + key);
                    loaded++;
                    if (btn) btn.innerText = `Lỗi tải ảnh... (${Math.round((loaded/totalImages)*100)}%)`;
                    if (loaded === totalImages) {
                        if (btn) {
                            btn.disabled = false;
                            btn.innerText = 'XUẤT QUÂN TRẬN ĐỒ';
                        }
                        callback();
                    }
                };
                assets[key].src = 'assets/' + key + '.png';
            }
        }

        // ─── GAME CONSTANTS & STATE ───
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // Dimensions
        const COLS = 16;
        const ROWS = 11;
        const CELL_SIZE = 50; // Total size 800x550

        // Gates
        const START_CELL = { x: 0, y: 5 };
        const EXIT_CELL = { x: 15, y: 5 };

        // Resources
        let gold = 350; // Dư dả vàng để xây dựng ban đầu
        let hp = 30;
        const MAX_HP = 30;
        let currentWaveNum = -1;
        const MAX_WAVES = 10;
        let totalExpectedEnemies = 0;
        let totalSpawnedEnemies = 0;
        let selectedLevelNum = 1; // 1: Co Loa (flat), 2: Cao Lo (obstacles), 3: Bach Dang (river)

        // Arrays
        let grid = Array(COLS).fill().map(() => Array(ROWS).fill(0)); // 0 = empty, 1 = tower, 2 = level obstacles
        let towers = [];
        let enemies = [];
        let projectiles = [];
        let particles = [];
        let shortestPath = []; // BFS cache

        // Controls
        let selectedBuildType = null; // 'arrow', 'slow', 'bomb', 'flame', 'tesla'
        let selectedPlacedTower = null; // clicked tower
        let waveActive = false;
        let isPaused = true;
        let gameSpeed = 1; // 1 or 2
        let showFlowField = true;
        let gameLoopId = null;

        // Costs & Specs (Fieldrunners-style)
        const TOWER_SPECS = {
            arrow: {
                name: 'Nỏ Thần Cổ Loa',
                cost: 40,
                upgradeCost: 40,
                sellValue: 30,
                range: 135,
                damage: 18,
                fireRate: 0.65, // s per shot — nhanh hơn
                color: '#C8960C',
                desc: 'Bắn liên châu nỏ tre đơn mục tiêu nhanh. Cấp 3 nâng thành nỏ nòng kép bắn liên thanh.'
            },
            slow: {
                name: 'Bẫy Độc Lục Bảo',
                cost: 55,
                upgradeCost: 45,
                sellValue: 40,
                range: 105,
                damage: 3,
                fireRate: 1.0,
                color: '#5ABCAA',
                slowEffect: 0.50, // slows by 50%
                desc: 'Phun chất bám dính làm chậm kẻ địch. Cấp 3 phun dung dịch độc ăn mòn rút HP.'
            },
            bomb: {
                name: 'Thần Cơ Pháo Đồng',
                cost: 80,
                upgradeCost: 65,
                sellValue: 60,
                range: 170,
                damage: 55,
                fireRate: 1.6,
                color: '#B87333',
                splash: 85,
                desc: 'Bắn pháo cối parabol nổ lan AoE lớn. Nâng cấp tăng tầm bắn và uy lực khói lửa. Diệt được cả Không Quân.'
            },
            flame: {
                name: 'Hỏa Tháp Thần Long',
                cost: 180,
                upgradeCost: 120,
                sellValue: 135,
                range: 95,
                damage: 12,
                fireRate: 0.08, // Chùm lửa phun liên tiếp — nhanh hơn
                color: '#ff006e',
                desc: 'Phun chùm lửa liên tiếp hình quạt thiêu cháy tất cả kẻ địch đi qua, làm mất HP âm ỉ.'
            },
            tesla: {
                name: 'Lôi Tháp Thần Kim',
                cost: 250,
                upgradeCost: 160,
                sellValue: 190,
                range: 145,
                damage: 100,
                fireRate: 0.85,
                color: '#3a86ff',
                desc: 'Phóng tia sét giật chuỗi truyền liên hoàn qua 3-5 mục tiêu gần nhau với sát thương hủy diệt.'
            }
        };

        // Enemy Waves Database (Fieldrunners 10-wave — cân bằng dễ hơn)
        const WAVE_DATABASE = [
            { scout: 4, normal: 0, heavy: 0, air: 0, boss: 0 },
            { scout: 3, normal: 3, heavy: 0, air: 0, boss: 0 },
            { scout: 2, normal: 5, heavy: 1, air: 0, boss: 0 },
            { scout: 0, normal: 4, heavy: 0, air: 3, boss: 0 }, // Không quân xuất kích!
            { scout: 5, normal: 6, heavy: 2, air: 0, boss: 0 },
            { scout: 2, normal: 5, heavy: 3, air: 2, boss: 0 },
            { scout: 0, normal: 0, heavy: 1, air: 6, boss: 0 }, // Cơn bão Không quân!
            { scout: 4, normal: 8, heavy: 4, air: 3, boss: 0 },
            { scout: 6, normal: 7, heavy: 5, air: 4, boss: 0 },
            { scout: 0, normal: 6, heavy: 3, air: 3, boss: 1 }  // Boss cuối cùng xuất kích!
        ];

        // Enemy Templates — HP giảm, tốc độ chậm hơn, thưởng nhiều hơn
        const ENEMY_TEMPLATES = {
            scout: {
                name: 'Lính Trinh Sát',
                hp: 25,
                speed: 1.6,
                reward: 12,
                color: '#F5EED6',
                radius: 10,
                emoji: '🏃',
                isAir: false
            },
            normal: {
                name: 'Bộ Binh Yêu Quái',
                hp: 55,
                speed: 1.0,
                reward: 18,
                color: '#B87333',
                radius: 12,
                emoji: '👹',
                isAir: false
            },
            heavy: {
                name: 'Voi Chiến Quỷ Số',
                hp: 180,
                speed: 0.55,
                reward: 35,
                color: '#C0332E',
                radius: 17,
                emoji: '🐘',
                isAir: false
            },
            air: {
                name: 'Quạ Sắt Cơ Khí',
                hp: 80,
                speed: 1.2,
                reward: 30,
                color: '#3a86ff',
                radius: 12,
                emoji: '🦅',
                isAir: true
            },
            boss: {
                name: 'Đại Tướng Quỷ Số',
                hp: 900,
                speed: 0.4,
                reward: 200,
                color: '#9b5de5',
                radius: 22,
                emoji: '👑',
                isAir: false
            }
        };

        // Mouse hover position
        let hoverCell = null;

        // Level Select Handler
        function selectLevel(lvlNum) {
            selectedLevelNum = lvlNum;
            
            // Toggle active card
            document.querySelectorAll('.level-card').forEach((card, idx) => {
                card.classList.toggle('active', idx + 1 === lvlNum);
            });
            sfx.playBuy();
        }

        // Initialize Level Obstacles
        function initLevelLayout() {
            grid = Array(COLS).fill().map(() => Array(ROWS).fill(0));
            towers = [];
            enemies = [];
            projectiles = [];
            particles = [];

            if (selectedLevelNum === 1) {
                // Flat open map
            } else if (selectedLevelNum === 2) {
                // Cao Lo Hill: blocking ancient stones
                grid[4][2] = 2; grid[4][3] = 2;
                grid[4][7] = 2; grid[4][8] = 2;
                grid[11][3] = 2; grid[11][4] = 2;
                grid[11][7] = 2; grid[11][8] = 2;
            } else if (selectedLevelNum === 3) {
                // Bach Dang River: fixed river canal in the middle
                // 3 rows for river canal where towers cannot be built, except on shores
                for (let c = 2; c < COLS - 2; c++) {
                    for (let r = 0; r < ROWS; r++) {
                        if (r !== 5) { // Leave a narrow bridge in the middle for ground units
                            if (r >= 3 && r <= 7) {
                                grid[c][r] = 2;
                            }
                        }
                    }
                }
            }
            updateAllPaths();
        }

        function updateAllPaths() {
            shortestPath = calculateBFSPath(null, START_CELL);
            if (typeof enemies !== 'undefined') {
                enemies.forEach(e => {
                    if (e.recalculatePath) e.recalculatePath();
                });
            }
        }

        // Canvas UI initialization
        function updateUI() {
            document.getElementById('goldDisplay').innerText = gold;
            document.getElementById('hpDisplay').innerText = hp;
            document.getElementById('waveDisplay').innerText = Math.min(Math.max(currentWaveNum + 1, 1), MAX_WAVES);

            // Update build buttons disabled state
            document.getElementById('buildArrow').classList.toggle('disabled', gold < TOWER_SPECS.arrow.cost);
            document.getElementById('buildSlow').classList.toggle('disabled', gold < TOWER_SPECS.slow.cost);
            document.getElementById('buildBomb').classList.toggle('disabled', gold < TOWER_SPECS.bomb.cost);
            document.getElementById('buildFlame').classList.toggle('disabled', gold < TOWER_SPECS.flame.cost);
            document.getElementById('buildTesla').classList.toggle('disabled', gold < TOWER_SPECS.tesla.cost);

            // Selected build state
            document.getElementById('buildArrow').classList.toggle('selected', selectedBuildType === 'arrow');
            document.getElementById('buildSlow').classList.toggle('selected', selectedBuildType === 'slow');
            document.getElementById('buildBomb').classList.toggle('selected', selectedBuildType === 'bomb');
            document.getElementById('buildFlame').classList.toggle('selected', selectedBuildType === 'flame');
            document.getElementById('buildTesla').classList.toggle('selected', selectedBuildType === 'tesla');

            // Render info panel
            const defaultPanel = document.getElementById('infoDefault');
            const detailsPanel = document.getElementById('infoDetails');

            if (selectedPlacedTower) {
                defaultPanel.classList.add('hidden');
                detailsPanel.classList.remove('hidden');

                const spec = TOWER_SPECS[selectedPlacedTower.type];
                document.getElementById('infoName').innerText = `${spec.name} (Cấp ${selectedPlacedTower.level})`;
                document.getElementById('infoStats').innerText = `Sát thương: ${Math.round(selectedPlacedTower.damage)} | Giãn bắn: ${selectedPlacedTower.fireRate.toFixed(1)}s | Tầm: ${selectedPlacedTower.range}px`;

                const upgradeBtn = document.getElementById('upgradeBtn');
                if (selectedPlacedTower.level >= 3) {
                    upgradeBtn.innerText = 'Cấp Tối Đa';
                    upgradeBtn.classList.add('disabled');
                } else {
                    const upCost = spec.upgradeCost * selectedPlacedTower.level;
                    upgradeBtn.innerText = `Nâng cấp (💰${upCost})`;
                    upgradeBtn.classList.toggle('disabled', gold < upCost);
                }

                const sellVal = Math.round(spec.sellValue * selectedPlacedTower.level);
                document.getElementById('sellBtn').innerText = `Bán (💰${sellVal})`;
            } else {
                defaultPanel.classList.remove('hidden');
                detailsPanel.classList.add('hidden');
            }
        }

        // ─── ALGORITHMS: BFS PATHFINDING ───
        // Calculate shortest path from start to exit
        function calculateBFSPath(gridOverride = null, startNode = START_CELL) {
            const tempGrid = gridOverride || grid;
            const queue = [];
            const visited = Array(COLS).fill().map(() => Array(ROWS).fill(false));
            const parent = Array(COLS).fill().map(() => Array(ROWS).fill(null));

            queue.push(startNode);
            visited[startNode.x][startNode.y] = true;

            let pathFound = false;

            while (queue.length > 0) {
                const curr = queue.shift();

                if (curr.x === EXIT_CELL.x && curr.y === EXIT_CELL.y) {
                    pathFound = true;
                    break;
                }

                // 4 directions (up, down, left, right)
                const dirs = [
                    { dx: 1, dy: 0 },  // right
                    { dx: -1, dy: 0 }, // left
                    { dx: 0, dy: 1 },  // down
                    { dx: 0, dy: -1 }  // up
                ];

                for (const d of dirs) {
                    const nx = curr.x + d.dx;
                    const ny = curr.y + d.dy;

                    if (nx >= 0 && nx < COLS && ny >= 0 && ny < ROWS) {
                        if (!visited[nx][ny] && tempGrid[nx][ny] === 0) {
                            visited[nx][ny] = true;
                            parent[nx][ny] = curr;
                            queue.push({ x: nx, y: ny });
                        }
                    }
                }
            }

            if (!pathFound) return null;

            // Reconstruct path
            const path = [];
            let curr = EXIT_CELL;
            while (curr !== null) {
                path.unshift(curr);
                curr = parent[curr.x][curr.y];
            }
            return path;
        }

        // Verify if placing a tower at (x, y) completely blocks path
        function wouldBlockPath(x, y) {
            if ((x === START_CELL.x && y === START_CELL.y) || (x === EXIT_CELL.x && y === EXIT_CELL.y)) {
                return true;
            }

            // Create temporary grid
            const tempGrid = grid.map(row => [...row]);
            tempGrid[x][y] = 1;

            const testPath = calculateBFSPath(tempGrid);
            return (testPath === null);
        }

        // ─── CONTROL FUNCTIONS ───
        function closeStartScreen() {
            document.getElementById('startScreen').classList.add('hidden');
            sfx.playBuy();
            sfx.startMusic(); // Bật nhạc nền ambient
            isPaused = false;
            initLevelLayout();
            startGameLoop();
            // Pulse the play button to indicate "press me to start!"
            document.getElementById('playBtn').classList.add('pulse');
        }

        function togglePlay() {
            if (waveActive) return;
            startNextWave();
        }

        function toggleSpeed() {
            gameSpeed = gameSpeed === 1 ? 2 : 1;
            document.getElementById('speedBtn').innerText = gameSpeed === 2 ? '⏩' : '⚡';
            document.getElementById('speedBtn').classList.toggle('active', gameSpeed === 2);
        }

        function toggleFlowField() {
            showFlowField = !showFlowField;
            document.getElementById('flowBtn').classList.toggle('active', showFlowField);
        }

        function selectTowerBuild(type) {
            if (selectedBuildType === type) {
                selectedBuildType = null;
            } else {
                selectedBuildType = type;
            }
            selectedPlacedTower = null; // de-select currently clicked tower
            updateUI();
        }

        function exitMinigame() {
            if (window.parent !== window) {
                window.parent.postMessage('close_profile', '*');
            } else {
                window.location.href = 'map.html';
            }
        }

        // Upgrade selected tower
        function upgradeSelectedTower() {
            if (!selectedPlacedTower) return;
            const spec = TOWER_SPECS[selectedPlacedTower.type];
            const upCost = spec.upgradeCost * selectedPlacedTower.level;
            
            if (gold >= upCost && selectedPlacedTower.level < 3) {
                gold -= upCost;
                selectedPlacedTower.level += 1;
                selectedPlacedTower.damage *= 1.5;
                selectedPlacedTower.range *= 1.15;
                selectedPlacedTower.fireRate *= 0.9; // faster firing
                sfx.playBuy();
                updateUI();
                createParticleExplosion(selectedPlacedTower.x, selectedPlacedTower.y, '#C8960C', 20);
            } else {
                sfx.playDeny();
            }
        }

        // Sell selected tower
        function sellSelectedTower() {
            if (!selectedPlacedTower) return;
            const spec = TOWER_SPECS[selectedPlacedTower.type];
            const sellVal = Math.round(spec.sellValue * selectedPlacedTower.level);
            
            gold += sellVal;
            grid[selectedPlacedTower.gridX][selectedPlacedTower.gridY] = 0;
            
            // Remove from array
            towers = towers.filter(t => t !== selectedPlacedTower);
            sfx.playBuy();
            
            selectedPlacedTower = null;
            updateAllPaths(); // update path
            updateUI();
        }

        // ─── TOWER AND ENEMY SYSTEM ───
        class Tower {
            constructor(gridX, gridY, type) {
                this.gridX = gridX;
                this.gridY = gridY;
                this.x = gridX * CELL_SIZE + CELL_SIZE / 2;
                this.y = gridY * CELL_SIZE + CELL_SIZE / 2;
                this.type = type;
                this.level = 1;
                
                const spec = TOWER_SPECS[type];
                this.range = spec.range;
                this.damage = spec.damage;
                this.fireRate = spec.fireRate; // delay in seconds
                this.color = spec.color;
                
                this.lastShotTime = 0;
                this.angle = 0;
                this.recoil = 0;
            }

            update(now) {
                // Decay barrel recoil
                if (this.recoil > 0) {
                    this.recoil = Math.max(0, this.recoil - 0.4 * gameSpeed);
                }

                if (!waveActive) {
                    // Slow idle rotate to neutral angle (0 / facing right)
                    let diff = 0 - this.angle;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    this.angle += diff * 0.03 * gameSpeed;
                    return;
                }

                // Find enemies in range
                const target = this.findTarget();
                if (target) {
                    // Dynamic angle tracking
                    const targetAngle = Math.atan2(target.y - this.y, target.x - this.x);
                    let diff = targetAngle - this.angle;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    this.angle += diff * 0.16 * gameSpeed; // smooth rotation lerp

                    // Fire rate throttling
                    if (now - this.lastShotTime >= this.fireRate * 1000) {
                        this.shoot(target);
                        this.lastShotTime = now;
                        this.recoil = this.type === 'flame' ? 2 : 9; // trigger barrel recoil
                    }
                } else {
                    // Neutral idle returning
                    let diff = 0 - this.angle;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    this.angle += diff * 0.03 * gameSpeed;
                }
            }

            findTarget() {
                let bestTarget = null;
                let maxDistOnPath = -1;
                let maxDistAir = -1;

                for (const e of enemies) {
                    if (e.isDead) continue;
                    
                    // Anti-air targeting rules (Goo and Flame cannot target air units)
                    if ((this.type === 'slow' || this.type === 'flame') && e.isAir) {
                        continue;
                    }

                    const dx = e.x - this.x;
                    const dy = e.y - this.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    
                    if (dist <= this.range) {
                        if (e.isAir) {
                            // Priority: Air units furthest along the screen (max X coordinate)
                            if (e.x > maxDistAir) {
                                maxDistAir = e.x;
                                bestTarget = e;
                            }
                        } else {
                            // Priority: Ground units furthest along the BFS shortestPath
                            if (maxDistAir === -1 && e.pathIndex > maxDistOnPath) {
                                maxDistOnPath = e.pathIndex;
                                bestTarget = e;
                            }
                        }
                    }
                }
                return bestTarget;
            }

            shoot(target) {
                sfx.playShoot(this.type);
                
                if (this.type === 'slow') {
                    projectiles.push(new Projectile(this.x, this.y, target, 'slow', this.damage));
                } else if (this.type === 'bomb') {
                    projectiles.push(new Projectile(this.x, this.y, target, 'bomb', this.damage));
                } else if (this.type === 'flame') {
                    projectiles.push(new Projectile(this.x, this.y, target, 'flame', this.damage));
                } else if (this.type === 'tesla') {
                    projectiles.push(new Projectile(this.x, this.y, target, 'tesla', this.damage));
                } else {
                    projectiles.push(new Projectile(this.x, this.y, target, 'arrow', this.damage));
                }
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);

                let imgKey = this.type + '_tower';
                if (assets[imgKey] && assets[imgKey].complete) {
                    const rec = this.recoil;
                    ctx.rotate(this.angle); // Rotate towards target
                    ctx.drawImage(assets[imgKey], -CELL_SIZE/2, -CELL_SIZE/2, CELL_SIZE, CELL_SIZE);
                    
                    if (rec > 0) {
                        ctx.fillStyle = 'rgba(255, 200, 0, 0.5)';
                        ctx.beginPath();
                        ctx.arc(CELL_SIZE/2, 0, rec, 0, Math.PI*2);
                        ctx.fill();
                    }
                }

                ctx.restore();

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.fillStyle = '#C8960C';
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'center';
                let stars = '★';
                if (this.level === 2) stars = '★★';
                else if (this.level === 3) stars = '★★★';
                ctx.fillText(stars, 0, CELL_SIZE / 2 - 2);
                ctx.restore();
            }
        }

        class Enemy {
            constructor(type, waveFactor) {
                const temp = ENEMY_TEMPLATES[type];
                this.name = temp.name;
                this.maxHp = Math.round(temp.hp * waveFactor);
                this.hp = this.maxHp;
                this.baseSpeed = temp.speed;
                this.speed = temp.speed;
                this.reward = temp.reward;
                this.color = temp.color;
                this.radius = temp.radius;
                this.emoji = temp.emoji;
                this.isAir = temp.isAir;
                
                // Position initial
                this.x = START_CELL.x * CELL_SIZE + CELL_SIZE / 2;
                this.y = START_CELL.y * CELL_SIZE + CELL_SIZE / 2;
                
                this.myPath = calculateBFSPath(null, START_CELL);
                this.pathIndex = 0;
                
                this.isDead = false;
                this.slowTimer = 0;
                this.burnTimer = 0;
                this.burnDamage = 0;
                
                // Wobble animation time
                this.wobbleTime = Math.random() * 100;
            }

            recalculatePath() {
                if (this.isAir || this.isDead) return;
                
                const cx = Math.floor(this.x / CELL_SIZE);
                const cy = Math.floor(this.y / CELL_SIZE);
                
                let startNode = {x: cx, y: cy};
                // Use current target node to prevent backtracking
                if (this.myPath && this.myPath[this.pathIndex + 1]) {
                    startNode = this.myPath[this.pathIndex + 1];
                }
                
                let newPath = calculateBFSPath(null, startNode);
                if (!newPath) {
                    newPath = calculateBFSPath(null, {x: cx, y: cy});
                }
                
                this.myPath = newPath || [];
                this.pathIndex = -1; // Next step will be myPath[0]
            }

            update(dt) {
                if (this.isDead) return;

                // Handle slow effects (reduced by 50% for bosses)
                const isBoss = this.name.includes("Đại Tướng");
                if (this.slowTimer > 0) {
                    this.slowTimer -= dt;
                    this.speed = this.baseSpeed * (isBoss ? 0.75 : 0.55); // boss slows less
                } else {
                    this.speed = this.baseSpeed;
                }

                // Handle burn damage over time (Flamethrower DOT)
                if (this.burnTimer > 0) {
                    this.burnTimer -= dt;
                    this.takeDamage(this.burnDamage * (dt / 1000), false); // silent tick
                    
                    // Spawn flame smoke embers floating up from the target body
                    if (Math.random() < 0.25) {
                        particles.push(new Particle(this.x + (Math.random() - 0.5) * 12, this.y + (Math.random() - 0.5) * 12, '#ff4500'));
                    }
                }

                // Wobble walk speed factor
                this.wobbleTime += 0.16 * gameSpeed * (dt / 16.66);

                // --- AIR UNIT FLIGHT MECHANICS ---
                if (this.isAir) {
                    // Airplanes fly straight from Left to Right, ignoring the ground maze completely
                    this.x += this.speed * gameSpeed * (dt / 16.66);
                    // Floating micro-wave height variation
                    this.y += Math.sin(Date.now() / 150) * 0.18;

                    // Escape! reached exit gate
                    if (this.x >= EXIT_CELL.x * CELL_SIZE + CELL_SIZE / 2) {
                        hp -= 1;
                        this.isDead = true;
                        sfx.playLeak();
                        createParticleExplosion(this.x, this.y, '#3a86ff', 15);
                        updateUI();
                        if (hp <= 0) {
                            endGame(false);
                        }
                    }
                    return;
                }

                // --- GROUND UNIT MAZE PATHING ---
                if (!this.myPath || this.myPath.length === 0) return;

                const targetNode = this.myPath[this.pathIndex + 1];
                if (!targetNode) {
                    // Escape! reached exit gate
                    hp -= 1;
                    this.isDead = true;
                    sfx.playLeak();
                    createParticleExplosion(this.x, this.y, '#C0332E', 15);
                    updateUI();
                    if (hp <= 0) {
                        endGame(false);
                    }
                    return;
                }

                const tx = targetNode.x * CELL_SIZE + CELL_SIZE / 2;
                const ty = targetNode.y * CELL_SIZE + CELL_SIZE / 2;

                const dx = tx - this.x;
                const dy = ty - this.y;
                const dist = Math.sqrt(dx*dx + dy*dy);

                const moveStep = this.speed * gameSpeed * (dt / 16.66);

                if (dist <= moveStep) {
                    this.x = tx;
                    this.y = ty;
                    this.pathIndex++;
                } else {
                    this.x += (dx / dist) * moveStep;
                    this.y += (dy / dist) * moveStep;
                }
            }

            takeDamage(dmg, playSfx = true) {
                if (this.isDead) return;
                this.hp -= dmg;
                
                // Play hit sound occasionally to keep audio clean and pleasant
                if (playSfx && Math.random() < 0.25) {
                    sfx.playHit();
                }
                
                // Spawn subtle hit particles
                if (Math.random() < 0.4) {
                    createParticleExplosion(this.x, this.y, this.color, 2);
                }

                if (this.hp <= 0) {
                    this.isDead = true;
                    gold += this.reward;
                    sfx.playHit();
                    
                    if (this.isAir) {
                        // Copter falls spinning from above
                        createParticleExplosion(this.x, this.y, '#3a86ff', 12);
                        for (let i = 0; i < 8; i++) {
                            particles.push(new Particle(this.x, this.y, '#160E1C')); // black smoke trail
                        }
                    } else {
                        createParticleExplosion(this.x, this.y, this.color, 15);
                    }

                    // Large screen shake if Boss dies!
                    if (this.name.includes("Đại Tướng")) {
                        triggerScreenShake(20);
                        sfx.playExplode();
                        createParticleExplosion(this.x, this.y, '#ffd700', 40);
                    }

                    updateUI();
                }
            }

            applySlow(duration) {
                this.slowTimer = duration; // duration in ms
            }

            applyBurn(duration, dmgPerSec) {
                this.burnTimer = duration; // duration in ms
                this.burnDamage = dmgPerSec;
            }

            draw() {
                if (this.isDead) return;

                ctx.save();
                ctx.translate(this.x, this.y);

                const wobbleAngle = Math.sin(this.wobbleTime) * 0.08;
                const wobbleScaleY = 1 + Math.cos(this.wobbleTime) * 0.05;
                ctx.rotate(wobbleAngle);
                ctx.scale(1, wobbleScaleY);

                if (this.slowTimer > 0) {
                    ctx.beginPath();
                    ctx.arc(0, 0, this.radius + 4, 0, Math.PI * 2);
                    ctx.strokeStyle = 'rgba(90, 188, 170, 0.8)';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }

                let imgKey = 'enemy_soldier';
                if (this.name.includes('Trinh Sát')) imgKey = 'enemy_scout';
                else if (this.name.includes('Voi Chiến')) imgKey = 'enemy_heavy';
                else if (this.isAir) imgKey = 'enemy_air';
                else if (this.name.includes('Đại Tướng')) imgKey = 'enemy_heavy'; 

                if (assets[imgKey] && assets[imgKey].complete) {
                    const drawSize = this.radius * 2.5;
                    ctx.drawImage(assets[imgKey], -drawSize/2, -drawSize/2, drawSize, drawSize);
                }

                ctx.restore();

                ctx.save();
                ctx.translate(this.x, this.y);
                const barW = this.radius * 2;
                const barH = 4;
                ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
                ctx.fillRect(-barW / 2, -this.radius - 8, barW, barH);
                const hpPct = Math.max(0, this.hp / this.maxHp);
                ctx.fillStyle = hpPct > 0.5 ? '#5ABCAA' : hpPct > 0.2 ? '#C8960C' : '#C0332E';
                ctx.fillRect(-barW / 2, -this.radius - 8, barW * hpPct, barH);
                ctx.restore();
            }
        }

        // --- TESLA CHAIN ELECTRIC ARC DRAWING CLASS ---
        class LightningEffect {
            constructor(x1, y1, x2, y2, color) {
                this.x1 = x1;
                this.y1 = y1;
                this.x2 = x2;
                this.y2 = y2;
                this.color = color;
                this.alpha = 1.0;
                this.decay = 0.16; // decays in 6-7 frames
                
                // Generate random lightning arc fracture nodes
                this.points = [];
                const dx = x2 - x1;
                const dy = y2 - y1;
                const dist = Math.sqrt(dx*dx + dy*dy);
                const steps = Math.max(3, Math.floor(dist / 20));
                
                this.points.push({ x: x1, y: y1 });
                for (let i = 1; i < steps; i++) {
                    const ratio = i / steps;
                    const tx = x1 + dx * ratio;
                    const ty = y1 + dy * ratio;
                    const offset = (Math.random() - 0.5) * 14;
                    this.points.push({ x: tx - offset, y: ty + offset });
                }
                this.points.push({ x: x2, y: y2 });
            }

            update() {
                this.alpha -= this.decay * gameSpeed;
            }

            draw() {
                if (this.alpha <= 0) return;
                ctx.save();
                ctx.globalAlpha = Math.max(0, this.alpha);
                ctx.strokeStyle = '#b3e5fc';
                ctx.lineWidth = 3;
                ctx.shadowBlur = 15;
                ctx.shadowColor = this.color;
                
                ctx.beginPath();
                ctx.moveTo(this.points[0].x, this.points[0].y);
                for (let i = 1; i < this.points.length; i++) {
                    ctx.lineTo(this.points[i].x, this.points[i].y);
                }
                ctx.stroke();
                ctx.restore();
            }
        }

        class Projectile {
            constructor(x, y, target, type, damage) {
                this.x = x;
                this.y = y;
                this.startX = x;
                this.startY = y;
                this.target = target;
                this.type = type;
                this.damage = damage;
                this.isDone = false;
                
                // High velocity for Flamethrower / Instant hit for Tesla
                this.speed = type === 'arrow' ? 7.5 : type === 'slow' ? 5.5 : type === 'flame' ? 9.0 : 4.0;
                this.history = [];
                
                // For arc pathing of bomb mortar
                this.totalDistance = 0;
                this.currentDistance = 0;
                if (type === 'bomb') {
                    const dx = target.x - x;
                    const dy = target.y - y;
                    this.totalDistance = Math.sqrt(dx*dx + dy*dy);
                }

                if (type === 'tesla') {
                    // Tesla lightning chains instantly in constructor
                    this.isDone = true;
                    this.hit();
                }
            }

            update() {
                if (this.isDone) return;
                if (this.target.isDead) {
                    this.isDone = true;
                    return;
                }

                // Trace history for gorgeous motion trails
                this.history.push({ x: this.x, y: this.y });
                if (this.history.length > 8) this.history.shift();

                const dx = this.target.x - this.x;
                const dy = this.target.y - this.y;
                const dist = Math.sqrt(dx*dx + dy*dy);

                const step = this.speed * gameSpeed;

                if (dist <= step) {
                    this.hit();
                    this.isDone = true;
                } else {
                    this.x += (dx / dist) * step;
                    this.y += (dy / dist) * step;
                    this.currentDistance += step;
                }
            }

            hit() {
                if (this.type === 'slow') {
                    this.target.takeDamage(this.damage);
                    this.target.applySlow(3000); // 3 seconds slow
                } else if (this.type === 'bomb') {
                    sfx.playExplode();
                    createParticleExplosion(this.x, this.y, '#C0332E', 25);
                    
                    // Area of effect splash damage
                    const splashRange = TOWER_SPECS.bomb.splash;
                    for (const e of enemies) {
                        if (e.isDead) continue;
                        const edx = e.x - this.x;
                        const edy = e.y - this.y;
                        const edist = Math.sqrt(edx*edx + edy*edy);
                        if (edist <= splashRange) {
                            e.takeDamage(this.damage);
                        }
                    }
                } else if (this.type === 'flame') {
                    // Flamethrower deals hit damage + applies Burn DOT (2 seconds)
                    this.target.takeDamage(this.damage);
                    this.target.applyBurn(2000, this.damage * 0.7);
                    
                    // Spawn rich fire particles
                    for (let i = 0; i < 3; i++) {
                        particles.push(new Particle(this.x, this.y, '#ff4500'));
                    }
                } else if (this.type === 'tesla') {
                    // --- TESLA CHAIN ELECTRIC ARC HIT MECHANICS ---
                    let currentSource = { x: this.startX, y: this.startY };
                    let currentTarget = this.target;
                    let chainedEnemies = [currentTarget];
                    
                    // Deal damage to first target
                    currentTarget.takeDamage(this.damage);
                    createParticleExplosion(currentTarget.x, currentTarget.y, '#3a86ff', 5);
                    
                    // Chain electricity to adjacent targets
                    const maxChains = this.damage > 120 ? 5 : 3; // level 3 chains up to 5 targets
                    for (let c = 1; c < maxChains; c++) {
                        let nextTarget = null;
                        let minDist = 75; // chain jumping distance radius
                        
                        for (const e of enemies) {
                            if (e.isDead || chainedEnemies.includes(e)) continue;
                            if (e.isAir) continue; // lightning only chains ground units
                            
                            const edx = e.x - currentTarget.x;
                            const edy = e.y - currentTarget.y;
                            const edist = Math.sqrt(edx*edx + edy*edy);
                            
                            if (edist < minDist) {
                                minDist = edist;
                                nextTarget = e;
                            }
                        }
                        
                        if (nextTarget) {
                            chainedEnemies.push(nextTarget);
                            nextTarget.takeDamage(this.damage * 0.8); // 20% damage decay per chain jump
                            createParticleExplosion(nextTarget.x, nextTarget.y, '#3a86ff', 3);
                            currentTarget = nextTarget;
                        } else {
                            break;
                        }
                    }
                    
                    // Create lightning visual arcs
                    for (let i = 0; i < chainedEnemies.length; i++) {
                        const startPoint = i === 0 ? { x: this.startX, y: this.startY } : chainedEnemies[i-1];
                        const endPoint = chainedEnemies[i];
                        particles.push(new LightningEffect(startPoint.x, startPoint.y, endPoint.x, endPoint.y, '#00e5ff'));
                    }
                } else {
                    this.target.takeDamage(this.damage);
                }
            }

            draw() {
                if (this.isDone) return;

                ctx.save();

                // Draw gorgeous motion trails
                if (this.history.length > 1) {
                    ctx.save();
                    const color = this.type === 'arrow' ? 'rgba(200, 150, 12,' : this.type === 'slow' ? 'rgba(90, 188, 170,' : this.type === 'flame' ? 'rgba(255, 69, 0,' : 'rgba(192, 51, 46,';
                    for (let i = 0; i < this.history.length - 1; i++) {
                        const alpha = (i / this.history.length) * 0.45;
                        ctx.beginPath();
                        ctx.moveTo(this.history[i].x, this.history[i].y);
                        ctx.lineTo(this.history[i+1].x, this.history[i+1].y);
                        ctx.strokeStyle = color + alpha + ')';
                        ctx.lineWidth = (i / this.history.length) * (this.type === 'bomb' ? 8 : this.type === 'flame' ? 6 : 4);
                        ctx.lineCap = 'round';
                        ctx.stroke();
                    }
                    ctx.restore();
                }

                // Head drawing
                let currentHeight = 0;
                if (this.type === 'bomb') {
                    const pct = this.currentDistance / this.totalDistance;
                    currentHeight = 45 * Math.sin(pct * Math.PI); // parabolic rise
                    
                    // Draw spinning mortar bronze shell
                    ctx.translate(this.x, this.y - currentHeight);
                    ctx.rotate((this.currentDistance / 10) % (Math.PI * 2));
                    ctx.fillStyle = '#B87333';
                    ctx.strokeStyle = '#F5EED6';
                    ctx.lineWidth = 1;
                    
                    ctx.beginPath();
                    ctx.arc(0, 0, 5, 0, Math.PI*2);
                    ctx.fill();
                    ctx.stroke();
                    
                    // Small gold fire fuse dot
                    ctx.fillStyle = '#C8960C';
                    ctx.beginPath();
                    ctx.arc(-5, 0, 2, 0, Math.PI*2);
                    ctx.fill();
                } else if (this.type === 'slow') {
                    // Toxic acid emerald bead
                    ctx.shadowBlur = 8;
                    ctx.shadowColor = '#5ABCAA';
                    ctx.fillStyle = '#5ABCAA';
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, 4, 0, Math.PI*2);
                    ctx.fill();
                } else if (this.type === 'flame') {
                    // Chùm hạt hỏa công bay vút
                    ctx.fillStyle = '#ff4500';
                    ctx.shadowBlur = 6;
                    ctx.shadowColor = '#ff8c00';
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, 5, 0, Math.PI*2);
                    ctx.fill();
                } else {
                    // Golden crossbow bolt head
                    ctx.fillStyle = '#C8960C';
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, 2.5, 0, Math.PI*2);
                    ctx.fill();
                }

                ctx.restore();
            }
        }

        // ─── PARTICLE EFFECT ENGINE ───
        class Particle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.color = color;
                this.vx = (Math.random() - 0.5) * 4;
                this.vy = (Math.random() - 0.5) * 4;
                this.alpha = 1;
                this.decay = Math.random() * 0.03 + 0.02;
                this.size = Math.random() * 3 + 1.5;
            }

            update() {
                this.x += this.vx * gameSpeed;
                this.y += this.vy * gameSpeed;
                this.alpha -= this.decay * gameSpeed;
            }

            draw() {
                ctx.save();
                ctx.globalAlpha = Math.max(0, this.alpha);
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.restore();
            }
        }

        // Fieldrunners glowing expanding shockwave rings
        class Shockwave {
            constructor(x, y, maxRadius, color) {
                this.x = x;
                this.y = y;
                this.radius = 2;
                this.maxRadius = maxRadius;
                this.color = color;
                this.alpha = 1;
                this.decay = 0.035;
            }

            update() {
                this.radius += 3.5 * gameSpeed;
                this.alpha -= this.decay * gameSpeed;
            }

            draw() {
                ctx.save();
                ctx.globalAlpha = Math.max(0, this.alpha);
                ctx.strokeStyle = this.color;
                ctx.lineWidth = 2.5;
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.stroke();
                ctx.restore();
            }
        }

        function createParticleExplosion(x, y, color, count) {
            // If it is a bomb splash hit (large explosion), spawn gorgeous shockwave rings!
            if (count > 20) {
                particles.push(new Shockwave(x, y, TOWER_SPECS.bomb.splash, '#ff4500'));
                particles.push(new Shockwave(x, y, TOWER_SPECS.bomb.splash * 0.7, '#ffd700'));
            }
            for (let i = 0; i < count; i++) {
                particles.push(new Particle(x, y, color));
            }
        }
        function showWaveBanner(text) {
            const banner = document.getElementById('waveBanner');
            banner.innerText = text;
            banner.classList.remove('show');
            // Force reflow to restart animation
            void banner.offsetWidth;
            banner.classList.add('show');
            setTimeout(() => banner.classList.remove('show'), 2600);
        }

        function startNextWave() {
            if (waveActive) return;
            
            currentWaveNum++;
            if (currentWaveNum >= WAVE_DATABASE.length) {
                currentWaveNum = WAVE_DATABASE.length - 1; // clamp
            }

            enemies = [];
            projectiles = [];
            
            const wData = WAVE_DATABASE[currentWaveNum];
            
            // Track total expected enemies for this wave to prevent premature completion
            totalExpectedEnemies = wData.scout + wData.normal + wData.heavy + wData.air + wData.boss;
            totalSpawnedEnemies = 0;
            
            // Factor representing scaling up enemy stats per wave
            const waveFactor = 1 + currentWaveNum * 0.25; // Tăng chậm hơn — game dễ hơn
            const isBossWave = wData.boss > 0;

            // Show wave announcement banner + fanfare sound
            sfx.playWaveStart();
            if (isBossWave) {
                triggerScreenShake(15);
                sfx.playExplode();
                showWaveBanner(`⚔️ ĐỢT ${currentWaveNum + 1} — BOSS XUẤT KÍCH!`);
            } else if (wData.air > 0 && wData.air >= wData.normal) {
                showWaveBanner(`✈️ ĐỢT ${currentWaveNum + 1} — KHÔNG QUÂN!`);
            } else {
                showWaveBanner(`⚔️ ĐỢT ${currentWaveNum + 1}`);
            }

            // Generate enemy array with staggered spawn delays
            let delayOffset = 800; // Small initial delay for banner to show

            function spawnEnemy(type, factor) {
                if (hp > 0 && waveActive) {
                    enemies.push(new Enemy(type, factor));
                    totalSpawnedEnemies++;
                }
            }

            for (let i = 0; i < wData.scout; i++) {
                setTimeout(() => spawnEnemy('scout', waveFactor), delayOffset);
                delayOffset += 500;
            }

            for (let i = 0; i < wData.normal; i++) {
                setTimeout(() => spawnEnemy('normal', waveFactor), delayOffset);
                delayOffset += 900;
            }

            for (let i = 0; i < wData.heavy; i++) {
                setTimeout(() => spawnEnemy('heavy', waveFactor), delayOffset);
                delayOffset += 2000;
            }

            for (let i = 0; i < wData.air; i++) {
                setTimeout(() => spawnEnemy('air', waveFactor), delayOffset);
                delayOffset += 1500;
            }

            for (let i = 0; i < wData.boss; i++) {
                setTimeout(() => spawnEnemy('boss', waveFactor * 1.5), delayOffset);
                delayOffset += 3000;
            }

            waveActive = true;
            document.getElementById('playBtn').innerText = '⚔️';
            document.getElementById('playBtn').classList.remove('pulse');
            document.getElementById('playBtn').classList.add('active');
            updateUI();
        }

        // Check if wave finished
        function checkWaveProgress() {
            if (!waveActive) return;

            // Don't check completion until all enemies have been spawned
            if (totalSpawnedEnemies < totalExpectedEnemies) return;

            const allDeadOrEscaped = enemies.every(e => e.isDead) && enemies.length > 0;
            if (allDeadOrEscaped) {
                // Wave completed!
                waveActive = false;
                enemies = [];
                projectiles = [];
                sfx.playWin();
                
                // Reward gold
                gold += 80 + currentWaveNum * 15; // Thưởng nhiều hơn
                
                document.getElementById('playBtn').innerText = '▶️';
                document.getElementById('playBtn').classList.remove('active');
                document.getElementById('playBtn').classList.add('pulse');

                // Check win condition
                if (currentWaveNum === MAX_WAVES - 1) {
                    endGame(true);
                } else {
                    showWaveBanner(`🏆 ĐỢT ${currentWaveNum + 1} — THẮNG!`);
                    updateUI();
                }
            }
        }

        // Screen Shake Global Variable
        let screenShakeIntensity = 0;
        function triggerScreenShake(intensity) {
            screenShakeIntensity = intensity;
        }

        // ─── END GAME LOGIC ───
        function endGame(isWin) {
            isPaused = true;
            waveActive = false;
            clearInterval(gameLoopId);

            const screen = document.getElementById('gameOverScreen');
            const content = document.getElementById('gameOverContent');
            screen.classList.remove('hidden');

            if (isWin) {
                sfx.playWin();
                
                // Save progress to parents
                localStorage.setItem('cbToan_tower_defense_victory', 'true');
                window.parent.postMessage('minigame_won', '*');

                content.innerHTML = `
                    <h1 style="color: var(--success); font-size: 2.8rem; font-family: var(--font-title); text-shadow: 0 0 20px rgba(78,255,159,0.5); text-transform: uppercase;">Chiến Thắng Oai Hùng!</h1>
                    <h2 style="font-size: 1.2rem; text-align: center; color: #fff; font-weight: 400; margin-top: 10px;">Bát quái trận đồ thành Cổ Loa đã khuất phục hoàn toàn giặc ngoại bang! Cao Lỗ được nhà vua ban thưởng tước vị!</h2>
                    <div style="background: rgba(200,150,12,0.1); border: 1px solid var(--primary); border-radius: 10px; padding: 15px; margin: 15px; font-size: 1rem; line-height: 1.5; color: var(--primary); backdrop-filter: blur(5px);">
                        <strong>👑 Thục Phán An Dương Vương ngợi ca:</strong><br>"Cao Lỗ khanh gia quả tài giỏi! Sử dụng chiến thuật nỏ liên châu và lôi tháp lừng lẫy, giữ yên bờ cõi Âu Lạc!"
                    </div>
                    <button class="start-btn" onclick="exitMinigame()">QUAY LẠI BẢN ĐỒ</button>
                `;
            } else {
                sfx.playLose();
                content.innerHTML = `
                    <h1 style="color: var(--danger); font-size: 2.8rem; font-family: var(--font-title); text-shadow: 0 0 20px rgba(255,0,85,0.5); text-transform: uppercase;">Lũy Thành Sụp Đổ!</h1>
                    <h2 style="font-size: 1.2rem; text-align: center; color: #fff; font-weight: 400; line-height: 1.6; margin-top: 10px;">Quân giặc đã phá vỡ thế trận phòng thủ! Cổ Loa ngập chìm trong khói lửa.</h2>
                    <button class="start-btn" onclick="restartGame()">THỬ LẠI</button>
                    <button class="start-btn" onclick="exitMinigame()" style="background: transparent; border: 2px solid var(--primary); color: var(--primary); margin-left: 10px;">THOÁT</button>
                `;
            }
        }

        function restartGame() {
            document.getElementById('gameOverScreen').classList.add('hidden');
            
            gold = 350;
            hp = 30;
            currentWaveNum = -1; // resets to 0 on wave start
            waveActive = false;
            isPaused = false;
            totalExpectedEnemies = 0;
            totalSpawnedEnemies = 0;
            
            initLevelLayout(); // Khởi tạo lại chướng ngại vật màn chơi
            
            document.getElementById('playBtn').innerText = '▶️';
            document.getElementById('playBtn').classList.remove('active');
            document.getElementById('playBtn').classList.add('pulse');
            
            updateUI();
            startGameLoop();
        }

        // ─── BOARD RENDERING ENGINE ───
        function drawBoard() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Apply screen shake effect
            ctx.save();
            if (screenShakeIntensity > 0) {
                const dx = (Math.random() - 0.5) * screenShakeIntensity;
                const dy = (Math.random() - 0.5) * screenShakeIntensity;
                ctx.translate(dx, dy);
                screenShakeIntensity = Math.max(0, screenShakeIntensity - 0.5 * gameSpeed);
            }

            // 1. Draw map background
            if (assets.map_tile && assets.map_tile.complete) {
                for (let c = 0; c < COLS; c++) {
                    for (let r = 0; r < ROWS; r++) {
                        ctx.drawImage(assets.map_tile, c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE);
                    }
                }
            } else {
                ctx.fillStyle = '#0f0714';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }

            // Faint grid cells
            ctx.strokeStyle = 'rgba(184, 115, 51, 0.08)';
            ctx.lineWidth = 1;
            for (let c = 0; c <= COLS; c++) {
                ctx.beginPath(); ctx.moveTo(c * CELL_SIZE, 0); ctx.lineTo(c * CELL_SIZE, canvas.height); ctx.stroke();
            }
            for (let r = 0; r <= ROWS; r++) {
                ctx.beginPath(); ctx.moveTo(0, r * CELL_SIZE); ctx.lineTo(canvas.width, r * CELL_SIZE); ctx.stroke();
            }

            // --- DRAW LEVEL OBSTACLES ---
            for (let c = 0; c < COLS; c++) {
                for (let r = 0; r < ROWS; r++) {
                    if (grid[c][r] === 2) {
                        ctx.save();
                        ctx.translate(c * CELL_SIZE + CELL_SIZE/2, r * CELL_SIZE + CELL_SIZE/2);
                        
                        if (selectedLevelNum === 2) {
                            // Draw ancient Đông Sơn bronze rock obstacles
                            ctx.fillStyle = '#160E1C';
                            ctx.strokeStyle = '#B87333';
                            ctx.lineWidth = 2.5;
                            ctx.shadowBlur = 10;
                            ctx.shadowColor = 'rgba(184,115,51,0.5)';
                            
                            ctx.beginPath();
                            ctx.arc(0, 0, CELL_SIZE / 2 - 4, 0, Math.PI * 2);
                            ctx.fill();
                            ctx.stroke();
                            
                            // Concentric bronze details
                            ctx.beginPath();
                            ctx.arc(0, 0, 8, 0, Math.PI * 2);
                            ctx.stroke();
                            
                            // Moss jade green overlay
                            ctx.fillStyle = 'rgba(90, 188, 170, 0.3)';
                            ctx.beginPath();
                            ctx.arc(-4, -4, 6, 0, Math.PI * 2);
                            ctx.fill();
                        } else if (selectedLevelNum === 3) {
                            // Draw sparkling dynamic river canal
                            ctx.fillStyle = 'rgba(58, 134, 255, 0.15)';
                            ctx.strokeStyle = '#3a86ff';
                            ctx.lineWidth = 1.5;
                            ctx.fillRect(-CELL_SIZE/2 + 2, -CELL_SIZE/2 + 2, CELL_SIZE - 4, CELL_SIZE - 4);
                            
                            // Draw running water streams
                            ctx.beginPath();
                            ctx.moveTo(-CELL_SIZE/2 + 6, -CELL_SIZE/4 + Math.sin(Date.now()/300 + c)*3);
                            ctx.lineTo(CELL_SIZE/2 - 6, -CELL_SIZE/4 + Math.sin(Date.now()/300 + c + 1)*3);
                            ctx.moveTo(-CELL_SIZE/2 + 6, CELL_SIZE/4 + Math.sin(Date.now()/300 + c + 2)*3);
                            ctx.lineTo(CELL_SIZE/2 - 6, CELL_SIZE/4 + Math.sin(Date.now()/300 + c + 3)*3);
                            ctx.stroke();
                        }
                        
                        ctx.restore();
                    }
                }
            }

            // 2. Draw Start (Spawn) and Exit (Thành) gates
            ctx.save();
            // Start Gate (Left)
            ctx.fillStyle = 'rgba(90, 188, 170, 0.15)';
            ctx.strokeStyle = '#5ABCAA';
            ctx.lineWidth = 3;
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#5ABCAA';
            ctx.fillRect(START_CELL.x * CELL_SIZE + 2, START_CELL.y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4);
            ctx.strokeRect(START_CELL.x * CELL_SIZE + 2, START_CELL.y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4);
            ctx.fillStyle = '#fff';
            ctx.font = '10px var(--font-mono)';
            ctx.textAlign = 'center';
            ctx.fillText('CỔNG VÀO', START_CELL.x * CELL_SIZE + CELL_SIZE/2, START_CELL.y * CELL_SIZE + CELL_SIZE/2 + 4);

            // Exit Gate (Right)
            ctx.fillStyle = 'rgba(192, 51, 46, 0.15)';
            ctx.strokeStyle = '#C0332E';
            ctx.lineWidth = 3;
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#C0332E';
            ctx.fillRect(EXIT_CELL.x * CELL_SIZE + 2, EXIT_CELL.y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4);
            ctx.strokeRect(EXIT_CELL.x * CELL_SIZE + 2, EXIT_CELL.y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4);
            ctx.fillStyle = '#fff';
            ctx.fillText('ẢI THÀNH', EXIT_CELL.x * CELL_SIZE + CELL_SIZE/2, EXIT_CELL.y * CELL_SIZE + CELL_SIZE/2 + 4);
            ctx.restore();

            // 3. Chevron Glowing Flow Field along shortestPath
            if (shortestPath && shortestPath.length > 1) {
                ctx.save();
                ctx.strokeStyle = 'rgba(200, 150, 12, 0.25)';
                ctx.lineWidth = 2;
                ctx.setLineDash([4, 8]);
                ctx.beginPath();
                ctx.moveTo(shortestPath[0].x * CELL_SIZE + CELL_SIZE/2, shortestPath[0].y * CELL_SIZE + CELL_SIZE/2);
                for (let i = 1; i < shortestPath.length; i++) {
                    ctx.lineTo(shortestPath[i].x * CELL_SIZE + CELL_SIZE/2, shortestPath[i].y * CELL_SIZE + CELL_SIZE/2);
                }
                ctx.stroke();
                ctx.restore();

                // Draw moving glowing chevrons along path
                ctx.save();
                const time = Date.now();
                const arrowSpacing = 60; // distance between chevrons
                const offset = (time / 25) % arrowSpacing;

                // Flatten coordinates
                let pathPoints = [];
                for (let i = 0; i < shortestPath.length; i++) {
                    pathPoints.push({
                        x: shortestPath[i].x * CELL_SIZE + CELL_SIZE/2,
                        y: shortestPath[i].y * CELL_SIZE + CELL_SIZE/2
                    });
                }

                // Interpolate along path
                let totalDist = 0;
                let segments = [];
                for (let i = 0; i < pathPoints.length - 1; i++) {
                    const p1 = pathPoints[i];
                    const p2 = pathPoints[i+1];
                    const dx = p2.x - p1.x;
                    const dy = p2.y - p1.y;
                    const len = Math.sqrt(dx*dx + dy*dy);
                    segments.push({ p1, p2, dx: dx/len, dy: dy/len, len, startDist: totalDist });
                    totalDist += len;
                }

                ctx.fillStyle = 'rgba(200, 150, 12, 0.65)';
                ctx.shadowBlur = 8;
                ctx.shadowColor = '#C8960C';

                for (let d = offset; d < totalDist; d += arrowSpacing) {
                    const seg = segments.find(s => d >= s.startDist && d <= s.startDist + s.len);
                    if (seg) {
                        const ratio = (d - seg.startDist) / seg.len;
                        const x = seg.p1.x + seg.dx * (d - seg.startDist);
                        const y = seg.p1.y + seg.dy * (d - seg.startDist);

                        ctx.save();
                        ctx.translate(x, y);
                        ctx.rotate(Math.atan2(seg.dy, seg.dx));
                        ctx.beginPath();
                        ctx.moveTo(-6, -4);
                        ctx.lineTo(0, 0);
                        ctx.lineTo(-6, 4);
                        ctx.lineTo(-3, 4);
                        ctx.lineTo(3, 0);
                        ctx.lineTo(-3, -4);
                        ctx.closePath();
                        ctx.fill();
                        ctx.restore();
                    }
                }
                ctx.restore();
            }

            // 4. Draw selected tower range overlay
            if (selectedPlacedTower) {
                ctx.save();
                ctx.beginPath();
                ctx.arc(
                    selectedPlacedTower.gridX * CELL_SIZE + CELL_SIZE/2,
                    selectedPlacedTower.gridY * CELL_SIZE + CELL_SIZE/2,
                    selectedPlacedTower.range,
                    0, Math.PI * 2
                );
                ctx.fillStyle = 'rgba(200, 150, 12, 0.04)';
                ctx.strokeStyle = 'rgba(200, 150, 12, 0.25)';
                ctx.lineWidth = 1.5;
                ctx.fill();
                ctx.stroke();
                ctx.restore();
            }

            // 5. Viền chỉ thị xây dựng tháp đỏ/xanh (assist hover grid) của selectedBuildType
            if (selectedBuildType && hoverCell) {
                const spec = TOWER_SPECS[selectedBuildType];
                const blocked = grid[hoverCell.x][hoverCell.y] === 1 ||
                                grid[hoverCell.x][hoverCell.y] === 2 || // Cản trở bởi chướng ngại vật màn chơi
                                wouldBlockPath(hoverCell.x, hoverCell.y) ||
                                (hoverCell.x === START_CELL.x && hoverCell.y === START_CELL.y) ||
                                (hoverCell.x === EXIT_CELL.x && hoverCell.y === EXIT_CELL.y) ||
                                gold < spec.cost;

                ctx.save();
                ctx.translate(hoverCell.x * CELL_SIZE + CELL_SIZE/2, hoverCell.y * CELL_SIZE + CELL_SIZE/2);
                
                // Draw Range circle
                ctx.beginPath();
                ctx.arc(0, 0, spec.range, 0, Math.PI * 2);
                ctx.fillStyle = blocked ? 'rgba(192, 51, 46, 0.06)' : 'rgba(90, 188, 170, 0.06)';
                ctx.strokeStyle = blocked ? 'rgba(192, 51, 46, 0.3)' : 'rgba(90, 188, 170, 0.3)';
                ctx.lineWidth = 1.5;
                ctx.fill();
                ctx.stroke();
                ctx.restore();

                // Draw cell box highlight
                ctx.save();
                ctx.fillStyle = blocked ? 'rgba(192, 51, 46, 0.25)' : 'rgba(90, 188, 170, 0.25)';
                ctx.strokeStyle = blocked ? '#C0332E' : '#5ABCAA';
                ctx.lineWidth = 2.5;
                ctx.fillRect(hoverCell.x * CELL_SIZE, hoverCell.y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
                ctx.strokeRect(hoverCell.x * CELL_SIZE, hoverCell.y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
                ctx.restore();
            }

            // 6. Render actual items
            towers.forEach(t => t.draw());
            enemies.forEach(e => e.draw());
            projectiles.forEach(p => p.draw());
            particles.forEach(p => p.draw());

            ctx.restore(); // end screen shake
        }

        // ─── CORE GAME LOOP ───
        let lastTimestamp = 0;
        function gameTick(timestamp) {
            if (isPaused) return;

            const dt = lastTimestamp ? timestamp - lastTimestamp : 16.66;
            lastTimestamp = timestamp;

            // Limit huge lag dt jumps (e.g. background tab active)
            const clampedDt = Math.min(100, dt);

            // Update
            const now = Date.now();
            towers.forEach(t => t.update(now));
            enemies.forEach(e => e.update(clampedDt));
            projectiles.forEach(p => p.update());
            particles.forEach(p => p.update());

            // Clear finished items
            projectiles = projectiles.filter(p => !p.isDone);
            particles = particles.filter(p => p.alpha > 0);

            // Check wave status
            checkWaveProgress();

            // Render
            drawBoard();

            gameLoopId = requestAnimationFrame(gameTick);
        }

        function startGameLoop() {
            lastTimestamp = 0;
            gameLoopId = requestAnimationFrame(gameTick);
        }

        // ─── CLICK AND INTERACTION HANDLERS ───
        function handleHover(clientX, clientY) {
            const rect = canvas.getBoundingClientRect();
            const x = (clientX - rect.left) * (canvas.width / rect.width);
            const y = (clientY - rect.top) * (canvas.height / rect.height);
            
            const gx = Math.floor(x / CELL_SIZE);
            const gy = Math.floor(y / CELL_SIZE);

            if (gx >= 0 && gx < COLS && gy >= 0 && gy < ROWS) {
                hoverCell = { x: gx, y: gy };
            } else {
                hoverCell = null;
            }

            // Re-render board immediately if not actively in loop
            if (isPaused) drawBoard();
        }

        // Mouse Move coordinates mapping
        canvas.addEventListener('mousemove', (e) => {
            handleHover(e.clientX, e.clientY);
        });

        // Touch Move support for drag preview on mobile/tablets
        canvas.addEventListener('touchmove', (e) => {
            if (e.touches && e.touches.length > 0) {
                const touch = e.touches[0];
                handleHover(touch.clientX, touch.clientY);
                e.preventDefault(); // prevent scrolling while hovering/placing towers
            }
        }, { passive: false });

        canvas.addEventListener('mouseleave', () => {
            hoverCell = null;
            if (isPaused) drawBoard();
        });

        canvas.addEventListener('touchend', () => {
            hoverCell = null;
            if (isPaused) drawBoard();
        });

        function handleInteraction(clientX, clientY) {
            if (isPaused) return;
            const rect = canvas.getBoundingClientRect();
            const x = (clientX - rect.left) * (canvas.width / rect.width);
            const y = (clientY - rect.top) * (canvas.height / rect.height);
            
            const gx = Math.floor(x / CELL_SIZE);
            const gy = Math.floor(y / CELL_SIZE);

            if (gx < 0 || gx >= COLS || gy < 0 || gy >= ROWS) return;

            if (selectedBuildType) {
                // TRY TO BUILD
                const spec = TOWER_SPECS[selectedBuildType];
                if (grid[gx][gy] === 1 || grid[gx][gy] === 2) { // Cản trở bởi tháp khác hoặc chướng ngại vật màn chơi
                    sfx.playDeny();
                    return;
                }

                // Verify constraints
                if (wouldBlockPath(gx, gy)) {
                    sfx.playDeny();
                    alert("⚠️ Cảnh báo: Lũy tháp này chặn mất lối di chuyển của quân giặc!");
                    return;
                }

                if (gold < spec.cost) {
                    sfx.playDeny();
                    return;
                }

                // Build successful!
                gold -= spec.cost;
                grid[gx][gy] = 1;
                towers.push(new Tower(gx, gy, selectedBuildType));
                sfx.playBuy();

                updateAllPaths(); // update shortest path
                createParticleExplosion(gx * CELL_SIZE + CELL_SIZE/2, gy * CELL_SIZE + CELL_SIZE/2, spec.color, 15);

                selectedBuildType = null; // de-select build mode
                updateUI();
            } else {
                // SELECT AN EXISTING PLACED TOWER
                const clicked = towers.find(t => t.gridX === gx && t.gridY === gy);
                if (clicked) {
                    selectedPlacedTower = clicked;
                } else {
                    selectedPlacedTower = null;
                }
                updateUI();
            }

            drawBoard();
        }

        // Click handler to build or select
        canvas.addEventListener('click', (e) => {
            handleInteraction(e.clientX, e.clientY);
        });

        // Touch start support for instant building/selection on mobile/tablets
        canvas.addEventListener('touchstart', (e) => {
            if (e.touches && e.touches.length > 0) {
                const touch = e.touches[0];
                handleInteraction(touch.clientX, touch.clientY);
                e.preventDefault();
            }
        }, { passive: false });

        // Helper color utility
        function varToColor(varName) {
            return getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
        }

        // Initialize board
        // Initialize board AFTER assets load
        document.querySelector('.start-btn').innerText = 'Đang tải ảnh... (0%)';
        initAssets(() => {
            document.querySelector('.start-btn').innerText = 'XUẤT QUÂN TRẬN ĐỒ';
            initLevelLayout(); // Khởi tạo ban đầu với Level 1
            drawBoard();
            updateUI();
        });

    