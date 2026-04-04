/** Draw peak waveform into canvas (logic from drum-pattern-visualizer.html). */

export function drawWaveform(canvas, audioBuffer) {
  if (!canvas || !audioBuffer) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const dpr = window.devicePixelRatio || 1;
  const r = canvas.getBoundingClientRect();
  canvas.width = r.width * dpr;
  canvas.height = r.height * dpr;
  ctx.scale(dpr, dpr);
  const d = audioBuffer.getChannelData(0);
  const step = Math.ceil(d.length / r.width);
  const amp = r.height / 2;
  ctx.clearRect(0, 0, r.width, r.height);
  ctx.fillStyle = '#1a1714';
  for (let i = 0; i < r.width; i++) {
    let mn = 1;
    let mx = -1;
    for (let j = 0; j < step; j++) {
      const v = d[i * step + j] || 0;
      if (v < mn) mn = v;
      if (v > mx) mx = v;
    }
    const h = Math.max(1, (mx - mn) * amp);
    ctx.globalAlpha = 0.3 + 0.5 * Math.abs(mx - mn);
    ctx.fillRect(i, amp - h / 2, 1, h);
  }
}
