export interface CaptureHandle {
  close: () => Promise<void>;
}

export async function createPcmCapture(
  onChunk: (chunk: ArrayBuffer) => void,
): Promise<CaptureHandle> {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error(
      "Microphone capture is not available in this browser or page context.",
    );
  }
  if (!("AudioWorkletNode" in window)) {
    throw new Error("This browser does not support AudioWorklet microphone capture.");
  }

  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      channelCount: { ideal: 1 },
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
    video: false,
  });

  let context: AudioContext | null = null;
  let source: MediaStreamAudioSourceNode | null = null;
  let processor: AudioWorkletNode | null = null;
  let silentOutput: GainNode | null = null;
  try {
    context = new AudioContext();
    const workletPath = import.meta.env.BASE_URL + "pcm16-worklet.js";
    await context.audioWorklet.addModule(workletPath);
    source = context.createMediaStreamSource(stream);
    processor = new AudioWorkletNode(context, "pcm16-mono-16k", {
      numberOfInputs: 1,
      numberOfOutputs: 1,
      outputChannelCount: [1],
      channelCount: 1,
      channelCountMode: "explicit",
    });
    silentOutput = context.createGain();
    silentOutput.gain.value = 0;
    processor.port.onmessage = (event: MessageEvent<ArrayBuffer>) => {
      if (event.data instanceof ArrayBuffer) onChunk(event.data);
    };
    source.connect(processor);
    processor.connect(silentOutput);
    silentOutput.connect(context.destination);
    await context.resume();
  } catch (error) {
    stream.getTracks().forEach((track) => track.stop());
    await context?.close();
    throw error;
  }

  return {
    close: async () => {
      processor?.port.close();
      source?.disconnect();
      processor?.disconnect();
      silentOutput?.disconnect();
      stream.getTracks().forEach((track) => track.stop());
      await context?.close();
    },
  };
}
