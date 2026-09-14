from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
MODELS = ROOT / 'models'
MODELS.mkdir(exist_ok=True)

def train(name, file, target):
    df = pd.read_csv(DATA / file)
    X = df.drop(columns=[target] + ([c for c in ['urgency_score'] if c in df.columns]))
    y = df[target]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)
    model = XGBClassifier(n_estimators=220, max_depth=5, learning_rate=.06, subsample=.85, colsample_bytree=.85, eval_metric='logloss', random_state=42)
    model.fit(Xtr, ytr)
    p = model.predict(Xte)
    pp = model.predict_proba(Xte)[:,1]
    metrics = {
        'accuracy': round(accuracy_score(yte,p),4),
        'precision': round(precision_score(yte,p,zero_division=0),4),
        'recall': round(recall_score(yte,p,zero_division=0),4),
        'f1': round(f1_score(yte,p,zero_division=0),4),
        'roc_auc': round(roc_auc_score(yte,pp),4),
        'rows': len(df),
        'features': list(X.columns)
    }
    joblib.dump(model, MODELS / f'{name}.joblib')
    return metrics

metrics = {
    'need_model': train('need_model', 'patient_need.csv', 'need_within_7d'),
    'reachability_model': train('reachability_model', 'donor_reachability.csv', 'reachable'),
    'burnout_model': train('burnout_model', 'donor_burnout.csv', 'burnout_risk'),
}
(MODELS / 'metrics.json').write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))
