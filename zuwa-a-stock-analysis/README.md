# 🐸 祖蛙沪深A股分析系统

> 一个基于多Agent协作的智能A股股票分析系统

## 系统架构

祖蛙采用**辩论式投研架构**，模拟真实投研团队的工作流程：

```
                    🧠 首席Agent (Chief Analyst)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
       🐂 多头           🐻 空头            👥 散户情绪
      Agent            Agent              Agent
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
   📊 数据               📈 技术                💰 资金
  Agent                Agent                 Agent
    │                      │                      │
   🔍 情报               🏭 行业
  Agent                Agent
```

## Agent分工

| Agent | 职责 | 输出 |
|-------|------|------|
| 🧠 首席Agent | 决策中枢，综合所有分析 | 最终投资建议 |
| 🐂 多头Agent | 寻找看涨理由 | 看多分析报告 |
| 🐻 空头Agent | 寻找风险隐患 | 看空分析报告 |
| 👥 散户情绪Agent | 监控散户情绪 | 情绪指数+反向信号 |
| 📊 数据Agent | 收集清洗数据 | 结构化数据 |
| 📈 技术Agent | 技术指标分析 | 技术评分+点位 |
| 💰 资金Agent | 资金流向分析 | 资金面评分 |
| 🔍 情报Agent | 新闻舆情监控 | 消息面评分 |
| 🏭 行业Agent | 行业对比分析 | 行业景气度 |

## 特色功能

- 🔥 **多空辩论机制**：多头vs空头观点碰撞，避免confirmation bias
- 💹 **散户情绪监控**：反向指标，避免追高杀低
- 🎯 **A股专属指标**：涨停、龙虎榜、北向资金、主力资金
- 📊 **可视化报告**：Streamlit仪表盘 + 飞书推送
- 🔄 **回测验证**：验证Agent建议的历史表现

## 快速开始

### 1. 安装依赖

```bash
cd zuwa-a-stock-analysis
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
cp .env.example .env
# 编辑.env文件，填入你的API密钥
```

**必需配置：**
- `MOONSHOT_API_KEY` - Moonshot (Kimi) API Key，用于智能分析
  - 获取地址: https://platform.moonshot.cn/
  - 新用户有免费额度

**可选配置：**
- `TUSHARE_TOKEN` - Tushare Pro 数据接口（增强财务数据）
- `BAIDU_API_KEY` - 百度搜索 API（新闻舆情分析）
- `FEISHU_APP_ID` / `FEISHU_APP_SECRET` - 飞书机器人推送

### 3. 运行分析

```bash
# 分析单只股票
python main.py --symbol 600519 --name 贵州茅台

# 启动Web界面
streamlit run ui/streamlit_app.py
```

## 配置说明

编辑 `config/agents.yaml` 可以调整：
- Agent性格参数（乐观/谨慎程度）
- 分析权重配置
- 阈值设定

## 数据说明

本系统使用以下数据源：
- **Tushare Pro**: A股基础数据、财务数据
- **AKShare**: 实时行情、龙虎榜、资金流向
- **东方财富**: 主力资金、北向资金

## 免责声明

⚠️ **本系统仅供学习研究使用，不构成投资建议**

- 股市有风险，投资需谨慎
- AI分析仅供参考，不构成买卖依据
- 过往表现不代表未来收益

## License

MIT License

---

🐸 *祖蛙祝你投资顺利！*
