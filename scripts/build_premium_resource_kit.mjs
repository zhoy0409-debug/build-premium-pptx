import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

async function loadArtifactTool() {
  try {
    return await import("@oai/artifact-tool");
  } catch {
    // Standalone skills live outside the bundled runtime's node_modules tree.
  }

  const runtimeRoots = [process.env.USERPROFILE, process.env.HOME].filter(Boolean);
  const candidates = [];
  if (process.env.CODEX_ARTIFACT_TOOL_PATH) candidates.push(process.env.CODEX_ARTIFACT_TOOL_PATH);
  for (const root of runtimeRoots) {
    candidates.push(path.join(
      root,
      ".cache",
      "codex-runtimes",
      "codex-primary-runtime",
      "dependencies",
      "node",
      "node_modules",
      "@oai",
      "artifact-tool",
    ));
  }

  for (const candidate of candidates) {
    const entrypoints = candidate.endsWith(".mjs")
      ? [candidate]
      : [
          path.join(candidate, "dist", "node", "artifact_tool.mjs"),
          path.join(candidate, "dist", "artifact_tool.mjs"),
        ];
    for (const entrypoint of entrypoints) {
      if (fsSync.existsSync(entrypoint)) return import(pathToFileURL(entrypoint).href);
    }
  }

  throw new Error(
    "@oai/artifact-tool was not found. Run this inside Codex's bundled presentation runtime or set CODEX_ARTIFACT_TOOL_PATH.",
  );
}

const { Presentation, PresentationFile } = await loadArtifactTool();

const HERE = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).reduce((rows, value, index, all) => {
  if (value.startsWith("--")) rows.push([value.slice(2), all[index + 1]]);
  return rows;
}, []));
const assetsDir = path.resolve(args.assets || path.join(HERE, "../assets"));
const outFile = path.resolve(args.out || path.join(assetsDir, "premium-green-layout-kit.pptx"));
const previewFile = path.resolve(args.preview || path.join(assetsDir, "premium-green-layout-kit-preview.webp"));
const qaDir = path.resolve(args.qa || path.join(process.cwd(), "work", "premium-ppt-qa"));

const C = {
  ink: "#162019",
  forest: "#0B3B2A",
  green: "#1D6B43",
  green2: "#2D8355",
  sage: "#AFC3B2",
  pale: "#E7EFE8",
  cream: "#F7F3EA",
  gold: "#D89A2B",
  gold2: "#F0C56A",
  gray: "#667168",
  line: "#CBD5CC",
  white: "#FFFFFF",
};
const FONT = "Microsoft YaHei";
const SERIF = "Georgia";
const W = 1280;
const H = 720;
const FRAME = { left: 72, top: 64, width: 1136, height: 592 };

async function imageBytes(name) {
  return new Uint8Array(await fs.readFile(path.join(assetsDir, name)));
}

function rect(slide, left, top, width, height, fill, options = {}) {
  return slide.shapes.add({
    geometry: options.geometry || "rect",
    name: options.name,
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: options.line || fill, width: options.lineWidth ?? 0 },
    ...(options.radius ? { borderRadius: options.radius } : {}),
  });
}

function text(slide, value, left, top, width, height, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name: options.name,
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    fontSize: options.size || 20,
    bold: options.bold || false,
    color: options.color || C.ink,
    typeface: options.typeface || FONT,
    alignment: options.align || "left",
    verticalAlignment: options.vAlign || "top",
    autoFit: options.autoFit || "shrinkText",
    insets: options.insets || { left: 0, right: 0, top: 0, bottom: 0 },
    ...(options.lineSpacing ? { lineSpacing: options.lineSpacing } : {}),
  };
  return shape;
}

function base(slide, number, dark = false, label = "PREMIUM LAYOUT KIT") {
  slide.background.fill = dark ? C.forest : C.cream;
  rect(slide, 72, 34, 44, 4, dark ? C.gold : C.green);
  text(slide, label, 128, 26, 310, 24, { size: 12, bold: true, color: dark ? C.pale : C.gray });
  text(slide, String(number).padStart(2, "0"), 1160, 670, 48, 20, { size: 12, color: dark ? C.sage : C.gray, align: "right" });
}

