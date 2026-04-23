# CB Test 无服务器版本（TradingView 指标）

已将仓库中的核心引擎思路迁移为 TradingView Pine Script 指标：`tradingview/cb_test_indicator.pine`。

## 使用方式
1. 打开 TradingView → Pine Editor  
2. 复制 `cb_test_indicator.pine` 全部内容并粘贴  
3. 点击 **Add to chart**  
4. 在指标参数中按你的品种和周期调整阈值  
5. 回归验证建议先开启 `Only trigger on bar close`（默认开启）

## 对应关系（与原 Python 引擎）
- **P1 中长线**：EMA20/EMA50 + ADX + RSI + MACD 柱变化 + 回踩带
- **P2 异动**：成交量倍增 + 当根价格振幅阈值
- **P3 短线**：EMA5/EMA15 交叉 + 布林位置 + RSI 过滤
- **P4 波浪提示**：基于 pivot 高低点的简化结构提示

## 说明
- 这是图表端信号指标，不依赖服务器、定时任务、数据库或 Webhook。
- 支持 `alertcondition`，可在 TradingView 内部直接创建提醒。
- 指标增加了“仅收线触发”开关，减少未收线波动带来的信号抖动。
- 已清理当前指标实现中的未使用逻辑，便于后续维护与回归。

## 当前验证限制
- 当前执行环境访问 `https://www.tradingview.com/` 被拦截（`ERR_BLOCKED_BY_CLIENT`），无法在此环境直接登录你的账号做网页侧自动回归。
- 已完成代码侧稳定性改进；你可在账号内按同一参数进行人工回归（BTC/ETH 的 5m、15m、1h 三个周期）。
