class Pcm16MonoProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.targetSampleRate = 16000;
    this.sourceStep = sampleRate / this.targetSampleRate;
    this.sourceSamples = [];
    this.sourcePosition = 0;
    const cutoff = Math.min(7200, sampleRate * 0.45);
    const omega = (2 * Math.PI * cutoff) / sampleRate;
    const cosine = Math.cos(omega);
    const alpha = Math.sin(omega) / (2 * Math.SQRT1_2);
    const a0 = 1 + alpha;
    this.b0 = (1 - cosine) / 2 / a0;
    this.b1 = (1 - cosine) / a0;
    this.b2 = this.b0;
    this.a1 = (-2 * cosine) / a0;
    this.a2 = (1 - alpha) / a0;
    this.x1 = 0;
    this.x2 = 0;
    this.y1 = 0;
    this.y2 = 0;
    this.chunk = new Int16Array(1600);
    this.chunkOffset = 0;
  }

  process(inputs) {
    const channels = inputs[0];
    if (!channels || channels.length === 0 || channels[0].length === 0) return true;

    const frameCount = channels[0].length;
    for (let frame = 0; frame < frameCount; frame += 1) {
      let mixed = 0;
      let channelCount = 0;
      for (let channel = 0; channel < channels.length; channel += 1) {
        const samples = channels[channel];
        if (samples && frame < samples.length) {
          mixed += samples[frame];
          channelCount += 1;
        }
      }
      const input = channelCount ? mixed / channelCount : 0;
      const filtered =
        this.b0 * input +
        this.b1 * this.x1 +
        this.b2 * this.x2 -
        this.a1 * this.y1 -
        this.a2 * this.y2;
      this.x2 = this.x1;
      this.x1 = input;
      this.y2 = this.y1;
      this.y1 = filtered;
      this.sourceSamples.push(filtered);
    }

    while (this.sourcePosition + 1 < this.sourceSamples.length) {
      const lowerIndex = Math.floor(this.sourcePosition);
      const fraction = this.sourcePosition - lowerIndex;
      const lower = this.sourceSamples[lowerIndex];
      const upper = this.sourceSamples[lowerIndex + 1];
      const value = lower + (upper - lower) * fraction;
      const clipped = Math.max(-1, Math.min(1, value));
      this.chunk[this.chunkOffset] = clipped < 0 ? clipped * 32768 : clipped * 32767;
      this.chunkOffset += 1;
      this.sourcePosition += this.sourceStep;

      if (this.chunkOffset === this.chunk.length) {
        const completedChunk = this.chunk;
        this.port.postMessage(completedChunk.buffer, [completedChunk.buffer]);
        this.chunk = new Int16Array(1600);
        this.chunkOffset = 0;
      }
    }

    const consumed = Math.floor(this.sourcePosition);
    if (consumed > 0) {
      this.sourceSamples.splice(0, consumed);
      this.sourcePosition -= consumed;
    }
    return true;
  }
}

registerProcessor("pcm16-mono-16k", Pcm16MonoProcessor);
