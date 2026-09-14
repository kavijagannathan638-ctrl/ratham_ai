import json
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
from app.core.config import settings
from app.core.logging import logger

class ModelRegistry:
    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or settings.MODELS_DIR
        self.models: Dict[str, Any] = {}
        self.metrics: Dict[str, Any] = {}
        self.load_models()

    def load_models(self):
        try:
            metrics_path = self.models_dir / "metrics.json"
            if metrics_path.exists():
                self.metrics = json.loads(metrics_path.read_text())

            need_path = self.models_dir / "need_model.joblib"
            if need_path.exists():
                self.models["need_model"] = joblib.load(need_path)

            reach_path = self.models_dir / "reachability_model.joblib"
            if reach_path.exists():
                self.models["reachability_model"] = joblib.load(reach_path)

            burn_path = self.models_dir / "burnout_model.joblib"
            if burn_path.exists():
                self.models["burnout_model"] = joblib.load(burn_path)

            logger.info(f"Loaded {len(self.models)} ML models from {self.models_dir}")
        except Exception as e:
            logger.error(f"Failed to load ML models: {e}")

    def get_model(self, model_name: str):
        return self.models.get(model_name)

    def is_healthy(self) -> bool:
        return len(self.models) == 3

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics

registry = ModelRegistry()
