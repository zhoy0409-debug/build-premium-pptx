---
name: build-premium-pptx
description: Turn rough notes, documents, spreadsheets, research materials, or an existing deck into a polished editable PowerPoint with almost no design decisions required from the user. Uses four original 20-slide theme kits and automatically selects green-gold, academic blue, institutional red, or consulting purple; can privately mine a local template library when useful, organizes the story, matches content to layouts, adds relevant visuals, and renders every slide for QA. Use for PPT制作, PPT美化, 工作汇报, 答辩PPT, 学术报告, 科研分享, 文献汇报, 研究生讲座, 项目提案, pitch decks, reports, and users who say they are bad at design, organization, or PowerPoint.
---

# Build Premium PPTX

Create the deck for the user, not a template-choosing exercise. The normal beginner workflow is:

```text
user drops materials -> infer brief -> organize story -> choose layouts -> build -> render -> repair -> deliver editable PPTX
```

The user should not need to understand masters, grids, visual hierarchy, charts, palettes, or slide roles.

## Load the built-in system

Before storyboarding, read:

- [references/layout-recipes.json](references/layout-recipes.json) for deterministic layout and scenario selection;
- [references/aesthetic-patterns.md](references/aesthetic-patterns.md) for research, consulting, institutional, and scientific visual grammars;
- [references/design-and-qa.md](references/design-and-qa.md) for design, data-integrity, and render checks.

The built-in system contains four original, editable 16:9 theme kits. Each has the same 20 medium-to-high-density layouts, native charts, and replaceable hero images.

| Theme | Resource | Select by default for |
|---|---|---|
| Green-gold | [assets/premium-green-layout-kit.pptx](assets/premium-green-layout-kit.pptx) | work reports, projects, education, sustainability |
| Academic blue | [assets/premium-blue-layout-kit.pptx](assets/premium-blue-layout-kit.pptx) | thesis defenses, research, technical talks |
| Institutional red | [assets/premium-red-layout-kit.pptx](assets/premium-red-layout-kit.pptx) | universities, public institutions, formal reviews |
| Consulting purple | [assets/premium-purple-layout-kit.pptx](assets/premium-purple-layout-kit.pptx) | strategy, analytics, business and executive briefs |

Use exactly one theme per deck. If the user supplies brand colors, follow them; otherwise infer the theme from the audience and scenario and give one recommended result. Do not ask a beginner to compare palettes. A private local template library is optional, not a prerequisite.

## Beginner contract

- Accept a one-line request plus any mix of notes, Word/PDF files, spreadsheets, images, or an old deck. Do not require a design brief.
- Ask at most two plain-language questions, and only when the answers materially change the result: `Who will see it?` and `How long will you present?`
- If the user says “直接做”, “你决定”, “我不会”, “I don't know”, or equivalent, proceed immediately.
- Infer language, aspect ratio, tone, slide count, story structure, visual direction, and layout selection.
- Never ask a beginner to choose a template, palette, font pair, layout family, or design style from a long list.
- Present one recommended direction. Only offer alternatives when the user asks or when two directions have genuinely different business consequences.
- Keep everything reversible: editable text, native charts, editable simple diagrams, replaceable images, and theme colors.

Before building, state the inferred plan in five short lines: audience, goal, length, visual direction, and story arc. This is an informative checkpoint, not a request for permission; continue unless the user objects.

## 1. Diagnose the material

Extract and preserve:

- required facts, numbers, units, dates, names, logos, citations, and wording;
- audience, desired action, delivery time, language, and output format;
- available photos, figures, tables, charts, brand assets, and templates.

Then separate the material into:

1. `must show`: required evidence or decisions;
2. `should say`: context needed to understand the evidence;
3. `appendix`: useful detail that interrupts the main story;
4. `omit`: duplication, unsupported claims, and formatting noise.

Do not invent missing data, citations, user quotes, logos, or research results. Mark genuine gaps clearly or turn them into a next action.

Safe defaults when context is missing:

- 16:9 landscape;
- the user's language;
- concise professional tone;
- roughly one slide per minute for a live talk;
- one visual system, one dominant color, one accent color;
- conclusion-led slide titles.

## 2. Build the story before the slides

Create an internal storyboard with:

```text
slide | takeaway title | evidence | layout role | visual needed
```

Use only the slides needed to move the audience through:

1. promise or question;
2. context and problem;
3. approach or argument;
4. evidence and implications;
5. conclusion and next action.

Each slide must answer one audience question and communicate one takeaway. Write that takeaway as the title when possible. Split a slide instead of shrinking text or stacking unrelated points.

## 3. Select layouts automatically

Identify the closest scenario in `scenario_recipes` inside [references/layout-recipes.json](references/layout-recipes.json), then adjust the recipe to the actual evidence. Map every storyboard row to a layout by message type, not by decoration.

Choose one theme from `resource.themes` and one `style_archetype`. Apply their navigation, evidence-container, density, branding, and color rules consistently. Do not mix themes or archetypes slide by slide.

Examples:

