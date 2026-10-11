#!/usr/bin/env node
/*
 * Sound lab renderer - turns the game's Web Audio sounds into WAV files.
 *
 * Usage:
 *   node tools/soundlab/render.js <game.html> <out-dir> [sound ...] [options]
 *
 *   node tools/soundlab/render.js carCrash.html notes/sounds/new
 *   node tools/soundlab/render.js carCrash.html /tmp/snd crash@1 siren music@chase
 *   node tools/soundlab/render.js --list
 *
 * Sounds: a recipe name, optionally with an argument after "@" (crash@0.5 = crash at speed
 * ratio 0.5, music@chase = the "chase" track). With no names, DEFAULT_SET below is rendered.
 * The file is named after the sound with "@" -> "-" (crash@0.5 -> crash-0.5.wav).
 *
 * Options:
 *   --seed N        seed for Math.random (noise bursts, track picks). Default 1. Same seed = same WAV.
 *   --mix full      (default) every volume (master + all categories) at 1.0 - the raw recipe level
 *   --mix game      the game's out-of-the-box volumes (master 0.3, music 0.5, siren 0.7, sfx/explosion 1, ambience 0.6)
 *   --rate HZ       sample rate, default 44100
 *   --recipes FILE  a .js file that exports more recipes ({ name: recipe }) - merged over the built-ins
 *   --list          print the recipe names and exit
 *
 * How it works: the page is loaded headless (playwright-core + /opt/google/chrome/chrome --no-sandbox).
 * For each sound, an OfflineAudioContext is made and the game's own `getAudio()` is pointed
 * at it, so the game's real code (playSound, startSiren, musicTick, ...) builds its node graph into the
 * offline context. Things the game drives per frame (siren distance, music scheduler) are driven with
 * `api.at(t, fn)` / `api.every(dt, fn)`, which use OfflineAudioContext.suspend() to stop the render at
 * that time, run fn, and carry on. The result is written as 16-bit PCM WAV.
 *
 * Adding a sound: add an entry to RECIPES (or a --recipes file). A recipe is
 *   { dur: seconds, channels: 1|2, run: function (api, arg) { ... } }
 * `run` is serialized and run INSIDE the page, in global scope, so it can call any game function or
 * read any top-level game variable by name. It is called once at t=0 of the WAV. `api` has:
 *   api.ctx           the OfflineAudioContext
 *   api.dur           the render length
 *   api.at(t, fn)     run fn() when the render reaches t seconds (rounded to a 128-frame block)
 *   api.every(dt, fn) run fn(t) every dt seconds from dt up to the end (frame-driven sounds)
 * Times given to api.at / api.every are WAV times. The game's own code sees ctx.currentTime = PREROLL_S
 * + that time: every render first runs PREROLL_S of silence that is cut from the WAV, so the game's
 * master limiter (Batch 606, built with the context) has settled before the sound starts, the way it
 * has in the game. A fresh DynamicsCompressor starts fully clamped. So schedule with
 * api.ctx.currentTime + offset, never with absolute times.
 * Do not reference anything from this node file inside `run` - it is not in scope there.
 * Only code inside `run` / `at` / `every` sees the offline context (and the seeded Math.random): a game
 * timer the recipe starts (setTimeout) would play into the real context instead, so drive schedulers
 * with api.every and clear the game's own timer, as the music recipe does.
 * If the game file has no such function (an old file and a new sound), that sound fails alone and
 * the rest still render.
 */
'use strict';
const fs = require('fs');
const path = require('path');

let chromium;
try { ({ chromium } = require('playwright-core')); }
catch (e) { ({ chromium } = require(process.env.PLAYWRIGHT_CORE || '/home/coder/projects/handy-tool/node_modules/playwright-core')); }
const CHROME = process.env.CHROME || '/opt/google/chrome/chrome';

