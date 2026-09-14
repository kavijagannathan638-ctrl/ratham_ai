from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
MODELS = ROOT / "models"
MODELS.mkdir(exist_ok=True)

def train_need_model():
    print("Training Need Forecast Model...")
    df = pd.read_csv(DATA / "patient_need.csv")
    X = df.drop(columns=["need_within_7d"] + [c for c in ["urgency_score"] if c in df.columns])
    y = df["need_within_7d"]
    
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = XGBClassifier(
        n_estimators=220, max_depth=5, learning_rate=0.06,
        subsample=0.85, colsample_bytree=0.85, eval_metric="logloss", random_state=42
    )
    model.fit(Xtr, ytr)
    
    p = model.predict(Xte)
    pp = model.predict_proba(Xte)[:, 1]
    
    metrics = {
        "accuracy": round(float(accuracy_score(yte, p)), 4),
        "precision": round(float(precision_score(yte, p, zero_division=0)), 4),
        "recall": round(float(recall_score(yte, p, zero_division=0)), 4),
        "f1": round(float(f1_score(yte, p, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(yte, pp)), 4),
        "rows": len(df),
        "features": list(X.columns)
    }
    
    joblib.dump(model, MODELS / "need_model.joblib")
    print("Need Forecast Model trained and saved:", metrics)
    return metrics

if __name__ == "__main__":
    train_need_model()