function titleBlock(slide, kicker, titleValue, subtitle = "", dark = false) {
  text(slide, kicker.toUpperCase(), 72, 78, 360, 24, { size: 13, bold: true, color: C.gold });
  text(slide, titleValue, 72, 112, 870, 82, { size: 42, bold: true, color: dark ? C.white : C.ink, lineSpacing: 0.92 });
  if (subtitle) text(slide, subtitle, 72, 202, 820, 52, { size: 18, color: dark ? C.sage : C.gray });
}

function smallRule(slide, x, y, w, color = C.green) {
  rect(slide, x, y, w, 2, color);
}

function addBullet(slide, index, heading, body, x, y, width, dark = false) {
  rect(slide, x, y + 3, 30, 30, dark ? C.gold : C.green, { geometry: "ellipse" });
  text(slide, String(index).padStart(2, "0"), x, y + 8, 30, 18, { size: 11, bold: true, color: dark ? C.forest : C.white, align: "center" });
  text(slide, heading, x + 44, y, width - 44, 30, { size: 19, bold: true, color: dark ? C.white : C.ink });
  text(slide, body, x + 44, y + 36, width - 44, 58, { size: 15, color: dark ? C.sage : C.gray });
}

async function writeBlob(file, blob) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

const [nature, science, strategy] = await Promise.all([
  imageBytes("hero-nature-campus.png"),
  imageBytes("hero-science-network.png"),
  imageBytes("hero-strategy-landscape.png"),
]);

const p = Presentation.create({ slideSize: { width: W, height: H } });

// 01 — nature cover
{
  const s = p.slides.add();
  s.images.add({ blob: nature, contentType: "image/png", alt: "Green research campus in terraced landscape", fit: "cover", position: { left: 480, top: 0, width: 800, height: 720 } });
  rect(s, 0, 0, 555, 720, C.cream);
  rect(s, 72, 92, 54, 6, C.gold);
  text(s, "PREMIUM STORY DECK", 72, 116, 360, 24, { size: 13, bold: true, color: C.green });
  text(s, "让复杂内容，\n变成清晰结论", 72, 184, 430, 154, { size: 48, bold: true, color: C.ink, lineSpacing: 0.9 });
  text(s, "适合工作汇报 · 项目提案 · 科研分享", 72, 374, 390, 42, { size: 18, color: C.gray });
  smallRule(s, 72, 458, 360, C.line);
  [["12 MIN", "演讲时长"], ["1 PATH", "推荐方向"], ["100%", "可编辑"]].forEach(([v, k], i) => {
    const x = 72 + i * 124;
    text(s, v, x, 482, 108, 28, { size: 18, bold: true, color: i === 1 ? C.gold : C.green, typeface: SERIF });
    text(s, k, x, 520, 108, 24, { size: 12, color: C.gray });
  });
  text(s, "PROJECT BRIEF / 2026", 72, 590, 280, 24, { size: 11, bold: true, color: C.gray });
  text(s, "01", 72, 630, 72, 34, { size: 18, bold: true, color: C.gold, typeface: SERIF });
}

// 02 — science cover
{
  const s = p.slides.add();
  s.images.add({ blob: science, contentType: "image/png", alt: "Abstract scientific cellular network", fit: "cover", position: { left: 0, top: 0, width: 1280, height: 720 } });
  rect(s, 1148, 64, 60, 6, C.gold);
  text(s, "SCIENCE / RESEARCH", 790, 104, 418, 24, { size: 13, bold: true, color: C.gold, align: "right" });
  text(s, "从问题出发，\n让证据说话", 740, 166, 468, 136, { size: 48, bold: true, color: C.white, align: "right", lineSpacing: 0.9 });
  text(s, "学术报告 · 论文答辩 · 技术分享", 796, 338, 412, 34, { size: 18, color: C.sage, align: "right" });
  text(s, "02", 1150, 646, 58, 24, { size: 16, bold: true, color: C.gold, align: "right", typeface: SERIF });
}

// 03 — strategy cover
{
  const s = p.slides.add();
  s.images.add({ blob: strategy, contentType: "image/png", alt: "Layered green and gold strategy landscape", fit: "cover", position: { left: 0, top: 0, width: 1280, height: 720 } });
  text(s, "STRATEGY / DECISION", 740, 82, 450, 24, { size: 13, bold: true, color: C.green, align: "right" });
  text(s, "把选择，\n变成行动", 736, 124, 454, 128, { size: 48, bold: true, color: C.ink, align: "right", lineSpacing: 0.9 });
  smallRule(s, 1008, 282, 182, C.gold);
  text(s, "年度规划 · 商业方案 · 复盘总结", 730, 302, 460, 34, { size: 18, color: C.gray, align: "right" });
  text(s, "03", 1130, 648, 60, 24, { size: 16, bold: true, color: C.green, align: "right", typeface: SERIF });
}

