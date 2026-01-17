import os
import pickle
from pathlib import Path
import pandas as pd
from flask import Blueprint, request, jsonify, current_app

bp = Blueprint('future_disease', __name__)

# Default model path (can be overridden via app config RISK_PROB_MODEL_PATH)
DEFAULT_MODEL = Path('models_store') / 'trained_models' / 'risk_prob_model_20260117_142705.pkl'


def _load_model():
    model_path = current_app.config.get('RISK_PROB_MODEL_PATH') or str(DEFAULT_MODEL)
    if not Path(model_path).exists():
        raise FileNotFoundError(f'Model not found at {model_path}')

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    return model


@bp.route('/future-disease/predict', methods=['POST'])
def predict():
    try:
        payload = request.get_json() or {}
        if not payload:
            return jsonify({"success": False, "error": "No input provided"}), 400

        model = _load_model()

        # If model is a dict with metadata
        if isinstance(model, dict):
            numeric_cols = model.get('numeric_cols', [])
            categorical_cols = model.get('categorical_cols', [])
            encoder = model.get('encoder')
            clf = model.get('clf')
        else:
            # Not a dict: try to delegate to existing predictor if available
            from app.services.risk_prob_predictor import MODEL_NUMERIC_COLS, MODEL_CATEGORICAL_COLS
            numeric_cols = MODEL_NUMERIC_COLS
            categorical_cols = MODEL_CATEGORICAL_COLS
            encoder = None
            clf = model

        if clf is None:
            return jsonify({"success": False, "error": "Classifier component not found in model file"}), 500

        # Convert payload to dataframe
        df = pd.DataFrame([payload])

        # Ensure numeric columns
        for col in numeric_cols:
            if col not in df.columns:
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Ensure categorical columns
        for col in categorical_cols:
            if col not in df.columns:
                df[col] = 'unknown'
            df[col] = df[col].astype(str).fillna('unknown')

        # Encode categoricals if encoder present
        if encoder is not None:
            try:
                encoded = encoder.transform(df[categorical_cols])
                encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols))
                X = pd.concat([df[numeric_cols].reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
            except Exception:
                X = df[numeric_cols]
        else:
            X = df[numeric_cols]

        # Prediction -- support predict_proba or predict
        if hasattr(clf, 'predict_proba'):
            probs = clf.predict_proba(X)
            # If multi-class, return per-class probs for first row
            first = probs[0]
            classes = getattr(clf, 'classes_', list(range(len(first))))
            result = {}
            for cls, prob in zip(classes, first):
                level = (
                    "High Risk" if prob >= 0.7 else
                    "Medium Risk" if prob >= 0.4 else
                    "Low Risk"
                )
                result[str(cls)] = {"probability": float(prob), "level": level}

            return jsonify({"success": True, "predictions": result})

        else:
            # fallback to predict (regression probabilities)
            preds = clf.predict(X)
            # If preds is multi-output, map to target names if present
            # Try to use keys in model dict
            if isinstance(preds, (list, tuple)) or (hasattr(preds, 'shape') and getattr(preds, 'ndim', 0) > 1):
                # flatten first row
                row = preds[0] if hasattr(preds[0], '__len__') else preds
                result = {}
                # prefer target names
                target_names = model.get('target_names') if isinstance(model, dict) else None
                if target_names and len(target_names) == len(row):
                    for name, val in zip(target_names, row):
                        result[name] = {"probability": float(val), "level": ("High" if val >= 0.2 else "Low")}
                else:
                    for i, val in enumerate(row):
                        result[f'out_{i}'] = {"probability": float(val), "level": ("High" if val >= 0.2 else "Low")}

                return jsonify({"success": True, "predictions": result})

            # scalar prediction
            val = float(preds[0]) if hasattr(preds, '__len__') else float(preds)
            level = "High Risk" if val >= 0.7 else ("Medium Risk" if val >= 0.4 else "Low Risk")
            return jsonify({"success": True, "predictions": {"risk": {"probability": val, "level": level}}})

    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
