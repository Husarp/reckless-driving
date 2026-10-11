#!/usr/bin/env python3
"""Sound lab analyzer - quick numbers for WAV files, so sounds can be compared without ears.

Usage:
  /tmp/sndvenv/bin/python tools/soundlab/analyze.py FILE.wav [FILE.wav ...] [--png-dir DIR] [--no-png]
  /tmp/sndvenv/bin/python tools/soundlab/analyze.py --compare REF.wav OTHER.wav [...]

Per file it prints: length, audible span (from the first to the last 10 ms window within 40 dB of
the loudest one, i.e. how long it actually sounds), peak and RMS in dBFS (RMS over the audible span),
spectral centroid (the "brightness": low = dull/boomy, high = bright/hissy), and an 8-band spectrum
(each band's share of the energy, in dB relative to the whole sound; 0 dB = all energy in that band).
With --compare, the first file is the reference and each other file gets per-band differences.

Spectral numbers and the PNG spectrogram need numpy (+ matplotlib for the PNG). Set up once with:
  uv venv /tmp/sndvenv && VIRTUAL_ENV=/tmp/sndvenv uv pip install numpy matplotlib
Without numpy only length/peak/RMS are printed. 8/16/24/32-bit PCM WAV, any channel count
(channels are averaged to mono for the analysis).
"""
import math
import os
import struct
import sys
import wave

try:
    import numpy as np
except ImportError:
    np = None

BANDS = [(20, 60), (60, 150), (150, 400), (400, 1000), (1000, 2500), (2500, 6000), (6000, 12000), (12000, 22050)]
BAND_NAMES = ['sub', 'bass', 'lowmid', 'mid', 'upmid', 'presence', 'bright', 'air']


