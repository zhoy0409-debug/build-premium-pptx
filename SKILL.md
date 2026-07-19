---
name: build-premium-pptx
description: Create or redesign polished PowerPoint presentations (.pptx) by mining a local template library, matching content to proven slide layouts, sourcing strong visuals, preserving theme consistency, and rendering the finished deck for visual QA. Use for pitch decks, reports, academic talks, thesis defenses, scientific presentations, image-rich slides, executive presentations, PPT美化, 答辩PPT, 工作汇报, or when the user provides PowerPoint templates to reuse.
---

# Build Premium PPTX

Turn rough content into a coherent, visual deck by reusing the strongest layouts in an existing template library. Default to an autopilot experience for people who do not know presentation design. Keep the result editable and validate the rendered slides, not just the source code.

## Default to beginner autopilot

Assume the user may not know the right slide count, structure, template, layout, palette, font, or image style.

- Accept a one-line request plus any notes, document, spreadsheet, or existing deck. Do not require a design brief.
- Ask at most two plain-language questions only when the answers materially change the deck: who will see it, and how long the presentation is. Infer everything else.
- Do not ask the user to browse a large template library or choose among design terms. Select the best template yourself and explain it as a benefit, such as “clear for a thesis defense” or “more visual for a product pitch.”
- Present one recommended direction. Offer up to two alternatives only when they are genuinely different or the user asks.
- If the user says “直接做”, “你决定”, “I don't know”, or equivalent, proceed without another design question.
- Before editing, summarize the inferred plan in five short lines: audience, goal, length, visual direction, and story arc. Continue unless the user objects.
- Keep choices reversible: editable text, replaceable images, theme colors, and reusable layouts.

Example beginner requests:

```text
把这个 Word 做成 10 页答辩 PPT，听众是老师，时间 8 分钟；我不懂设计，请直接决定模板和排版。
Turn these notes into an investor deck. I am new to PowerPoint, so choose the structure, visuals, and template for me.
```

## Apply the house rules

- Use one primary template and at most one donor template. Keep aspect ratio, theme fonts, palette, spacing, and illustration style coherent.
- Make each slide communicate one takeaway. Write the takeaway as the title when possible.
- Prefer a strong image, diagram, or chart over decorative filler. Do not invent data or evidence.
- Preserve editability for text, charts, and simple diagrams.
- Do not redistribute template files, fonts, or stock assets unless their license permits it. Treat user-provided templates as local inputs by default.
- Read [references/design-and-qa.md](references/design-and-qa.md) before storyboarding and again before final QA.

## 1. Set the brief

Extract the audience, purpose, duration or slide count, language, output format, and available brand/template assets. Infer safe defaults instead of blocking when details are absent:

- 16:9 landscape
- the user's language
- concise, professional tone
- one visual system and one accent color
- roughly one slide per minute for a live talk

Keep mandatory logos, citations, data, and wording. Do not preserve weak source formatting merely because it exists.

## 2. Discover reusable templates

If the user provides a template directory, catalog it before opening files one by one:

```bash
python scripts/catalog_pptx.py "/path/to/templates" --query academic --query green --output work/catalog.json
```

Use repeatable `--query` terms as OR filters. The catalog reports slide count, aspect ratio, media, charts, diagrams, layouts, transitions, animation timing, theme fonts, and theme colors. Run `python scripts/catalog_pptx.py --self-test` after modifying the script.

Cache a full catalog in the working directory and reuse it until the template library changes. Use targeted queries for fast one-off work.

Shortlist no more than three decks with the right audience, aspect ratio, visual density, and slide roles. Render candidate decks or contact sheets with the available presentation tooling and inspect the actual slides. Metadata is a filter, not a design verdict. Make the final selection for a beginner; do not hand the shortlist back as homework.

Choose:

1. one primary deck for cover, sections, body, and ending;
2. optionally one donor deck for a missing layout type;
3. no donor when the primary deck already covers the story.

If no template library is available, build a minimal visual system from the user's brand assets and follow the reference guide.

## 3. Storyboard before editing

Create a slide list with four fields: `slide number | takeaway | evidence | layout role`. Cover the narrative with only the slides needed:

1. opening promise or question;
2. context and problem;
3. approach or argument;
4. evidence and implications;
5. conclusion and next action.

Map each row to a proven layout in the primary deck. Prefer a close structural match over a visually impressive but semantically wrong slide.

## 4. Reuse layouts safely

- Duplicate source slides inside the source deck when possible; replace text and media without disturbing geometry.
- Preserve masters, theme relationships, crop behavior, grouping, and animations.
- Rebuild only when the layout cannot fit the message cleanly.
- If the editing library cannot preserve transitions or animation timing, use native PowerPoint automation or select a static layout. Do not silently flatten a dynamic deck.
- Replace rather than stack content. Remove unused placeholders, sample copy, hidden artifacts, and source-only slides.
- Keep a consistent header, footer, page-number policy, and citation style.

## 5. Source useful visuals

Use this order: user assets, licensed local library, authoritative/official sources, licensed stock, then generated visuals. Record source URLs or credit lines when attribution is required. Reject watermarks, low-resolution images, inconsistent icon families, and images that merely repeat the title.

For research or technical decks, preserve units, legends, sample sizes, uncertainty, and source notes. Redraw a figure only when its meaning remains unchanged.

## 6. Build and render

Use the presentation tooling already available in the environment. Avoid adding a new dependency when existing slide tooling can edit or generate the deck.

After building:

1. save the editable `.pptx`;
2. render every slide to images;
3. create a contact sheet for whole-deck rhythm;
4. inspect dense slides at full resolution;
5. revise and render again.

## 7. Deliver only after QA

Apply the full checklist in [references/design-and-qa.md](references/design-and-qa.md). Confirm that the deck opens, all slides render, nothing is clipped or overlapping, text is readable, images are sharp, and the narrative works without speaker explanation.

Deliver the final `.pptx` and any requested PDF. Briefly disclose the primary template, donor template if any, externally sourced assets, and the two or three easiest places the user can edit later. Do not include the user's template library in the deliverable.

