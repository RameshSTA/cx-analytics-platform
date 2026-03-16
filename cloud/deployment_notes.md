# Customer Experience Analytics Platform — AWS Deployment Guide

**Service:** Foot Traffic Forecast API
**Runtime:** Python 3.11
**Last updated:** March 2026

---

## Overview

The inference pipeline follows a three-step architecture:

```
[ Training Pipeline ]     [ Storage ]      [ Serving Layer ]       [ Consumers ]
  notebooks/               Amazon S3       AWS Lambda               API Gateway
  02_forecasting.ipynb  ──► model bucket ──► lambda_handler.py ──► HTTP endpoint
                                                                    ▼
                                                             the retail operator Dashboard
                                                             CX Analytics Team
```

1. **Train** — Run `02_forecasting.ipynb` to fit the LightGBM model on Rossmann/the retail operator data.
2. **Store** — Export the model artifact to S3 (`retail-cx-models` bucket).
3. **Serve** — Lambda loads the model on warm start and returns forecasts via API Gateway.

---

## Step 1: Train and Export the Model

Run the following at the end of `02_forecasting.ipynb` (or in a standalone training script):

```python
import joblib
import boto3

# Save model artifact locally
joblib.dump(model, "lgbm_forecaster_v1.pkl")

# Upload to S3
s3 = boto3.client("s3")
s3.upload_file(
    "lgbm_forecaster_v1.pkl",
    "retail-cx-models",
    "models/lgbm_forecaster_v1.pkl",
)

# Upload feature statistics (store-level baseline stats for inference)
import pickle
with open("feature_stats_v1.pkl", "wb") as f:
    pickle.dump(feature_stats_dict, f)

s3.upload_file(
    "feature_stats_v1.pkl",
    "retail-cx-models",
    "models/feature_stats_v1.pkl",
)

print("Model artifacts uploaded to s3://retail-cx-models/models/")
```

**S3 bucket structure:**
```
retail-cx-models/
  models/
    lgbm_forecaster_v1.pkl      ← trained model
    feature_stats_v1.pkl        ← per-store historical statistics
  archive/
    lgbm_forecaster_v0.pkl      ← previous version (kept for rollback)
```

---

## Step 2: Create the Lambda Function

**Option A — AWS Console:**

1. Open Lambda → Create function → Author from scratch
2. Function name: `retail-cx-forecast`
3. Runtime: Python 3.11
4. Architecture: x86_64
5. Execution role: create new (configure in Step 3)

**Option B — AWS CLI:**

```bash
# Package the handler and dependencies
pip install boto3 numpy lightgbm -t ./package
cp cloud/lambda_handler.py ./package/
cd package && zip -r ../westfield_forecast.zip . && cd ..

# Create the function
aws lambda create-function \
  --function-name retail-cx-forecast \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://westfield_forecast.zip \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/retail-lambda-role \
  --memory-size 512 \
  --timeout 30 \
  --region eu-west-2
```

**Function configuration:**
| Setting | Value | Rationale |
|---------|-------|-----------|
| Memory | 512 MB | LightGBM model + numpy arrays fit comfortably |
| Timeout | 30 seconds | Includes S3 cold-load; warm starts are <200ms |
| Concurrency | 10 reserved | Sufficient for 42 destinations × typical request rate |
| Ephemeral storage | 512 MB (default) | Model is loaded into memory, not disk |

---

## Step 3: Configure the IAM Role

Create a role named `retail-lambda-role` with the following inline policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadModelArtifacts",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::retail-cx-models/models/*"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:eu-west-2:YOUR_ACCOUNT_ID:log-group:/aws/lambda/retail-cx-forecast:*"
    }
  ]
}
```

Also attach the AWS managed policy `AWSLambdaBasicExecutionRole` as the trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

---

## Step 4: Set Environment Variables

Configure these environment variables on the Lambda function (do not hardcode in source):

| Variable | Value | Description |
|----------|-------|-------------|
| `MODEL_BUCKET` | `retail-cx-models` | S3 bucket containing model artifacts |
| `MODEL_KEY` | `models/lgbm_forecaster_v1.pkl` | S3 key for the trained model |
| `FEATURE_KEY` | `models/feature_stats_v1.pkl` | S3 key for per-store feature statistics |

**AWS CLI:**
```bash
aws lambda update-function-configuration \
  --function-name retail-cx-forecast \
  --environment "Variables={
    MODEL_BUCKET=retail-cx-models,
    MODEL_KEY=models/lgbm_forecaster_v1.pkl,
    FEATURE_KEY=models/feature_stats_v1.pkl
  }"
```

---

## Step 5: Test with a Sample Payload

**Via AWS CLI (invoke directly):**
```bash
aws lambda invoke \
  --function-name retail-cx-forecast \
  --payload '{"store_id": 42, "forecast_horizon_weeks": 4}' \
  --cli-binary-format raw-in-base64-out \
  response.json && cat response.json
```

**Expected response:**
```json
{
  "statusCode": 200,
  "body": "{\"store_id\": 42, \"destination_name\": \"Retail Destination 042\", \"generated_at\": \"2026-03-15T09:00:00Z\", \"forecast_horizon_weeks\": 4, \"forecasts\": [{\"week\": 1, \"week_starting\": \"2026-03-22\", \"predicted_sales\": 12450, \"lower_80\": 11200, \"upper_80\": 13700}, ...], \"model_version\": \"lgbm_v1\", \"mape_estimate\": \"6.8%\"}"
}
```

**Validate error handling:**
```bash
# Missing store_id
aws lambda invoke \
  --function-name retail-cx-forecast \
  --payload '{"forecast_horizon_weeks": 4}' \
  --cli-binary-format raw-in-base64-out \
  error_response.json && cat error_response.json
