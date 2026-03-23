# astrbot_plugin_payment_qr
自制的astrbot插件，你的bot会觉得自己缺钱吗？找别人主动要钱吧！
## 功能

- **关键词触发**：当用户消息中包含预设关键词（如"付款"、"转账"、"多少钱"等）时，自动发送收款码图片
- **模糊匹配**：支持语义模糊匹配，例如"付个款"、"怎么付钱"都能触发
- **可配置**：关键词、图片路径、回复文字均可在 WebUI 中配置
- **手动指令**：发送 `/payment_qr` 可手动触发发送收款码

## 安装

将本插件目录放入 AstrBot 的 `data/plugins/` 目录下，然后在 WebUI 中重载插件。

## 配置

在 WebUI 的插件管理中配置以下选项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| enabled | 是否启用 | true |
| qr_image_path | 收款码图片路径 | （需手动设置） |
| keywords | 触发关键词列表 | 付款、转账、打赏等 |
| reply_text | 附带的回复文字 | "请扫描下方收款码完成付款~" |
| match_mode | 匹配模式（fuzzy/exact） | fuzzy |

### 图片路径说明

- 相对路径（如 `payment_qr.png`）：会在 AstrBot 的 `data/` 目录下查找
- 绝对路径（如 `/home/user/images/qr.png`）：直接使用该路径

## 指令

| 指令 | 说明 |
|------|------|
| `/payment_qr` | 手动发送收款码 |
| `/payment_qr_reload` | 重新加载插件配置 |

