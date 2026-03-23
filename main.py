import os
import re

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp


class PaymentQRPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self._load_config()

    def _load_config(self):
        """加载配置"""
        self.qr_image_path = self.config.get("qr_image_path", "")
        self.keywords = self.config.get("keywords", [
            "付款", "转账", "打赏", "赞赏", "支付", "收款",
            "多少钱", "怎么付", "费用", "价格", "收费",
            "买单", "结账", "付钱", "给钱", "汇款",
        ])
        self.reply_text = self.config.get("reply_text", "请扫描下方收款码完成付款~")
        self.enabled = self.config.get("enabled", True)
        # 语义匹配模式：exact（精确包含关键词）或 fuzzy（模糊匹配，支持关键词拆字）
        self.match_mode = self.config.get("match_mode", "fuzzy")

        if self.qr_image_path and not os.path.isabs(self.qr_image_path):
            # 如果是相对路径，基于 data 目录解析
            self.qr_image_path = os.path.join("data", self.qr_image_path)

        if self.qr_image_path and os.path.exists(self.qr_image_path):
            logger.info(f"收款码插件已加载，图片路径: {self.qr_image_path}")
        else:
            logger.warning(f"收款码插件：图片路径未配置或文件不存在: {self.qr_image_path}")

    def _match_keywords(self, text: str) -> bool:
        """检查消息是否匹配关键词"""
        if not text:
            return False

        text_lower = text.lower()

        if self.match_mode == "exact":
            # 精确模式：消息中直接包含关键词
            return any(kw.lower() in text_lower for kw in self.keywords)
        else:
            # 模糊模式：支持关键词字符之间有其他字符插入
            # 例如关键词"付款"可以匹配"付个款"、"付一下款"等
            for kw in self.keywords:
                kw_lower = kw.lower()
                # 先检查直接包含
                if kw_lower in text_lower:
                    return True
                # 再检查模糊匹配（仅对2字及以上的关键词）
                if len(kw_lower) >= 2:
                    # 构建正则：每个字符之间允许插入0-3个其他字符
                    pattern = ".{0,3}".join(re.escape(c) for c in kw_lower)
                    if re.search(pattern, text_lower):
                        return True
            return False

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        """监听所有消息，匹配关键词后发送收款码"""
        if not self.enabled:
            return

        if not self.qr_image_path or not os.path.exists(self.qr_image_path):
            return

        message_text = event.message_str
        if not message_text:
            return

        if self._match_keywords(message_text):
            logger.info(f"收款码插件：匹配到关键词，消息内容: {message_text}")
            chain = []
            if self.reply_text:
                chain.append(Comp.Plain(self.reply_text))
            chain.append(Comp.Image.fromFileSystem(self.qr_image_path))
            yield event.chain_result(chain)

    @filter.command("payment_qr")
    async def manual_send(self, event: AstrMessageEvent):
        """手动发送收款码指令"""
        if not self.qr_image_path or not os.path.exists(self.qr_image_path):
            yield event.plain_result("收款码图片未配置或文件不存在，请在插件配置中设置 qr_image_path。")
            return

        chain = []
        if self.reply_text:
            chain.append(Comp.Plain(self.reply_text))
        chain.append(Comp.Image.fromFileSystem(self.qr_image_path))
        yield event.chain_result(chain)

    @filter.command("payment_qr_reload")
    async def reload_config(self, event: AstrMessageEvent):
        """重新加载配置"""
        self._load_config()
        status = "已启用" if self.enabled else "已禁用"
        keywords_str = "、".join(self.keywords[:10])
        if len(self.keywords) > 10:
            keywords_str += f" 等共 {len(self.keywords)} 个"
        img_status = "已配置" if (self.qr_image_path and os.path.exists(self.qr_image_path)) else "未配置或不存在"
        yield event.plain_result(
            f"收款码插件配置已重载！\n"
            f"状态: {status}\n"
            f"图片: {img_status}\n"
            f"匹配模式: {self.match_mode}\n"
            f"关键词: {keywords_str}"
        )

    async def terminate(self):
        """插件卸载时调用"""
        logger.info("收款码插件已卸载")
