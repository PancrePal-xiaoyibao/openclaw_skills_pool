# Schemas

当前版本支持两种输入：

- `input-chart-driven.example.json`：你先给结构化盘面
- `input-auto-hour.example.json`：你给公历时间，skill 自动排出 hour chart

注意：
- `chart-driven` 依然可用
- `auto-hour` 当前采用固定 hour-chart 规则，优先支持 `拆补`，并保留 `置闰` 协议位
- `chart.palaces` 不要求九宫全量，但至少必须覆盖用神落宫；若要提高置信度，建议提供 3 宫以上，最好全盘
