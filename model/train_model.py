import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

# Load dataset
df = pd.read_csv("data/paper_dataset.csv")

# Features and targets
features = [
    "num_citations", "num_figures", "num_equations",
    "total_words", "avg_sentence_length"
]
X = df[features]
y_novelty = df["novelty_score"]
y_clarity = df["clarity_score"]

# Train-test split
X_train, X_test, y_n_train, y_n_test = train_test_split(X, y_novelty, test_size=0.2, random_state=42)
X_train, X_test, y_c_train, y_c_test = train_test_split(X, y_clarity, test_size=0.2, random_state=42)

# Train Random Forest Regressors
novelty_model = RandomForestRegressor(n_estimators=100, random_state=42)
clarity_model = RandomForestRegressor(n_estimators=100, random_state=42)

novelty_model.fit(X_train, y_n_train)
clarity_model.fit(X_train, y_c_train)

# Save models
os.makedirs("model", exist_ok=True)
joblib.dump(novelty_model, "model/novelty_model.pkl")
joblib.dump(clarity_model, "model/clarity_model.pkl")

print("✅ Models trained and saved.")