// 04 — section divider
{
  const s = p.slides.add();
  base(s, 4, true, "SECTION DIVIDER");
  text(s, "01", 72, 118, 310, 186, { size: 132, bold: true, color: C.gold, typeface: SERIF });
  smallRule(s, 72, 330, 186, C.sage);
  text(s, "先确定故事，\n再选择版式", 402, 166, 670, 126, { size: 46, bold: true, color: C.white, lineSpacing: 0.92 });
  text(s, "章节页负责切换节奏，不承担解释任务。", 406, 328, 618, 44, { size: 18, color: C.sage });
  [["01", "CONTEXT", "为什么现在重要"], ["02", "EVIDENCE", "哪些事实支持判断"], ["03", "ACTION", "下一步需要做什么"]].forEach(([n, h, b], i) => {
    const x = 404 + i * 252;
    smallRule(s, x, 416, 214, i === 1 ? C.gold : C.sage);
    text(s, n, x, 434, 34, 24, { size: 14, bold: true, color: C.gold, typeface: SERIF });
    text(s, h, x + 42, 432, 164, 26, { size: 14, bold: true, color: C.white });
    text(s, b, x, 474, 214, 44, { size: 14, color: C.sage });
  });
  rect(s, 0, 594, 1280, 126, C.gold);
  text(s, "STRUCTURE BEFORE DECORATION", 72, 630, 700, 36, { size: 18, bold: true, color: C.forest });
}

// 05 — agenda
{
  const s = p.slides.add();
  base(s, 5, false, "AGENDA / CHAPTER MAP");
  titleBlock(s, "One clear path", "四个章节，回答一个核心问题", "让听众始终知道：现在讲到哪里，下一步为什么重要。", false);
  const items = [["01", "背景", "为什么现在必须讨论"], ["02", "洞察", "证据揭示了什么"], ["03", "方案", "我们准备如何行动"], ["04", "结果", "成功将如何衡量"]];
  items.forEach(([n, h, b], i) => {
    const x = 72 + i * 284;
    rect(s, x, 292, 260, 322, i === 1 ? "#F1E7CF" : C.white, { line: C.line, lineWidth: 1 });
    rect(s, x, 292, 260, 7, i === 1 ? C.gold : C.green);
    text(s, n, x + 22, 324, 92, 66, { size: 46, bold: true, color: i === 1 ? C.gold : C.green, typeface: SERIF });
    text(s, h, x + 22, 404, 210, 36, { size: 24, bold: true });
    text(s, b, x + 22, 454, 210, 58, { size: 16, color: C.gray });
    smallRule(s, x + 22, 534, 54, i === 1 ? C.gold : C.green);
    text(s, ["形成共同背景", "提炼关键判断", "明确执行路径", "定义衡量标准"][i], x + 22, 554, 210, 34, { size: 14, bold: true, color: C.green });
  });
}

// 06 — statement
{
  const s = p.slides.add();
  base(s, 6, false, "OPENING THESIS");
  text(s, "ONE THESIS / THREE PROOFS", 72, 82, 360, 24, { size: 13, bold: true, color: C.gold });
  text(s, "真正高级的演示，\n不是信息更多，\n而是判断更清楚。", 72, 126, 684, 210, { size: 48, bold: true, lineSpacing: 0.9 });
  smallRule(s, 72, 356, 168, C.gold);
  text(s, "结论先行，证据随后，行动收束。\n每一页都承担清晰的叙事任务。", 72, 384, 642, 78, { size: 18, color: C.gray, lineSpacing: 1.18 });
  rect(s, 72, 500, 684, 112, C.pale, { line: C.line, lineWidth: 1 });
  text(s, "判断标准", 98, 526, 120, 28, { size: 14, bold: true, color: C.green });
  text(s, "听众能否在 5 秒内复述这一页的结论？", 98, 562, 612, 32, { size: 20, bold: true });
  rect(s, 820, 104, 388, 508, C.forest);
  const points = [["01", "少而关键", "只保留推动结论的信息"], ["02", "标题有判断", "让听众先知道这页意味着什么"], ["03", "系统要稳定", "图像、字体和节奏保持一致"]];
  points.forEach(([h, b], i) => {
    const y = 142 + i * 148;
    if (i) smallRule(s, 852, y - 22, 324, C.green2);
    text(s, h, 852, y, 54, 28, { size: 16, bold: true, color: C.gold, typeface: SERIF });
    text(s, b, 916, y - 2, 250, 30, { size: 20, bold: true, color: C.white });
    text(s, points[i][2], 916, y + 38, 250, 54, { size: 15, color: C.sage });
  });
}

