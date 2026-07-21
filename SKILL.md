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
- [references/design-and-qa.md](references/design-and-qa.md) for design, data-integrity, and render checks;
- [references/local-library.json](references/local-library.json), when it exists, for the user's own template library resolved into scenario packs. See [section 4](#4-prefer-a-configured-local-library); prefer it over the built-in kits when it covers the scenario.

The built-in system contains four original, editable 16:9 theme kits. Each has the same 20 medium-to-high-density layouts, native charts, and replaceable hero images.

| Theme | Resource | Select by default for |
|---|---|---|
| Green-gold | [assets/premium-green-layout-kit.pptx](assets/premium-green-layout-kit.pptx) | work reports, projects, education, sustainability |
| Academic blue | [assets/premium-blue-layout-kit.pptx](assets/premium-blue-layout-kit.pptx) | thesis defenses, research, technical talks |
| Institutional red | [assets/premium-red-layout-kit.pptx](assets/premium-red-layout-kit.pptx) | universities, public institutions, formal reviews |
| Consulting purple | [assets/premium-purple-layout-kit.pptx](assets/premium-purple-layout-kit.pptx) | strategy, analytics, business and executive briefs |

Use exactly one theme per deck. If the user supplies brand colors, follow them; otherwise infer the theme from the audience and scenario and give one recommended result. Do not ask a beginner to compare palettes.

A private local template library is optional. When one is configured it becomes the preferred source of layouts, because purchased layout banks carry more layouts and native charts than these kits; the built-in kits then cover whatever the library cannot express.

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

## 4. Prefer a configured local library

If [references/local-library.json](references/local-library.json) exists, a local template library is configured and it outranks the built-in kits. Purchased layout banks carry far more layouts and native charts than the 20-slide built-in kits, so use them when they cover the scenario, and fall back to the built-in kits when they do not.

Never show the user a file list. Filenames in these libraries describe topics, not message types, so they cannot support a choice. Resolve everything through scenario packs instead.

### Read the pack, not the folder

`local-library.json` maps a plain-language scenario to a concrete deck, colorway, and ordered slide list:

```text
年终述职 -> family work-report-cn-300, colorway blue-white, theme academic-blue
           cover 7 | agenda 11 | body 19 | bar-chart 156 | timeline 122
           line-chart 161 | comparison 88 | risk 25 | closing 17
```

Each step records `role`, `slide`, `matched_as`, `reused_layout`, `density`, and `charts`. Follow the pack's slide order, then adjust to the actual evidence: drop steps the material does not support, and duplicate a chart step when there is genuinely more than one chart to show.

Treat these fields as warnings:

- `matched_as` different from `role` means the layout is an approximation; verify it still carries the intended message.
- `reused_layout: true` means the same source slide already appears earlier in the pack; vary the content and confirm the deck does not look repetitive.
- `unmatched_roles` lists parts of the story the library cannot express; take those slides from the built-in kit.

Pick the colorway from audience and scenario exactly as with built-in themes, and keep one colorway per deck. Do not ask a beginner to compare colorways.

### One-time setup, and refresh when the library changes

```bash
python scripts/index_slides.py "/path/to/templates" --output work/slide-index.json
python scripts/build_scenario_packs.py work/slide-index.json --output references/local-library.json
```

`index_slides.py` records role, density, title, chart kinds, and structure for every usable slide, and drops vendor instruction pages such as font-install and recolor tutorials. `build_scenario_packs.py` collapses that index into the scenario packs above. Use `--exclude` to keep personal or third-party material out of the index; never index folders holding other people's names or records. Both scripts support `--self-test`; run it after changing either one.

Use `scripts/catalog_pptx.py` for deck-level questions the packs do not answer, such as auditing aspect ratios or locating a deck by theme font:

```bash
python scripts/catalog_pptx.py "/path/to/templates" --query academic --query green --output work/catalog.json
```

`--query` values are repeatable OR filters. Cache a full catalog until the library changes.

### Recolour only on request

[references/palette-library.json](references/palette-library.json), when present, holds palettes read from the library's colour cards, each with a `dominant`, an `accent`, and `legible_pairs` scored for contrast. Use it when the user asks for a specific mood — 复古, 渐变, 高级感 — rather than as a default; the deck's own colorway is already coherent, and recolouring a purchased master is easy to get wrong.

Take the text and background from a pair in `legible_pairs`, never from two arbitrary swatches. A pair with `ok_small_text: false` clears the large-text bar only: use it for titles and KPI numbers, and keep citations, source notes, and axis labels on a pair that passes.

### Clean every borrowed slide

Purchased masters carry the vendor's marketing, not the user's. Before delivering, confirm each of these on every reused slide:

- **Vendor branding is gone.** These decks place a logo in the master, so deleting it on one slide is not enough; remove it in the slide master and check the corner of every rendered page. Shipping a defense deck with a template seller's logo is a real failure.
- **Sample copy is gone.** Filler such as `You can write your subtitle here` and `这边可以写上你的副标题` repeats across many layouts and survives casual editing.
- **Required fonts are installed**, or the layout silently reflows. Report missing fonts to the user instead of substituting quietly; the font files usually ship inside the library's own `字体` folder.
- **Real content still fits.** Sample text is length-tuned to the design, so genuine titles and labels often overflow. Re-render and check, and split the slide rather than shrinking type.

### When no pack fits

Shortlist at most three decks from the slide index, render only those slides, and make the final selection yourself. Use one primary deck and at most one donor deck. Prefer a structurally correct layout over a more decorative but semantically wrong one.

### Licensing

Treat purchased or user-provided templates as private inputs. `local-library.json` holds metadata only — roles, slide numbers, and relative paths — and carries no slide content, so it is safe to commit. The masters themselves stay on the user's disk: never publish or redistribute the originals, embedded stock, or fonts unless redistribution rights are explicit. Public deliverables may contain original layouts and generated or separately licensed assets derived from design principles, not copied slides.

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
