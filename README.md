# Block Dessa Voice AI: Architecture, Model Comparison & Full-Duplex Analysis Tools

[![DessaVoice: listen to the Dessa recordings and try live voice AI](https://img.shields.io/badge/DessaVoice-Listen_%26_try_live_voice_AI-FF4500?style=for-the-badge)](https://dessavoiceai.org/?utm_source=github&utm_medium=readme_badge&utm_campaign=block_dessa_repo)
[![Source: block.xyz/dessa](https://img.shields.io/badge/Source-block.xyz%2Fdessa-000000?style=for-the-badge)](https://block.xyz/dessa)
[![License: MIT](https://img.shields.io/badge/License-MIT-0071E3?style=for-the-badge)](./LICENSE)

> **Unofficial community resource. Not affiliated with, endorsed by, or connected to Block, Inc.**
> Block's Dessa model is a research preview with a waitlist at [block.xyz/dessa](https://block.xyz/dessa). Its weights, API and local runtime have not been released, and it is not available through this repository or through DessaVoice.

This repository collects what Block has published about **Dessa**, compares it with other conversational voice models using only published sources, and provides open-source Python tools for measuring turn-taking and overlap in your own two-track conversation recordings.

To hear Block's six official recordings with synchronized two-track waveforms, check whether your Mac meets Block's M4 Max baseline, or talk to a live voice AI in your browser, visit **[DessaVoice (dessavoiceai.org)](https://dessavoiceai.org/?utm_source=github&utm_medium=top_callout&utm_campaign=block_dessa_repo)**.

---

## 1. What is Block Dessa?

Dessa is a full-duplex speech model from a small AI research lab at Block, released as a research preview. According to [Block's official page](https://block.xyz/dessa):

- **Zero text:** trained from scratch on nothing but human conversation audio, with no text and no pretrained models. Audio in, audio out.
- **Full-duplex:** listens and talks at the same time, cuts in, and backchannels with "yeah!" or "got it!".
- **Paralinguistics:** hears and produces emotion, sarcasm, laughter and sighs. Asked to speak up, it gets louder.
- **Compute:** trained on a single NVIDIA GB200 NVL72.
- **Local inference:** runs faster than real time on a MacBook Pro with an M4 Max chip or better.

The model shares its name with Dessa, the Toronto deep learning startup that Square (now Block) acquired in 2020; the lab behind the model was founded by former members of that startup.

### Cascaded pipeline vs. Dessa

```text
Cascaded voice assistant:  speech → ASR → text LLM → TTS → audio   (turn-based; tone is lost in text)
Block Dessa:               raw audio → Dessa (no text) → expressive audio   (full-duplex)
```

---

## 2. Dessa vs. Sesame CSM vs. OpenAI GPT-Live-1 vs. Kyutai Moshi

Based only on what each lab has published, as of November 2026. Machine-readable version: [`data/model_comparison.json`](./data/model_comparison.json). "Not disclosed" means the lab has not documented it publicly. Latency is omitted on purpose: no lab publishes independently measured numbers that can be compared fairly.

| Feature | **Block Dessa** | **Sesame AI (CSM)** | **OpenAI GPT-Live-1** | **Kyutai Moshi** |
| :--- | :--- | :--- | :--- | :--- |
| **Core architecture** | End-to-end speech-to-speech; no text [1] | Llama backbone plus audio decoder; speech from text and context [2] | Full-duplex voice model; delegates reasoning to a backend model [4] | Speech-text model: 7B Temporal Transformer, Depth Transformer, Mimi codec [6] |
| **Training data** | Only human conversation audio [1] | ~1M hours of transcribed public audio, mostly English [2] | Not disclosed | Helium text LLM init; 7M audio hours; Fisher; synthetic dialogues [6] |
| **Full-duplex & backchannels** | Yes [1] | Not in CSM; listed as future work [2] | Yes [4] | Yes: parallel user and model streams [6] |
| **Local / open weights** | Runs on MacBook Pro M4 Max or better; weights not released [1] | CSM-1B base, Apache 2.0 [3] | Hosted API only [4] | Open weights (CC-BY 4.0); MLX version for Mac [7] |
| **Availability** | Research preview; waitlist [1] | Research preview app; CSM-1B on GitHub [3] | OpenAI API since Sep 10, 2026; $0.05/min [5] | GitHub, Hugging Face; demo at moshi.chat [7] |

Sources: [1] [Block — Dessa](https://block.xyz/dessa) · [2] [Sesame — Crossing the uncanny valley of conversational voice](https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice) · [3] [Sesame — CSM on GitHub](https://github.com/SesameAILabs/csm) · [4] [OpenAI — GPT-Live 1 model page](https://developers.openai.com/api/docs/models/gpt-live-1) · [5] [OpenAI — Introducing GPT-Live-1 in the API](https://openai.com/index/introducing-gpt-live-1-in-the-api/) · [6] [Kyutai — Moshi paper (arXiv 2410.00037)](https://arxiv.org/abs/2410.00037) · [7] [Kyutai — Moshi on GitHub](https://github.com/kyutai-labs/moshi)

An interactive version of this table is on [dessavoiceai.org](https://dessavoiceai.org/?utm_source=github&utm_medium=comparison#comparison).

---

## 3. The six official Dessa recordings

Block published six live two-track recordings on [block.xyz/dessa](https://block.xyz/dessa). They are **not** redistributed here; all rights belong to Block, Inc. Listen to the full recordings on Block's page, or to annotated excerpts with person/Dessa waveform lanes on DessaVoice:

| Recording | What to listen for | Annotated excerpt |
| :--- | :--- | :--- |
| Talking about the release | Laughs mid-sentence; gets louder when asked to speak up | [Listen](https://dessavoiceai.org/?utm_source=github&utm_medium=samples#demo-ai-release) |
| Remembering a movie | The person blanks on a title; Dessa finishes the sentence | [Listen](https://dessavoiceai.org/?utm_source=github&utm_medium=samples#demo-dc-comics) |
| An anniversary surprise | A gasped "oh my god", then teary-sounding gratitude | [Listen](https://dessavoiceai.org/?utm_source=github&utm_medium=samples#demo-anniversary) |
| Expressive conversation | Wide range of intonation and speed | [Listen](https://dessavoiceai.org/?utm_source=github&utm_medium=samples#demo-coffee-ding) |
| Life advice | An empathetic tone | [Listen](https://dessavoiceai.org/?utm_source=github&utm_medium=samples#demo-life-advice) |
| Dessa in conversation with GPT-Live-1 | Two AI voices; Dessa backchannels while GPT-Live-1 is still talking | [Listen](https://dessavoiceai.org/?utm_source=github&utm_medium=samples#demo-gpt-live-1) |

In the GPT-Live-1 recording both voices are AI-generated; OpenAI is not affiliated with Block and has not reviewed or endorsed Dessa.

---

## 4. Measure turn-taking in your own recordings

[`scripts/analyze_duplex_latency.py`](./scripts/analyze_duplex_latency.py) analyzes a **stereo recording with one speaker per channel** (left = person, right = AI by default) and reports:

- **Overlap ratio (%)**: share of active speech time where both speakers talk at once.
- **Turn-taking gaps (ms)**: median and 90th percentile from one speaker ending a turn to the other starting. Negative values mean the second speaker started before the first finished.
- **Level range (dB)**: per speaker, 95th minus 10th percentile of active-frame levels in dBFS.

Anything that cannot be measured is reported as `null`; nothing is estimated or filled in.

```bash
git clone https://github.com/parlayofficial001-creator/block-dessa-voice-ai.git
cd block-dessa-voice-ai
pip install -r requirements.txt

python scripts/analyze_duplex_latency.py my_call.wav
python scripts/analyze_duplex_latency.py a.wav b.wav --threshold-db -45 --min-pause 0.3
```

Example: a synthetic 6-second test file where the AI answers 300 ms and 500 ms after the person stops, the person barges in 200 ms before the AI finishes, and the AI's last reply rises from 0.1 to 0.4 amplitude (≈12 dB). Measurements use 10 ms frames, so expect ±10–20 ms of quantization.

```json
{
  "file": "my_call.wav",
  "sample_rate": 16000,
  "duration_sec": 6.0,
  "threshold_dbfs": -40.0,
  "overlap_ratio_pct": 4.64,
  "person_to_ai_gap": { "count": 2, "median_ms": 390.0, "p90_ms": 470.0 },
  "ai_to_person_gap": { "count": 1, "median_ms": -210.0, "p90_ms": -210.0 },
  "person_level_range_db": 0.0,
  "ai_level_range_db": 12.11
}
```

Render a two-lane waveform (person blue, AI red) as PNG and MP4 with ffmpeg:

```bash
scripts/generate_waveforms.sh my_call.wav   # → assets/waveforms/my_call.{png,mp4}
```

Only process recordings you have the right to use. Audio and renders are gitignored.

---

## 5. FAQ

<details>
<summary><b>Is Block's Dessa open source or available to download?</b></summary>
<br>
No. Dessa is a research preview with a waitlist at <a href="https://block.xyz/dessa">block.xyz/dessa</a>. Block has not published weights, an API or a local runtime.
</details>

<details>
<summary><b>Can I run Dessa locally on a MacBook Pro M4 Max?</b></summary>
<br>
Block says Dessa runs faster than real time on a MacBook Pro M4 Max or better, but there is nothing to download yet. <a href="https://dessavoiceai.org/?utm_source=github&utm_medium=faq#hardware-checker">DessaVoice's free hardware checker</a> shows how your Mac compares with that baseline.
</details>

<details>
<summary><b>How is Dessa different from Kyutai Moshi?</b></summary>
<br>
Moshi is initialized from Helium, a 7B text language model, and predicts a text "inner monologue" alongside its audio tokens. Block says Dessa uses no text and no pretrained models at all.
</details>

<details>
<summary><b>Is DessaVoice the official Dessa website?</b></summary>
<br>
No. <a href="https://dessavoiceai.org/?utm_source=github&utm_medium=faq">DessaVoice</a> is an independent site that breaks down Block's published recordings and offers its own live voice AI. Its live calls run on a hosted real-time pipeline (speech recognition, a language model and speech synthesis), and a free bring-your-own-key mode uses OpenAI Realtime with your own API key. Neither runs Block's Dessa model.
</details>

---

## Links

- **DessaVoice — recordings, hardware checker and live voice AI:** [dessavoiceai.org](https://dessavoiceai.org/?utm_source=github&utm_medium=footer&utm_campaign=block_dessa_repo)
- **Block's official Dessa page:** [block.xyz/dessa](https://block.xyz/dessa)

Dessa and Block are trademarks of Block, Inc. They are used here only to identify the model being discussed.
