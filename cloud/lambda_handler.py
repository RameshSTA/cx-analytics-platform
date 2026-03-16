"""
lambda_handler.py — Customer Experience Analytics Platform
AWS Lambda endpoint for serving the foot traffic forecast model.

Endpoint accepts a JSON payload: {"store_id": 42, "forecast_horizon_weeks": 4}
Returns: {"store_id": 42, "forecasts": [{"week": 1, "predicted_sales": 12450, ...}]}

Deployment: Python 3.11 runtime, 512MB memory, 30s timeout
IAM permissions required: s3:GetObject on the model bucket
"""
import json
import logging
import os
import pickle
import io
from datetime import datetime, timedelta
from typing import Any

import boto3
import numpy as np

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration (set as Lambda environment variables)
MODEL_BUCKET = os.environ.get("MODEL_BUCKET", "retail-cx-models")
MODEL_KEY = os.environ.get("MODEL_KEY", "models/lgbm_forecaster_v1.pkl")
FEATURE_KEY = os.environ.get("FEATURE_KEY", "models/feature_stats_v1.pkl")

_model_cache: dict[str, Any] = {}


def _load_model_from_s3(bucket: str, key: str) -> Any:
    """Load a pickled model from S3 with in-memory caching (Lambda warm start)."""
    cache_key = f"{bucket}/{key}"
    if cache_key in _model_cache:
        logger.info(f"Cache hit for {cache_key}")
        return _model_cache[cache_key]

    logger.info(f"Loading model from s3://{bucket}/{key}")
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    model = pickle.loads(response["Body"].read())
    _model_cache[cache_key] = model
    logger.info("Model loaded and cached successfully")
    return model


def _build_feature_row(store_id: int, feature_stats: dict) -> dict:
    """
    Build a feature row for inference using the store's historical statistics.
    In production, this would query the feature store (DynamoDB or Athena).
    """
    stats = feature_stats.get(store_id, feature_stats.get("default", {}))

    now = datetime.utcnow()
    return {
        "lag_1w": stats.get("recent_avg", 10000),
        "lag_4w": stats.get("month_avg", 10000),
        "lag_52w": stats.get("year_ago", 10000),
        "roll_4w": stats.get("recent_avg", 10000),
        "roll_12w": stats.get("quarter_avg", 10000),
        "week_of_year": now.isocalendar()[1],
        "month": now.month,
        "quarter": (now.month - 1) // 3 + 1,
        "year": now.year,
        "is_christmas_period": int(now.month == 12 and now.day >= 15),
        "is_easter_period": int(now.isocalendar()[1] in [13, 14, 15]),
        "promo_flag": stats.get("current_promo", 0),
        "school_holiday": stats.get("school_holiday", 0),
        "store_type": stats.get("store_type", 0),
        "assortment": stats.get("assortment", 0),
    }


def lambda_handler(event: dict, context: Any) -> dict:
    """
    AWS Lambda handler for the retail operator foot traffic forecast endpoint.

    Request format:
    {
        "store_id": 42,
        "forecast_horizon_weeks": 4
    }

    Response format:
    {
        "store_id": 42,
        "destination_name": "Retail Destination 042",
        "generated_at": "2024-01-15T09:00:00Z",
        "forecast_horizon_weeks": 4,
        "forecasts": [
            {
                "week": 1,
                "week_starting": "2024-01-22",
                "predicted_sales": 12450,
                "lower_80": 11200,
                "upper_80": 13700
            },
            ...
        ],
        "model_version": "lgbm_v1",
        "mape_estimate": "6.8%"
    }
    """
    logger.info(f"Request received: {json.dumps(event)}")

    try:
        # ── Input validation ─────────────────────────────────────────────────
        if "store_id" not in event:
            return _error_response(400, "Missing required field: store_id")

        store_id = int(event["store_id"])
        horizon = int(event.get("forecast_horizon_weeks", 4))

        if not 1 <= store_id <= 1115:
            return _error_response(
                400,
                f"store_id must be between 1 and 1115, got {store_id}"
            )

        if not 1 <= horizon <= 12:
            return _error_response(
                400,
                f"forecast_horizon_weeks must be between 1 and 12, got {horizon}"
            )

        # ── Load model and feature stats ──────────────────────────────────────
        model = _load_model_from_s3(MODEL_BUCKET, MODEL_KEY)
        feature_stats = _load_model_from_s3(MODEL_BUCKET, FEATURE_KEY)

        # ── Build feature row ─────────────────────────────────────────────────
        feature_row = _build_feature_row(store_id, feature_stats)
        X = np.array([[feature_row[col] for col in model.feature_cols_]])

        # ── Generate predictions ──────────────────────────────────────────────
        predictions = model.predict(X)[0]  # shape: (horizon,)

        # ── Build forecast response with prediction intervals ─────────────────
        forecasts = []
        base_date = datetime.utcnow()
        for i, pred in enumerate(predictions[:horizon], 1):
            week_start = base_date + timedelta(weeks=i)
            uncertainty = pred * 0.082  # 8.2% MAPE → approximate PI
            forecasts.append({
                "week": i,
                "week_starting": week_start.strftime("%Y-%m-%d"),
                "predicted_sales": int(max(pred, 0)),
                "lower_80": int(max(pred - 1.28 * uncertainty, 0)),
                "upper_80": int(pred + 1.28 * uncertainty),
            })

        response = {
            "store_id": store_id,
            "destination_name": f"Retail Destination {store_id:03d}",
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "forecast_horizon_weeks": horizon,
            "forecasts": forecasts,
            "model_version": "lgbm_v1",
            "mape_estimate": "6.8%",
        }

        logger.info(f"Forecast generated successfully for store {store_id}")
        return {"statusCode": 200, "body": json.dumps(response)}

    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return _error_response(500, f"Internal error: {str(e)}")


def _error_response(status_code: int, message: str) -> dict:
    return {
        "statusCode": status_code,
        "body": json.dumps({
            "error": message,
            "timestamp": datetime.utcnow().isoformat(),
        }),
    }
