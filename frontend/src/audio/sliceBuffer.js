/**
 * Extract a time-range from an AudioBuffer into a new AudioBuffer.
 * @param {AudioBuffer} buf  Source buffer
 * @param {number} startSec  Start time in seconds (clamped to 0)
 * @param {number} endSec    End time in seconds (clamped to duration)
 * @returns {AudioBuffer}
 */
export function sliceAudioBuffer(buf, startSec, endSec) {
  const sr = buf.sampleRate;
  const startSample = Math.max(0, Math.floor(startSec * sr));
  const endSample = Math.min(buf.length, Math.ceil(endSec * sr));
  const length = endSample - startSample;
  if (length <= 0) return buf;

  const sliced = new AudioBuffer({
    numberOfChannels: buf.numberOfChannels,
    length,
    sampleRate: sr,
  });

  for (let ch = 0; ch < buf.numberOfChannels; ch++) {
    const src = buf.getChannelData(ch);
    const dst = sliced.getChannelData(ch);
    for (let i = 0; i < length; i++) {
      dst[i] = src[startSample + i];
    }
  }

  return sliced;
}