// ---------- recipes (run inside the page) ----------
const RECIPES = {
    // One-shots: playSound(type) at t=0. Lengths leave room for the tail.
    crash:    { dur: 2.0, run: (api, arg) => { playSound('crash', arg === undefined ? 0.5 : parseFloat(arg)); } },
    jump:     { dur: 0.4, run: () => { playSound('jump'); } },
    ram:      { dur: 0.4, run: () => { playSound('ram'); } },
    pickup:   { dur: 0.4, run: () => { playSound('pickup'); } },
    tankshot: { dur: 0.5, run: () => { playSound('tankshot'); } },
    click1:   { dur: 0.15, run: () => { playSound('click1'); } },
    click2:   { dur: 0.15, run: () => { playSound('click2'); } },

    // Ambulance pass-by: far -> alongside (1.5 s) -> held -> pulls away -> stopSiren at 3.0 s (its own
    // fade tail runs past the end). Distance is fed every frame like the game's main loop does.
    siren: { dur: 4, run: (api) => {
        const R = AMBULANCE_SIREN_RANGE;
        const s = startSiren();
        const dist = t => t < 1.5 ? R * (1 - t / 1.5) : t < 2.5 ? 0 : R * Math.min(1, (t - 2.5) / 0.5);
        updateSirenVolume(s, dist(0));
        api.every(1 / 60, t => { if (t < 3) updateSirenVolume(s, dist(t)); });
        api.at(3, () => stopSiren(s));
    } },
    // Ram (Shield Bump) wind rush: on at 0, off at 2.5 s.
    wind: { dur: 3, run: (api) => {
        startWindSound();
        api.at(2.5, () => stopWindSound());
    } },

    // Gameplay music: one named track (default the first) from the top, with the game's fade-in.
    // musicTick() is called on a 0.1 s clock, as the game's own 80 ms timer would.
    music: { dur: 8, run: (api, arg) => {
        const idx = Math.max(0, MUSIC_TRACKS.findIndex(t => t.name === (arg || MUSIC_TRACKS[0].name)));
        musicActive = true; musicTrackIdx = idx; musicStep = 0; musicNextTime = api.ctx.currentTime + 0.05;
        musicFadeIn('game', MUSIC_FADE_S);
        const tick = () => { musicTick(); clearTimeout(musicTimer); musicTimer = null; };
        tick(); api.every(0.1, tick);
        api.at(api.dur - 0.01, () => { musicActive = false; });
    } },
    // Menu pad music: one pattern (index, default 0).
    menumusic: { dur: 8, run: (api, arg) => {
        menuMusicActive = true; menuMusicPatternIdx = parseInt(arg || '0', 10); menuMusicStep = 0; menuMusicNextTime = api.ctx.currentTime + 0.1;
        musicFadeIn('menu', MUSIC_FADE_S);
        const tick = () => { menuMusicTick(); clearTimeout(menuMusicTimer); menuMusicTimer = null; };
        tick(); api.every(0.1, tick);
        api.at(api.dur - 0.01, () => { menuMusicActive = false; });
    } },

    // Player engine (Batch 607) at a fixed speed ratio, fed every frame like the main loop does.
    // engine@0.5 = the stock car at ratio 0.5; engine@0.5,roller = another garage car (heavy ones sit lower).
    engine: { dur: 3, run: (api, arg) => {
        const [r, car] = (arg || '0.5').split(',');
        const savedCar = selectedCarKey; if (car) selectedCarKey = car;
        startEngineSound();
        selectedCarKey = savedCar;
        api.every(1 / 60, () => updateEngineSound(+r));
    } },
    // Engine from standstill-speed (ratio 0) to top speed (1) over the 6 s.
    engineramp: { dur: 6, run: (api) => {
        startEngineSound();
        api.every(1 / 60, t => updateEngineSound(t / 6));
    } },

    // Traffic pass whoosh (Batch 608): whoosh@car (left) / whoosh@truck (right), one pass at t=0.
    whoosh: { dur: 0.9, channels: 2, run: (api, arg) => {
        const big = arg === 'truck';
        playTrafficWhoosh(big, big ? 0.5 : -0.5);
    } },
    // 6 s of passes: cars and trucks on both sides, then a burst of 5 in 0.2 s that the overlap cap trims to 3.
    whooshseq: { dur: 6, channels: 2, run: (api) => {
        const seq = [[0, 0, -0.5], [0.7, 0, 0.5], [1.3, 1, -0.5], [2.2, 0, 0.5], [2.6, 0, -0.5], [3.4, 1, 0.5],
            [4.2, 0, -0.5], [4.25, 0, 0.5], [4.3, 1, -0.5], [4.35, 0, 0.5], [4.4, 0, -0.5]];
        for (const [t, big, pan] of seq) api.at(t, () => playTrafficWhoosh(!!big, pan));
    } },
    // Traffic hum pool: a fake player in lane centre, a car overtaken on the left (0-4 s) and a truck
    // creeping past on the right (1-6 s), positions fed every frame like the main loop's vehicles.
    traffichum: { dur: 6, channels: 2, run: (api) => {
        const lw = Math.floor(ROAD_WIDTH / config.lanes), px = ROAD_BORDER_LEFT + lw * 1.5;
        player = { x: px - 12, y: 150, width: 24, height: 44 };
        const car = { type: 'car', x: px - lw - 12, y: 0, width: 24, height: 40 };
        const truck = { type: 'truck', x: px + lw - 14, y: -80, width: 28, height: 70 };
        vehicles = [car, truck];
        startTrafficHum();
        api.every(1 / 60, t => {
            car.y = 30 + t * 60; truck.y = -80 + Math.max(0, t - 1) * 60;
            updateTrafficHum();
        });
        api.at(5.6, () => { stopTrafficHum(); player = null; vehicles = []; });
    } },

    // Biome ambience (Batch 609): bed@<biome> = that biome's bed fading in, plus whatever event falls due
    // (the first comes 2-5 s in). Fed every frame like the main loop does. bed with no biome = meadow.
    bed: { dur: 6, channels: 2, run: (api, arg) => {
        startBiomeAmbience();
        updateBiomeAmbience(arg || 'meadow');
        api.every(1 / 60, () => updateBiomeAmbience(arg || 'meadow'));
    } },
    // One biome event alone, centred: bioev@bird / water / horn / gust / wave / rumble.
    bioev: { dur: 3.6, run: (api, arg) => { playBiomeEvent(getAudio(), arg || 'bird', 0); } },
    // Crossfade: bedx@forest,city = the first biome, switching to the second at 2.5 s.
    bedx: { dur: 6, channels: 2, run: (api, arg) => {
        const [a, b] = (arg || 'forest,city').split(',');
        startBiomeAmbience();
        api.every(1 / 60, t => updateBiomeAmbience(t < 2.5 ? a : b));
    } },
};
const PREROLL_S = 0.5;   // silent lead-in before each sound, cut from the WAV (see the top of the file)
const DEFAULT_SET = ['crash@0', 'crash@0.5', 'crash@1', 'jump', 'ram', 'pickup', 'tankshot', 'click1', 'click2', 'siren', 'wind', 'music'];

