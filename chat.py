# -*- coding: utf-8 -*-
"""
Adaptación del chatbot a Streamlit (sin Gradio)
"""

import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from datetime import datetime
import os

# ------------------------------
# Archivo Excel
# ------------------------------
EXCEL_FILE = "interacciones_chatbot.xlsx"

def save_interaction(user_msg, bot_response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_new = pd.DataFrame({
        "timestamp": [timestamp],
        "usuario": [user_msg],
        "bot": [bot_response]
    })
    if os.path.exists(EXCEL_FILE):
        df_existing = pd.read_excel(EXCEL_FILE)
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_final = df_new
    df_final.to_excel(EXCEL_FILE, index=False)

# ------------------------------
# Base de Respuestas
# ------------------------------
pqrs_responses = {
    "saludo": "👋 ¡Hola! **Soy Meeiko tu asistente de experiencia**. ¿Cómo puedo ayudarte hoy?",
    "solicitar_nombre": "📝 ¡Gracias por tu comentario! Para iniciar el proceso de tu PQRS, por favor, dime tu **primer nombre**.",
    "solicitar_categoria": "✅ ¡Hola {nombre}! Ahora, por favor, escribe la categoría a la que pertenece tu PQRS:",
    "solicitar_detalle": "👍 ¡Entendido! Por favor, detalla tu PQRS en el campo abierto que tienes a continuación. Cuanta más información, mejor.",
    "confirmacion_final": "🎉 ¡Hecho! Hemos recibido tu PQRS con éxito. Agradecemos tu valiosa retroalimentación. Un agente se comunicará contigo pronto.",
    "reporte_ventas": "📊 ¡Claro! Puedes ver los reportes de ventas y otros datos de interés en el siguiente link: [Ver Reporte de Ventas](https://ejemplo7storytellingpy-brtsy4qyrbmneg4ynxwz8o.streamlit.app/)",
    "desconocido": "❓ No entendí tu consulta. Por favor, usa palabras clave como 'queja', 'sugerencia', 'felicitación', 'ventas' o 'reportes'."
}

# ------------------------------
# Palabras clave y frases de entrenamiento
# ------------------------------
training_phrases = {
    "saludo": ["hola", "buenas", "qué tal", "hey", "saludos"],
    "iniciar_pqrs": ["tengo una queja", "quiero hacer un reclamo", "tengo una sugerencia",
                     "quiero dejar una opinión", "necesito reportar un problema",
                     "no estoy conforme", "felicitacion"],
    "reportes": ["reporte", "ventas", "informe", "datos", "resultados"],
}

# ------------------------------
# Entrenamiento NLP
# ------------------------------
X, y = [], []
for intent, phrases in training_phrases.items():
    for phrase in phrases:
        X.append(phrase)
        y.append(intent)

vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)
model = NearestNeighbors(n_neighbors=1, metric="cosine").fit(X_vec)

def predict_intent(user_input):
    user_vec = vectorizer.transform([user_input])
    dist, idx = model.kneighbors(user_vec)
    intent = y[idx[0][0]]
    confidence = 1 - dist[0][0]
    return intent if confidence >= 0.5 else None

# ------------------------------
# Lógica del Chatbot
# ------------------------------
if "s
