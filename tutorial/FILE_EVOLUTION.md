# FILE EVOLUTION - 本轮教学重建的真实演化计划

本项目此前没有 Git commit，因此下表只记录本轮为教学目的重新构造并实际验证的增量状态。任何 snapshot 只有在对应测试通过后才能标记 `VERIFIED`。

| Phase | File | Action | Purpose | Verification |
|---:|---|---|---|---|
| 00 | `README.md` | Review | 明确比赛边界与限制 | requirement checklist |
| 01 | `learning/hello_python.py` | Create | 验证 Python/VS Code/venv | prints environment message |
| 02 | `learning/python_foundations.py` | Create/Modify | 练习 list/dict/function/class/type | phase test |
| 03 | `learning/bio_demo.py` | Create | 手工理解 token 与 BIO | exact spans |
| 04 | `src/constants.py` | Create | 集中路径、标签、seed | import test |
| 05 | `src/generate_data.py` | Create/Modify | 生成两个语料及 split | leakage tests |
| 06 | `src/preprocessing.py` | Create/Modify | tokenizer/BIO/vocab | preprocessing tests |
| 07 | `src/dataset.py` | Create | token->tensor 与 features | tensor shape tests |
| 08 | `src/dataset.py` | Modify | Dataset/collate/padding/mask | batch tests |
| 09 | `src/model.py` | Create, Versions 1-6 | 从空 Module 增量到 BiLSTM | six independent checks |
| 10 | `src/train.py` | Create | loss/backward/optimizer | parameter update test |
| 11 | `src/train.py` | Modify | epoch/validation/checkpoint | checkpoint round trip |
| 12 | `src/predict.py` | Create/Modify | load/predict/BIO decode | CPU prediction tests |
| 13 | `src/redact.py` | Create/Modify | character-span redaction | formatting preservation |
| 14 | `src/train.py` | Modify | 合入 Malaysian train/validation | checkpoint dataset counts |
| 15 | `src/evaluate.py` | Create/Modify | 双测试集 entity metrics | JSON metrics |
| 16 | `app/main.py` | Create | FastAPI text endpoint | real Uvicorn POST |
| 17 | `app/main.py` | Modify | TXT/PDF/size/error handling | upload tests |
| 18 | `app/main.py` | Modify | HTML/CSS/JS UI | end-to-end test |
| 19 | `tests/*.py` | Create/Modify | 19 类验收覆盖 | full pytest |
| 20 | reports/docs | Create/Modify | README/acceptance/synchronization | validators |
| 21 | final snapshot/PDF | Finalize | 空目录复现与教学交付 | final hash + visual QA |

状态由 `tutorial/code_snapshots/phase_XX/snapshot.json` 中的 `verified` 字段和测试证据决定，不能只修改本表。