// ---------- in-page renderer ----------
// Runs in the page. Returns { b64 (Int16 LE interleaved), channels, rate, frames } or { error }.
async function renderInPage({ src, name, arg, dur, channels, rate, seed, mix, preroll }) {
    // Quiet everything the menu may have started, while the real context is still in place.
    try { stopMenuMusic(true); } catch (e) {}
    try { stopMusic(true); } catch (e) {}
    try { stopAllSirens(); } catch (e) {}
    try { stopWindSound(); } catch (e) {}

    // Seeded Math.random (mulberry32), so a render is repeatable.
    let s = (seed ^ [...name + (arg || '')].reduce((h, c) => Math.imul(h ^ c.charCodeAt(0), 16777619), 2166136261)) >>> 0;
    const realRandom = Math.random;
    const seeded = () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

    const v = mix === 'game'
        ? { soundVolume: 0.3, musicVolume: 0.5, sirenVolume: 0.7, sfxVolume: 1, explosionVolume: 1, ambienceVolume: 0.6 }
        : { soundVolume: 1, musicVolume: 1, sirenVolume: 1, sfxVolume: 1, explosionVolume: 1, ambienceVolume: 1 };
    const savedCfg = {};
    for (const k of Object.keys(v).concat('soundEnabled')) savedCfg[k] = config[k];
    Object.assign(config, v, { soundEnabled: true });

    const Q = 128;
    const pre = Math.max(Q, Math.round(preroll * rate / Q) * Q);   // silent lead-in, cut from the WAV (see top)
    const frames = Math.ceil(dur * rate);
    const ctx = new OfflineAudioContext(channels, pre + frames, rate);
    const realGetAudio = window.getAudio;
    // The offline context is handed out ONLY while recipe code runs. The menu keeps its own timers
    // going (menu music restarts itself), and a timer firing mid-render would otherwise schedule its
    // notes into this WAV - which is exactly what happened before this guard.
    let inRecipe = false;
    // Math.random is seeded only inside recipe code too, so the menu's own animation cannot eat numbers.
    const guard = fn => (...a) => { inRecipe = true; Math.random = seeded; try { return fn(...a); } finally { inRecipe = false; Math.random = realRandom; } };
    window.getAudio = () => inRecipe ? ctx : realGetAudio();

    // quantized frame (pre-roll included) -> [fn]. Each frame gets one suspend, registered when its first
    // fn is added - recipes add events from inside run(), which itself runs mid-render at the pre-roll's end.
    const events = new Map();
    let error = null;
    let nowF = -1;   // the frame whose events are running right now
    const add = (t, fn) => {
        const f = pre + Math.round(t * rate / Q) * Q;
        if (f >= pre + frames) return;
        if (f <= nowF) { fn(); return; }
        if (!events.has(f)) {
            events.set(f, []);
            ctx.suspend(f / rate).then(() => {
                nowF = f;
                for (const fn of events.get(f)) { try { fn(); } catch (e) { error = error || String(e && e.stack || e); } }
                ctx.resume();
            });
        }
        events.get(f).push(fn);
    };
    const api = {
        ctx, dur,
        at: (t, fn) => add(t, guard(() => fn(t))),
        every: (dt, fn) => { for (let t = dt; t < dur; t += dt) { const tt = t; add(tt, guard(() => fn(tt))); } },
    };
    try {
        const recipeRun = (0, eval)('(' + src + ')');
        // The game's buses (if this version has them) are built at t=0, as getAudio() does with a new context.
        if (typeof audioBus === 'function') guard(() => audioBus('master'))();
        add(0, () => guard(recipeRun)(api, arg));
        const buf = await ctx.startRendering();
        if (error) throw new Error(error);
        // Int16 interleaved
        const n = frames, ch = buf.numberOfChannels, out = new Int16Array(n * ch);
        const data = []; for (let c = 0; c < ch; c++) data.push(buf.getChannelData(c));
        let clipped = 0;
        for (let i = 0; i < n; i++) for (let c = 0; c < ch; c++) {
            let x = data[c][pre + i];
            if (x > 1 || x < -1) { clipped++; x = Math.max(-1, Math.min(1, x)); }
            out[i * ch + c] = Math.round(x * 32767);
        }
        const bytes = new Uint8Array(out.buffer);
        let bin = ''; for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
        return { b64: btoa(bin), channels: ch, rate, frames: n, clipped };
    } catch (e) {
        return { error: String(e && e.stack || e) };
    } finally {
        // Put the game back and drop whatever the recipe left pointing at the offline context.
        window.getAudio = realGetAudio;
        Math.random = realRandom;
        Object.assign(config, savedCfg);
        try { activeSirens = []; } catch (e) {}
        try { windSound = null; } catch (e) {}
        try { engineSound = null; } catch (e) {}
        try { biomeAmb = null; } catch (e) {}
        try { musicActive = false; clearTimeout(musicTimer); musicTimer = null; } catch (e) {}
        try { menuMusicActive = false; clearTimeout(menuMusicTimer); menuMusicTimer = null; } catch (e) {}
    }
}

