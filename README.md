---
title: Council of Chuckles
emoji: "🎭"
colorFrom: purple
colorTo: yellow
sdk: gradio
python_version: 3.10.13
app_file: app.py
short_description: Tiny AI advisors with jokes.
fullWidth: true
pinned: false
models:
  - CohereLabs/tiny-aya-water
  - openai/whisper-small
  - openbmb/VoxCPM2
  - openbmb/MiniCPM5-1B
tags:
  - build-small
  - thousand-token-wood
  - gradio
  - small-models
  - tiny-titan
  - off-brand
  - best-demo
  - best-agent
  - best-use-of-codex
  - bonus-quest-champion
  - multilingual
  - voice
  - codex
  - cohere
  - tiny-aya
  - openbmb
  - voxcpm
  - whimsical
  - local-ai
  - zerogpu
  - council-engine
---

# Council of Chuckles

**Assemble your Mastermind Alliance. Ask a serious question. Receive wisdom with a wink.**

Council of Chuckles is a whimsical Gradio app for the Hugging Face x Gradio Build Small Hackathon. Users select a personal council from `data/advisors.json`, ask a question by text or optional voice input, and receive practical, compassionate advice staged as advisor cards or a short Campfire Council dialogue.

## Submission Links

- Live Space: add the final Hugging Face Space URL after deployment
- GitHub repo: https://github.com/jd-coderepos/council-of-chuckles
- Demo video: add the demo video URL after recording
- Social post: add the required social-media post URL before final submission

## Why It Fits Thousand Token Wood

The app is a tiny AI council chamber: part multilingual companion, part small-model theater, part practical perspective tool. It targets the Thousand Token Wood track by making AI load-bearing for an original, playful experience that would not make sense as a static form or ordinary chatbot.

## More Than A Prompt Wrapper

Council of Chuckles is not just a prompt wrapper. A lightweight programmed Council Engine runs before generation. It detects the user's themes, emotions, and needs; matches advisors using profile metadata; balances archetypes; plans dialogue turns; and only then asks the small language model to perform the scene. This keeps the app playful, explainable, and reliable even when fallback mode is active.

## Built With Codex

This submission was developed with help from OpenAI Codex. The connected Git history includes Codex-attributed commits for the application, ZeroGPU preparation, and submission preflight tooling.

## The Council Engine

Pipeline:

```text
User input
-> safety router
-> topic / emotion / need analyzer
-> advisor matching engine
-> archetype balancing
-> active speaker selection
-> dialogue planner
-> prompt builder
-> LLM generation or fallback generation
-> verdict builder
-> optional TTS
```

The app displays the engine panel before output so users can see detected themes, emotions, needs, active archetypes, triggered advisors, and the speaker strategy.

## Models Used And Parameter Counts

| Component | Model | Parameters | Default? | Purpose |
| --- | ---: | ---: | --- | --- |
| Multilingual text generation | `CohereLabs/tiny-aya-water` | 3.35B | Yes | Generates advisor responses in 70+ languages |
| Speech recognition | `openai/whisper-small` | 244M | Yes, if voice enabled | Transcribes voice input in 15 curated Whisper languages |
| Speech output | `openbmb/VoxCPM2` | 2B | Optional/off by default | Speaks the final verdict or advisor replies |
| English fallback | `openbmb/MiniCPM5-1B` | ~1.08B | Optional/off by default | Lightweight English fallback |
| Template fallback | none | 0B | Always available | Keeps app usable if models fail |

Default multilingual text-only stack: **3.35B**.

Default multilingual voice-input stack: **3.594B**.

Optional full voice-in/voice-out stack: **5.594B**.

All configurations are below the 32B hackathon cap. The ASR model itself stays well below 3B.

## Multilingual Support

Council of Chuckles supports multilingual interaction at two levels. In text mode, the app uses Tiny Aya Water for multilingual text generation across 70+ languages. In voice mode, spoken input is transcribed with the multilingual `openai/whisper-small` model. The app intentionally exposes a curated spoken-language list instead of Whisper's full tokenizer list, because the smallest Whisper models can be uneven across languages and the UI should not overpromise. The transcribed text can then be answered in the same language or in a different selected output language.

