import joblib
import pandas as pd

# Chargement du modèle
model = joblib.load("modele_rendement_agricole.pkl")

def predict_rendement(region, culture, type_sol,
                      surface_ha, pluviometrie_mm, temperature_c):
    data = pd.DataFrame([{
        "region": region,
        "culture": culture,
        "type_sol": type_sol,
        "surface_ha": surface_ha,
        "pluviometrie_mm": pluviometrie_mm,
        "temperature_moyenne_c": temperature_c
    }])

    prediction = model.predict(data)
    return round(prediction[0], 2)
