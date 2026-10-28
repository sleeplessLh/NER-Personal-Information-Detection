# 教学系统维护说明

此目录是最终 PDF 的唯一教学来源。旧 `docs/*.md` 仅作为历史参考，不再参与新 PDF 构建。

```text
tutorial/
  chapters/         每个 Phase 一个 Markdown 文件
  code_snapshots/   每个 Phase 结束时可运行的项目状态
  assets/           图示与渲染资源
  manifest.json     章节顺序、标题和质量规则
  FILE_EVOLUTION.md 本轮重建中各文件的真实演化记录
  build_pdf.py      从章节与快照生成 PDF
scripts/
  validate_tutorial.py  检查章节教学质量与完整性
  verify_tutorial.py    检查快照、路径、命令和最终代码一致性
```

修改正式源码后必须执行：

```powershell
uv run python scripts/verify_tutorial.py
uv run python scripts/validate_tutorial.py
uv run python tutorial/build_pdf.py
uv run python -m pytest -q
```

快照是本轮“教材重建历史”，不是伪造的旧 Git 历史。每个快照都必须有 manifest、阶段测试和到下一阶段的明确修改说明。
