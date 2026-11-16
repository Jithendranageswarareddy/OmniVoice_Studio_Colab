# 🎙️ Telugu AI Voice Cloner: Prosody, Emotion & Quality Roadmap
> **Living Master Tracker:** Audio Issue Diagnostics, Script Engineering Rules, and Custom Model Development Guidelines for Social Media & YouTube Content.

---

## 1. Acoustic & Prosody Audit: Current 28-Second Baseline Take

| Timestamp | Script Line | Current Delivery (Acoustic Finding) | Ideal Delivery for YouTube / Social Media | Root Cause |
| :--- | :--- | :--- | :--- | :--- |
| **0:00 – 0:02** | *మీరు ఎప్పుడైనా సూపర్ మార్కెట్కి వెళ్లారా?* | **Flat/Falling Pitch:** Sounds like a statement (*"వెళ్లారు."*). No rising intonation on question mark `?`. | **Curious Hook:** Rising pitch on *"వెళ్లారాఆ?"* with upward inflection inviting the viewer to respond mentally. | TTS tokenizer treats `?` as a boundary pause rather than pitch contour modifier. |
| **0:02 – 0:07** | *అక్కడ క్యాషియర్ దగ్గర మూడు యాపిల్స్ ఉంటే, వాటిని చూడగానే మూడు అని చెప్పగలరు.* | **Neutral/Monotone:** Clear pronunciation, but conversational energy is flat. | **Casual / Relatable:** Conversational ease, emphasizing the contrast on *"మూడు"*. | Diffusion model has equal weight across all syllables without dynamic stress markers. |
| **0:07 – 0:12** | *కానీ అదే చోట ఏడు యాపిల్స్ ఉంటే, వాటిని ఒక్కొక్కటిగా లెక్కపెట్టాల్సి రావచ్చు.* | **Even Tempo:** *"ఏడు"* is pronounced with the exact same weight as *"మూడు"*. | **Dramatic Contrast:** Vocal stress and pitch jump on *"కానీ..."* and *"ఏడు యాపిల్స్"*, followed by reflective hesitation on *"రావచ్చు"*. | Lack of punctuation contrast (e.g. ellipses `...` or exclamation marks `!`). |
| **0:12 – 0:14** | *ఎందుకిలా జరుగుతుంది?* | **Falling Tone:** Reads as a flat observation rather than an intriguing question. | **Genuine Mystery / Questioning:** Pitch rise on *"జరుగుతుందీ?"* creating tension. | TTS engine declarative default contour. |
| **0:14 – 0:17** | *మన కళ్ళు ఒకేసారి ఎన్ని వస్తువుల్ని గుర్తించగలవు?* | **Monotone:** Flat delivery of key metric *"ఎన్ని వస్తువుల్ని"*. | **Inquisitive:** Pitch peak on *"ఎన్ని"* and rising question end on *"గుర్తించగలవూ?"*. | No stress tokenization in base Telugu G2P. |
| **0:17 – 0:21** | *అసలు లెక్కపెట్టకుండానే వస్తువుల సంఖ్యను గుర్తించడం సాధ్యమేనా?* | **Flat Cadence:** Drops pitch on *"సాధ్యమేనా"*. | **Climax Challenge:** Suspenseful, engaging tone building toward the punchline. | Standard sentence splitter lacks prosodic grouping. |
| **0:21 – 0:22** | *అవును!* | **Weak Energy:** Sounds like a quiet acknowledgment. | **Punchy Resolution:** Confident, energetic, smiling delivery with exclamation punch (*"అవును!!"*). | Model requires higher guidance scale for exclamation energy. |
| **0:22 – 0:28** | *దీనికి సంబంధించిన ఒక ఆసక్తికరమైన స్కిల్ గురించి ఇప్పుడు తెలుసుకుందాం. దాని పేరు సబిటైజింగ్.* | **Continuous Readout:** Good clarity, but lacks suspense before the big reveal. | **Suspenseful Reveal:** Dramatic micro-pause (350ms) before the reveal: *"దాని పేరు... సబిటైజింగ్!"*. | Fixed 180ms pause between all chunks without dramatic pacing variation. |