def read_wav(path):
    with wave.open(path, 'rb') as w:
        ch, width, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if width == 1:
        vals = [(b - 128) / 128 for b in raw]
    elif width == 2:
        vals = [v / 32768 for v in struct.unpack('<%dh' % (len(raw) // 2), raw)]
    elif width == 3:
        vals = [int.from_bytes(raw[i:i + 3], 'little', signed=True) / 8388608 for i in range(0, len(raw), 3)]
    elif width == 4:
        vals = [v / 2147483648 for v in struct.unpack('<%di' % (len(raw) // 4), raw)]
    else:
        raise ValueError('unsupported sample width %d' % width)
    mono = [sum(vals[i:i + ch]) / ch for i in range(0, len(vals), ch)]
    return mono, rate, ch


def db(x):
    return 20 * math.log10(x) if x > 0 else float('-inf')


def audible_span(x, rate):
    win = max(1, rate // 100)
    rms = [math.sqrt(sum(v * v for v in x[i:i + win]) / len(x[i:i + win])) for i in range(0, len(x), win)]
    top = max(rms) if rms else 0
    if top <= 0:
        return 0, 0
    keep = [i for i, r in enumerate(rms) if r >= top * 0.01]   # within 40 dB of the loudest window
    return keep[0] * win, min(len(x), (keep[-1] + 1) * win)


def spectrum(x, rate):
    a = np.asarray(x, dtype=np.float64)
    n = 2048
    if len(a) < n:
        a = np.pad(a, (0, n - len(a)))
    win = np.hanning(n)
    frames = [a[i:i + n] * win for i in range(0, len(a) - n + 1, n // 2)]
    p = np.mean([np.abs(np.fft.rfft(f)) ** 2 for f in frames], axis=0)
    f = np.fft.rfftfreq(n, 1 / rate)
    return f, p


def analyze(path, png_dir=None, make_png=True):
    x, rate, ch = read_wav(path)
    out = {'path': path, 'rate': rate, 'ch': ch, 'dur': len(x) / rate}
    peak = max((abs(v) for v in x), default=0)
    s0, s1 = audible_span(x, rate)
    seg = x[s0:s1] or x
    rms = math.sqrt(sum(v * v for v in seg) / len(seg)) if seg else 0
    out.update(peak=db(peak), rms=db(rms), span=(s0 / rate, s1 / rate))
    if np is not None and peak > 0:
        f, p = spectrum(seg, rate)
        tot = p.sum() or 1
        out['centroid'] = float((f * p).sum() / tot)
        out['bands'] = [db(math.sqrt(p[(f >= lo) & (f < hi)].sum() / tot)) for lo, hi in BANDS]
        if make_png:
            out['png'] = spectrogram(x, rate, path, png_dir)
    return out


def spectrogram(x, rate, path, png_dir):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    a = np.asarray(x, dtype=np.float64)
    base = os.path.splitext(os.path.basename(path))[0]
    dest = os.path.join(png_dir or os.path.dirname(path) or '.', base + '.png')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), sharex=True, gridspec_kw={'height_ratios': [1, 3]})
    t = np.arange(len(a)) / rate
    ax1.plot(t, a, lw=0.5, color='#333')
    ax1.set_ylim(-1, 1)
    ax1.set_ylabel('wave')
    nfft = 1024 if len(a) >= 1024 else 256
    ax2.specgram(a + 1e-12, NFFT=nfft, Fs=rate, noverlap=nfft * 3 // 4, cmap='magma', vmin=-120)
    ax2.set_yscale('symlog', linthresh=200)
    ax2.set_ylim(20, rate / 2)
    ax2.set_ylabel('Hz')
    ax2.set_xlabel('s')
    ax1.set_title(base)
    fig.tight_layout()
    fig.savefig(dest, dpi=90)
    plt.close(fig)
    return dest


def fmt(r):
    lines = ['%s' % r['path'],
             '  length %.2fs  audible %.2f-%.2fs (%.2fs)  %d Hz %dch' % (r['dur'], r['span'][0], r['span'][1], r['span'][1] - r['span'][0], r['rate'], r['ch']),
             '  peak %.1f dBFS  rms %.1f dBFS%s' % (r['peak'], r['rms'], '  SILENT (peak below -40 dBFS)' if r['peak'] < -40 else '')]
    if 'centroid' in r:
        lines.append('  centroid %d Hz' % r['centroid'])
        lines.append('  bands  ' + '  '.join('%s %s' % (n, ('%.0f' % b) if b > -99 else '-inf') for n, b in zip(BAND_NAMES, r['bands'])))
        lines.append('         (%s Hz)' % ' '.join('%d-%d' % lh for lh in BANDS))
    elif np is None:
        lines.append('  (centroid/bands/spectrogram need numpy - see the header)')
    if r.get('png'):
        lines.append('  spectrogram %s' % r['png'])
    return '\n'.join(lines)


def main(argv):
    png_dir, make_png, compare, files = None, True, False, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--png-dir':
            png_dir = argv[i + 1]; i += 1
        elif a == '--no-png':
            make_png = False
        elif a == '--compare':
            compare = True
        elif a in ('-h', '--help'):
            print(__doc__); return 0
        else:
            files.append(a)
        i += 1
    if not files:
        print(__doc__); return 2
    if png_dir:
        os.makedirs(png_dir, exist_ok=True)
    results = [analyze(f, png_dir, make_png) for f in files]
    for r in results:
        print(fmt(r))
    if compare and len(results) > 1 and 'bands' in results[0]:
        ref = results[0]
        print('\nCompared with %s (other minus reference):' % ref['path'])
        for r in results[1:]:
            if 'bands' not in r:
                continue
            d = ['%s %+.0f' % (n, b - rb) if b > -99 and rb > -99 else '%s n/a' % n for n, b, rb in zip(BAND_NAMES, r['bands'], ref['bands'])]
            print('  %s: length %+.2fs  audible %+.2fs  peak %+.1f dB  rms %+.1f dB  centroid %+d Hz\n    bands %s' % (
                r['path'], r['dur'] - ref['dur'], (r['span'][1] - r['span'][0]) - (ref['span'][1] - ref['span'][0]),
                r['peak'] - ref['peak'], r['rms'] - ref['rms'], r['centroid'] - ref['centroid'], '  '.join(d)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
