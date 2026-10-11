// In-game balance mixes: engine ramp + traffic hum + passes + biome bed + music, ending in the crash.
// Use with --mix game:  node tools/soundlab/render.js carCrash.html OUT mix@city --recipes tools/soundlab/mix-recipes.js --mix game
module.exports = {
    mix: { dur: 20, channels: 2, run: (api, arg) => {
        const biome = arg || 'meadow';
        musicActive = true; musicTrackIdx = 0; musicStep = 0; musicNextTime = api.ctx.currentTime + 0.05;
        musicFadeIn('game', MUSIC_FADE_S);
        const mtick = () => { musicTick(); clearTimeout(musicTimer); musicTimer = null; };
        mtick(); api.every(0.1, mtick);
        startBiomeAmbience(); updateBiomeAmbience(biome);
        startEngineSound();
        const lw = Math.floor(ROAD_WIDTH / config.lanes), px = ROAD_BORDER_LEFT + lw * 1.5;
        player = { x: px - 12, y: 150, width: 24, height: 44 };
        const car = { type: 'car', x: px - lw - 12, y: 0, width: 24, height: 40 };
        const truck = { type: 'truck', x: px + lw - 14, y: -80, width: 28, height: 70 };
        vehicles = [car, truck];
        startTrafficHum();
        const CRASH = 17;
        api.every(1 / 60, t => {
            if (t < CRASH) {
                updateEngineSound(Math.min(1, 0.1 + t / 14));
                updateBiomeAmbience(biome);
                car.y = 30 + (t % 8) * 60; truck.y = -80 + ((t + 4) % 8) * 60;
                updateTrafficHum();
            }
        });
        for (const [t, big, pan] of [[2, 0, -0.5], [4.5, 0, 0.5], [7, 1, -0.5], [9.5, 0, 0.5], [11, 0, -0.5], [13, 1, 0.5], [14.5, 0, -0.5], [16, 0, 0.5]])
            api.at(t, () => playTrafficWhoosh(!!big, pan));
        api.at(CRASH, () => { stopEngineSound(0.05); stopTrafficHum(0.1); playSound('crash', 0.9); });
        api.at(api.dur - 0.05, () => { musicActive = false; player = null; vehicles = []; });
    } },
};