// 07 — image + text frame
{
  const s = p.slides.add();
  base(s, 7, false, "VISUAL EVIDENCE");
  titleBlock(s, "Image + claim", "一张图，只负责证明一个结论", "用可替换主视觉建立情境，用三条证据完成解释。", false);
  rect(s, 72, 282, 646, 342, C.pale, { line: C.line, lineWidth: 1, name: "replaceable-visual-frame" });
  rect(s, 96, 306, 598, 254, C.sage);
  text(s, "可替换主视觉", 218, 402, 354, 48, { size: 28, bold: true, color: C.forest, align: "center", vAlign: "middle" });
  rect(s, 96, 560, 598, 40, C.forest);
  text(s, "CAPTION / SOURCE / KEY OBSERVATION", 116, 570, 558, 22, { size: 11, bold: true, color: C.pale });
  [["01", "先给结论", "标题直接说明这张图意味着什么。"], ["02", "再给证据", "保留数字、事实、来源和必要限定。"], ["03", "最后给行动", "明确下一步、风险或需要作出的决定。"]].forEach(([n, h, b], i) => {
    const y = 292 + i * 108;
    rect(s, 752, y, 420, 92, i === 1 ? C.forest : C.white, { line: i === 1 ? C.forest : C.line, lineWidth: 1 });
    text(s, n, 772, y + 18, 44, 24, { size: 14, bold: true, color: i === 1 ? C.gold : C.green, typeface: SERIF });
    text(s, h, 828, y + 14, 310, 28, { size: 19, bold: true, color: i === 1 ? C.white : C.ink });
    text(s, b, 828, y + 48, 310, 30, { size: 14, color: i === 1 ? C.sage : C.gray });
  });
  text(s, "一张图 + 一个判断 + 三条解释", 752, 626, 420, 24, { size: 13, bold: true, color: C.green });
}

// 08 — visual gallery
{
  const s = p.slides.add();
  base(s, 8, false, "VISUAL GALLERY");
  titleBlock(s, "Three views", "用三种视角，解释同一个主题", "适合案例、产品、实验过程和阶段成果。", false);
  const captions = [["01", "全景", "建立背景与尺度"], ["02", "细节", "突出关键差异"], ["03", "结果", "让价值可以被看见"]];
  captions.forEach(([n, h, b], i) => {
    const x = 72 + i * 382;
    rect(s, x, 282, 342, 252, i === 1 ? C.sage : C.pale, { line: C.line, lineWidth: 1, name: `gallery-frame-${i + 1}` });
    rect(s, x, 534, 342, 78, i === 1 ? C.forest : C.white, { line: C.line, lineWidth: 1 });
    text(s, n, x + 18, 552, 44, 22, { size: 14, bold: true, color: C.gold, typeface: SERIF });
    text(s, h, x + 66, 548, 100, 28, { size: 19, bold: true, color: i === 1 ? C.white : C.ink });
    text(s, b, x + 18, 582, 300, 22, { size: 13, color: i === 1 ? C.sage : C.gray });
  });
}

