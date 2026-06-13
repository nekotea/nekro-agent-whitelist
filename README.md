# nekro-agent-whitelist

[NekroAgent](https://github.com/KroMiose/nekro-agent) 的聊天过滤插件，针对群聊和私聊分别提供**白名单**、**黑名单**、**不拦截**三种独立过滤模式。

## 功能

- 群聊和私聊过滤模式完全独立配置
- 三种模式：
  - **不拦截**：全部放行（默认）
  - **白名单**：仅列表内的群/用户可触发机器人
  - **黑名单**：列表内的群/用户无法触发机器人
- 白名单和黑名单列表独立存储，切换模式不会丢失配置
- 支持填写纯数字 ID 或完整 chat_key（如 \11-group_331320444\）
- 可开关的拦截日志

## 安装

将 \plugin.py\ 放入 NekroAgent 的插件工作目录：


ekro_agent_data/plugins/workdir/whitelist.py
在管理面板 → 插件 页面重载插件即可。

## 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| \GROUP_FILTER_MODE\ | 不拦截 | 群聊过滤模式（下拉选择） |
| \GROUP_WHITELIST\ | [] | 群聊白名单，填群号 |
| \GROUP_BLACKLIST\ | [] | 群聊黑名单，填群号 |
| \PRIVATE_FILTER_MODE\ | 不拦截 | 私聊过滤模式（下拉选择） |
| \PRIVATE_WHITELIST\ | [] | 私聊白名单，填用户 ID |
| \PRIVATE_BLACKLIST\ | [] | 私聊黑名单，填用户 ID |
| \LOG_BLOCKED_EVENTS\ | true | 是否记录拦截日志 |

## 作者

Teeea
