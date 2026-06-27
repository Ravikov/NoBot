# 配置说明

## 文件位置

每个用户独立的配置文件存放在 `nobot/config/<用户名>/config.json`。

## 完整配置项

### 模型配置

每个模型包含三个字段：`url`、`key`、`name`。

| 配置键 | 用途 | 默认模型 |
|---|---|---|
| `API` | **主模型** — 用于回复生成 | `deepseek-v4-flash` |
| `secAPI` | **辅助模型** — 搜索决策、智能等待 | `qwen3.7-plus` |
| `searchAPI` | **联网搜索模型** — 带搜索能力的 LLM | `qwen3.7-plus` |
| `multimodalAPI` | **多模态模型** — 图片/视频理解 | `qwen3.6-plus` |
| `imageAPI` | **生图模型** — 已预留，暂未启用 | `qwen3.7-plus` |

**默认 API 地址：**

| 用途 | URL |
|---|---|
| DeepSeek | `https://api.deepseek.com/v1/chat/completions` |
| 阿里云百炼 | `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` |

### 核心参数

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `max_tokens` | int | 1500 | 每次回复最大生成 token 数 |
| `temperature` | float | 1.0 | LLM 温度参数（0~2）。对话用 0.8~1.0，硬件控制建议 0.3 |
| `prompt_file` | string | `"soul"` | 角色提示词文件名（自动补 `.md`） |
| `max_history_turns` | int | 20 | 达到此轮数后自动触发记忆压缩 |
| `save_turns` | int | 10 | 记忆压缩后保留的对话轮数 |
| `wait` | int | 8 | 消息积累基础等待时间（秒） |
| `llm_decide_wait` | bool | true | 是否使用辅助模型动态调整等待时间 |
| `or_search` | bool | true | 是否启用联网搜索 |
| `or_time_feel` | bool | true | 是否将当前时间注入 LLM 上下文 |
| `debug` | bool | false | 调试模式，在回复尾部追加缓存命中率 |
| `wash_comma` | bool | false | 是否将中文逗号替换为空格 |
| `repeat` | bool | false | 复读鸡模式，原样回复消息 |

### 系统参数

| 字段 | 说明 |
|---|---|
| `memory_prompt` | 记忆压缩时发给 LLM 的提示词，定义如何总结记忆 |
| `or_search_prompt` | 判断是否需要联网搜索的触发提示词 |
| `txt_wash` | 从回复中剔除的字符列表，默认 `["*", "\\n", "。"]` |
| `non_setup` | 首次启动标记，`false` 表示已配置完成 |

## 角色提示词

编辑 `nobot/config/<用户名>/soul.md` 自定义机器人的性格和行为。

硬件控制用户的提示词会额外加入 JSON 输出格式约束，确保 LLM 输出可解析的指令。

## 配置备份

每次运行 `set` 命令修改配置后，程序会自动备份到 `config.json.bak`。

手动备份/恢复：
- 启动菜单输入 `save` — 备份当前配置
- 启动菜单输入 `load` — 恢复上次备份

## 默认配置参考

```json
{
  "API": {
    "key": "",
    "url": "https://api.deepseek.com/v1/chat/completions",
    "name": "deepseek-v4-flash"
  },
  "max_tokens": 1500,
  "temperature": 1.0,
  "max_history_turns": 20,
  "save_turns": 10,
  "wait": 8,
  "or_search": true,
  "or_time_feel": true,
  "debug": false,
  "repeat": false
}
```