---

## 2. Pillar 1: Script Engineering & Prompting Guide (Immediate Fix)

You can dramatically improve emotion, question intonation, and emphasis **today** without retraining the model by structuring your Telugu scripts with specific prosodic formatting hacks:

### A. Question Intonation Hacks for Telugu TTS
Because the neural model flattens question marks `?`, use **phonetic vowel lengthening** and **rhetorical punctuation combos**:

| Standard Script (Flat Output) | Engineered Script (Expressive Rising Pitch) | Why it Works |
| :--- | :--- | :--- |
| `మీరు ఎప్పుడైనా సూపర్ మార్కెట్కి వెళ్లారా?` | `మీరు ఎప్పుడైనా సూపర్ మార్కెట్ కి వెళ్లారాఆ?!` | Adding `ఆ?!` forces the model to synthesize a sustained rising vocal tract formant. |
| `ఎందుకిలా జరుగుతుంది?` | `అసలు... ఎందుకిలా జరుగుతుందీ??` | Ellipses `...` forces a thinking pause; `ఈ??` triggers inquisitive vocal rise. |
| `గుర్తించడం సాధ్యమేనా?` | `గుర్తించడం నిజంగా సాధ్యమేనాఆ?!` | `నిజంగా` adds natural semantic weight; `నాఆ?!` forces rising question tone. |
| `అవును!` | `అవును!! ఖచ్చితంగా!` | Double exclamation `!!` triggers higher energy and decibel peaks. |
| `దాని పేరు సబిటైజింగ్.` | `దాని పేరేంటో తెలుసా?... సబిటైజింగ్!` | Rhetorical setup creates dramatic anticipation before the reveal. |

---

### B. Master System Prompt for Script Generation AI (ChatGPT / Claude / Gemini)

Copy-paste this prompt into your script generation tool whenever generating Telugu scripts for this voice cloner:

```markdown
You are an expert Telugu YouTube / Instagram Reels Scriptwriter.
Format the script specifically for an AI Voice Cloner (TTS) to ensure high emotional dynamic range, natural conversational pauses, and expressive question intonations:

1. RISING QUESTION INFLECTION:
   - Never end a Telugu question with a bare single question mark '?'.
   - Always extend the final vowel phonetically and use '?!' or '??' (e.g., use "వెళ్లారాఆ?!" instead of "వెళ్లారా?", use "జరుగుతుందీ??" instead of "జరుగుతుంది?").
   - Include rhetorical inquiry words like "అసలు...", "నిజంగా...", "ఎప్పుడైనా...".

2. DRAMATIC PAUSES & CONTRASTS:
   - Use triple dots '...' where a human speaker would hesitate, take a breath, or build curiosity (e.g., "దాని పేరేంటో తెలుసా?... సబిటైజింగ్!").
   - Use double exclamation marks '!!' for punchy, confident words (e.g., "అవును!!", "ఖచ్చితంగా!").

3. RHYTHMIC CHUNKING:
   - Keep each sentence between 8 to 15 words so the speech engine maintains crystal-clear articulation.
   - Do not combine multiple complex ideas into run-on sentences.

Output the script in clean Telugu Unicode, ready for direct voiceover synthesis.
```

---

## 3. Pillar 2: Engine & Audio Pipeline Upgrades (Colab Studio)

The following pipeline enhancements are being integrated into `colab_server.py`:

### 1. Punctuation-Aware Guidance Scaling
* **Declarative Sentences (`.`):** Guidance scale = `1.2` (smooth, warm, natural).
* **Questions (`?`, `?!`):** Guidance scale = `1.5 – 1.6` (forces tighter alignment to phonetics, boosting pitch contour).
* **Exclamations (`!`, `!!`):** Guidance scale = `1.7` (boosts vocal projection, punch, and presence).

