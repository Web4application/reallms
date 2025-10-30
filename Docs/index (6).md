---
title: Realtime WebSockets API · Cloudflare AI Gateway docs
description: Some AI providers support real-time, low-latency interactions over
  WebSockets. AI Gateway allows seamless integration with these APIs, supporting
  multimodal interactions such as text, audio, and video.
lastUpdated: 2025-10-09T17:51:29.000Z
chatbotDeprioritize: false
source_url:
  html: https://developers.cloudflare.com/ai-gateway/usage/websockets-api/realtime-api/
  md: https://developers.cloudflare.com/ai-gateway/usage/websockets-api/realtime-api/index.md
---

Some AI providers support real-time, low-latency interactions over WebSockets. AI Gateway allows seamless integration with these APIs, supporting multimodal interactions such as text, audio, and video.

## Supported Providers

* [OpenAI](https://platform.openai.com/docs/guides/realtime-websocket)
* [Google AI Studio](https://ai.google.dev/gemini-api/docs/multimodal-live)
* [Cartesia](https://docs.cartesia.ai/api-reference/tts/tts)
* [ElevenLabs](https://elevenlabs.io/docs/conversational-ai/api-reference/conversational-ai/websocket)
* [Fal AI](https://docs.fal.ai/model-apis/model-endpoints/websockets)
* [Deepgram (Workers AI)](https://developers.cloudflare.com/workers-ai/models/?authors=deepgram)

## Authentication

For real-time WebSockets, authentication can be done using:

* Headers (for non-browser environments)
* `sec-websocket-protocol` (for browsers)

Note

Provider specific API Keys can also be alternatively configured on AI Gateway using our [BYOK](https://developers.cloudflare.com/ai-gateway/configuration/bring-your-own-keys) feature. You must still include the `cf-aig-authorization` header in the websocket request.

## Examples

### OpenAI

```javascript
import WebSocket from "ws";


const url =
  "wss://gateway.ai.cloudflare.com/v1/<account_id>/<gateway>/openai?model=gpt-4o-realtime-preview-2024-12-17";
const ws = new WebSocket(url, {
  headers: {
    "cf-aig-authorization": process.env.CLOUDFLARE_API_KEY,
    Authorization: "Bearer " + process.env.OPENAI_API_KEY,
    "OpenAI-Beta": "realtime=v1",
  },
});


ws.on("open", () => console.log("Connected to server."));
ws.on("message", (message) => console.log(JSON.parse(message.toString())));


ws.send(
  JSON.stringify({
    type: "response.create",
    response: { modalities: ["text"], instructions: "Tell me a joke" },
  }),
);
```

### Google AI Studio

```javascript
const ws = new WebSocket(
  "wss://gateway.ai.cloudflare.com/v1/<account_id>/<gateway>/google?api_key=<google_api_key>",
  ["cf-aig-authorization.<cloudflare_token>"],
);


ws.on("open", () => console.log("Connected to server."));
ws.on("message", (message) => console.log(message.data));


ws.send(
  JSON.stringify({
    setup: {
      model: "models/gemini-2.5-flash",
      generationConfig: { responseModalities: ["TEXT"] },
    },
  }),
);
```

### Cartesia

```javascript
const ws = new WebSocket(
  "wss://gateway.ai.cloudflare.com/v1/<account_id>/<gateway>/cartesia?cartesia_version=2024-06-10&api_key=<cartesia_api_key>",
  ["cf-aig-authorization.<cloudflare_token>"],
);


ws.on("open", function open() {
  console.log("Connected to server.");
});


ws.on("message", function incoming(message) {
  console.log(message.data);
});


ws.send(
  JSON.stringify({
    model_id: "sonic",
    transcript: "Hello, world! I'm generating audio on ",
    voice: { mode: "id", id: "a0e99841-438c-4a64-b679-ae501e7d6091" },
    language: "en",
    context_id: "happy-monkeys-fly",
    output_format: {
      container: "raw",
      encoding: "pcm_s16le",
      sample_rate: 8000,
    },
    add_timestamps: true,
    continue: true,
  }),
);
```

### ElevenLabs

```javascript
const ws = new WebSocket(
  "wss://gateway.ai.cloudflare.com/v1/<account_id>/<gateway>/elevenlabs?agent_id=<elevenlabs_agent_id>",
  [
    "xi-api-key.<elevenlabs_api_key>",
    "cf-aig-authorization.<cloudflare_token>",
  ],
);


ws.on("open", function open() {
  console.log("Connected to server.");
});


ws.on("message", function incoming(message) {
  console.log(message.data);
});


ws.send(
  JSON.stringify({
    text: "This is a sample text ",
    voice_settings: { stability: 0.8, similarity_boost: 0.8 },
    generation_config: { chunk_length_schedule: [120, 160, 250, 290] },
  }),
);
```

### Fal AI

Fal AI supports WebSocket connections for real-time model interactions through their HTTP over WebSocket API.

```javascript
const ws = new WebSocket(
  "wss://gateway.ai.cloudflare.com/v1/<account_id>/<gateway>/fal/fal-ai/fast-lcm-diffusion",
  ["fal-api-key.<fal_api_key>", "cf-aig-authorization.<cloudflare_token>"],
);


ws.on("open", function open() {
  console.log("Connected to server.");
});


ws.on("message", function incoming(message) {
  console.log(message.data);
});


ws.send(
  JSON.stringify({
    prompt: "generate an image of a cat flying an aeroplane",
  }),
);
```

For more information on Fal AI's WebSocket API, see their [HTTP over WebSocket documentation](https://docs.fal.ai/model-apis/model-endpoints/websockets).

### Deepgram (Workers AI)

Workers AI provides Deepgram models for real-time speech-to-text (STT) and text-to-speech (TTS) capabilities through WebSocket connections.

#### Speech-to-Text (STT)

Workers AI supports two Deepgram STT models: `@cf/deepgram/nova-3` and `@cf/deepgram/flux`. The following example demonstrates real-time audio transcription from a microphone:

```javascript
import WebSocket from "ws";
import mic from "mic";


const ws = new WebSocket(
  "wss://gateway.ai.cloudflare.com/v1/<account_id>/<gateway>/workers-ai?model=@cf/deepgram/nova-3&encoding=linear16&sample_rate=16000&interim_results=true",
  {
    headers: {
      "cf-aig-authorization": process.env.CLOUDFLARE_API_KEY,
    },
  },
);


// Configure microphone
const micInstance = mic({
  rate: "16000",
  channels: "1",
  debug: false,
  exitOnSilence: 6,
});


const micInputStream = micInstance.getAudioStream();


micInputStream.on("data", (data) => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(data);
  }
});


micInputStream.on("error", (error) => {
  console.error("Microphone error:", error);
});


ws.onopen = () => {
  console.log("Connected to WebSocket");
  console.log("Starting microphone...");
  micInstance.start();
};


ws.onmessage = (event) => {
  try {
    const parse = JSON.parse(event.data);
    if (parse.channel?.alternatives?.[0]?.transcript) {
      if (parse.is_final) {
        console.log(
          "Final transcript:",
          parse.channel.alternatives[0].transcript,
        );
      } else {
        console.log(
          "Interim transcript:",
          parse.channel.alternatives[0].transcript,
        );
      }
    }
  } catch (error) {
    console.error("Error parsing message:", error);
  }
};


ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};


ws.onclose = () => {
  console.log("WebSocket closed");
  micInstance.stop();
};
```

#### Text-to-Speech (TTS)

Workers AI supports the Deepgram `@cf/deepgram/aura-1` model for TTS. The following example demonstrates converting text input to audio:

```javascript
import WebSocket from "ws";
import readline from "readline";
import Speaker from "speaker";


const ws = new WebSocket(
  "wss://gateway.ai.cloudflare.com/v1/<account_id>/<gateway>/workers-ai?model=@cf/deepgram/aura-1",
  {
    headers: {
      "cf-aig-authorization": process.env.CLOUDFLARE_API_KEY,
    },
  },
);


// Speaker management
let currentSpeaker = null;
let isPlayingAudio = false;


// Setup readline for text input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: "Enter text to speak (or \"quit\" to exit): ",
});


ws.onopen = () => {
  console.log("Connected to Deepgram TTS WebSocket");
  rl.prompt();
};


ws.onmessage = (event) => {
  // Check if message is JSON (metadata, flushed, etc.) or raw audio
  if (event.data instanceof Buffer || event.data instanceof ArrayBuffer) {
    // Raw audio data - create new speaker if needed
    if (!currentSpeaker) {
      currentSpeaker = new Speaker({
        channels: 1,
        bitDepth: 16,
        sampleRate: 24000,
      });
      isPlayingAudio = true;
    }
    currentSpeaker.write(Buffer.from(event.data));
  } else {
    try {
      const message = JSON.parse(event.data);
      switch (message.type) {
        case "Metadata":
          console.log("Model info:", message.model_name, message.model_version);
          break;
        case "Flushed":
          console.log("Audio complete");
          // End speaker after flush to prevent buffer underflow
          if (currentSpeaker && isPlayingAudio) {
            currentSpeaker.end();
            currentSpeaker = null;
            isPlayingAudio = false;
          }
          rl.prompt();
          break;
        case "Cleared":
          console.log("Audio cleared, sequence:", message.sequence_id);
          break;
        case "Warning":
          console.warn("Warning:", message.description);
          break;
      }
    } catch (error) {
      // Not JSON, might be raw audio as string
      if (!currentSpeaker) {
        currentSpeaker = new Speaker({
          channels: 1,
          bitDepth: 16,
          sampleRate: 24000,
        });
        isPlayingAudio = true;
      }
      currentSpeaker.write(Buffer.from(event.data));
    }
  }
};


ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};


ws.onclose = () => {
  console.log("WebSocket closed");
  if (currentSpeaker) {
    currentSpeaker.end();
  }
  rl.close();
  process.exit(0);
};


// Handle user input
rl.on("line", (input) => {
  const text = input.trim();


  if (text.toLowerCase() === "quit") {
    // Send Close message
    ws.send(JSON.stringify({ type: "Close" }));
    ws.close();
    return;
  }


  if (text.length > 0) {
    // Send text to TTS
    ws.send(
      JSON.stringify({
        type: "Speak",
        text: text,
      }),
    );


    // Flush to get audio immediately
    ws.send(JSON.stringify({ type: "Flush" }));
    console.log("Flushing audio");
  }


  rl.prompt();
});


rl.on("close", () => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.close();
  }
});
```
