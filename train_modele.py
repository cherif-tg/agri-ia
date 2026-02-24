import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# 1. Chargement des données
df = pd.read_csv("donnees_agricoles_togo.csv")

X = df.drop("rendement_t_ha", axis=1)
y = df["rendement_t_ha"]

# 2. Colonnes
categorical_features = ["region", "culture", "type_sol"]
numerical_features = [
    "surface_ha",
    "pluviometrie_mm",
    "temperature_moyenne_c"
]

# 3. Prétraitement
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("num", "passthrough", numerical_features)
    ]
)

# 4. Modèle
model = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    random_state=42
)

# 5. Pipeline complet
pipeline = Pipeline(
    steps=[
        ("preprocessing", preprocessor),
        ("model", model)
    ]
)

# 6. Séparation train / test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 7. Entraînement
pipeline.fit(X_train, y_train)

# 8. Évaluation
y_pred = pipeline.predict(X_test)

print("MAE :", mean_absolute_error(y_test, y_pred))
print("RMSE :", mean_squared_error(y_test, y_pred, squared=False))
print("R² :", r2_score(y_test, y_pred))

# 9. Sauvegarde du modèle
joblib.dump(pipeline, "modele_rendement_agricole.pkl")

print("Modèle entraîné et sauvegardé avec succès.")
