# app/ia/modelos_ia.py
import os
from openai import OpenAI
from flask import current_app

class ModeloIA: #Clase para interactuar con el modelo de lenguaje
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY no configurada en variables de entorno")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url='https://api.groq.com/openai/v1'
        )
        self.modelo = "llama-3.3-70b-versatile"
    
    def generar_respuesta(self, sistema, usuario, temperatura=0.7, max_tokens=500):
        # Generamos respuesta usando IA
        try:
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": usuario}
                ],
                temperature=temperatura,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error al generar respuesta: {str(e)}"
    
    def generar_resumen(self, texto, longitud=100):
        #Resumen de grandes textos 
        sistema = "Eres un asistente especializado en resumir información de manera concisa."
        usuario = f"Resume el siguiente texto en {longitud} palabras máximo:\n\n{texto}"
        return self.generar_respuesta(sistema, usuario, temperatura=0.5, max_tokens=200)

    def generar_respuesta_con_historial(self, sistema, historial, usuario, temperatura=0.7, max_tokens=500):
        # Generamos respuesta usando IA considerando el historial de la conversación
        try:
            # Construir mensajes con historial
            messages = [{"role": "system", "content": sistema}]
            
            # Agregar historial
            for msg in historial:
                role = "user" if msg.es_usuario else "assistant"
                messages.append({"role": role, "content": msg.mensaje})
            
            # Agregar mensaje actual
            messages.append({"role": "user", "content": usuario})
            
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=messages,
                temperature=temperatura,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error al generar respuesta: {str(e)}"

