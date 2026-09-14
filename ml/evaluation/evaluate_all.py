from pathlib import Path
import json
from ml.training.train_need import train_need_model
from ml.training.train_reachability import train_reachability_model
from ml.training.train_burnout import train_burnout_model

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "models"

def evaluate_all():
    print("Evaluating and retraining all 3 RATHAM ML models...")
    all_metrics = {
        "need_model": train_need_model(),
        "reachability_model": train_reachability_model(),
        "burnout_model": train_burnout_model(),
    }
    metrics_path = MODELS / "metrics.json"
    metrics_path.write_text(json.dumps(all_metrics, indent=2))
    print(f"Metrics written to {metrics_path}")
    return all_metrics

if __name__ == "__main__":
    evaluate_all()
