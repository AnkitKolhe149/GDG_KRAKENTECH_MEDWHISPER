import os
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from flask import current_app

# Model metadata (from user-provided config)
MODEL_NUMERIC_COLS = [
    "age","bmi","hemoglobin","wbc","platelets","creatinine","egfr","ast","alt",
    "bilirubin_total","sodium","potassium","crp","fasting_glucose","hba1c","ppbs",
    "triglycerides","hdl","ldl","insulin","c_peptide","tsh","systolic_bp",
    "diastolic_bp","heart_rate","ntprobnp","troponin_hs","bun","urine_acr",
    "dengue_ns1","dengue_igm","malaria_rdt","ferritin","d_dimer","inr","aptt",
    "mpv","rapid_creatinine_rise_flag"
]

MODEL_CATEGORICAL_COLS = [
    "sex",
    "primary_report_type"
]

TARGET_PROB_COLS = [
    "risk_ckd_prob",
    "risk_cad_prob",
    "risk_aki_prob",
    "risk_sepsis_prob",
    "risk_metabolic_syndrome_prob",
]

# Risk level thresholds (closed form based on metadata)
RISK_THRESHOLDS = [
    (0.001, 'Very Low'),
    (0.01, 'Low'),
    (0.05, 'Moderate'),
    (0.20, 'High'),
    (1.01, 'Critical')  # anything >= 0.20
]

_MODEL = None


def _default_model_path():
    # Prefer app config, fallback to repository path
    cfg = None
    try:
        cfg = current_app.config.get('RISK_PROB_MODEL_PATH')
    except Exception:
        cfg = None

    if cfg:
        return cfg

    candidate = Path('models_store') / 'trained_models' / 'risk_prob_model_20260117_142705.pkl'
    return str(candidate)


def get_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    model_path = _default_model_path()
    if not model_path or not Path(model_path).exists():
        raise FileNotFoundError(f"Risk probability model not found at {model_path}")

    with open(model_path, 'rb') as f:
        _MODEL = pickle.load(f)

    return _MODEL


def _map_level(p: float) -> str:
    try:
        p = float(p)
    except Exception:
        return 'Unknown'

    if p < 0.001:
        return 'Very Low'
    if p < 0.01:
        return 'Low'
    if p < 0.05:
        return 'Moderate'
    if p < 0.20:
        return 'High'
    return 'Critical'


def predict_risks(data: dict) -> dict:
    """Accepts a dict of feature values, returns dict with probability and level for targets."""
    model = get_model()
    # If the pickle is a dict with explicit components, use them (hardcoded pattern)
    if isinstance(model, dict):
        numeric_cols = model.get('numeric_cols', MODEL_NUMERIC_COLS)
        categorical_cols = model.get('categorical_cols', MODEL_CATEGORICAL_COLS)
        encoder = model.get('encoder', None)
        clf = model.get('clf', None)
        target_cols = model.get('target_prob_cols', TARGET_PROB_COLS)

        # Build DataFrame from provided data
        row = {}
        for c in list(numeric_cols) + list(categorical_cols):
            v = data.get(c)
            row[c] = np.nan if v is None else v

        df = pd.DataFrame([row])

        # Ensure numeric types
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            else:
                df[c] = 0

        # Ensure categorical
        for c in categorical_cols:
            if c not in df.columns:
                df[c] = 'unknown'
            df[c] = df[c].astype(str).fillna('unknown')

        # Apply encoder if present
        if encoder is not None:
            try:
                encoded = encoder.transform(df[categorical_cols])
                try:
                    encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols))
                except Exception:
                    encoded_df = pd.DataFrame(encoded)
                X = pd.concat([df[numeric_cols].reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
            except Exception:
                X = df[numeric_cols]
        else:
            X = df[numeric_cols]

        # Predict using classifier
        if clf is None:
            raise TypeError('Model dict does not contain a classifier under key "clf"')

        # Prefer predict_proba when available
        if hasattr(clf, 'predict_proba'):
            proba = clf.predict_proba(X)
            # If multi-output (list of arrays), handle appropriately
            if isinstance(proba, list):
                # multi-output classifiers sometimes return list of arrays
                # flatten into single row vector
                flat = []
                for arr in proba:
                    flat.extend(list(arr[0]))
                values = flat
            else:
                values = proba[0] if proba.ndim == 2 else proba

            # Map values to target_cols
            result = {}
            for i, name in enumerate(target_cols):
                try:
                    v = float(values[i])
                except Exception:
                    v = None
                result[name] = {'probability': v, 'level': _map_level(v) if v is not None else 'Unknown'}

            return result

        # Fallback: use predict (regression outputs)
        preds = clf.predict(X)
        if hasattr(preds, 'shape') and preds.ndim > 1:
            row = preds[0]
        else:
            row = [preds[0]] if hasattr(preds, '__len__') else [float(preds)]

        result = {}
        for i, name in enumerate(target_cols):
            try:
                v = float(row[i])
            except Exception:
                v = None
            result[name] = {'probability': v, 'level': _map_level(v) if v is not None else 'Unknown'}

        return result

    # Otherwise fall back to previous heuristic behavior
    # Build single-row DataFrame with expected columns
    input_cols = MODEL_NUMERIC_COLS + MODEL_CATEGORICAL_COLS
    row = {}
    for c in input_cols:
        v = data.get(c)
        if v is None:
            row[c] = np.nan
        else:
            row[c] = v

    df = pd.DataFrame([row], columns=input_cols)

    # Ensure numeric columns are numeric
    for c in MODEL_NUMERIC_COLS:
        if c in df.columns:
            try:
                df[c] = pd.to_numeric(df[c], errors='coerce')
            except Exception:
                pass

    # Prediction: try several possibilities depending on object saved in pickle
    preds = None
    try:
        # Most common: estimator or pipeline with predict
        if hasattr(model, 'predict'):
            preds = model.predict(df)
        # If the pickle contains a dict wrapper
        elif isinstance(model, dict):
            # common keys: 'model', 'estimator', 'pipeline'
            for k in ('model', 'estimator', 'pipeline'):
                if k in model and hasattr(model[k], 'predict'):
                    preds = model[k].predict(df)
                    break
        # If the pickle is an array of estimators (object dtype)
        elif isinstance(model, (list, tuple)) or (hasattr(model, 'dtype') and str(getattr(model, 'dtype')) == 'object'):
            # attempt to treat as ensemble of estimators and average predictions
            estimators = list(model)
            all_preds = []
            for est in estimators:
                if hasattr(est, 'predict'):
                    try:
                        p = est.predict(df)
                    except Exception:
                        # try passing numpy array
                        p = est.predict(df.values)
                    all_preds.append(np.asarray(p))

            if all_preds:
                # stack and average across estimator axis
                stacked = np.stack([p if p.ndim == 2 else p.reshape(-1, 1) for p in all_preds], axis=0)
                preds = np.mean(stacked, axis=0)

    except Exception as pred_err:
        raise RuntimeError(f'Prediction failed: {pred_err}')

    if preds is None:
        raise TypeError('Loaded model object cannot be used for prediction (no predict method found)')

    # Handle single-output vs multi-output shapes
    if hasattr(preds, 'shape') and len(preds.shape) == 1:
        preds = preds.reshape(1, -1)

    result = {}
    for i, name in enumerate(TARGET_PROB_COLS):
        try:
            val = float(preds[0, i])
        except Exception:
            val = None
        result[name] = {
            'probability': val,
            'level': _map_level(val) if val is not None else 'Unknown'
        }

    return result
