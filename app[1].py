from flask import Flask, request, jsonify, render_template
import numpy as np
import joblib
import os
import json
import sys
from pathlib import Path
import pandas as pd

# Crucial: Import make_1D so that joblib can deserialize the model pipeline successfully
from model_pipeline import make_1D

# The saved joblib was created from a script where make_1D lived in __main__.
# Gunicorn imports this app as a module, so expose the function there as well.
sys.modules['__main__'].make_1D = make_1D

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent

# Load model at startup
model_path = BASE_DIR / 'airbnb_model.joblib'
if os.path.exists(model_path):
    print(f"Loading trained model from {model_path}...")
    model = joblib.load(model_path)
else:
    print(f"WARNING: Model file {model_path} not found. Please run model_pipeline.py first.")
    model = None

# Load compact deployment metadata instead of the full feature engineering CSV.
metadata_path = BASE_DIR / 'model_metadata.json'
if os.path.exists(metadata_path):
    print(f"Loading deployment metadata from {metadata_path}...")
    with open(metadata_path, encoding='utf-8') as metadata_file:
        metadata = json.load(metadata_file)

    group_to_neighbourhoods = metadata['group_to_neighbourhoods']
    neighbourhood_stats = metadata['neighbourhood_stats']
    global_defaults = metadata['global_defaults']
else:
    print(f"ERROR: Metadata file {metadata_path} not found. Default stats cannot be computed.")
    group_to_neighbourhoods = {}
    neighbourhood_stats = {}
    global_defaults = {}

def haversine_distance(lat1, lon1, lat2=40.7580, lon2=-73.9855):
    """
    Computes distance to Times Square in km.
    """
    r = 6371.0 # Radius of Earth in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return r * c

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """
    Endpoint returning the neighborhood groups and corresponding neighborhoods list.
    """
    return jsonify(group_to_neighbourhoods)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint to receive inputs, compute features on the fly, run inference, and return predictions.
    """
    global model
    if model is None:
        # Try to load model again in case it was created after startup
        if os.path.exists(model_path):
            model = joblib.load(model_path)
        else:
            return jsonify({'error': 'Model is not trained/available yet. Please run training script first.'}), 500
            
    try:
        data = request.json
        
        # User input features
        name = data.get('name', '')
        neighbourhood_group = data.get('neighbourhood_group', '')
        neighbourhood = data.get('neighbourhood', '')
        room_type = data.get('room_type', 'Private room')
        minimum_nights = float(data.get('minimum_nights', 1))
        number_of_reviews = float(data.get('number_of_reviews', 0))
        availability_365 = float(data.get('availability_365', 0))
        
        # Look up neighborhood stats for coordinate and feature defaults
        stats = neighbourhood_stats.get(neighbourhood, global_defaults)
        
        latitude = stats.get('latitude', global_defaults['latitude'])
        longitude = stats.get('longitude', global_defaults['longitude'])
        calculated_host_listings_count = stats.get('calculated_host_listings_count', global_defaults['calculated_host_listings_count'])
        is_professional_host = stats.get('is_professional_host', global_defaults['is_professional_host'])
        
        # Calculate dynamic text feature flags from name
        name_lower = name.lower()
        is_luxury = 1 if any(word in name_lower for word in ['luxury', 'luxurious', 'penthouse', 'high-end', 'modernist', 'elegant']) else 0
        is_cozy = 1 if any(word in name_lower for word in ['cozy', 'cosy', 'charming', 'sweet', 'warm', 'cute']) else 0
        is_studio = 1 if any(word in name_lower for word in ['studio', 'loft', '1-bedroom', '1br', 'efficiency']) else 0
        is_subway = 1 if any(word in name_lower for word in ['subway', 'train', 'metro', 'transit', 'bus', 'station']) else 0
        name_length = float(len(name))
        
        # reviews_per_month defaults to mean of neighborhood if reviews > 0, else 0.0
        if number_of_reviews > 0:
            reviews_per_month = stats.get('reviews_per_month', global_defaults['reviews_per_month'])
        else:
            reviews_per_month = 0.0
            
        # is_available
        is_available = 1 if availability_365 > 0 else 0
        
        # Dates of last review
        last_review_day = stats.get('last_review_day', global_defaults['last_review_day'])
        last_review_year = stats.get('last_review_year', global_defaults['last_review_year'])
        last_review_month = stats.get('last_review_month', global_defaults['last_review_month'])
        last_review_day_of_week = stats.get('last_review_day_of_week', global_defaults['last_review_day_of_week'])
        
        # Distance to Times Square
        distance_to_times_square_km = haversine_distance(latitude, longitude)
        
        # Build the final features dataframe row in the EXACT same order as model was trained
        # Order: ['name', 'neighbourhood_group', 'neighbourhood', 'latitude', 'longitude', 
        #         'room_type', 'minimum_nights', 'number_of_reviews', 'reviews_per_month', 
        #         'calculated_host_listings_count', 'availability_365', 'is_available', 
        #         'last_review_day', 'last_review_year', 'last_review_month', 'last_review_day_of_week', 
        #         'name_length', 'is_luxury', 'is_cozy', 'is_studio', 'is_subway', 
        #         'is_professional_host', 'distance_to_times_square_km']
        
        feature_dict = {
            'name': [name],
            'neighbourhood_group': [neighbourhood_group],
            'neighbourhood': [neighbourhood],
            'latitude': [latitude],
            'longitude': [longitude],
            'room_type': [room_type],
            'minimum_nights': [minimum_nights],
            'number_of_reviews': [number_of_reviews],
            'reviews_per_month': [reviews_per_month],
            'calculated_host_listings_count': [calculated_host_listings_count],
            'availability_365': [availability_365],
            'is_available': [is_available],
            'last_review_day': [last_review_day],
            'last_review_year': [last_review_year],
            'last_review_month': [last_review_month],
            'last_review_day_of_week': [last_review_day_of_week],
            'name_length': [name_length],
            'is_luxury': [is_luxury],
            'is_cozy': [is_cozy],
            'is_studio': [is_studio],
            'is_subway': [is_subway],
            'is_professional_host': [is_professional_host],
            'distance_to_times_square_km': [distance_to_times_square_km]
        }
        
        X_input = pd.DataFrame(feature_dict)
        
        # Perform prediction
        pred_price = model.predict(X_input)[0]
        
        # Bound predicted price to be positive and realistic (since winsorization makes it between 5th and 90th percentile)
        pred_price = max(10.0, float(pred_price))
        
        # Return response
        return jsonify({
            'success': True,
            'prediction': round(pred_price, 2),
            'derived_features': {
                'distance_to_times_square_km': round(distance_to_times_square_km, 2),
                'name_length': int(name_length),
                'is_luxury': bool(is_luxury),
                'is_cozy': bool(is_cozy),
                'is_studio': bool(is_studio),
                'is_subway': bool(is_subway)
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
