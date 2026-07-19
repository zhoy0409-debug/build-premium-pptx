# Design and QA reference

## Layout selection

| Message | Prefer | Avoid |
|---|---|---|
| Opening | One promise, question, or hero image | Agenda-shaped title slide |
| Section | Large chapter number or short statement | Dense preview of the next section |
| Explanation | Claim + supporting visual | Paragraph plus unrelated decoration |
| Comparison | Aligned two-column or matrix | Two unrelated card styles |
| Process | Numbered flow with direction | Unordered icons connected by lines |
| Timeline | One axis and selective milestones | Equal emphasis on every date |
| Quantitative evidence | Chart with direct annotation | Screenshot of a spreadsheet |
| Qualitative evidence | Quote, photo, or coded themes | Wall of interview text |
| Portfolio/gallery | Consistent image grid | Mixed crops and arbitrary sizes |
| Conclusion | Three memorable points or one action | Repeated agenda |

## Visual system

- Treat whitespace as structure. Use consistent margins of roughly 5–7% of the slide width.
- Use purposeful whitespace, but avoid empty canvases. On normal body slides, occupy roughly 60–80% of the content frame with evidence or visual structure; add only elements that clarify the message.
- Make information-rich slides readable at three speeds: takeaway in 5 seconds, evidence in 30 seconds, and supporting detail during Q&A.
- High density must come from a stronger grid and grouped evidence, never from shrinking all text or pasting more figures.
- Use a grid and align visible edges. Intentional overlap is acceptable; accidental near-alignment is not.
- Keep two typefaces at most. Use the template's theme fonts before introducing replacements.
- Use no more than four text sizes on a normal slide. As a practical floor, keep titles at 24 pt or larger, body text at 16 pt or larger, and citations at 9 pt or larger.
- Use one dominant color, one accent, and neutrals unless the template already defines a stronger system.
- Maintain strong contrast. Never rely on color alone for a critical distinction.
- Keep repeated components identical: corner radius, stroke width, icon style, caption position, and image treatment.
- Prefer calm hierarchy over gradients, shadows, glow, and decorative lines. Use an effect only when it clarifies grouping or depth.

## Visual assets

- Use one strong hero image or a deliberate 2–4 image grid; avoid many small, unrelated thumbnails.
- Crop to the message, preserve faces and important labels, and never stretch an image.
- Use vector icons from one family. Do not mix outline, filled, 3D, and emoji styles.
- Make diagrams explain relationships that prose cannot. Use a consistent reading direction.
- For generated imagery, keep subject, palette, lighting, and aspect ratio consistent across the deck.

## Data and scientific integrity

- Keep chart encodings truthful and readable. Avoid 3D charts and decorative axes.
- Preserve units, denominators, sample sizes, error bars, confidence intervals, and statistical notes when relevant.
- Start bar charts at zero unless a clearly labeled alternative is analytically necessary.
- Direct-label important series when space permits; de-emphasize gridlines and minor categories.
- Never fabricate a citation, result, logo, participant quote, or product claim.
- Put short source notes on the slide and full references in the requested citation format.

## Render QA

Inspect the contact sheet for:

- a clear opening, section rhythm, evidence sequence, and ending;
- coherent colors, type, imagery, and density;
- no unexplained style changes or isolated donor-template slides;
- no repeated layout more often than the story requires.

Inspect every full-size slide for:

- clipped, overlapping, off-canvas, or hidden content;
- orphan words, awkward line breaks, inconsistent punctuation, and placeholder text;
- stretched, pixelated, watermarked, or badly cropped images;
- unreadable labels, legends, footnotes, and citations;
- inconsistent alignment, margins, strokes, shadows, and corner radii;
- missing glyphs, font substitution, broken equations, or altered scientific symbols;
- charts whose numbers, labels, or source notes disagree with the supplied data.

Finally open the `.pptx` in a compatible presentation application when available. Confirm slide size, theme, media, transitions, videos, and fonts survive the round trip. Re-render after every material revision.
