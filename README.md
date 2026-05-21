# 每日打卡 (DailyCheckin)

**多 Agent 协作的家庭日常关怀系统** —— 将碎片化的日常记录，自动转化为给父母看的温馨日报。

## 解决的痛点

年轻人在忙碌的生活中难以及时、有质量地与父母分享日常。一条条零散的微信消息缺乏温度，父母也感受不到孩子完整的一天。每日打卡通过 **4 个 AI Agent 协作**，把当天的碎片记录变成一份有逻辑、有温度、长辈能读懂的日报。

## 核心逻辑流

```
用户输入（碎片文字/语音）
    │
    ▼
┌─────────────────┐
│  Collector Agent │  采集 & 结构化：将碎片输入拆分为独立事件条目
└────────┬────────┘
         │ RawEntry[]
         ▼
┌─────────────────┐
│  Analyzer Agent  │  理解 & 推理：情绪识别 + 关键词提取 + 父母视角二次解读
└────────┬────────┘
         │ AnalyzedEntry[]
         ▼
┌─────────────────┐
│ Generator Agent  │  聚合 & 生成：以父母为读者，生成温馨日报（标题+问候+亮点+时间线+心情+结尾）
└────────┬────────┘
         │ DailyReport
         ▼
┌─────────────────┐
│  Pusher Agent    │  推送 & 存档：保存本地 + Webhook推送 + 控制台预览
└─────────────────┘
```

**长链推理**体现在 Analyzer 环节：Agent 需要先理解事件本身的语义，再换位到 50-60 岁中国父母的视角进行二次推理，生成他们真正关心的解读（而不是 AI 自己的理解）。

**多 Agent 协作**：4 个 Agent 各司其职，管道串联，任何一个 Agent 的输出都是下一个 Agent 的输入，形成完整的端到端链路。

## 技术栈

- **语言**: Python 3.10+
- **AI 引擎**: Claude API (Anthropic) — 支持 Sonnet 4.6
- **数据模型**: Pydantic v2
- **终端美化**: Rich
- **配置管理**: python-dotenv

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/1uhkey/daily-checkin.git
cd daily-checkin

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 ANTHROPIC_API_KEY

# 4. 运行演示（不需要 API Key）
python demo.py

# 5. 运行完整管道（需要 API Key）
python -m src.main "今天8点起床去健身房，中午和同事吃了川菜，下午写了3小时代码，晚上7点到家"
```

## 项目结构

```
daily-checkin/
├── src/
│   ├── main.py              # 主入口 & 管道调度
│   ├── agents/
│   │   ├── base.py          # Agent 基类 (Claude调用封装)
│   │   ├── collector.py     # 采集 Agent
│   │   ├── analyzer.py      # 分析 Agent (长链推理)
│   │   ├── generator.py     # 生成 Agent
│   │   └── pusher.py        # 推送 Agent
│   ├── models/
│   │   └── schemas.py       # Pydantic 数据模型
│   ├── storage/
│   │   └── journal.py       # 本地持久化
│   └── utils/
│       └── config.py        # 配置加载
├── tests/
│   └── test_agents.py       # 单元测试
├── templates/
├── demo.py                  # 免 API 演示脚本
├── requirements.txt
└── README.md
```

## 运行测试

```bash
pytest tests/ -v
```

## License

MIT
