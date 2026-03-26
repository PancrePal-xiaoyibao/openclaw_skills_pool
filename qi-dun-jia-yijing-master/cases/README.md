# Qimen Benchmark Cases

每个 case 用于验证：

- 输出结构是否完整
- 五维取象是否出现
- 问题类型的权重是否有差异
- 总结是否与预期 band 一致
- 自动排局模式是否能给出稳定的干支/节气/盘面
- 与 `teacher_goldens.json` 的人工金标准要点是否大致一致

运行：

```bash
python3 workspace/skills/qi-dun-jia-yijing-master/scripts/qimen_bench.py   --cases workspace/skills/qi-dun-jia-yijing-master/cases/benchmark_cases.json   --output-dir workspace/skills/qi-dun-jia-yijing-master/cases/output
```

如需显式指定金标准文件：

```bash
python3 workspace/skills/qi-dun-jia-yijing-master/scripts/qimen_bench.py   --cases workspace/skills/qi-dun-jia-yijing-master/cases/benchmark_cases.json   --teacher-goldens workspace/skills/qi-dun-jia-yijing-master/cases/teacher_goldens.json   --output-dir workspace/skills/qi-dun-jia-yijing-master/cases/output
```
