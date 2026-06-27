# 具身接入（Embodiment）配置说明

## 概述

NoBot 的 **embodiment**（具身/实体）机制允许 AI 通过 WebSocket 控制物理硬件。硬件端运行 [NoBot-esp32](https://github.com/Ravikov/NoBot-esp32-demo) 固件（ESP32-S3），通过 WiFi 连接 NoBot 的 WebSocket 服务，接收 LLM 生成的指令并执行。

## 系统架构

```
                    NoBot 服务端
                         │
               WebSocket 服务 (端口 7323)
                         │
                    ┌────┴────┐
                    │         │
                微信/CLI    ESP32-S3
                用户输入    硬件执行
```

## 用户类型

NoBot 有两种用户类型：

| 类型 | type 值 | 说明 |
|---|---|---|
| 对话用户 | `chat` | 纯文本对话，用于微信/CLI |
| 实体用户 | `esp32` | 用于连接并控制 ESP32 硬件 |

## 自动创建

首次启动 NoBot 时，系统会自动创建一个名为 **`embodiment`**、类型为 `esp32` 的用户。你也可以在用户选择界面手动创建更多实体用户：

```
creat → 名称: 任意名称 → 类型: esp32
```

## 配置文件

每个实体用户拥有以下配置文件(与chat用户基本一致)：

### 1. `config/embodiment/config.json` — API 配置

```json
{
  "API": {
    "key": "sk-xxx",
    "url": "https://api.deepseek.com/v1/chat/completions",
    "name": "deepseek-v4-flash"
  },
  "temperature": 0.3,
  "max_history_turns": 30,
  "or_search": false,
  ...
}
```

与对话chat用户的主要区别：
- `temperature` 更改无效, 软件锁死低温度以防模型抽风生成不合规消息
- `or_search` 可手动关闭，硬件控制不需要联网搜索
- `wait` 建议缩短（2-3s），加快响应速度

### 2. `config/embodiment/soul.md` — 角色提示词

定义 LLM 在硬件控制场景下的行为规范。会注入默认提示词，要求 LLM 以严格 JSON 格式输出指令。

### 3. `config/embodiment/actionAndHardware.txt` — 能力表

ESP32 首次连接时自动上报并写入，内容示例：

```
action:
    LED_GLOW   #点亮led
    LED_OUT    #熄灭led
    LED_BLINK  #闪烁led
hardware:
    RED_LED    #红色led
    GREEN_LED  #绿色led
    WHILE_LED  #白色
```

## LLM 指令格式

控制硬件时，LLM 被要求输出如下 JSON：

```json
{"msg":"回复消息","action":0,"hardware":0}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `msg` | string | 给用户的回复文本 |
| `action` | int | 动作编号（与能力表顺序对应） |
| `hardware` | int | 硬件编号（与能力表顺序对应） |

如需执行多个指令，大模型回复中用 `#` 分隔：

```json
{"msg":"开始","action":0,"hardware":0}
#
{"action":1,"hardware":1}
```

## 消息类型

| type | 方向 | 说明 |
|---|---|---|
| 100 | ESP32 → NoBot | 首次连接，更新能力表 |
| 101 | ESP32 → NoBot | 普通硬件控制请求 |
| 105 | 微信 → NoBot → ESP32 | 微信用户发出的硬件控制消息 |

## WebSocket 协议

详见 [doc/websocket-zh.md](./websocket-zh.md)。

## 启动模式

| 模式 | 编号 | 说明 |
|---|---|---|
| WebSocket 模式 | **5** | 仅启动 WebSocket 服务，等待 ESP32 连接，适用于纯硬件控制场景 |
| 联动模式 | **6** | 同时启动 WebSocket 和微信 ClawBot，ESP32 连接后才开启微信监听，支持微信控制硬件 |

## 客户端扩展建议(详细请参考[NoBot-esp32](https://github.com/Ravikov/NoBot-esp32-demo))

- **增加硬件**：编辑 `execute.h` 的 `Hardware` 枚举 → 添加 GPIO → 更新 `actionAndHardware.txt`
- **增加动作**：编辑 `execute.h` 的 `Action` 枚举 → 在 `execute.cpp` 实现逻辑
- **替换通信**：WebSocket 可换成 MQTT、HTTP、BLE 等，只需修改 `websocket/server.py` 和 ESP32 端对应模块
