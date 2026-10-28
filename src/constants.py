from pathlib import Path

# 所有路径都由当前文件位置推导，避免依赖用户从哪个目录启动 Python。
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MALAYSIAN_DIR = DATA_DIR / "malaysian"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"

# `<PAD>` 用于补齐 Batch；`<UNK>` 代表训练词表未见词。
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"
# Label ID 的顺序会写入 checkpoint；训练和推理必须完全一致。
LABELS = ["<PAD>", "O", "B-PER", "I-PER", "B-LOC", "I-LOC", "B-ORG", "I-ORG"]
PAD_LABEL = "<PAD>"
SEED = 42
