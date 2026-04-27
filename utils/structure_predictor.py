import joblib
import numpy as np
from pathlib import Path

# -------------------------------------------
# SET PROJECT PATHS
# -------------------------------------------

# Get base directory of project
BASE_DIR = Path(__file__).resolve().parent.parent

# Path where trained ML models are stored
MODEL_DIR = BASE_DIR / "model"

# -------------------------------------------
# LOAD TRAINED MODELS
# -------------------------------------------

# Load novelty prediction model (ML regression model)
novelty_model = joblib.load(MODEL_DIR / "novelty_model.pkl")

# Load clarity prediction model (ML regression model)
clarity_model = joblib.load(MODEL_DIR / "clarity_model.pkl")


def predict_scores(features: dict):
    """
    Predicts:
    1. Novelty Score
    2. Clarity Score

    using trained machine learning models.

    Input:
    features (dict) → extracted from paper
    """

    # -------------------------------------------
    # PREPARE INPUT FOR ML MODEL
    # -------------------------------------------

    # Convert dictionary features into numpy array
    # Order must match training data format
    input_features = np.array([
        features["num_citations"],        # Number of references
        features["num_figures"],          # Number of figures
        features["num_equations"],        # Number of equations
        features["total_words"],          # Total words in paper
        features["avg_sentence_length"]   # Average sentence length
    ]).reshape(1, -1)  # reshape for model input (1 row, multiple columns)

    # -------------------------------------------
    # PREDICT USING ML MODELS
    # -------------------------------------------

    # Predict novelty score
    novelty_score = round(
        float(novelty_model.predict(input_features)[0]),
        2
    )

    # Predict clarity score
    clarity_score = round(
        float(clarity_model.predict(input_features)[0]),
        2
    )

    # -------------------------------------------
    # RETURN RESULTS
    # -------------------------------------------

    return novelty_score, clarity_score