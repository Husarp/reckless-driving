// Copies the single-file game into www/index.html, which is what Capacitor packages.
// The game has exactly one source of truth - ../carCrash.html - and this keeps it that way:
// www/index.html is build output, never edited by hand, and is gitignored.
const fs = require('fs');
const path = require('path');

const src = path.join(__dirname, '..', 'carCrash.html');
const outDir = path.join(__dirname, 'www');
const dest = path.join(outDir, 'index.html');

const html = fs.readFileSync(src, 'utf8');

// Same guard the Windows build uses: a packaged app must not need the network for its fonts.
if (/fonts\.(googleapis|gstatic)\.com/.test(html)) {
    console.error('carCrash.html still references Google Fonts - run: python tools/embed_fonts.py');
    process.exit(1);
}

const m = html.match(/GAME_VERSION\s*=\s*'([^']+)'/);
if (!m) { console.error('Could not read GAME_VERSION from carCrash.html'); process.exit(1); }

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(dest, html);
console.log('Copied carCrash.html -> www/index.html (version ' + m[1] + ', ' + html.length + ' bytes)');
