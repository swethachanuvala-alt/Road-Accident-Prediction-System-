"""Re-create the model files in model/  ->  python train_model.py"""
from roadwatch import pipeline as P

if __name__ == "__main__":
    out = P.save_artifacts()
    d = out["data"]
    print("Saved model files to:", P.MODEL_DIR)
    print(f"Train rows: {len(d['y_train'])}  Test rows: {len(d['y_test'])}")
    for name, m in out["models"].items():
        r = P.evaluate(m, d["X_test_scaled"], d["y_test"])
        print(f"{name:14s} test accuracy {r['accuracy']:.4f}   ROC-AUC {r['roc_auc']:.3f}")