function wavBytes(pcm, channels, rate) {
    const h = Buffer.alloc(44);
    h.write('RIFF', 0); h.writeUInt32LE(36 + pcm.length, 4); h.write('WAVE', 8);
    h.write('fmt ', 12); h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(channels, 22);
    h.writeUInt32LE(rate, 24); h.writeUInt32LE(rate * channels * 2, 28); h.writeUInt16LE(channels * 2, 32); h.writeUInt16LE(16, 34);
    h.write('data', 36); h.writeUInt32LE(pcm.length, 40);
    return Buffer.concat([h, pcm]);
}

function parseArgs(argv) {
    const o = { names: [], seed: 1, mix: 'full', rate: 44100, recipes: null, list: false, pos: [] };
    for (let i = 0; i < argv.length; i++) {
        const a = argv[i];
        if (a === '--seed') o.seed = parseInt(argv[++i], 10);
        else if (a === '--mix') o.mix = argv[++i];
        else if (a === '--rate') o.rate = parseInt(argv[++i], 10);
        else if (a === '--recipes') o.recipes = argv[++i];
        else if (a === '--list') o.list = true;
        else if (a.startsWith('--')) throw new Error('unknown option ' + a);
        else o.pos.push(a);
    }
    [o.html, o.out, ...o.names] = o.pos;
    return o;
}

