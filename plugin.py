"""聊天过滤插件

针对群聊和私聊分别提供白名单、黑名单、不拦截三种模式，互相独立配置。
"""

import re
from typing import List, Literal, Optional

from pydantic import Field

from nekro_agent.api.schemas import AgentCtx
from nekro_agent.core import logger
from nekro_agent.schemas.chat_message import ChatMessage, ChatType
from nekro_agent.schemas.signal import MsgSignal
from nekro_agent.services.plugin.base import ConfigBase, NekroPlugin

plugin = NekroPlugin(
    name="聊天过滤",
    module_name="whitelist",
    description="针对群聊和私聊分别提供白名单、黑名单、不拦截三种过滤模式。",
    version="3.0.0",
    author="Teeea",
    url="https://github.com/nekotea/nekro-agent-whitelist",
)

FilterMode = Literal["不拦截", "白名单", "黑名单"]


@plugin.mount_config()
class WhitelistConfig(ConfigBase):
    """过滤配置"""

    # 群聊
    GROUP_FILTER_MODE: FilterMode = Field(
        default="不拦截",
        title="群聊过滤模式",
        description="不拦截=全部放行 / 白名单=仅列表内群响应 / 黑名单=列表内群不响应",
    )
    GROUP_WHITELIST: List[str] = Field(
        default_factory=list,
        title="群聊白名单",
        description="群聊模式为【白名单】时生效，填写允许响应的群号。",
    )
    GROUP_BLACKLIST: List[str] = Field(
        default_factory=list,
        title="群聊黑名单",
        description="群聊模式为【黑名单】时生效，填写需要屏蔽的群号。",
    )

    # 私聊
    PRIVATE_FILTER_MODE: FilterMode = Field(
        default="不拦截",
        title="私聊过滤模式",
        description="不拦截=全部放行 / 白名单=仅列表内用户响应 / 黑名单=列表内用户不响应",
    )
    PRIVATE_WHITELIST: List[str] = Field(
        default_factory=list,
        title="私聊白名单",
        description="私聊模式为【白名单】时生效，填写允许响应的用户ID。",
    )
    PRIVATE_BLACKLIST: List[str] = Field(
        default_factory=list,
        title="私聊黑名单",
        description="私聊模式为【黑名单】时生效，填写需要屏蔽的用户ID。",
    )

    LOG_BLOCKED_EVENTS: bool = Field(
        default=True,
        title="记录拦截事件",
        description="是否将被拦截的消息记录到日志中。",
    )


config = plugin.get_config(WhitelistConfig)


def _extract_numeric_id(chat_key: str) -> str:
    """从 chat_key 中提取末尾的纯数字 ID（如 'v11-group_331320444' → '331320444'）。
    若末尾无数字则返回原始 chat_key。
    """
    match = re.search(r"(\d+)$", chat_key)
    return match.group(1) if match else chat_key


def _in_list(numeric_id: str, chat_key: str, id_list: List[str]) -> bool:
    """支持列表中填纯数字 ID 或完整 chat_key 两种形式。"""
    return numeric_id in id_list or chat_key in id_list


def _should_block(mode: str, numeric_id: str, chat_key: str, whitelist: List[str], blacklist: List[str]) -> bool:
    if mode == "不拦截":
        return False
    if mode == "白名单":
        return not _in_list(numeric_id, chat_key, whitelist)
    if mode == "黑名单":
        return _in_list(numeric_id, chat_key, blacklist)
    return False


@plugin.mount_on_user_message()
async def chat_filter(ctx: AgentCtx, message: ChatMessage) -> Optional[MsgSignal]:
    try:
        chat_type: str = message.chat_type if isinstance(message.chat_type, str) else message.chat_type.value

        if chat_type == ChatType.GROUP.value:
            group_id = _extract_numeric_id(message.chat_key)
            if _should_block(config.GROUP_FILTER_MODE, group_id, message.chat_key, config.GROUP_WHITELIST, config.GROUP_BLACKLIST):
                if config.LOG_BLOCKED_EVENTS:
                    logger.info(f"[群聊过滤/{config.GROUP_FILTER_MODE}] 拦截群 {group_id} (chat_key={message.chat_key})")
                return MsgSignal.BLOCK_ALL
            return None

        elif chat_type == ChatType.PRIVATE.value:
            user_id = message.sender_id
            if _should_block(config.PRIVATE_FILTER_MODE, user_id, message.chat_key, config.PRIVATE_WHITELIST, config.PRIVATE_BLACKLIST):
                if config.LOG_BLOCKED_EVENTS:
                    logger.info(f"[私聊过滤/{config.PRIVATE_FILTER_MODE}] 拦截用户 {user_id} (chat_key={message.chat_key})")
                return MsgSignal.BLOCK_ALL
            return None

        else:
            logger.warning(f"[聊天过滤] 未知聊天类型 '{chat_type}'，来源 '{message.chat_key}'，默认放行")
            return None

    except Exception as e:
        logger.error(f"[聊天过滤] 意外错误: {e}", exc_info=True)
        return None


@plugin.mount_cleanup_method()
async def clean_up():
    logger.info("聊天过滤插件资源已清理。")