// 09 — evidence columns
{
  const s = p.slides.add();
  base(s, 9, false, "EVIDENCE FRAME");
  titleBlock(s, "Three signals", "三个证据，共同支持一个判断", "横向比较时保持同一尺度，避免把信息堆成卡片墙。", false);
  const cols = [["72%", "需求已经出现", "受访者主动提出更快、更简单的流程。"], ["2.4×", "效率可以提升", "重复工作被压缩，\n团队把时间留给判断。"], ["18%", "风险仍需管理", "必须保留人工复核和来源追踪。"]];
  cols.forEach(([metric, h, b], i) => {
    const x = 72 + i * 382;
    const dark = i === 1;
    rect(s, x, 292, 342, 324, dark ? C.forest : C.white, { line: dark ? C.forest : C.line, lineWidth: 1 });
    rect(s, x, 292, 342, 8, dark ? C.gold : C.green);
    text(s, metric, x + 24, 330, 292, 78, { size: 52, bold: true, color: dark ? C.gold : C.green, typeface: SERIF });
    text(s, h, x + 24, 430, 292, 34, { size: 22, bold: true, color: dark ? C.white : C.ink });
    text(s, b, x + 24, 484, 292, 72, { size: 16, color: dark ? C.sage : C.gray });
    smallRule(s, x + 24, 570, 52, dark ? C.gold : C.green);
    text(s, ["SIGNAL / DEMAND", "SIGNAL / SPEED", "SIGNAL / CONTROL"][i], x + 24, 584, 260, 20, { size: 11, bold: true, color: dark ? C.sage : C.gray });
  });
}

// 10 — process
{
  const s = p.slides.add();
  base(s, 10, true, "PROCESS / HOW IT WORKS");
  titleBlock(s, "Four steps", "从零散材料到可讲述的演示", "默认自动完成，用户只需提供内容。", true);
  rect(s, 72, 372, 1136, 6, C.sage);
  const items = [["01", "诊断", "识别受众与目标"], ["02", "组织", "形成故事线"], ["03", "匹配", "选择最佳版式"], ["04", "质检", "渲染并修正"]];
  items.forEach(([n, h, b], i) => {
    const x = 72 + i * 284;
    rect(s, x, 340, 70, 70, i === 2 ? C.gold : C.green2, { geometry: "ellipse" });
    text(s, n, x, 361, 70, 28, { size: 18, bold: true, color: i === 2 ? C.forest : C.white, align: "center", typeface: SERIF });
    text(s, h, x, 440, 230, 34, { size: 22, bold: true, color: C.white });
    text(s, b, x, 490, 224, 52, { size: 15, color: C.sage });
  });
  rect(s, 0, 584, 1280, 136, "#123F30");
  [["INPUT", "原始材料"], ["MAP", "故事结构"], ["LAYOUT", "可编辑页面"], ["QA", "渲染成品"]].forEach(([k, v], i) => {
    const x = 72 + i * 284;
    if (i) rect(s, x - 22, 612, 1, 62, C.green2);
    text(s, k, x, 612, 100, 22, { size: 11, bold: true, color: C.gold });
    text(s, v, x, 642, 220, 30, { size: 18, bold: true, color: C.white });
  });
  text(s, "10", 1160, 680, 48, 20, { size: 12, color: C.sage, align: "right" });
}

// 11 — timeline
{
  const s = p.slides.add();
  base(s, 11, false, "TIMELINE");
  titleBlock(s, "Momentum", "把时间线写成变化，而不是日期清单", "每个节点只回答：发生了什么，以及它为何改变下一步。", false);
  rect(s, 114, 392, 1040, 3, C.line);
  const years = [["2022", "验证问题"], ["2023", "形成方法"], ["2024", "扩大应用"], ["2025", "建立标准"], ["2026", "规模化"]];
  years.forEach(([year, h], i) => {
    const x = 114 + i * 260;
    rect(s, x, 373, 40, 40, i === 3 ? C.gold : C.green, { geometry: "ellipse" });
    text(s, year, x - 24, 316, 88, 28, { size: 16, bold: true, color: i === 3 ? C.gold : C.green, align: "center", typeface: SERIF });
    text(s, h, x - 50, 438, 140, 32, { size: 18, bold: true, align: "center" });
    text(s, "一个可验证的阶段结果", x - 64, 486, 168, 54, { size: 14, color: C.gray, align: "center" });
  });
}

// 12 — comparison
{
  const s = p.slides.add();
  base(s, 12, false, "COMPARISON");
  titleBlock(s, "Before / after", "对比的重点，是变化带来的意义", "使用同一维度和同一尺度，避免左右两边各说各话。", false);
  rect(s, 72, 300, 500, 280, C.pale, { radius: "rounded-2xl" });
  rect(s, 708, 300, 500, 280, C.forest, { radius: "rounded-2xl" });
  text(s, "过去", 112, 332, 160, 36, { size: 24, bold: true, color: C.green });
  text(s, "材料分散\n结构依赖个人经验\n修改成本高", 112, 402, 360, 126, { size: 20, color: C.gray, lineSpacing: 1.22 });
  text(s, "现在", 748, 332, 160, 36, { size: 24, bold: true, color: C.gold });
  text(s, "自动诊断\n按任务匹配版式\n全套渲染质检", 748, 402, 360, 126, { size: 20, color: C.white, lineSpacing: 1.22 });
  rect(s, 610, 412, 60, 60, C.gold, { geometry: "ellipse" });
  text(s, "→", 610, 422, 60, 36, { size: 28, bold: true, color: C.forest, align: "center" });
}

