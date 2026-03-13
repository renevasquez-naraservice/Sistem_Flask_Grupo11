# app/ia/chatbot.py
from datetime import datetime
from flask_login import current_user
from ..extensions import db
from ..models import ConversacionChatbot, MensajeChatbot, LogInteraccionChatbot
from .modelos_ia import ModeloIA
from .clasificador import Intencion

class ChatbotInteligente:
    #modelos de IA, clasificador y consultas se inyectan para facilitar testing y mantenimiento
    def __init__(self):
        self.nombre_negocio = "Flask Parrilla"
        self.contexto_base = self._generar_contexto_base()
        self.modelo_ia = ModeloIA()
    
    def _get_clasificador(self):
        from .config import clasificador
        return clasificador
    
    def _get_consultas(self):
        from .config import consultas
        return consultas
    
    # ... resto del código igual, usando self._get_clasificador() y self._get_consultas()
    def _generar_contexto_base(self):
        # Texto de entrada del negocio para la IA, con información clave y personalidad del bot
        return f"""
        Eres un asistente virtual de '{self.nombre_negocio}', restaurante especializado en carnes a la parrilla y comida tradicional boliviana.
        
        INFORMACIÓN DEL NEGOCIO:
        - Ofrecemos productos de carnes de alta calidad
        - Atendemos pedidos personalizados
        - Horario de atención: 9:00 AM - 8:00 PM
        
        PERSONALIDAD:
        - Amable y servicial
        - Conocimiento experto en carnes y comida tradicional boliviana
        - Responde de manera concisa y útil
        
        VALORES:
        - Calidad: Cortes seleccionados y frescos
        - Tradición: Técnicas de asado heredadas
        - Innovación: Gestión tecnológica de vanguardia
        - Servicio: Atención cálida y personalizada
        
        REGLAS:
        - Siempre saluda amablemente
        - Si no sabes algo, ofrece ayuda para encontrar la información
        - Mantén respuestas cortas (máximo 3 oraciones)

        ESLOGAN
        - Donde la tecnología y el buen gusto se encuentran.
        """
        
    def procesar_mensaje(self, mensaje_usuario, id_conversacion=None):
        inicio = datetime.utcnow()
        
        try:
            # 1. Obtener historial de la conversación
            historial = self._obtener_historial_conversacion(id_conversacion)
            
            # 2. Clasificar intención
            clasificador = self._get_clasificador()
            intencion = clasificador.clasificar(mensaje_usuario)
            entidades = clasificador.extraer_entidades(mensaje_usuario)
            
            # 3. Ejecutar consulta a BD según intención
            if intencion != Intencion.SALUDO and intencion != Intencion.AYUDA:
                consultas = self._get_consultas()
                datos_bd = consultas.ejecutar(intencion, entidades)
            else:
                datos_bd = None
            
            # 4. Construir contexto con historial
            contexto = self._construir_contexto_con_historial(
                intencion, datos_bd, entidades, historial
            )
            
            # 5. Generar respuesta con IA
            respuesta_ia = self.modelo_ia.generar_respuesta_con_historial(
                sistema=self.contexto_base,
                historial=historial,
                usuario=mensaje_usuario,
                temperatura=0.7,
                max_tokens=300
            )
            
            # 6. Si hay datos estructurados, mejorar respuesta
            respuesta_final = self._mejorar_respuesta(respuesta_ia, datos_bd)
            
            # 7. Guardar en base de datos
            id_conversacion = self._guardar_interaccion(
                mensaje_usuario, 
                respuesta_final, 
                intencion, 
                entidades,
                id_conversacion,
                inicio
            )
            
            return {
                'respuesta': respuesta_final,
                'id_conversacion': id_conversacion,
                'intencion': intencion.value,
                'datos': datos_bd
            }
            
        except Exception as e:
            self._guardar_error(mensaje_usuario, str(e), id_conversacion)
            return {
                'respuesta': "Lo siento, tuve un problema procesando tu mensaje. ¿Puedes intentar de nuevo?",
                'id_conversacion': id_conversacion,
                'error': True
            }
    def _construir_contexto(self, intencion, datos_bd, entidades):
        # Construye un contexto específico para la IA basado en la intención y datos disponibles (IA)
        contexto = self.contexto_base + "\n\n"
        
        if intencion == Intencion.SALUDO:
            contexto += "El usuario te está saludando. Responde amablemente y ofrece tu ayuda."
        
        elif intencion == Intencion.AYUDA:
            contexto += """
            El usuario necesita ayuda. Explícale brevemente lo que puedes hacer:
            - Consultar productos disponibles
            - Verificar stock
            - Recomendar productos
            - Información de ventas y pedidos
            - Análisis del negocio
            """
        
        elif datos_bd:
            # Incluir datos de la BD en el contexto
            contexto += f"INFORMACIÓN ACTUAL DEL SISTEMA:\n"
            
            if datos_bd.get('tipo') == 'lista_productos':
                productos = datos_bd.get('productos', [])
                contexto += "Productos disponibles:\n"
                for p in productos[:5]:
                    contexto += f"- {p.nombre}: ${p.precio:.2f} (stock: {p.stock})\n"
            
            elif datos_bd.get('tipo') == 'stock':
                contexto += f"{datos_bd.get('mensaje', '')}\n"
                
                productos = datos_bd.get('con_stock', [])
                for p in productos[:5]:
                    contexto += f"- {p.nombre}: {p.stock} unidades\n"
            
            elif datos_bd.get('tipo') == 'recomendaciones':
                recomendados = datos_bd.get('recomendados', [])
                contexto += "Productos recomendados:\n"
                for p in recomendados[:3]:
                    contexto += f"- {p.nombre}: ${p.precio:.2f} - {p.descripcion[:50]}...\n"
        
        return contexto
    
    def _mejorar_respuesta(self, respuesta_ia, datos_bd):
        #Mejora la respuesta del CHATBOT
        if not datos_bd:
            return respuesta_ia
        
        # Si hay datos estructurados, asegurar que la respuesta los incluya
        if datos_bd.get('tipo') == 'conteo':
            return f"{respuesta_ia}\n\n📊 En resumen: {datos_bd.get('mensaje', '')}"
        
        elif datos_bd.get('tipo') == 'top_producto':
            return f"🏆 {respuesta_ia}"
        
        elif datos_bd.get('tipo') == 'recomendaciones':
            productos = datos_bd.get('recomendados', [])
            if productos:
                return respuesta_ia + "\n\nPuedes ver más detalles en nuestro catálogo."
        
        return respuesta_ia
    
    def _guardar_interaccion(self, pregunta, respuesta, intencion, entidades, id_conversacion, inicio):
        #guardar interacción en la Base de datos
        tiempo_respuesta = (datetime.utcnow() - inicio).total_seconds() * 1000
        
        # Obtener o crear conversación
        if not id_conversacion and current_user.is_authenticated:
            conv = ConversacionChatbot(
                id_usuario=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(conv)
            db.session.flush()
            id_conversacion = conv.id
        
        # Guardar mensaje del usuario
        msg_usuario = MensajeChatbot(
            id_conversacion=id_conversacion,
            es_usuario=True,
            mensaje=pregunta,
            intencion_detectada=intencion.value,
            entidades_extraidas=entidades
        )
        
        # Guardar respuesta del bot
        msg_bot = MensajeChatbot(
            id_conversacion=id_conversacion,
            es_usuario=False,
            mensaje=respuesta,
            intencion_detectada=intencion.value,
            tiempo_respuesta=tiempo_respuesta
        )
        
        db.session.add_all([msg_usuario, msg_bot])
        db.session.commit()
        
        return id_conversacion
    
    def _guardar_error(self, pregunta, error, id_conversacion):
        #Errores guardar para debuging y mejora continua
        log = LogInteraccionChatbot(
            id_usuario=current_user.id if current_user.is_authenticated else None,
            id_conversacion=id_conversacion,
            tipo_accion='error',
            descripcion=f"Error procesando: {pregunta}",
            datos_consulta={'pregunta': pregunta},
            resultado=error,
            exitoso=False
        )
        db.session.add(log)
        db.session.commit()

    def _obtener_historial_conversacion(self, id_conversacion, limite=5):
        #Obtiene el historial de mensajes de una conversación específica
        if not id_conversacion:
            return []
        
        mensajes = MensajeChatbot.query.filter_by(
            id_conversacion=id_conversacion
        ).order_by(MensajeChatbot.fecha.desc()).limit(limite * 2).all()
        
        # Invertir para orden cronológico
        return list(reversed(mensajes))
    def _construir_contexto_con_historial(self, intencion, datos_bd, entidades, historial):
        # construye un contexto para la IA que incluye información relevante de la conversación anterior y datos actuales, para mejorar la coherencia y relevancia de las respuestas. Esto es especialmente útil para mantener el hilo de la conversación y evitar respuestas genéricas o repetitivas.
        contexto = self.contexto_base + "\n\n"
        
        # Resumir la conversación anterior (últimos 3 intercambios)
        if historial:
            contexto += "📝 **RESUMEN DE LA CONVERSACIÓN ANTERIOR:**\n"
            # Tomar los últimos 3 mensajes (pares usuario-asistente)
            mensajes_mostrar = historial[-6:] if len(historial) > 6 else historial
            for msg in mensajes_mostrar:
                emoji = "👤" if msg.es_usuario else "🤖"
                preview = msg.mensaje[:80] + "..." if len(msg.mensaje) > 80 else msg.mensaje
                contexto += f"{emoji} {preview}\n"
            contexto += "\n"
            
            # Instrucción especial para evitar saludos repetidos
            if any(msg.es_usuario and "hola" in msg.mensaje.lower() for msg in historial):
                contexto += "⚠️ IMPORTANTE: El usuario YA saludó antes. NO vuelvas a saludar. Continúa la conversación naturalmente.\n\n"
        
        # Información actual según intención
        if intencion == Intencion.SALUDO:
            if historial:
                contexto += "El usuario ya ha hablado antes. No repitas el saludo inicial, simplemente continúa la conversación de manera natural preguntando cómo puedes ayudarle."
            else:
                contexto += "El usuario te está saludando por primera vez. Preséntate brevemente y ofrece tu ayuda."
        
        elif intencion == Intencion.AYUDA:
            contexto += """
            El usuario necesita ayuda. Basándote en la conversación anterior, puedes:
            - Si ya hablaron de productos, profundiza en esos temas
            - Si es primera vez, ofrece las opciones generales
            - Sé específico y útil
            """
        
        elif datos_bd:
            contexto += f"📊 **INFORMACIÓN ACTUAL DEL SISTEMA:**\n"
            
            if datos_bd.get('tipo') == 'lista_productos':
                productos = datos_bd.get('productos', [])
                contexto += "Productos disponibles:\n"
                for p in productos[:5]:
                    contexto += f"- {p.nombre}: ${p.precio:.2f} (stock: {p.stock})\n"
            
            elif datos_bd.get('tipo') == 'stock':
                contexto += f"{datos_bd.get('mensaje', '')}\n"
                productos = datos_bd.get('con_stock', [])
                for p in productos[:5]:
                    contexto += f"- {p.nombre}: {p.stock} unidades\n"
            
            elif datos_bd.get('tipo') == 'recomendaciones':
                recomendados = datos_bd.get('recomendados', [])
                contexto += "Productos recomendados:\n"
                for p in recomendados[:3]:
                    contexto += f"- {p.nombre}: ${p.precio:.2f} - {p.descripcion[:50]}...\n"
        
        return contexto


