import base64

from astrbot.api import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api.web import error_response, json_response, request

from .renderer import BubbleRenderer, TEMPLATE_PATH

PLUGIN_NAME = "feiyusays"

DEFAULTS = {
    "command_keyword": "肥鱼说",
    "bubble_x1": 200,
    "bubble_y1": 200,
    "bubble_x2": 450,
    "bubble_y2": 600,
    "base_font_size": 48,
    "min_font_size": 24,
    "line_spacing_ratio": 1.25,
    "max_text_len": 200,
    "font_path": "",
    "text_color": "#000000",
    "text_align_h": "center",
    "text_align_v": "middle",
    "box_padding": 10,
    "wrap_text": True,
}

INT_KEYS = (
    "bubble_x1",
    "bubble_y1",
    "bubble_x2",
    "bubble_y2",
    "base_font_size",
    "min_font_size",
    "max_text_len",
    "box_padding",
)

BOOL_KEYS = ("wrap_text",)


class FeiyuSays(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context)
        self.config = config if isinstance(config, dict) else {}
        if hasattr(context, "register_web_api"):
            context.register_web_api(
                f"/{PLUGIN_NAME}/template",
                self.web_template,
                ["GET"],
                "获取模板图片",
            )
            context.register_web_api(
                f"/{PLUGIN_NAME}/preview",
                self.web_preview,
                ["POST"],
                "渲染气泡预览图",
            )
            context.register_web_api(
                f"/{PLUGIN_NAME}/config",
                self.web_config,
                ["GET", "POST"],
                "读取/保存插件配置",
            )

    def _cfg(self, key, default):
        value = self.config.get(key)
        return default if value in (None, "") else value

    def _build_renderer(self, overrides=None):
        def value(key):
            if overrides is not None and key in overrides:
                return overrides[key]
            return self._cfg(key, DEFAULTS[key])

        return BubbleRenderer(
            box=(
                value("bubble_x1"),
                value("bubble_y1"),
                value("bubble_x2"),
                value("bubble_y2"),
            ),
            base_font_size=value("base_font_size"),
            min_font_size=value("min_font_size"),
            line_spacing_ratio=value("line_spacing_ratio"),
            font_path=value("font_path"),
            text_color=value("text_color"),
            align_h=value("text_align_h"),
            align_v=value("text_align_v"),
            padding=value("box_padding"),
            wrap_text=value("wrap_text"),
        )

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        keyword = str(self._cfg("command_keyword", DEFAULTS["command_keyword"]))
        message_str = (event.message_str or "").strip()
        if not message_str.startswith(keyword):
            return
        text = message_str[len(keyword):].strip()
        if not text:
            yield event.plain_result(f"用法：{keyword} <要说的话>")
            return
        max_len = int(self._cfg("max_text_len", DEFAULTS["max_text_len"]))
        if len(text) > max_len:
            text = text[:max_len].rstrip() + "\u2026"
        try:
            renderer = self._build_renderer()
            output_path = renderer.render(text)
        except Exception as exc:
            logger.error(f"肥鱼说渲染失败: {exc}")
            yield event.plain_result(f"渲染失败：{exc}")
            return
        yield event.image_result(str(output_path))

    async def web_template(self):
        try:
            with open(TEMPLATE_PATH, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode()
        except Exception as exc:
            logger.error(f"肥鱼说模板图片读取失败: {exc}")
            return error_response(f"模板图片读取失败：{exc}")
        return json_response({"image": f"data:image/jpeg;base64,{image_b64}"})

    async def web_preview(self):
        payload = await request.json(default={})
        text = str(payload.get("text", "")).strip()
        if not text:
            return error_response("请输入要渲染的文字内容")
        overrides = {
            key: payload.get(key, self._cfg(key, DEFAULTS[key])) for key in DEFAULTS
        }
        try:
            renderer = self._build_renderer(overrides)
            output_path = renderer.render(text)
            with open(output_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode()
        except Exception as exc:
            logger.error(f"肥鱼说 WebUI 预览渲染失败: {exc}")
            return error_response(f"渲染失败：{exc}")
        return json_response({"image": f"data:image/jpeg;base64,{image_b64}"})

    async def web_config(self):
        if request.method == "GET":
            return json_response(
                {key: self._cfg(key, default) for key, default in DEFAULTS.items()}
            )
        payload = await request.json(default={})
        updated = {}
        for key, default in DEFAULTS.items():
            if key not in payload or payload[key] in (None, ""):
                continue
            raw = payload[key]
            try:
                if key in INT_KEYS:
                    value = int(raw)
                elif key in BOOL_KEYS:
                    value = bool(raw)
                elif key == "line_spacing_ratio":
                    value = float(raw)
                else:
                    value = str(raw)
            except (TypeError, ValueError):
                continue
            self.config[key] = value
            updated[key] = value
        saver = getattr(self.config, "save_config", None)
        if callable(saver):
            try:
                saver()
            except Exception as exc:
                logger.error(f"肥鱼说配置保存失败: {exc}")
        return json_response({"updated": updated})
