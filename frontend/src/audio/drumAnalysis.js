/**
 * Client-side drum onset / BPM helpers (ported from drum-pattern-visualizer.html).
 */

export function detectBPM(d, sr) {
  const hs = 512;
  const fs = 1024;
  const nf = Math.floor(d.length / hs) - 1;
  const en = new Float32Array(nf);
  for (let i = 0; i < nf; i++) {
    let sum = 0;
    const st = i * hs;
    for (let j = 0; j < fs && st + j < d.length; j++) sum += d[st + j] ** 2;
    en[i] = sum;
  }
  const od = new Float32Array(nf);
  for (let i = 1; i < nf; i++) od[i] = Math.max(0, en[i] - en[i - 1]);
  const fps = sr / hs;
  const mnL = Math.floor((fps * 60) / 200);
  const mxL = Math.floor((fps * 60) / 60);
  let bL = mnL;
  let bC = 0;
  for (let l = mnL; l <= mxL && l < od.length; l++) {
    let c = 0;
    const ln = Math.min(od.length - l, 2000);
    for (let i = 0; i < ln; i++) c += od[i] * od[i + l];
    if (c > bC) {
      bC = c;
      bL = l;
    }
  }
  let b = Math.round((fps * 60) / bL);
  while (b < 70) b *= 2;
  while (b > 180) b /= 2;
  return b;
}

export function detectOnsets(d, sr, lf, hf, sens) {
  const fs = 2048;
  const hs = 512;
  const o = [];
  let pe = 0;
  const th = 0.02 * (1 - sens * 0.8);
  const mi = 0.05;
  let lo = -1;
  for (let f = 0; f < Math.floor(d.length / hs) - 2; f++) {
    const st = f * hs;
    let e = 0;
    for (let i = 0; i < fs && st + i < d.length; i++) e += d[st + i] ** 2;
    if (hf < 200) e *= 2.5;
    if (lf > 3000) e *= 1.5;
    const df = e - pe;
    const t = st / sr;
    if (df > th && t - lo > mi) {
      o.push({ time: t, energy: df });
      lo = t;
    }
    pe = e * 0.7 + pe * 0.3;
  }
  return o;
}

export function qtg(onsets, sd, ns, dur) {
  const g = new Array(ns).fill(0);
  for (const x of onsets) {
    if (x.time > dur) break;
    g[Math.round(x.time / sd) % ns] = 1;
  }
  return g;
}

export function estSwing(o, sd) {
  if (o.length < 4) return 0;
  const dv = [];
  for (const x of o) {
    const sf = x.time / sd;
    const ns = Math.round(sf);
    if (ns % 2 === 1) dv.push(sf - ns);
  }
  if (!dv.length) return 0;
  return Math.round(Math.abs(dv.reduce((a, b) => a + b, 0) / dv.length) * 100);
}

export function classifyPattern(k, s, h, bpm) {
  const kc = k.filter((v) => v > 0).length;
  const hc = h.filter((v) => v > 0).length;
  const st = k.length;
  const spb = st / 4;
  let fof = true;
  for (let i = 0; i < 4; i++) if (!k[i * spb]) fof = false;
  if (fof && bpm >= 118 && bpm <= 135)
    return hc > st * 0.6
      ? { name: 'Techno', desc: 'Driving four-on-floor with dense hi-hats' }
      : { name: 'House', desc: 'Four-on-floor kick, offbeat hi-hats' };
  if (bpm >= 130 && bpm <= 160 && hc > st * 0.7)
    return { name: 'Trap', desc: 'Fast tempo with rapid hi-hat rolls' };
  if (bpm >= 80 && bpm <= 100 && kc <= 4)
    return { name: 'Boom Bap', desc: 'Mid-tempo with sparse, syncopated kicks' };
  if (kc >= st * 0.3) return { name: 'Breakbeat', desc: 'Syncopated, complex pattern' };
  const dn = (kc + s.filter((v) => v > 0).length + hc) / (st * 3);
  if (dn < 0.25) return { name: 'Minimal', desc: 'Sparse pattern with lots of space' };
  if (dn > 0.6) return { name: 'Dense', desc: 'Busy layered pattern' };
  return { name: 'Custom', desc: 'Unique pattern' };
}

export function tileArray(a, len) {
  const r = [];
  for (let i = 0; i < len; i++) r.push(a[i % a.length]);
  return r;
}

/**
 * @param {AudioBuffer} audioBuffer
 * @param {number} sensitivityPercent 0–100
 * @param {number} gridSize 8 | 16 | 32
 * @param {number} barCount 1 | 2 | 4
 */
export function analyzeAudioBuffer(audioBuffer, sensitivityPercent, gridSize, barCount) {
  const d = audioBuffer.getChannelData(0);
  const sr = audioBuffer.sampleRate;
  const sens = sensitivityPercent / 100;
  const ns = gridSize * barCount;
  const bpm = detectBPM(d, sr);
  const sd = 60 / bpm / (gridSize / 4);
  const ko = detectOnsets(d, sr, 40, 150, sens);
  const so = detectOnsets(d, sr, 150, 1500, sens);
  const ho = detectOnsets(d, sr, 5000, 16000, sens);
  const ad = Math.min(audioBuffer.duration, sd * ns);
  const k = qtg(ko, sd, ns, ad);
  const s = qtg(so, sd, ns, ad);
  const h = qtg(ho, sd, ns, ad);
  const st = classifyPattern(k, s, h, bpm);
  const sw = estSwing(ko.concat(so), sd);
  return {
    kick: k,
    snare: s,
    hihat: h,
    kickVel: k.map((v) => v * (0.7 + Math.random() * 0.3)),
    snareVel: s.map((v) => v * (0.7 + Math.random() * 0.3)),
    hihatVel: h.map((v) => v * (0.5 + Math.random() * 0.5)),
    bpm,
    style: st,
    swing: sw,
    steps: ns,
    desc: st.desc,
  };
}