// 13 — KPI + bar chart
{
  const s = p.slides.add();
  base(s, 13, false, "DATA / BAR CHART");
  titleBlock(s, "Decision metric", "效率提升来自流程简化，而非减少判断", "用一个主指标和一张图回答问题。", false);
  text(s, "2.4×", 72, 316, 280, 88, { size: 62, bold: true, color: C.green, typeface: SERIF });
  text(s, "交付速度", 72, 418, 280, 34, { size: 22, bold: true });
  text(s, "从整理到初稿的平均时间", 72, 468, 280, 50, { size: 15, color: C.gray });
  s.charts.add("bar", {
    position: { left: 386, top: 294, width: 790, height: 300 },
    categories: ["材料整理", "故事组织", "版式制作", "最终质检"],
    series: [{ name: "分钟", values: [42, 31, 18, 14], fill: C.green }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 46 },
    hasLegend: false,
    xAxis: { visible: false, majorGridlines: null },
    yAxis: { textStyle: { fill: C.gray, fontSize: 14 }, line: { style: "solid", fill: C.line, width: 1 } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fill: C.ink, fontSize: 14, bold: true } },
    chartFill: C.cream,
    plotAreaFill: C.cream,
  });
}

// 14 — line chart
{
  const s = p.slides.add();
  base(s, 14, false, "DATA / TREND");
  titleBlock(s, "Trend + meaning", "质量提升发生在每一次复用之后", "趋势图负责显示变化，右侧结论负责解释变化。", false);
  s.charts.add("line", {
    position: { left: 72, top: 292, width: 720, height: 302 },
    categories: ["第1次", "第2次", "第3次", "第4次", "第5次"],
    series: [{ name: "完成度", values: [0.58, 0.66, 0.74, 0.85, 0.92], line: { style: "solid", fill: C.green, width: 4 }, marker: { symbol: "circle", size: 8 } }],
    hasLegend: false,
    yAxis: { min: 0.4, max: 1, numberFormatCode: "0%", majorGridlines: { style: "solid", fill: C.line, width: 1 }, textStyle: { fill: C.gray, fontSize: 12 } },
    xAxis: { textStyle: { fill: C.gray, fontSize: 12 }, line: { style: "solid", fill: C.line, width: 1 } },
    chartFill: C.cream,
    plotAreaFill: C.cream,
  });
  rect(s, 838, 314, 338, 230, C.forest, { radius: "rounded-2xl" });
  text(s, "+34pt", 878, 348, 250, 72, { size: 46, bold: true, color: C.gold, typeface: SERIF });
  text(s, "复用带来的质量增益", 878, 438, 250, 32, { size: 20, bold: true, color: C.white });
  text(s, "把经验写进资源，而不是留在个人记忆里。", 878, 486, 250, 50, { size: 15, color: C.sage });
}

// 15 — doughnut chart
{
  const s = p.slides.add();
  base(s, 15, false, "DATA / COMPOSITION");
  titleBlock(s, "Composition", "一套好演示，时间应该花在哪里", "结构和证据优先，装饰只负责强化层级。", false);
  s.charts.add("doughnut", {
    position: { left: 72, top: 286, width: 520, height: 326 },
    categories: ["结构", "证据", "视觉", "装饰"],
    series: [{ name: "投入", values: [35, 30, 25, 10], points: [{ idx: 0, fill: C.forest }, { idx: 1, fill: C.green }, { idx: 2, fill: C.sage }, { idx: 3, fill: C.gold }] }],
    doughnutOptions: { holeSize: 62, firstSliceAngle: 270 },
    hasLegend: false,
    dataLabels: { showPercent: true, position: "outEnd", textStyle: { fill: C.ink, fontSize: 13, bold: true } },
    chartFill: C.cream,
    plotAreaFill: C.cream,
  });
  const parts = [["结构", "35%", C.forest], ["证据", "30%", C.green], ["视觉", "25%", C.sage], ["装饰", "10%", C.gold]];
  parts.forEach(([label, value, color], i) => {
    const y = 314 + i * 66;
    rect(s, 680, y + 4, 18, 18, color, { geometry: "ellipse" });
    text(s, label, 720, y, 140, 28, { size: 18, bold: true });
    text(s, value, 1030, y, 110, 28, { size: 18, bold: true, color, align: "right", typeface: SERIF });
    smallRule(s, 720, y + 42, 420, C.line);
  });
}

