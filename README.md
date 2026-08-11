# astrbot_plugin_feiyusays
大肥鱼有话说
高度ai开发，感谢大肥鱼
## 简介

收到形如「肥鱼说 + 一句话」的消息时，机器人把这句话渲染进模板图片（自带 Q 版猫耳女仆角色 + 思想气泡）的对话气泡中，然后以图片形式回复。支持在 **WebUI 中像 PPT 文字框一样拖拽绘制文字区域**，所见即所得。

## 特性

- 🖼️ 文字自动换行渲染进气泡，效果稳定不依赖第三方文生图服务
- 📐 **WebUI 拖拽绘制文字范围**：重新绘制 / 拖动移动 / 拖角缩放，坐标实时同步
- ✍️ 字号策略：优先首选字号，仅当文字**快要放不下时最小幅度缩小**，极限截断加省略号
- 🎨 支持水平/垂直对齐、框内边距、自动换行开关、文字颜色、自定义字体
- 🖥️ Windows / Linux 自动选择系统中文字体（微软雅黑 / Noto Sans CJK SC）
- ⚙️ 全部参数可在 AstrBot WebUI 配置页修改，即时生效

## 效果示例

| 短句 | 长句（自动缩小字号） |
| --- | --- |
| ![短句](docs/screenshot.jpg) | 可在 WebUI「气泡预览」页自行体验 |

## 安装

### 方式一：下载 zip

1. 下载 [astrbot_plugin_feiyusays.zip](https://github.com/你的用户名/astrbot_plugin_feiyusays/releases)（或本仓库 `Download ZIP` 后解压）
2. 将 `astrbot_plugin_feiyusays` 文件夹放入 `AstrBot/data/plugins/` 目录
3. 重启 AstrBot（或在 WebUI 插件页启用该插件），依赖 `pillow` 会在加载时自动安装

### 方式二：Git 克隆

```bash
cd AstrBot/data/plugins
git clone https://github.com/1570342081-commits/astrbot_plugin_feiyusays.git
```

## 使用方法

在群聊或私聊中发送：

```
肥鱼说 今天也要加油鸭！
```

机器人会回复一张渲染好的气泡图片。

- 空指令（只有「肥鱼说」）会返回用法提示：`用法：肥鱼说 <要说的话>`
- 文字中带换行符（`\n`）时按行渲染
- 指令词可通过配置项 `command_keyword` 修改

## WebUI 气泡预览

进入 AstrBot WebUI → 插件 → 肥鱼说 →「气泡预览」页面：

1. 页面自动加载模板图，红色虚线框即文字区域
2. 点「**重新绘制范围**」，在图上按住鼠标拖拽画出文字区域
3. 拖动红框移动位置，拖四角调整大小（同 PPT 文字框）
4. 输入文字 →「渲染预览」实时查看效果
5. 点「保存配置」立即生效；「加载当前配置」回读

> 坐标输入框（x1/y1/x2/y2）为高级选项，与图形框实时双向同步。

## 配置项

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `command_keyword` | `肥鱼说` | 触发指令词 |
| `bubble_x1 / bubble_y1` | `200 / 200` | 文字框左上角坐标（像素，模板左上角为原点） |
| `bubble_x2 / bubble_y2` | `450 / 600` | 文字框右下角坐标 |
| `base_font_size` | `48` | 首选字号 |
| `min_font_size` | `24` | 最小字号，缩到该值仍放不下则截断 |
| `line_spacing_ratio` | `1.25` | 行间距倍率 |
| `max_text_len` | `200` | 单条消息最大字符数 |
| `font_path` | 空 | 自定义字体路径，留空自动选择 |
| `text_color` | `#000000` | 文字颜色（十六进制） |
| `text_align_h` | `center` | 水平对齐：`left` / `center` / `right` |
| `text_align_v` | `middle` | 垂直对齐：`top` / `middle` / `bottom` |
| `box_padding` | `10` | 文字框内边距（像素） |
| `wrap_text` | `true` | 自动换行；关闭后单行显示，超出宽度截断 |

## 字体说明

- **Windows**：自动使用微软雅黑粗体（`msyhbd.ttc`）
- **Linux**：自动使用 Noto Sans CJK SC，未安装时执行 `apt install -y fonts-noto-cjk`，或用 `font_path` 指定其他中文字体
- 自定义字体：将 `font_path` 设为字体文件完整路径即可

## 更换模板图片

直接替换插件目录 `res/template.jpg`（建议 1:1 方形图），然后在 WebUI 中重新绘制文字区域。本仓库自带模板为 Q 版猫耳女仆角色的思想气泡图（1254×1254）。

## 目录结构

```
astrbot_plugin_feiyusays/
├── main.py               # 插件主逻辑 + WebUI 后端 API
├── renderer.py           # 文字渲染逻辑（纯 Pillow，无 AstrBot 依赖）
├── metadata.yaml         # 插件元数据
├── _conf_schema.json     # 插件配置 Schema
├── requirements.txt      # 依赖（pillow）
├── README.md
├── docs/
│   └── screenshot.jpg    # 效果示例图
├── pages/
│   └── bubble/           # WebUI 气泡预览页面
│       ├── index.html
│       └── app.js
└── res/
    └── template.jpg      # 模板图片
```

## 常见问题

**Q：机器人收到消息不回复？**
检查指令词是否带空格（应为「肥鱼说 + 空格 + 文字」），并确认插件已启用。

**Q：渲染出的文字是方块/乱码？**
中文字体缺失。Linux 安装 `fonts-noto-cjk`，或配置 `font_path` 指定中文字体。

**Q：emoji 显示异常？**
Pillow 默认不渲染 emoji，会显示为空白/方块，属已知限制。
