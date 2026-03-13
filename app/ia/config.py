# app/ia/config.py

# Archivo de configuración central para el módulo de IA
# Aquí se definen las instancias globales de IA, se importan los módulos necesarios y se establece una función de utilidad para acceder a los módulos de IA desde otras partes de la aplicación.
from .modelos_ia import ModeloIA
from .clasificador import ClasificadorIntenciones
from .consultas import ConsultasInteligentes
from .chatbot import ChatbotInteligente
from .analizador import AnalizadorInteligente

# ============================================
# INSTANCIAS GLOBALES DE IA
# ============================================

# Modelo base de IA (Groq/OpenAI)
ia_tools = ModeloIA()

# Clasificador de intenciones (analiza preguntas del usuario)
clasificador = ClasificadorIntenciones()

# Consultas inteligentes a la base de datos
consultas = ConsultasInteligentes()

# Motor principal del chatbot
chatbot = ChatbotInteligente()

# Analizador para dashboard inteligente
analizador = AnalizadorInteligente()

# ============================================
# FUNCIÓN DE UTILIDAD PARA ACCEDER A LOS MÓDULOS
# ============================================
def get_ia_module(module_name):
    # Función para acceder a los módulos de IA desde otras partes de la aplicación
    modules = {
        'ia_tools': ia_tools,
        'clasificador': clasificador,
        'consultas': consultas,
        'chatbot': chatbot,
        'analizador': analizador
    }
    return modules.get(module_name)