---
name: script-split
description: Step 1 of video generation - split user script into sections and steps, convert to oral style
---

# Step 1: Script Splitting & Oral Conversion

This is the first step of the video generation pipeline. The goal is to take the user's raw script/text and produce a structured plan that subsequent steps can consume.

## Two-Level Structure

The output has two levels, like a PPT presentation:

- **section（段）** = one visual page / slide in the video. All steps in the same section share the same animation and background.
- **step** = one sentence within a section. Steps are read aloud sequentially. Multiple steps on the same section play their audio one after another while the page stays.

```
Section 1 (一个动画页)
  ├── step 1: "第一句话"
  ├── step 2: "第二句话"
  └── step 3: "第三句话"
Section 2 (下一个动画页)
  ├── step 4: "..."
  └── step 5: "..."
```

## What This Step Does

1. **Read the user's script** - understand the overall topic and flow
2. **Split into sections** - group related sentences into the same visual page
3. **Split sections into steps** - break each section into individual spoken sentences
4. **Convert to oral/conversational style** - rewrite formal/written text as if someone is speaking naturally

## Output Format

Produce a JSON array saved to `steps.json` in the working directory:

```json
[
  {
    "section": 1,
    "steps": [
      { "step": 1, "text": "这一段的第一句话。" },
      { "step": 2, "text": "这一段的第二句话。" }
    ]
  },
  {
    "section": 2,
    "steps": [
      { "step": 3, "text": "下一段的文案。" },
      { "step": 4, "text": "继续说下去。" }
    ]
  }
]
```

### Fields

- `section` (int): Section number, starting from 1. Each section = one visual page in the video.
- `steps` (array): Ordered list of steps within this section.
  - `step` (int): Global sequential step number, starting from 1, unique across all sections.
  - `text` (string): The oral/conversational version of the text. This is what will be read aloud by TTS.

## Splitting Guidelines

### Section Splitting

- Each section should cover **one topic or one visual concept** - like a PPT slide
- A section typically corresponds to a paragraph, a topic shift, or a key message
- Aim for **30-120 seconds total spoken time** per section (multiple steps combined)
- Don't put unrelated ideas in the same section

### Step Splitting

- Each step should be **one sentence or one thought** - the smallest unit of speech
- Aim for **5-30 seconds of spoken audio** per step (roughly 15-80 Chinese characters or 10-50 English words)
- A section with 1 step is fine for short points; 2-4 steps per section is typical
- If a sentence is very long, split it into multiple steps at natural pause points

## Oral Conversion Rules

Convert written/formal text to natural spoken language:

- Remove bullet points, numbered lists, and markdown formatting
- Add natural transitions ("首先", "然后", "接下来", "另外", "First", "Next", "Also")
- Break up overly long sentences
- Replace书面化 expressions with口语化 equivalents:
  - "因此" -> "所以"
  - "然而" -> "但是"
  - "综上所述" -> "总的来说"
  - "旨在" -> "目的是"
  - "commence" -> "start"
  - "utilize" -> "use"
- Keep technical terms that are commonly spoken (AI, API, etc.) - the TTS script handles their normalization
- Add brief口头禅 or filler where natural (不要太刻意)

## Example

User input:
```
人工智能正在改变我们的生活方式。从医疗到教育，AI的应用无处不在。据统计，2024年全球AI市场规模已超过5000亿美元。与此同时，AI安全和伦理问题也日益受到关注。各国政府正在加快制定相关法规，确保AI技术的健康发展。
```

Output `steps.json`:
```json
[
  {
    "section": 1,
    "steps": [
      { "step": 1, "text": "你知道吗，人工智能其实已经在悄悄改变我们的生活了。" },
      { "step": 2, "text": "从看病就医到学校教育，AI 的应用可以说无处不在。" },
      { "step": 3, "text": "根据最新的数据，2024年全球 AI 市场的规模已经超过了5000亿美元，这个数字真的很惊人。" }
    ]
  },
  {
    "section": 2,
    "steps": [
      { "step": 4, "text": "不过与此同时，大家也越来越关注 AI 的安全和伦理问题。" },
      { "step": 5, "text": "各国政府也都在加快制定相关的法规，来确保 AI 技术能够健康地发展。" }
    ]
  }
]
```

In this example, Section 1 is one visual page about "AI 的发展现状"，Section 2 is another page about "AI 安全与监管"。
