const bridge = window.AstrBotPluginPage;
const $ = (id) => document.getElementById(id);

await bridge.ready();

const fields = {
  bubble_x1: "x1",
  bubble_y1: "y1",
  bubble_x2: "x2",
  bubble_y2: "y2",
  base_font_size: "base_font",
  min_font_size: "min_font",
  line_spacing_ratio: "line_spacing",
  text_color: "text_color",
  font_path: "font_path",
  text_align_h: "align_h",
  text_align_v: "align_v",
  box_padding: "padding",
  wrap_text: "wrap",
};

function fillForm(cfg) {
  for (const [key, id] of Object.entries(fields)) {
    const el = $(id);
    if (el.type === "checkbox") {
      el.checked = !!cfg[key];
    } else if (el.type === "color") {
      el.value = /^#[0-9a-fA-F]{6}$/.test(cfg[key] || "") ? cfg[key] : "#000000";
    } else {
      el.value = cfg[key] ?? "";
    }
  }
}

function readForm() {
  const payload = { text: $("text").value };
  for (const [key, id] of Object.entries(fields)) {
    const el = $(id);
    payload[key] = el.type === "checkbox" ? el.checked : el.value;
  }
  return payload;
}

function setStatus(text, ok = false) {
  const status = $("status");
  status.textContent = text;
  status.className = ok ? "ok" : "error";
}

// ---- 文字框拖拽 ----
const img = $("result");
const box = $("box");
let scale = 1;

function currentScale() {
  if (!img.naturalWidth) return 0;
  const rect = img.getBoundingClientRect();
  return rect.width / img.naturalWidth;
}

function syncBox() {
  const s = currentScale();
  if (!s) return;
  scale = s;
  const x1 = +$("x1").value || 0;
  const y1 = +$("y1").value || 0;
  const x2 = +$("x2").value || 0;
  const y2 = +$("y2").value || 0;
  box.style.left = x1 * s + "px";
  box.style.top = y1 * s + "px";
  box.style.width = Math.max(0, x2 - x1) * s + "px";
  box.style.height = Math.max(0, y2 - y1) * s + "px";
  box.style.display = img.hidden ? "none" : "block";
}

function setCoords(x1, y1, x2, y2) {
  $("x1").value = Math.round(x1);
  $("y1").value = Math.round(y1);
  $("x2").value = Math.round(x2);
  $("y2").value = Math.round(y2);
}

let drag = null;
let drawMode = false;
let drawing = null;

function clientToImg(e) {
  const rect = img.getBoundingClientRect();
  return {
    x: (e.clientX - rect.left) / scale,
    y: (e.clientY - rect.top) / scale,
  };
}

function beginDrag(e, mode) {
  if (drawMode || !img.naturalWidth) return;
  e.preventDefault();
  e.stopPropagation();
  drag = {
    mode,
    startX: e.clientX,
    startY: e.clientY,
    x1: +$("x1").value,
    y1: +$("y1").value,
    x2: +$("x2").value,
    y2: +$("y2").value,
  };
  window.addEventListener("pointermove", onDrag);
  window.addEventListener("pointerup", endDrag);
}

function onDrag(e) {
  if (!drag) return;
  const dx = (e.clientX - drag.startX) / scale;
  const dy = (e.clientY - drag.startY) / scale;
  const { mode, x1, y1, x2, y2 } = drag;
  const nw = img.naturalWidth;
  const min = 10;
  let nx1 = x1, ny1 = y1, nx2 = x2, ny2 = y2;
  if (mode === "move") {
    nx1 = x1 + dx; ny1 = y1 + dy; nx2 = x2 + dx; ny2 = y2 + dy;
    if (nx1 < 0) { nx2 -= nx1; nx1 = 0; }
    if (ny1 < 0) { ny2 -= ny1; ny1 = 0; }
    if (nx2 > nw) { nx1 -= nx2 - nw; nx2 = nw; }
    if (ny2 > nw) { ny1 -= ny2 - nw; ny2 = nw; }
  } else if (mode === "nw") { nx1 = x1 + dx; ny1 = y1 + dy; }
  else if (mode === "ne") { nx2 = x2 + dx; ny1 = y1 + dy; }
  else if (mode === "sw") { nx1 = x1 + dx; ny2 = y2 + dy; }
  else if (mode === "se") { nx2 = x2 + dx; ny2 = y2 + dy; }
  nx1 = Math.max(0, Math.min(nx1, nw - min));
  ny1 = Math.max(0, Math.min(ny1, nw - min));
  nx2 = Math.max(nx1 + min, Math.min(nx2, nw));
  ny2 = Math.max(ny1 + min, Math.min(ny2, nw));
  setCoords(nx1, ny1, nx2, ny2);
  syncBox();
}