- thesis defense -> science cover, central thesis, research method, visual evidence, editable charts, findings, risks, closing;
- long research lecture -> promise, system map, sparse chapter pause, module cards, tool comparison, workflow, evidence, chapter synthesis, closing rule;
- journal club or literature review -> paper identity, essential background, new question, method, figure evidence, result summary, next question, integrated mechanism, limitations;
- work report -> nature cover, thesis, agenda, evidence, process, timeline, results charts, closing;
- proposal -> strategy cover, problem, evidence, plan, comparison, economics, risk response, decision;
- short executive brief -> strategy cover, decision thesis, three signals, comparison, one chart, risks, action.

Respect every layout's `slots` limit. Replace sample copy, data, labels, and images; do not merely place new content on top. Use the deck as a layout bank: duplicate only the selected slides into the final deck and remove unused resource pages.

For a long technical lecture, `research_operating_system` may use a consistent dark canvas across the full deck; add sparse chapter dividers and verify projector contrast. For a paper review, use `figure_first_paper_review` and repeat the question → evidence → direct finding → next question loop. Do not force either archetype onto a short general-audience talk.

## 4. Use a private template library only when it adds value

Use the local-library route when the user explicitly supplies brand templates, requests a house style, or the built-in kit lacks a necessary layout.

Catalog first instead of opening hundreds of files:

```bash
python scripts/catalog_pptx.py "/path/to/templates" --query academic --query green --output work/catalog.json
```

`--query` values are repeatable OR filters. The catalog reports slide count, aspect ratio, media, charts, diagrams, layouts, transitions, animation timing, theme fonts, and theme colors. Cache a full catalog until the library changes. Run `python scripts/catalog_pptx.py --self-test` after changing the script.

Shortlist at most three decks internally, render them, and make the final selection yourself. Use one primary deck and at most one donor deck. Prefer a structurally correct layout over a more decorative but semantically wrong one.

Treat purchased or user-provided templates as private inputs. Reuse them locally when authorized, but never publish or redistribute the originals, embedded stock, or fonts unless redistribution rights are explicit. Public deliverables may contain original layouts and generated or separately licensed assets derived from design principles, not copied slides.

## 5. Build an editable deck

- Preserve native text, editable charts, and editable simple diagrams.
- Preserve masters, theme relationships, crops, grouping, transitions, and animation when the chosen editing path supports them.
- If transitions or animation cannot survive the editing library, use native PowerPoint automation or choose a static layout; do not silently flatten a dynamic deck.
- Keep headers, footers, page numbers, citations, margins, strokes, and corner radii consistent.
- Use one primary layout system. Avoid isolated slides that look imported from another deck.
- Do not confuse clean with empty. Normal body slides should feel complete at first glance, while every visible element must still explain, prove, compare, or guide.
- Keep titles at least 24 pt, body text at least 16 pt, and citations at least 9 pt unless the presentation tooling specifies stricter values.

When the environment provides `@oai/artifact-tool`, use it for programmatic slide creation and editing. The original resource kit can be regenerated with:

```bash
node scripts/build_premium_resource_kit.mjs --assets assets --theme green-gold
```

Use `--theme green-gold|academic-blue|institutional-red|consulting-purple` to rebuild a specific bundled kit.

Do not replace the presentation workflow with `python-pptx` when the environment's presentation tooling requires artifact-tool or native PowerPoint.

## 6. Add visuals that explain

Use this priority:

1. user-provided visuals;
2. licensed local assets;
3. authoritative or official sources;
4. licensed stock;
5. generated imagery.

Choose visuals that prove, compare, orient, or explain. Reject watermarks, low resolution, irrelevant decoration, stretched images, mixed icon families, and screenshots of spreadsheets. Replace cover heroes with images that match the user's actual topic.

For scientific or data slides, preserve units, denominators, legends, sample sizes, uncertainty, source notes, and statistical meaning. Redraw only when meaning remains unchanged.

## 7. Render, inspect, and repair

Never deliver after only editing the source file.

1. Save the editable `.pptx`.
2. Render every slide to an image.
3. Inspect a contact sheet for narrative rhythm and visual consistency.
4. Inspect every slide at full size for clipping, overlap, missing glyphs, bad crops, tiny labels, and placeholders.
5. Run available overflow and layout tests.
6. Repair every issue and render again.
7. Open the final `.pptx` in a compatible presentation application when available.

Apply the full checklist in [references/design-and-qa.md](references/design-and-qa.md). A deck is not complete while any slide fails render QA.

## 8. Deliver for a non-designer

Deliver the editable `.pptx` and the requested PDF when applicable. In the handoff, say only what helps the user act:

- what story direction was chosen;
- which template/resource system was used;
- any external visual sources or generation disclosure;
- the two or three easiest places to edit later;
- any factual gap the user still needs to fill.

Do not include the user's private template library in the deliverable.

Beginner examples:

```text
把这个 Word 和 Excel 做成 10 页工作汇报，我不会做 PPT，你直接决定。
把这些实验结果做成 8 分钟答辩，老师能迅速看懂结论。
Turn these notes into an investor deck. Choose the story, visuals, and layout for me.
美化这个旧 PPT，但数字、引用和图表含义都不能变。
```
