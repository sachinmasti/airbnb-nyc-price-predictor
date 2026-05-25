import pandas as pd
import numpy as np
from scipy.stats import mstats
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import FunctionTransformer, PowerTransformer
from sklearn.compose import TransformedTargetRegressor, ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from catboost import CatBoostRegressor
from category_encoders import TargetEncoder

# Define global variables for column selection
vector_col = ['name']
target_encoding_col = ['neighbourhood', 'neighbourhood_group', 'room_type']

def make_1D(x):
    """
    Helper function to flatten arrays for text vectorization inside pipeline.
    Must be defined globally for joblib serialization/deserialization.
    """
    return np.ravel(x)

def get_model_pipeline():
    """
    Constructs and returns the CatBoost regressor pipeline as defined by the user.
    """
    # 1. Base regressor inside a transformed target regressor (PowerTransformer on target)
    xgb_base = CatBoostRegressor(
        max_depth=4, 
        n_estimators=100, 
        learning_rate=0.1, 
        verbose=0  # set verbose to 0 to keep console output clean
    )

    target_transformer_model = TransformedTargetRegressor(
        regressor=xgb_base,
        transformer=PowerTransformer(method='yeo-johnson')
    )

    # 2. Text column preprocessing (Impute -> Flatten to 1D -> TF-IDF Vectorizer)
    impute_pipe = Pipeline(steps=[
        ('impute', SimpleImputer(strategy='most_frequent')),
        ('squeeze', FunctionTransformer(make_1D)),
        ('vectorized', TfidfVectorizer(max_features=100))
    ])

    # 3. Categorical column preprocessing (Target Encoder)
    target_encod_pipe = Pipeline(steps=[
        ('encoding', TargetEncoder())
    ])

    # 4. Column Transformer to combine preprocessing steps
    column_wise_process = ColumnTransformer(
        transformers=[
            ('impute', impute_pipe, vector_col),
            ('encoding', target_encod_pipe, target_encoding_col),
        ],
        remainder='passthrough'
    )

    # 5. Final full pipeline (Preprocessing -> Model)
    cat_pipe = Pipeline(steps=[
        ('processor', column_wise_process),
        ('model', target_transformer_model)
    ])

    return cat_pipe

def load_and_preprocess_data(filepath='feature_engineering_file'):
    """
    Loads features, splits train/test, and winsorizes the target column (price).
    """
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    
    # Split features and target
    X = df.drop(columns='price')
    y = df['price']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        shuffle=True, 
        random_state=42
    )
    
    # Winsorize the target variable (price) to handle outliers
    print("Winsorizing target variable (price)...")
    y_train_winsorized = np.asarray(mstats.winsorize(y_train, limits=[0.05, 0.10]))
    y_test_winsorized = np.asarray(mstats.winsorize(y_test, limits=[0.05, 0.10]))
    
    return X_train, X_test, y_train_winsorized, y_test_winsorized

def train_and_save(model_path='airbnb_model.joblib'):
    """
    Trains the full pipeline and saves the fitted model to disk.
    """
    X_train, X_test, y_train, y_test = load_and_preprocess_data()
    
    print("Initializing pipeline...")
    pipeline = get_model_pipeline()
    
    print("Fitting model (this may take a moment)...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print("\n--- Model Evaluation Results ---")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"Mean Squared Error (MSE):  {mse:.4f}")
    print(f"R-squared Score (R2):      {r2:.4f}")
    print("--------------------------------\n")
    
    print(f"Saving model to {model_path}...")
    joblib.dump(pipeline, model_path)
    print("Model successfully saved!")

if __name__ == '__main__':
    train_and_save()

