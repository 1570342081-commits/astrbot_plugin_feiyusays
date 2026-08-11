# astrbot_plugin_feiyusays（肥鱼说）

把用户指令中的文字自动换行并渲染到模板图片的对话气泡中，以图片形式回复。

## 使用方法

在群聊或私聊中发送：

```
肥鱼说 今天也要加油鸭！
```

机器人会把「今天也要加油鸭！」渲染进模板图片的气泡框并回复图片。

- 空指令（只有「肥鱼说」）会返回用法提示。
- 文字优先使用首选字号，仅当文字快要超出文字框时才缩小字号，且只缩小到刚好放得下的程度；缩到最小字号仍放不下时截断并加省略号。
- 换行符支持：文字中含 `\n` 会按行渲染。

## 指令词

默认指令词为 `肥鱼说`，可在插件配置页修改 `command_keyword`。

## WebUI

插件详情页提供「气泡预览」页面，进入后自动加载模板图，支持像 PPT 文字框一样编辑文字框：

- 点「**重新绘制范围**」，在模板图上按住鼠标拖拽，画出文字显示的区域。
- 直接拖动红色文字框移动位置，拖四角调整大小（同 PPT 文字框）。
- 文字框属性：水平/垂直对齐（左中右、上中下）、框内边距、自动换行开关。
- 坐标输入框（x1/y1/x2/y2）为高级选项，与图形框实时同步。
- 字号优先用首选字号，文字快要放不下时才缩小，只缩到刚好放得下；缩到最小字号仍放不下则截断加省略号。
- 点「渲染预览」查看文字效果，「保存配置」立即生效，「加载当前配置」回读。

## 配置项

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `command_keyword` | `肥鱼说` | 触发指令词 |
| `bubble_x1 / bubble_y1` | `200 / 200` | 气泡内容区左上角坐标（像素） |
| `bubble_x2 / bubble_y2` | `450 / 600` | 气泡内容区右下角坐标（像素） |
| `base_font_size` | `48` | 首选字号 |
| `min_font_size` | `24` | 最小字号（文字快要放不下时才缩小，低于此字号截断文本） |
| `line_spacing_ratio` | `1.25` | 行间距倍率 |
| `max_text_len` | `200` | 单条消息最大字符数 |
| `font_path` | 空 | 自定义字体路径，留空自动选择 |
| `text_color` | `#000000` | 文字颜色 |
| `text_align_h` | `center` | 水平对齐：`left` / `center` / `right` |
| `text_align_v` | `middle` | 垂直对齐：`top` / `middle` / `bottom` |
| `box_padding` | `10` | 文字框内边距（像素） |
| `wrap_text` | `true` | 自动换行；关闭后单行显示，超出宽度截断 |

坐标以模板图片左上角为原点，单位为像素（模板尺寸 1254×1254）。

## 字体

- Windows：自动使用微软雅黑粗体（`msyhbd.ttc`）。
- Linux：自动使用 Noto Sans CJK SC（需安装 `fonts-noto-cjk`，如未安装可执行
  `apt install -y fonts-noto-cjk`，或通过 `font_path` 指定其他中文字体）。
- 自定义字体：在配置中设置 `font_path` 为字体文件完整路径。

## 模板图片

模板图片位于插件目录 `res/template.jpg`，替换该文件即可更换模板。
更换模板后请同步在 WebUI 中调整气泡坐标与字号。

## 已知限制

- 表情符号（emoji）无法用 Pillow 默认方式渲染，会显示为空白/方块。
- 发送图片时请确保机器人使用的平台适配器支持图片消息。

## 目录结构

```
astrbot_plugin_feiyusays/
├── main.py               # 插件主逻辑 + WebUI 后端 API
├── renderer.py           # 文字渲染逻辑（纯 Pillow，无 AstrBot 依赖）
├── metadata.yaml         # 插件元数据
├── _conf_schema.json     # 插件配置 Schema
├── requirements.txt      # 依赖（pillow）
├── README.md
├── pages/
│   └── bubble/           # WebUI 气泡预览页面
│       ├── index.html
│       └── app.js
└── res/
    └── template.jpg      # 模板图片
```

## 部署

1. 将 `astrbot_plugin_feiyusays` 目录复制到 `AstrBot/data/plugins/` 下。
2. 在 AstrBot WebUI 的插件页面启用该插件（或重启 AstrBot）。
3. 需要 Pillow，插件依赖会在加载时自动安装。