Curated Whisper voice input languages in the app: English, German, Hindi, French, Spanish, Italian, Portuguese, Dutch, Polish, Greek, Arabic, Vietnamese, Mandarin Chinese, Japanese, and Korean. Whisper supports additional language tokens; this app keeps the selector smaller to match the reliability target for the demo. Source: [OpenAI Whisper README](https://github.com/openai/whisper).

If the model cannot load, template fallback remains available. Fallback mode is English-only and clearly labels requested non-English outputs.

## Voice Input Support

Voice input is optional and lazy-loaded. The app provides a separate spoken-language selector, transcribes audio into an editable textbox, and waits for the user to click **Use transcript as question** before generation.

If ASR fails, the app remains usable in text mode and displays: "Voice input is currently wandering in the woods. Please type your question instead."

## Optional Voice Output

TTS uses `openbmb/VoxCPM2` and is disabled by default for deployment reliability. The UI includes options to speak the final verdict, advisor cards, or Campfire Council turns. If TTS is unavailable, written output remains the source of truth.

## Council Selection Model

Users can build a large Mastermind Alliance from the advisor dataset. Each session invites only 3 to 7 active speakers, defaulting to 5, so the result stays fast and readable.

Speaker strategies:

- Surprise me
- Match to my topic
- Manual selection
- Balanced Council

Demo-friendly mode caps active speakers at 5 and Campfire turns at 6.

## Session And Continuation Model

The app stores session memory only in Gradio state during the active browser session. Users can export the session as Markdown. No conversations, transcripts, or audio are permanently stored by this app.

## Campfire Council Mode

Campfire Council Mode turns active advisors into a short scripted dialogue. The Council Engine plans the turn order and assigns functions such as validate, reframe, gentle disagreement, comic relief, practical action, synthesize, challenge, and tiny next step.

## Advisor Avatars

Advisor portraits are optional local assets. If an advisor has an `avatar` path in `data/advisors.json`, the app displays it. If not, the app falls back to polished initials and archetype/category styling. This keeps the app professional even before all 100 portraits are curated.

## Features

- Advisor gallery with search, category filter, selection state, and active speaker chips
- Deterministic Council Engine with transparent analysis
- Mastermind Mode, Comic Relief Mode, Council Mode, and Campfire Council Mode
- Safety routing for crisis, harmful humor, and high-stakes professional advice
- Lazy model loading and always-available fallback generation
- Optional ASR and TTS
- Session export as Markdown

## How To Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

To avoid downloading models during local UI testing, leave **Use local model when available** unchecked in the app.

## How To Deploy On Hugging Face Spaces / ZeroGPU

Create a Gradio Space, upload the repository, and keep `app.py` as the app file. Models are lazy-loaded, so the Space can render the UI before any generation model is loaded.

ZeroGPU deployment notes:

- Select ZeroGPU hardware in the Space settings.
- Accept the access terms for the Tiny Aya Water model page from the Hugging Face account that owns the Space.
- Add an `HF_TOKEN` Space secret if the Space needs authenticated model downloads for gated text models.
- Keep `ENABLE_TTS=false` for the first stable build, then enable optional voice output only after text and ASR are working.

Useful environment variables:

```bash
TEXT_MODEL_ID=CohereLabs/tiny-aya-water
ASR_MODEL_ID=openai/whisper-small
ENABLE_VOICE_INPUT=true
TTS_MODEL_ID=openbmb/VoxCPM2
ENABLE_TTS=false
ENABLE_ENGLISH_FALLBACK_MODEL=false
ENGLISH_FALLBACK_MODEL_ID=openbmb/MiniCPM5-1B
```

## Safety And Humor Policy

The app never claims generated outputs are real quotes. Every persona response is framed as inspired by a public persona or set of ideas.

If the user mentions self-harm, suicidal ideation, abuse, immediate danger, overdose, domestic violence, or crisis, the app stops humor and personas and returns a direct supportive response.

For medical, legal, financial, immigration, tax, investment, or other high-stakes professional topics, the app includes: "This is not professional advice."

If the user asks for cruel, hateful, discriminatory, or demeaning humor, the app refuses the harmful part and offers a safer playful alternative.

## Demo Script

Primary 60-90 second flow:

1. Open the app.
2. Choose input mode: Voice.
3. Choose spoken language: German.
4. Speak: "Ich habe Angst, mein Paper einzureichen, weil es vielleicht nicht gut genug ist."
5. Show the editable transcript.
6. Choose council reply language: German.
7. Click **Balanced Council**.
8. Choose **Campfire Council Mode**.
9. Mood: **Academic panic room**.
10. Dialogue turns: 6.
11. Humor intensity: 3.
12. Compassion: 5.
13. Generate the council.
14. Show the Council Engine panel.
15. Show the Campfire Council dialogue.
16. Show **The Gavel Falls** verdict.
17. If TTS is enabled, click **Speak final verdict**.
18. Ask a follow-up: "Was soll ich in den nachsten zehn Minuten tun?"
19. Show the short follow-up response.
20. Show **Export Session as Markdown**.

English text-mode demo:

```text
I am afraid to submit my paper because it might not be good enough.
```

## Badges / Categories Targeted

This app targets the following Build Small track, sponsor prize, and bonus badges. These are categories targeted, not awards claimed.

| Target | Why Council of Chuckles fits |
| --- | --- |
| Thousand Token Wood | Whimsical, AI-native council theater built around small-model generation, voice input, and playful advisor personas. |
| Tiny Titan | The default and optional models listed above are each under 4B parameters, with Tiny Aya Water at 3.35B and Whisper small at 244M. |
| Off Brand | The app uses a custom illustrated hero, themed panels, advisor chips, and a styled Council Stage instead of stock Gradio presentation. |
| Best Agent | The Council Engine performs multi-step routing, theme/emotion/need analysis, advisor matching, archetype balancing, speaker planning, and verdict synthesis before generation. |
| Best Demo | The README includes a 60-90 second demo script designed to show voice input, council assembly, model output, safety/fallback behavior, and export. Final eligibility depends on adding the recorded demo and social post links. |
| Best Use of Codex | The project was developed with OpenAI Codex, and the connected GitHub/Space history includes Codex-authored work. |
| Bonus Quest Champion | The build intentionally combines several target criteria: tiny models, custom UI, agentic planning, demo readiness, Codex use, ZeroGPU deployment, and a whimsical track fit. |
| Judges' Wildcard | No special entry is required; the field guide says every submission is automatically in the running. |

## Data File Format

The app loads advisors from `data/advisors.json`. Required fields are `id`, `name`, and `category`. Optional fields include `era`, `role`, `core_wisdom`, `signature_style`, `mastermind_voice`, `comic_voice`, `catchphrase`, `best_for`, `avoid`, `avatar`, and `avatar_alt`.

Legacy `jokester_voice` is supported and normalized to `comic_voice`.