// 16 — method flow
{
  const s = p.slides.add();
  base(s, 16, true, "RESEARCH METHOD");
  titleBlock(s, "Method", "方法页要让过程可复核", "用输入、处理、验证、输出四个环节建立可信度。", true);
  const items = [["输入", "原始材料\n数据与来源"], ["处理", "归纳主题\n提取证据"], ["验证", "核对事实\n检查偏差"], ["输出", "形成结论\n给出行动"]];
  items.forEach(([h, b], i) => {
    const x = 72 + i * 284;
    rect(s, x, 318, 242, 222, i === 2 ? C.gold : C.green2, { radius: "rounded-2xl" });
    text(s, String(i + 1).padStart(2, "0"), x + 28, 342, 72, 32, { size: 18, bold: true, color: i === 2 ? C.forest : C.gold, typeface: SERIF });
    text(s, h, x + 28, 398, 184, 36, { size: 24, bold: true, color: i === 2 ? C.forest : C.white });
    text(s, b, x + 28, 456, 184, 58, { size: 16, color: i === 2 ? C.forest : C.sage, lineSpacing: 1.18 });
  });
}

// 17 — findings matrix
{
  const s = p.slides.add();
  base(s, 17, false, "FINDINGS MATRIX");
  titleBlock(s, "Two dimensions", "用二维矩阵，把信息转成优先级", "横轴表示价值，纵轴表示可行性。", false);
  rect(s, 184, 300, 590, 300, C.white, { line: C.line, lineWidth: 1 });
  rect(s, 479, 300, 1, 300, C.line);
  rect(s, 184, 450, 590, 1, C.line);
  text(s, "高可行性", 84, 306, 84, 28, { size: 14, bold: true, color: C.gray, align: "right" });
  text(s, "低可行性", 84, 558, 84, 28, { size: 14, bold: true, color: C.gray, align: "right" });
  text(s, "低价值", 184, 614, 100, 24, { size: 14, bold: true, color: C.gray });
  text(s, "高价值", 674, 614, 100, 24, { size: 14, bold: true, color: C.gray, align: "right" });
  [[310, 500, 70, C.sage], [550, 364, 98, C.green], [674, 332, 54, C.gold], [372, 414, 48, C.green2], [604, 486, 76, C.forest]].forEach(([x, y, d, color]) => rect(s, x, y, d, d, color, { geometry: "ellipse" }));
  rect(s, 838, 324, 338, 242, C.pale, { radius: "rounded-2xl" });
  text(s, "优先做", 878, 356, 250, 34, { size: 24, bold: true, color: C.green });
  text(s, "高价值、低阻力的事项\n立即进入下一轮验证", 878, 420, 250, 88, { size: 18, color: C.ink, lineSpacing: 1.2 });
}

// 18 — risk matrix
{
  const s = p.slides.add();
  base(s, 18, false, "RISK MATRIX");
  titleBlock(s, "Risk + response", "风险页必须同时给出应对方式", "只标红问题没有价值；明确触发条件、负责人和动作。", false);
  const colors = [[C.pale, C.pale, "#F5E4BC"], [C.pale, "#F5E4BC", "#EBC17A"], ["#F5E4BC", "#EBC17A", C.gold]];
  colors.forEach((row, r) => row.forEach((color, c) => rect(s, 118 + c * 130, 336 + (2 - r) * 90, 118, 78, color, { radius: "rounded-md" })));
  text(s, "影响", 72, 292, 70, 24, { size: 14, bold: true, color: C.gray });
  text(s, "发生概率 →", 118, 620, 378, 24, { size: 14, bold: true, color: C.gray, align: "center" });
  [["A", 405, 360], ["B", 278, 454], ["C", 402, 540]].forEach(([label, x, y], i) => {
    rect(s, x, y, 34, 34, i === 0 ? C.forest : C.green, { geometry: "ellipse" });
    text(s, label, x, y + 7, 34, 18, { size: 12, bold: true, color: C.white, align: "center" });
  });
  const risks = [["A", "事实错误", "关键数据逐项复核"], ["B", "信息泄露", "输入内容分级处理"], ["C", "视觉失真", "全套渲染后再交付"]];
  risks.forEach(([n, h, b], i) => addBullet(s, n.charCodeAt(0) - 64, h, b, 614, 324 + i * 90, 520));
}