(async () => {
    const o = parseArgs(process.argv.slice(2));
    const recipes = Object.assign({}, RECIPES, o.recipes ? require(path.resolve(o.recipes)) : {});
    if (o.list) { console.log(Object.keys(recipes).join('\n')); return; }
    if (!o.html || !o.out) { console.error('usage: node render.js <game.html> <out-dir> [sound ...] [--seed N] [--mix full|game] [--recipes file.js] [--list]'); process.exit(2); }
    const names = o.names.length ? o.names : DEFAULT_SET;
    fs.mkdirSync(o.out, { recursive: true });

    const browser = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox', '--headless=new', '--autoplay-policy=no-user-gesture-required'] });
    const page = await (await browser.newContext()).newPage();
    page.on('pageerror', e => console.error('[pageerror]', e.message));
    page.on('console', m => { if (m.type() === 'error' && !/403/.test(m.text())) console.error('[console]', m.text()); });
    await page.goto('file://' + path.resolve(o.html));
    await page.waitForTimeout(1200);

    let failed = 0;
    for (const full of names) {
        const [name, arg] = full.split('@');
        const r = recipes[name];
        if (!r) { console.error(`${full}: no such recipe`); failed++; continue; }
        const res = await page.evaluate(renderInPage, {
            src: r.run.toString(), name, arg, dur: r.dur, channels: r.channels || 1, rate: o.rate, seed: o.seed, mix: o.mix, preroll: PREROLL_S,
        });
        if (res.error) { console.error(`${full}: FAILED - ${res.error.split('\n')[0]}`); failed++; continue; }
        const pcm = Buffer.from(res.b64, 'base64');
        let peak = 0; for (let i = 0; i < pcm.length; i += 2) peak = Math.max(peak, Math.abs(pcm.readInt16LE(i)));
        const file = path.join(o.out, full.replace(/@/g, '-') + '.wav');
        fs.writeFileSync(file, wavBytes(pcm, res.channels, res.rate));
        const peakDb = peak ? (20 * Math.log10(peak / 32767)).toFixed(1) : '-inf';
        console.log(`${file}  ${(res.frames / res.rate).toFixed(2)}s  ${res.channels}ch  peak ${peakDb} dBFS${res.clipped ? `  CLIPPED ${res.clipped} samples` : ''}`);
    }
    await browser.close();
    process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