# Expected: {"statusCode": 400, "body": "{\"error\": \"Missing required field: store_id\", ...}"}

# Out-of-range horizon
aws lambda invoke \
  --function-name retail-cx-forecast \
  --payload '{"store_id": 42, "forecast_horizon_weeks": 52}' \
  --cli-binary-format raw-in-base64-out \
  range_error.json && cat range_error.json
# Expected: {"statusCode": 400, "body": "{\"error\": \"forecast_horizon_weeks must be between 1 and 12...\"}"}
```

---

## Step 6: Attach API Gateway for HTTP Access

1. Open API Gateway → Create API → REST API (not HTTP API — we need usage plans)
2. Create resource: `/forecast`
3. Create method: `POST` → Lambda Function → `retail-cx-forecast`
4. Enable Lambda Proxy Integration (passes full event to handler)
5. Deploy to stage `prod`

**AWS CLI (HTTP API — simpler for internal use):**
```bash
aws apigatewayv2 create-api \
  --name retail-cx-forecast-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:eu-west-2:YOUR_ACCOUNT_ID:function:retail-cx-forecast

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission \
  --function-name retail-cx-forecast \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:eu-west-2:YOUR_ACCOUNT_ID:*"
```

**Resulting endpoint:**
```
POST https://XXXXXXXXXXXX.execute-api.eu-west-2.amazonaws.com/forecast
Content-Type: application/json

{"store_id": 42, "forecast_horizon_weeks": 4}
```

**Secure with API key (recommended for production):**
```bash
# Create usage plan + API key
aws apigateway create-api-key --name retail-dashboard-key --enabled
```

---

## Step 7: Monitor with CloudWatch

**CloudWatch Log Insights query — recent errors:**
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50
```

**CloudWatch Alarm — error rate threshold:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name retail-forecast-error-rate \
  --alarm-description "the retail operator forecast Lambda error rate > 1%" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --dimensions Name=FunctionName,Value=retail-cx-forecast \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:eu-west-2:YOUR_ACCOUNT_ID:retail-cx-alerts \
  --treat-missing-data notBreaching
```

**CloudWatch Dashboard — key metrics to track:**
| Metric | Threshold | Action if breached |
|--------|-----------|-------------------|
| `Errors` | > 5 per 5 min | Page on-call engineer |
| `Duration` (p99) | > 25,000ms | Investigate cold start; consider provisioned concurrency |
| `Throttles` | > 0 for 10 min | Increase reserved concurrency |
| `ConcurrentExecutions` | > 8 | Pre-scale before peak periods |

---

## Cost Estimate

Based on 42 retail destinations querying hourly (8,760 requests/destination/year = 367,920 annual requests):

| Service | Usage | Monthly Cost (est.) |
|---------|-------|-------------------|
| **Lambda** | 367,920 requests/yr × 512MB × avg 800ms | ~$1.20/month |
| **S3** | 2 model files (~50MB total) + GET requests | ~$0.10/month |
| **API Gateway** | 367,920 HTTP requests/yr | ~$0.40/month |
| **CloudWatch Logs** | ~5GB/month log ingestion | ~$2.50/month |
| **Total** | | **~$4.20/month** |

Notes:
- Cold start penalty (~2s) applies after 15 minutes of inactivity; use provisioned concurrency (~$15/month) if sub-second latency is required.
- Data transfer costs are negligible for payloads of this size.
- Cost scales linearly with request volume; dashboard refreshes should be rate-limited to avoid unnecessary invocations.

---

## Production Considerations

### VPC Configuration
Place Lambda inside the the operations VPC if it needs to access:
- RDS / Aurora (feature store)
- ElastiCache (response caching)
- Internal APIs

Add VPC configuration:
```bash
aws lambda update-function-configuration \
  --function-name retail-cx-forecast \
  --vpc-config SubnetIds=subnet-XXXXXX,subnet-YYYYYY,SecurityGroupIds=sg-ZZZZZZ
```

Note: VPC-attached Lambdas have higher cold start latency (~500ms extra). Use provisioned concurrency to mitigate.

### Encryption
- Model artifacts in S3 should use SSE-S3 or SSE-KMS encryption.
- Enable KMS envelope encryption for environment variables containing sensitive config.
- All API Gateway traffic is TLS 1.2+ by default.

### Model Versioning
Maintain a versioning convention so you can roll back without downtime:

```
models/
  lgbm_forecaster_v1.pkl    ← current production
  lgbm_forecaster_v2.pkl    ← candidate (A/B test or shadow mode)
  lgbm_forecaster_v0.pkl    ← previous production (kept 30 days)
```

Use Lambda aliases and weighted routing to run A/B tests between model versions:
```bash
# Route 10% of traffic to the new model version
aws lambda update-alias \
  --function-name retail-cx-forecast \
  --name prod \
  --routing-config AdditionalVersionWeights={"2"=0.1}
```

### CI/CD Pipeline
Automate model deployment with a GitHub Actions or AWS CodePipeline workflow:
1. Merge to `main` triggers training job (SageMaker or EC2)
2. On training success, upload new model artifact to S3 with version tag
3. Run integration tests against the Lambda test endpoint
4. Promote model to production via alias update if tests pass
5. Monitor error rate for 24 hours; auto-rollback if error rate exceeds threshold

### Observability Checklist
- [ ] CloudWatch alarms configured for errors and latency
- [ ] X-Ray tracing enabled for end-to-end latency profiling
- [ ] Structured logging (JSON) for log aggregation in CloudWatch Insights
- [ ] Model performance dashboard: weekly MAPE vs actuals (requires feedback loop)
- [ ] Dead-letter queue (SQS or SNS) for async invocation failures