// 19 — quote / proof point
{
  const s = p.slides.add();
  base(s, 19, true, "CASE / QUOTE");
  text(s, "“", 72, 118, 110, 96, { size: 88, bold: true, color: C.gold, typeface: SERIF });
  text(s, "用户不需要学会设计，\n只需要把真实材料\n交给系统。", 150, 158, 640, 190, { size: 44, bold: true, color: C.white, lineSpacing: 0.92 });
  smallRule(s, 152, 382, 220, C.sage);
  text(s, "— 资源型 skill 的产品原则", 152, 414, 560, 32, { size: 18, color: C.sage });
  rect(s, 846, 112, 362, 472, "#123F30", { line: C.green2, lineWidth: 1 });
  const stats = [["1", "推荐方向"], ["2", "必要问题上限"], ["100%", "逐页渲染质检"]];
  stats.forEach(([n, h], i) => {
    const y = 154 + i * 128;
    if (i) smallRule(s, 878, y - 20, 298, C.green2);
    text(s, n, 878, y, 112, 54, { size: 40, bold: true, color: C.gold, typeface: SERIF });
    text(s, h, 1002, y + 10, 174, 30, { size: 16, bold: true, color: C.white });
  });
  rect(s, 72, 526, 708, 58, C.green2);
  text(s, "RAW MATERIAL → CLEAR STORY → EDITABLE DECK → RENDER QA", 98, 544, 656, 24, { size: 13, bold: true, color: C.white });
}

// 20 — closing
{
  const s = p.slides.add();
  base(s, 20, false, "CLOSING / NEXT ACTION");
  text(s, "好的演示，\n让下一步变得简单。", 72, 128, 700, 130, { size: 50, bold: true, lineSpacing: 0.9 });
  text(s, "把材料交进来，剩下的由 skill 完成。", 72, 290, 650, 38, { size: 20, color: C.gray });
  const actions = [["01", "提供材料"], ["02", "确认听众与时长"], ["03", "领取可编辑成品"]];
  actions.forEach(([n, h], i) => {
    const x = 72 + i * 284;
    rect(s, x, 422, 242, 126, i === 2 ? C.forest : C.pale, { radius: "rounded-2xl" });
    text(s, n, x + 24, 444, 58, 24, { size: 15, bold: true, color: i === 2 ? C.gold : C.green, typeface: SERIF });
    text(s, h, x + 24, 492, 194, 34, { size: 20, bold: true, color: i === 2 ? C.white : C.ink });
  });
  rect(s, 1002, 112, 206, 456, C.gold);
  text(s, "READY", 1022, 180, 166, 48, { size: 30, bold: true, color: C.forest, align: "center", typeface: SERIF });
  text(s, "TO\nPRESENT", 1022, 268, 166, 130, { size: 32, bold: true, color: C.forest, align: "center", lineSpacing: 0.9, typeface: SERIF });
}

await fs.mkdir(qaDir, { recursive: true });
for (const [index, slide] of p.slides.items.entries()) {
  const stem = `slide-${String(index + 1).padStart(2, "0")}`;
  await writeBlob(path.join(qaDir, `${stem}.png`), await p.export({ slide, format: "png", scale: 1 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(qaDir, `${stem}.layout.json`), await layout.text(), "utf8");
}
await writeBlob(previewFile, await p.export({ format: "webp", montage: true, scale: 1 }));
const snapshot = await p.inspect({ kind: "slide,textbox,shape,image,chart", maxChars: 12000 });
await fs.writeFile(path.join(qaDir, "inspect.ndjson"), snapshot.ndjson, "utf8");
const pptx = await PresentationFile.exportPptx(p);
await fs.mkdir(path.dirname(outFile), { recursive: true });
await pptx.save(outFile);
await fs.rm(`${outFile}.inspect.ndjson`, { force: true });
console.log(JSON.stringify({ outFile, previewFile, slides: p.slides.items.length }));
