# Council of Chuckles Submission Steps

Follow these steps in order. The app has already been locally smoke-tested in fallback mode.

## 0. Run The Preflight Check

Before every push or Space update, run:

```powershell
python scripts/preflight.py
```

It checks required files, README metadata, Build Small tags, ZeroGPU hooks, and fallback generation.

## 1. Commit The Local Repo

Open PowerShell:

```powershell
cd "\\tib.tibub.de\DFS0\Home\DSouzaJ\Documents\council-of-chuckles"
git config --global --add safe.directory "//tib.tibub.de/DFS0/Home/DSouzaJ/Documents/council-of-chuckles"
git config user.name "YOUR NAME"
git config user.email "YOUR GITHUB EMAIL"
git commit -m "Prepare Council of Chuckles for Build Small submission" -m "Built with help from OpenAI Codex."
```

Use the email shown in your GitHub email settings. A GitHub `noreply` email is fine.

## 2. Push To GitHub

Create a new empty GitHub repository named `council-of-chuckles`.

Do not add a README, license, or `.gitignore` on GitHub because this folder already has them.

Then run:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/council-of-chuckles.git
git push -u origin main
```

## 3. Prepare Hugging Face Model Access

Log in to Hugging Face with the account that will own the Space.

Accept the access terms for:

- `CohereLabs/tiny-aya-water`
- `CohereLabs/cohere-transcribe-03-2026`

Create a Hugging Face access token with read access. You may need it as the Space secret `HF_TOKEN` so the Space can download gated model files.

## 4. Create The Hugging Face Space

Create the Space inside the official Build Small organization if the hackathon instructions give you access there.

Use:

- Space name: `council-of-chuckles`
- SDK: Gradio
- Hardware: ZeroGPU
- App file: `app.py`
- Python: `3.10.13`

Push the same files to the Space repo. If you connected GitHub sync, use that; otherwise clone the Space repo and copy/push the files.

### Two Ways To Get Files Into The Space

Use whichever path Hugging Face offers you.

Path A: GitHub sync

1. Connect the GitHub repo to the Space from the Space settings.
2. Make sure the synced branch is `main`.
3. Wait for the Space build logs to start.

Path B: direct Space git push

After creating the Space, Hugging Face will show a git URL like:

```text
https://huggingface.co/spaces/ORG_OR_USERNAME/council-of-chuckles
```

Add it as a second remote:

```powershell
git remote add space https://huggingface.co/spaces/ORG_OR_USERNAME/council-of-chuckles
git push space main
```

If Hugging Face asks for credentials, use your Hugging Face username and an access token as the password.

If the Space was initialized with files already, use:

```powershell
git pull space main --allow-unrelated-histories
git push space main
```

If Git opens an editor during the pull, save and close it to accept the merge commit.

## 5. Set Space Secrets And Variables

In the Space settings, add this secret if model downloads fail:

```text
HF_TOKEN=your_hugging_face_read_token
```

Set or keep these variables:

```text
TEXT_MODEL_ID=CohereLabs/tiny-aya-water
ASR_MODEL_ID=CohereLabs/cohere-transcribe-03-2026
ENABLE_VOICE_INPUT=true
TTS_MODEL_ID=openbmb/VoxCPM2
ENABLE_TTS=false
ENABLE_ENGLISH_FALLBACK_MODEL=false
ENGLISH_FALLBACK_MODEL_ID=openbmb/MiniCPM5-1B
```

Keep TTS off for the first judged build. Turn it on only after text and voice input are stable.

## 6. Test The Space

First test without the model checkbox:

1. Type: `I am afraid to submit my paper because it might not be good enough.`
2. Keep `Use local model when available` unchecked.
3. Click `Generate Council`.
4. Confirm the Council Engine, Campfire dialogue, and verdict appear.

Then test model mode:

1. Check `Use local model when available`.
2. Click `Generate Council`.
3. If the Space asks for GPU queue time, wait.
4. If it falls back, check the Space logs for model access, dependency, or memory errors.

Then test voice input.

### Reading Space Logs

Open the Space, then go to `Logs`.

Common first-build issues:

- Model access error: accept the Cohere model terms and add `HF_TOKEN`.
- Package install error: check `requirements.txt`.
- GPU queue delay: wait and try a shorter prompt.
- Out-of-memory or timeout: keep TTS off and use text mode first.
- App loads but model falls back: the demo is still usable, but check logs before final judging.

The fallback path is intentional. It proves the interface and Council Engine even when model quota or access is temporarily unavailable.

## 7. Record The Demo

Record a 60-90 second demo showing:

- the app loading
- advisor selection or Balanced Council
- one typed or spoken question
- Council Engine panel
- generated Campfire Council output
- final verdict
- the under-32B model explanation in the README or footer

Judges need the video even if live GPU quota is exhausted.

## 8. Post Social Proof

Post a short demo clip or screenshot on your chosen social platform.

Include:

- the app name
- the Hugging Face Space link
- `#BuildSmall`
- `#Gradio`
- `#HuggingFace`

Then replace the `Social post` placeholder in `README.md` with the final URL and push that update.

## 9. Final README Checklist

Before submitting, make sure `README.md` has:

- Build Small tags in the YAML block
- `thousand-token-wood`
- model names and parameter counts
- GitHub repo link
- live Space link
- demo video link
- social post link
- short explanation of ZeroGPU and fallback behavior

Also fix the YAML emoji line if it still appears corrupted in the GitHub/Hugging Face preview.

## 10. Build Small Requirement Map

Use this as the final audit before you submit:

| Rule | Evidence in this project | Still to do |
| --- | --- | --- |
| REQ-01: stay under 32B | `README.md` lists Tiny Aya Water 3.35B, Cohere Transcribe 2B, VoxCPM2 2B, and MiniCPM5-1B ~1.08B | Confirm live Space uses these model IDs |
| REQ-02: ship a Gradio app | `app.py`, `requirements.txt`, and README front matter use Gradio | Deploy inside the official Build Small Hugging Face org |
| REQ-03: record a demo | Demo script is in `README.md` | Record and link the final video |
| REQ-04: post it | `README.md` has a Social post placeholder | Publish the social post and replace the placeholder |
| REQ-05: mind the ZeroGPU limit | This is one ZeroGPU-targeted app | Keep your total ZeroGPU submissions at 10 or fewer |
| REQ-06: tag your README | YAML tags include `build-small`, `thousand-token-wood`, `gradio`, and `zerogpu` | Add/remove badge tags only if you intentionally target them |

For the OpenAI sponsor prize, keep the GitHub repo or Space connected to commits authored by `OpenAI Codex <codex@openai.com>`.
