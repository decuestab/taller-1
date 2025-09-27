# -*- coding: utf-8 -*-
"""
Created on Sat Sep 27 08:43:03 2025

@author: cuest
"""

import gradio as gr
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
# Se mantienen las frases de PQRS
training_phrases = {
    "saludo": ["hola", "buenas", "qué tal", "hey", "saludos"],
    "iniciar_pqrs": ["tengo una queja", "quiero hacer un reclamo", "tengo una sugerencia", "quiero dejar una opinión", "necesito reportar un problema", "no estoy conforme", "felicitacion"],
    # Se añade la intención para ventas y reportes
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
state = {"step": 0, "data": {}}

def chatbot(user_input, history):
    global state
    
    # Lógica para manejar el flujo de PQRS
    if state["step"] == 0:
        intent = predict_intent(user_input)
        
        if intent == "iniciar_pqrs":
            state["step"] = 1
            response = pqrs_responses["solicitar_nombre"]
        elif intent == "reportes":
            response = pqrs_responses["reporte_ventas"]
        else:
            response = pqrs_responses.get(intent, pqrs_responses["desconocido"])
    
    elif state["step"] == 1:
        state["data"]["nombre"] = user_input
        state["step"] = 2
        response = pqrs_responses["solicitar_categoria"].format(nombre=user_input)
    
    elif state["step"] == 2:
        state["data"]["categoria"] = user_input
        state["step"] = 3
        response = pqrs_responses["solicitar_detalle"]
        
    elif state["step"] == 3:
        state["data"]["detalle"] = user_input
        state["step"] = 0
        response = pqrs_responses["confirmacion_final"]
        
    save_interaction(user_input, response)
    
    if response == pqrs_responses["confirmacion_final"]:
        print("PQRS recibida y procesada:", state["data"])
        state["data"] = {}

    history.append({"role": "assistant", "content": response})
    return history

# ------------------------------
# Interfaz Gradio
# ------------------------------
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 Asistente de experiencia de Meeiko")
    gr.Markdown("Por favor, introduce tu Petición, Queja, Reclamo o Sugerencia.")
    
    chatbot_ui = gr.ChatInterface(
        fn=chatbot,
        type="messages",
        title="Asistente de experiencia",
        description="Estoy listo para conocer tu experciencia en Meeiko."
    )

demo.launch(share=True, debug=True)