"""Carga y gestión de modelos de machine learning"""

import joblib
import sys
from config.settings import MODEL_PATH, SCALER_PATH


class ModelLoader:
    def __init__(self):
        self.kmeans_model = None
        self.scaler = None
        self.load_models()

    def load_models(self):
        """Cargar modelo y escalador"""
        try:
            self.kmeans_model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            print("[OK] Modelo y escalador cargados correctamente")
            print(f"[INFO] Modelo con {self.kmeans_model.n_clusters} clusters")
        except FileNotFoundError:
            print("[ERROR] No se encontraron los archivos del modelo.")
            print("Ejecuta primero 'python quick_dataset_setup.py'")
            sys.exit(1)

    def get_model(self):
        return self.kmeans_model

    def get_scaler(self):
        return self.scaler
