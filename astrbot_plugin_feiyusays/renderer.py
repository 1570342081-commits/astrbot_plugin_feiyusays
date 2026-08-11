import os
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DEFAULT_FONT_CANDIDATES = [
    ("C:/Windows/Fonts/msyhbd.ttc", 0),
    ("C:/Windows/Fonts/msyh.ttc", 0),
    ("C:/Windows/Fonts/simhei.ttf", 0),
    ("C:/Windows/Fonts/simsun.ttc", 0),
    ("C:/Windows/Fonts/simsun.ttf", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 2),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 2),
    ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
    ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", 0),
]

TEMPLATE_PATH = Path(__file__).parent / "res" / "template.jpg"


def parse_color(value):
    if isinstance(value, (tuple, list)):
        return tuple(int(c) for c in value[:3])
    s = str(value).strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    try:
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 0, 0)


class BubbleRenderer:
    def __init__(self, box=(200, 200, 450, 600), base_font_size=48,
                 min_font_size=24, line_spacing_ratio=1.25,
                 font_path="", text_color="#000000", align_h="center",
                 align_v="middle", padding=10, wrap_text=True):
        self.box = tuple(int(v) for v in box)
        self.base_font_size = int(base_font_size)
        self.min_font_size = int(min_font_size)
        self.line_spacing_ratio = max(1.0, float(line_spacing_ratio))
        self.font_path = str(font_path or "").strip()
        self.text_color = parse_color(text_color)
        self.align_h = str(align_h or "center").lower()
        if self.align_h not in ("left", "center", "right"):
            self.align_h = "center"
        self.align_v = str(align_v or "middle").lower()
        if self.align_v not in ("top", "middle", "bottom"):
            self.align_v = "middle"
        self.padding = max(0, int(padding))
        self.wrap_text = bool(wrap_text)
        self._template = None
        self._font_cache = {}
        self.last_font_size = None

    def _get_font(self, size):
        if size in self._font_cache:
            return self._font_cache[size]
        candidates = [(self.font_path, 0)] if self.font_path else DEFAULT_FONT_CANDIDATES
        font = None
        for path, index in candidates:
            if path and os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, size, index=index)
                    break
                except OSError:
                    continue
        if font is None:
            font = ImageFont.load_default(size)
        self._font_cache[size] = font
        return font

    def _load_template(self):
        if self._template is None:
            with Image.open(TEMPLATE_PATH) as img:
                self._template = img.convert("RGB").copy()
        return self._template.copy()

    @staticmethod
    def _wrap_text(draw, text, font, max_width):
        lines = []
        for raw_line in text.split("\n"):
            if not raw_line:
                lines.append("")
                continue
            current = ""
            for ch in raw_line:
                trial = current + ch
                if not current or draw.textlength(trial, font=font) <= max_width:
                    current = trial
                else:
                    lines.append(current)
                    current = ch
            lines.append(current)
        return lines

    @staticmethod
    def _truncate_with_ellipsis(draw, text, font, max_width):
        if draw.textlength(text, font=font) <= max_width:
            return text
        ellipsis = "\u2026"
        ellipsis_w = draw.textlength(ellipsis, font=font)
        if ellipsis_w >= max_width:
            return text
        result = text
        while result and draw.textlength(result + ellipsis, font=font) > max_width:
            result = result[:-1]
        return result + ellipsis

    def _split_lines(self, draw, text, font, content_w):
        if self.wrap_text:
            return self._wrap_text(draw, text, font, content_w)
        return text.split("\n")

    def _fits(self, draw, text, font, content_w, content_h):
        lines = self._split_lines(draw, text, font, content_w)
        line_h = int(font.size * self.line_spacing_ratio)
        width_ok = self.wrap_text or max(
            (draw.textlength(line, font=font) for line in lines), default=0
        ) <= content_w
        return width_ok and line_h * len(lines) <= content_h, lines

    def _truncate_to_fit(self, draw, text, font, content_w, content_h):
        line_h = int(font.size * self.line_spacing_ratio)
        all_lines = self._split_lines(draw, text, font, content_w)
        width_ok = self.wrap_text or max(
            (draw.textlength(line, font=font) for line in all_lines), default=0
        ) <= content_w
        max_lines = max(1, content_h // line_h)
        if len(all_lines) <= max_lines and width_ok:
            return all_lines
        lines = all_lines[:max_lines]
        last = lines[-1]
        if not last.endswith("\u2026"):
            lines[-1] = self._truncate_with_ellipsis(draw, last, font, content_w)
        return lines

    def render(self, text, output_path=None):
        text = (text or "").strip()
        if not text:
            raise ValueError("文本不能为空")
        x1, y1, x2, y2 = self.box
        if x2 <= x1 or y2 <= y1:
            raise ValueError("气泡区域坐标无效")
        pad = self.padding
        draw_x1, draw_y1 = x1 + pad, y1 + pad
        draw_x2, draw_y2 = x2 - pad, y2 - pad
        if draw_x2 <= draw_x1 or draw_y2 <= draw_y1:
            raise ValueError("气泡区域坐标或内边距无效")
        content_w = draw_x2 - draw_x1
        content_h = draw_y2 - draw_y1

        canvas = self._load_template()
        draw = ImageDraw.Draw(canvas)

        base_font = self._get_font(self.base_font_size)
        fits, lines = self._fits(draw, text, base_font, content_w, content_h)
        if fits:
            font_size, font, lines = self.base_font_size, base_font, lines
        else:
            lo, hi = self.min_font_size, self.base_font_size - 1
            best_size = None
            while lo <= hi:
                mid = (lo + hi) // 2
                cand_font = self._get_font(mid)
                cand_fits, cand_lines = self._fits(
                    draw, text, cand_font, content_w, content_h
                )
                if cand_fits:
                    best_size, best_lines, best_font = mid, cand_lines, cand_font
                    lo = mid + 1
                else:
                    hi = mid - 1
            if best_size is not None:
                font_size, font, lines = best_size, best_font, best_lines
            else:
                font = self._get_font(self.min_font_size)
                font_size = self.min_font_size
                lines = self._truncate_to_fit(
                    draw, text, font, content_w, content_h
                )
        self.last_font_size = font_size

        line_h = int(font_size * self.line_spacing_ratio)
        block_h = line_h * len(lines)
        center_x = (draw_x1 + draw_x2) // 2
        if self.align_v == "top":
            start_y = draw_y1
        elif self.align_v == "bottom":
            start_y = draw_y2 - block_h
        else:
            start_y = draw_y1 + (content_h - block_h) // 2
        for i, line in enumerate(lines):
            y = start_y + i * line_h + line_h // 2
            if self.align_h == "left":
                anchor, x = "lm", draw_x1
            elif self.align_h == "right":
                anchor, x = "rm", draw_x2
            else:
                anchor, x = "mm", center_x
            draw.text(
                (x, y),
                line,
                font=font,
                fill=self.text_color,
                anchor=anchor,
            )

        if output_path is None:
            output_path = os.path.join(
                tempfile.gettempdir(),
                f"feiyusays_{os.getpid()}_{abs(hash((text, x1, x2, y1, y2, font_size)))}.jpg",
            )
        canvas.save(output_path, "JPEG", quality=95)
        return output_path
