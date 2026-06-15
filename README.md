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
tags:
  - build-small
  - track:wood
  - sponsor:openai
  - achievement:offgrid
  - achievement:offbrand
  - achievement:sharing
  - achievement:fieldnotes
  - thousand-token-wood
  - gradio
  - small-models
  - multilingual
  - voice-input
  - zerogpu
  - tiny-aya
---

# Council of Chuckles

## **🎭 Assemble a tiny council. Bring a messy moment. Receive wisdom with a wink.**

Council of Chuckles is a whimsical Gradio app built for the Hugging Face × Gradio Build Small Hackathon. It lets users summon a custom council from 100 historical and literary-inspired advisors, ask a question about a tricky or annoying situation by typing in their own language or speaking it aloud, and receive a staged response as advisor cards or a short Campfire Council dialogue.

*The twist:* these great thinkers are not here to give solemn advice. They bring their logic, worldview, and signature wisdom — but must deliver it playfully, like tiny-model philosophers who wandered into a comedy tent.

This submission targets the **Thousand Token Wood** track: playful, AI-native, and powered by small local/open-weight models. Users can type across Tiny Aya’s broad multilingual range via [CohereLabs/tiny-aya-water](https://huggingface.co/CohereLabs/tiny-aya-water), or speak a question through feather-light [openai/whisper-small](https://huggingface.co/openai/whisper-small), making the council multilingual in both text and voice input. Because sometimes our messy moments feel lighter when we can ask — and be answered — in the language closest to us: English, German, Spanish, French, Hindi, Arabic, Tamil, Chinese, Japanese, Swahili, and more.

## Submission Links

- Live Space: https://huggingface.co/spaces/build-small-hackathon/council-of-chuckles
- GitHub repo: https://github.com/jd-coderepos/council-of-chuckles
- Demo video: TODO: add final demo URL
- Social post: TODO: add final social-media post URL
- Field notes: 
- Agent traces: 

## Demo Script

A concise demo flow:

1. Open the [Council of Chuckles Space](https://huggingface.co/spaces/build-small-hackathon/council-of-chuckles).
2. **Panel 1:** Ask a question by typing it, or record a short voice input and transcribe it into the question box.
3. **Panel 2:** Select council members manually, or use the surprise-pick option. You can pick as many advisors as you like.
4. **Panel 3:** Choose **Campfire Council Mode**.
5. **Panel 3:** Keep speaker selection on **Best match to the question** so the app can choose the most relevant voices from the selected council.
6. **Panel 3:** Use 3–4 active speakers for the best council rhythm; the app can dynamically choose these from the larger council you selected — too many cooks spoil the philosophical soup. 😉
7. **Panel 3:** Generate the council response.
8. **Panel 4:** Review the Council Engine stage, active speakers, Campfire dialogue, and final verdict.
9. Export the session as Markdown.

Suggested demo questions:

**English**

```text
I am afraid to submit my paper because it might not be good enough.
```

**German**

```text
Ich habe Angst, mein Paper einzureichen, weil es vielleicht nicht gut genug ist.
```

**English**

```text
I added too much flour, my cake is a rock, and I am frustrated.
```

**French**

```text
J’ai ajouté trop de farine, mon gâteau est dur comme une pierre, et je suis frustrée.
```

**Swahili**

```text
Nimeongeza unga mwingi sana, keki yangu imekuwa kama jiwe, na nimechanganyikiwa.
```

⚠️ Note: The app does **not** claim to generate real quotes. The responses are original lines inspired by public personas, written for perspective, humor, and reflection.

## ℹ️ Main Features

* Custom illustrated [Gradio](https://www.gradio.app/) interface
* 100 advisor profiles in `data/advisors.json`
* Searchable advisor selection with category filtering
* Four response modes: Mastermind, Comic Relief, Council, and Campfire Council
* Lightweight analysis of topic, emotion, user need, and advisor archetype
* Advisor matching by best fit, balanced council composition, or random surprise
* Safety routing for crisis language, harmful humor, and high-stakes advice topics
* Lazy model loading and fallback generation for deployment reliability
* Markdown session export

### 🧠 Built-in Council Engine

Council of Chuckles is not just a prompt wrapper around a small language model. Before generation, the app runs a lightweight programmed Council Engine that routes the user’s input through several steps:

```text
User input
→ safety router
→ topic / emotion / need analysis
→ advisor matching
→ archetype balancing
→ active speaker selection
→ dialogue planning
→ prompt building
→ small-model generation or fallback generation
→ final verdict
```

The interface exposes this engine panel so users can see the detected themes, needs, selected voices, and speaker strategy before reading the council response.

🛠️ The design explores a simple idea: small models do not always need fine-tuning to produce distinctive behavior. With custom role design, dynamic prompting, message routing, and iterative refinement, a small open-weight model can support a playful multi-perspective interaction while keeping the user experience transparent.

## Models Used

| Component                    | Model                                                                           | Parameters | Used for                                                       |
| ---------------------------- | ------------------------------------------------------------------------------- | ---------: | -------------------------------------------------------------- |
| Multilingual text generation | [`CohereLabs/tiny-aya-water`](https://huggingface.co/CohereLabs/tiny-aya-water) |      3.35B | Advisor responses and council dialogue                         |
| Voice input / ASR            | [`openai/whisper-small`](https://huggingface.co/openai/whisper-small)           |       244M | Optional speech-to-text transcription                          |
| Template fallback            | none                                                                            |         0B | Keeps the app usable when model loading or ZeroGPU quota fails |

Text interaction uses [Tiny Aya Water](https://huggingface.co/CohereLabs/tiny-aya-water), a 3.35B multilingual small model trained across 70+ languages, with especially strong coverage for European and Asia-Pacific languages. In the app, this lets users type questions and receive council responses in languages such as English, German, French, Spanish, Italian, Portuguese, Polish, Greek, Hindi, Tamil, Vietnamese, Mandarin Chinese, Japanese, Korean, Swahili, Arabic, and more.

Voice input uses [Whisper small](https://huggingface.co/openai/whisper-small) with a curated spoken-language selector in the app: English, German, Hindi, French, Spanish, Italian, Portuguese, Dutch, Polish, Greek, Arabic, Vietnamese, Mandarin Chinese, Japanese, and Korean.

Voice input is optional. The written question remains editable before generation, and the app continues to work in text mode if ASR is unavailable.

## Data

Candidate council member advisor profiles are stored in `data/advisors.json`. This file is the app’s character layer: it does not simply list 100 names, but defines how each advisor should reason, speak, and safely participate in the council.

Each advisor entry includes:

* `id`, `name`, `category`, and `era` to identify and organize the advisor
* `role` and `core_wisdom` to define the advisor’s intellectual background and central perspective
* `signature_style`, `mastermind_voice`, and `jokester_voice` to guide tone across serious and playful response modes
* `catchphrase` to add memorable personality to the generated responses
* `best_for` to support advisor matching based on the user’s question
* `avoid` to provide safety and style boundaries for each persona

Together, these fields power advisor search, category filtering, speaker matching, response modes, and the app’s playful-but-grounded council behavior.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The app can be run locally after the model weights are downloaded. No external inference API is required for normal generation.

## Hugging Face Space / ZeroGPU Notes

The app is designed as a Gradio Space and uses lazy model loading so the UI can render before the text model or ASR pipeline is loaded.

Recommended Space settings:

```text
SDK: Gradio
Python: 3.10.13
App file: app.py
Hardware: ZeroGPU
```

Useful environment variables:

```text
TEXT_MODEL_ID=CohereLabs/tiny-aya-water
ASR_MODEL_ID=openai/whisper-small
ENABLE_VOICE_INPUT=true
ENABLE_ENGLISH_FALLBACK_MODEL=false
```

If model access fails on the Space, add an `HF_TOKEN` secret with read access and make sure the Space owner has accepted any required model access terms.

## 🛡️ Protective Guardrails

Council of Chuckles is designed for light reflection and playful perspective-shifting, not professional decision-making. Its routing and prompt design add caution around medical, legal, financial, immigration, tax, investment, and other high-stakes topics, keeping responses general and reminding users to seek qualified professional advice when needed.

The humor prompts are also bounded: the app is designed to avoid cruel, hateful, discriminatory, demeaning, or identity-based jokes, as well as terms that mock protected traits, personal hardship, trauma, self-harm, disability, religion, ethnicity, gender, sexuality, or nationality. When sensitive or crisis-like language appears, the prompt strategy prioritizes supportive, non-comedic wording over persona performance.

## 🙌 Acknowledgements

This project was built using [**OpenAI Codex**](https://openai.com/codex/) as a coding agent. Vibe coding with Codex supported the implementation of the [Gradio](https://www.gradio.app/) app structure, council orchestration logic, UI refinements, fallback behavior, and submission-readiness checks.

A big thank you to the **Gradio team**, especially **Yuvi**, and to all the [Build Small Hackathon](https://huggingface.co/build-small-hackathon) partners for creating such a generous playground for small-model experimentation. The hackathon resources — from Hugging Face Spaces and ZeroGPU to Codex credits and the field-guide tooling — made it possible to build, test, polish, and ship a playful local/open-weight AI app in the spirit of the jam. 🎭🚀✨

