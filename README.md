# 🏠 NYC Airbnb Price Predictor

> Estimate nightly Airbnb prices in New York City using listing details, neighbourhood, room type, reviews, and more — powered by a CatBoost ML model.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20App-FF5A5F?style=for-the-badge&logo=airbnb&logoColor=white)](https://airbnb-nyc-price-predictor.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

---

## ✨ Features

- 🔮 **Price Prediction** — Estimates nightly listing price based on multiple listing attributes
- 🗺️ **Dynamic Dropdowns** — Borough and neighbourhood options update automatically
- 🔑 **Keyword Analysis** — Detects title keywords like `luxury`, `cozy`, `studio`, `subway` to influence predictions
- 📍 **Location Scoring** — Calculates distance from Times Square as a proximity feature
- 📱 **Responsive UI** — Clean, mobile-friendly Flask web interface
- 🛡️ **Fallback Estimator** — Rule-based fallback if the ML model fails to load in the hosting environment

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ML Model | CatBoost, scikit-learn |
| Data Processing | Pandas, NumPy |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Render (free tier) |

---

## 📁 Project Structure

```
airbnb-price-predictor/
│
├── app.py                  # Flask backend & prediction endpoints
├── airbnb_model.joblib     # Trained model artifact
├── model_pipeline.py       # Pipeline helper for deserialization
├── model_metadata.json     # Location defaults from feature engineering
├── requirements.txt        # Python dependencies
│
├── templates/              # Jinja2 HTML templates
└── static/                 # CSS & JavaScript assets
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- pip

### Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/your-username/airbnb-nyc-price-predictor.git
cd airbnb-nyc-price-predictor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the Flask server
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## ☁️ Deploy on Render

1. Push your code to a GitHub repository
2. Connect the repo to [Render](https://render.com)
3. Use the following settings:

| Setting | Value |
|---|---|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT app:app` |

> **Note:** The app includes a rule-based fallback estimator so the demo stays usable even if the serialized `.joblib` model cannot be loaded in the Render environment.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is open source. Feel free to use and modify it for your own projects.

---

<p align="center">Made with ❤️ | Deployed on <a href="https://render.com">Render</a></p>