### 2. Adaptive Dramatic Pause Insertion
Currently, `concatenate_and_master` inserts a uniform `180ms` silence between all chunks.
* **Standard comma (`,`) pause:** `120ms` (natural breath gap).
* **Period (`.`) sentence boundary:** `220ms` (thought completion).
* **Question (`?`, `?!`) inquiry gap:** `300ms` (gives viewer time to absorb the question).
* **Ellipsis (`...`) dramatic pause:** `420ms` (builds anticipation before key reveals).

### 3. Emotion Conditioning via Reference Audio Slicing
* OmniVoice borrows the emotional timbre and pitch variance from the reference audio clip.
* **Current Reference Clip (`p_j_n_reddy_ref.wav`):** A calm, neutral explanation.
* **Future Upgrade:** Create two reference profiles:
  1. `P_J_N_Reddy_Narrator` (Calm, authoritative, storytelling).
  2. `P_J_N_Reddy_HighEnergy` (Enthusiastic, smiling, dynamic social media hook style).

---

## 4. Pillar 3: Living Issues & Improvements Backlog

| ID | Issue Description | Category | Impact | Planned Solution | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ISSUE-01** | **Question Inflection Flattening:** Sentences ending in `?` sound like flat declarative statements. | Prosody / Pitch | High | 1. Script vowel elongation (`ఆ?!`, `ఈ??`).<br>2. Punctuation-aware guidance scale modulation (`1.5x` on `?`). | 🟡 In Progress |
| **ISSUE-02** | **Monotonic Energy Across Script:** Whole take shares same vocal energy from hook to conclusion. | Emotion / Dynamic Range | High | 1. Dynamic speed ramping (`1.05x` on hook, `0.95x` on question, `1.0x` on explanation).<br>2. High-energy reference profile calibration. | 🟡 In Progress |
| **ISSUE-03** | **Uniform 180ms Pause Timing:** All pauses are identical, reducing dramatic pacing. | Audio Engine | Medium | Implement regex-based adaptive pause duration (`120ms`, `220ms`, `320ms`, `450ms`). | 🟡 In Progress |
| **ISSUE-04** | **Punch Word De-emphasis:** Words like *"అవును!"* lack excitement. | Phonetics / Gain | Medium | Dynamic gain boost (+1.5 dB) and micro-pitch shift on exclamation tokens. | ⚪ Backlog |
| **ISSUE-05** | **Custom Model Fine-Tuning Specification:** Prepare dataset for custom Telugu diffusion adapter. | Model Development | High (Future) | Record 15-minute multi-emotion Telugu speech corpus with annotated question/excitement tags for LoRA fine-tuning. | ⚪ Roadmap |

---

## 5. How to Test the Improved Script Today

Try generating the following **prosodically engineered version** in your studio:

```text
మీరు ఎప్పుడైనా సూపర్ మార్కెట్ కి వెళ్లారాఆ?!

అక్కడ క్యాషియర్ దగ్గర మూడు యాపిల్స్ ఉంటే... వాటిని చూడగానే మూడు అని చెప్పగలరు.

కానీ... అదే చోట ఏడు యాపిల్స్ ఉంటే, వాటిని ఒక్కొక్కటిగా లెక్కపెట్టాల్సి రావచ్చు.

అసలు... ఎందుకిలా జరుగుతుందీ??

మన కళ్ళు ఒకేసారి ఎన్ని వస్తువుల్ని గుర్తించగలవు?!

అసలు లెక్కపెట్టకుండానే వస్తువుల సంఖ్యను గుర్తించడం సాధ్యమేనాఆ?!

అవును!!

దీనికి సంబంధించిన ఒక ఆసక్తికరమైన స్కిల్ గురించి ఇప్పుడు తెలుసుకుందాం.

దాని పేరేంటో తెలుసా?... సబిటైజింగ్!
```
*(Notice how the elongated vowels `రాఆ?!`, dramatic ellipses `...`, double question marks `??`, and double exclamations `!!` naturally guide the neural diffusion attention to produce pitch inflection, breathing pauses, and enthusiastic delivery).*
