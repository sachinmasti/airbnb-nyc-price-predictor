---
title: Airbnb Price Predictor
emoji: 🏠
colorFrom: red
colorTo: pink
sdk: docker
pinned: false
---

# Airbnb Price Predictor

Flask UI for an NYC Airbnb nightly price prediction model trained with scikit-learn and CatBoost.

## Deploy on Render free tier

1. Push this `deploy` folder to a GitHub repository.
2. Create a new Render Web Service from that repository.
3. Render can use `render.yaml`, or set these manually:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - Python version: `3.12.8`

## Deploy on Hugging Face Spaces

1. Create a new Space.
2. Choose Docker as the Space SDK.
3. Upload the files from this folder.

## Files kept for deployment

- `app.py`: Flask backend and prediction endpoints.
- `airbnb_model.joblib`: trained model.
- `model_pipeline.py`: required for joblib deserialization.
- `model_metadata.json`: compact location defaults generated from the feature engineering CSV.
- `templates/` and `static/`: UI files.
## Live Demo

https://airbnb-nyc-price-predictor.onrender.com/

## Deployment Note

The deployed Render app includes a fallback estimator so the demo remains usable if the serialized Joblib model cannot be loaded in the hosting environment.
