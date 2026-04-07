/** Draw peak waveform into canvas, optionally restricted to a view window. */

/**
 * @param {HTMLCanvasElement} canvas
 * @param {AudioBuffer} audioBuffer
 * @param {{ start: number, end: number } | null} viewWindow - normalized 0–1 fractions of duration
 */
export function drawWaveform(canvas, audioBuffer, viewWindow = null) {
  if (!canvas || !audioBuffer) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const dpr = window.devicePixelRatio || 1;
  const r = canvas.getBoundingClientRect();
  canvas.width = r.width * dpr;
  canvas.height = r.height * dpr;
  ctx.scale(dpr, dpr);

  const d = audioBuffer.getChannelData(0);
  const totalSamples = d.length;

  const startFrac = viewWindow ? Math.max(0, viewWindow.start) : 0;
  const endFrac = viewWindow ? Math.min(1, viewWindow.end) : 1;

  const startSample = Math.floor(startFrac * totalSamples);
  const endSample = Math.ceil(endFrac * totalSamples);
  const viewSamples = endSample - startSample;

  const step = Math.ceil(viewSamples / r.width);
  const amp = r.height / 2;

  ctx.clearRect(0, 0, r.width, r.height);
  ctx.fillStyle = '#1a1714';

  for (let i = 0; i < r.width; i++) {
    let mn = 1;
    let mx = -1;
    const sampleBase = startSample + i * step;
    for (let j = 0; j < step; j++) {
      const v = d[sampleBase + j] || 0;
      if (v < mn) mn = v;
      if (v > mx) mx = v;
    }
    const h = Math.max(1, (mx - mn) * amp);
    ctx.globalAlpha = 0.3 + 0.5 * Math.abs(mx - mn);
    ctx.fillRect(i, amp - h / 2, 1, h);
  }
}

/**
 * Draw a compact mini-map waveform with a viewport indicator rect.
 * @param {HTMLCanvasElement} canvas
 * @param {AudioBuffer} audioBuffer
 * @param {{ start: number, end: number }} viewWindow - normalized 0–1 fractions
 */
export function drawMiniMap(canvas, audioBuffer, viewWindow) {
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
    ctx.globalAlpha = 0.25 + 0.4 * Math.abs(mx - mn);
    ctx.fillRect(i, amp - h / 2, 1, h);
  }

  // Draw viewport indicator
  ctx.globalAlpha = 1;
  const vx = viewWindow.start * r.width;
  const vw = (viewWindow.end - viewWindow.start) * r.width;
  ctx.strokeStyle = 'rgba(150, 215, 255, 0.8)';
  ctx.lineWidth = 1.5;
  ctx.strokeRect(vx, 1, vw, r.height - 2);
  ctx.fillStyle = 'rgba(150, 215, 255, 0.08)';
  ctx.fillRect(vx, 1, vw, r.height - 2);
}