function endDrag() {
  drag = null;
  window.removeEventListener("pointermove", onDrag);
  window.removeEventListener("pointerup", endDrag);
}

box.addEventListener("pointerdown", (e) => beginDrag(e, "move"));
for (const [id, mode] of [
  ["h-nw", "nw"],
  ["h-ne", "ne"],
  ["h-sw", "sw"],
  ["h-se", "se"],
]) {
  $(id).addEventListener("pointerdown", (e) => beginDrag(e, mode));
}

$("preview-wrap").addEventListener("pointerdown", (e) => {
  if (!drawMode) return;
  e.preventDefault();
  drawing = clientToImg(e);
  setCoords(drawing.x, drawing.y, drawing.x, drawing.y);
  syncBox();
  window.addEventListener("pointermove", onDraw);
  window.addEventListener("pointerup", endDraw);
});

function onDraw(e) {
  if (!drawing) return;
  const p = clientToImg(e);
  const x1 = Math.min(drawing.x, p.x);
  const y1 = Math.min(drawing.y, p.y);
  const x2 = Math.max(drawing.x, p.x);
  const y2 = Math.max(drawing.y, p.y);
  setCoords(x1, y1, x2, y2);
  syncBox();
}

function endDraw() {
  drawing = null;
  drawMode = false;
  window.removeEventListener("pointermove", onDraw);
  window.removeEventListener("pointerup", endDraw);
  setStatus("已绘制新范围，可拖动微调，点击「渲染预览」查看效果。", true);
}

img.addEventListener("load", syncBox);
window.addEventListener("resize", syncBox);

// ---- 按钮 ----
$("load").addEventListener("click", async () => {
  try {
    const cfg = await bridge.apiGet("config");
    fillForm(cfg);
    syncBox();
    setStatus("已加载当前配置。", true);
  } catch (error) {
    setStatus("加载配置失败：" + error.message);
  }
});

$("redraw").addEventListener("click", () => {
  drawMode = true;
  setStatus("绘制模式：请在模板图上按住鼠标拖拽，画出新的文字范围。");
});

$("preview").addEventListener("click", async () => {
  setStatus("渲染中…");
  try {
    const result = await bridge.apiPost("preview", readForm());
    img.src = result.image;
    img.hidden = false;
    setStatus("预览渲染完成，可拖动红色文字框微调。", true);
  } catch (error) {
    setStatus("渲染失败：" + error.message);
  }
});

$("save").addEventListener("click", async () => {
  try {
    const result = await bridge.apiPost("config", readForm());
    setStatus("配置已保存：" + JSON.stringify(result.updated), true);
  } catch (error) {
    setStatus("保存失败：" + error.message);
  }
});

fillForm({
  bubble_x1: 200,
  bubble_y1: 200,
  bubble_x2: 450,
  bubble_y2: 600,
  base_font_size: 48,
  min_font_size: 24,
  line_spacing_ratio: 1.25,
  text_color: "#000000",
  font_path: "",
  text_align_h: "center",
  text_align_v: "middle",
  box_padding: 10,
  wrap_text: true,
});

try {
  const template = await bridge.apiGet("template");
  img.src = template.image;
  img.hidden = false;
} catch (error) {
  setStatus("模板图加载失败：" + error.message);
}
