/**
 * Build a Type-0 single-track MIDI blob for kick / snare / hi-hat (GM drums).
 * Ported from drum-pattern-visualizer.html.
 */

export function buildDrumPatternMidi(pattern, gridSize) {
  const p = pattern;
  const bpm = p.bpm || 120;
  const ppq = 480;
  const spb = gridSize / 4;
  const tps = ppq / spb;
  const K = 36;
  const S = 38;
  const H = 42;
  const ev = [];

  const add = (d, v, n) => {
    d.forEach((x, i) => {
      if (x > 0) {
        const t = i * tps;
        ev.push({ tick: t, type: 'on', note: n, velocity: Math.round((v[i] || 0.8) * 127) });
        ev.push({ tick: t + tps / 2, type: 'off', note: n, velocity: 0 });
      }
    });
  };

  add(p.kick, p.kickVel, K);
  add(p.snare, p.snareVel, S);
  add(p.hihat, p.hihatVel, H);
  ev.sort((a, b) => a.tick - b.tick);

  const by = [];
  const ws = (s) => {
    for (let i = 0; i < s.length; i++) by.push(s.charCodeAt(i));
  };
  const w16 = (v) => {
    by.push((v >> 8) & 0xff, v & 0xff);
  };
  const w32 = (v) => {
    by.push((v >> 24) & 0xff, (v >> 16) & 0xff, (v >> 8) & 0xff, v & 0xff);
  };
  const wv = (v) => {
    const b = [];
    b.push(v & 0x7f);
    let x = v >> 7;
    while (x > 0) {
      b.push((x & 0x7f) | 0x80);
      x >>= 7;
    }
    b.reverse().forEach((byte) => by.push(byte));
  };

  ws('MThd');
  w32(6);
  w16(0);
  w16(1);
  w16(ppq);
  const ts = by.length;
  ws('MTrk');
  w32(0);
  const tds = by.length;
  wv(0);
  by.push(0xff, 0x51, 0x03);
  const u = Math.round(60000000 / bpm);
  by.push((u >> 16) & 0xff, (u >> 8) & 0xff, u & 0xff);
  let pt = 0;
  ev.forEach((e) => {
    wv(e.tick - pt);
    by.push(e.type === 'on' ? 0x99 : 0x89, e.note, e.type === 'on' ? e.velocity : 0);
    pt = e.tick;
  });
  wv(0);
  by.push(0xff, 0x2f, 0x00);
  const tl = by.length - tds;
  by[ts + 4] = (tl >> 24) & 0xff;
  by[ts + 5] = (tl >> 16) & 0xff;
  by[ts + 6] = (tl >> 8) & 0xff;
  by[ts + 7] = tl & 0xff;

  return new Blob([new Uint8Array(by)], { type: 'audio/midi' });
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
