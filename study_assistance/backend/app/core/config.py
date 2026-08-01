from pathlib import Path

from pydantic_settings import BaseSettings

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # storage
    upload_dir: Path = BACKEND_ROOT / "storage" / "uploads"
    output_dir: Path = BACKEND_ROOT / "storage" / "outputs"

    # VLM
    vlm_model_name: str = "Qwen/Qwen2-VL-2B-Instruct"
    vlm_device: str = "cuda"  # falls back to cpu if no GPU is available

    # page-context decay (LSTM forget-gate style)
    # weight of page N-k in the context of page N is decay_rate ** k
    context_decay_rate: float = 0.6
    context_max_lookback: int = 5

    class Config:
        env_prefix = "STUDY_ASSIST_"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
