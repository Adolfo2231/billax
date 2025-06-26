from typing import Dict, Any, List, Optional
from openai import OpenAI
from datetime import datetime
from app.config import Config
from openai import APIConnectionError
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIService:
    """
    Servicio de IA enfocado únicamente en procesamiento de inteligencia artificial.
    
    Responsabilidades:
    - Interactuar con OpenAI API
    - Construir prompts basados en datos proporcionados
    - Procesar respuestas de IA
    
    NO es responsable de:
    - Obtener datos financieros (eso lo hace ChatFacade)
    - Manejar persistencia (eso lo hace ChatRepository)
    - Orquestar servicios (eso lo hace ChatFacade)
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.OPENAI_MAX_TOKENS
        self.temperature = Config.OPENAI_TEMPERATURE
    
    def _build_system_prompt(self, financial_context: Dict[str, Any]) -> str:
        """
        Construye el prompt del sistema basado en el contexto financiero.
        
        Args:
            financial_context (Dict[str, Any]): Contexto financiero preparado
            
        Returns:
            str: Prompt del sistema para OpenAI
        """
        # Si no hay acceso a datos financieros
        if financial_context.get("note"):
            return """Eres un asistente financiero inteligente y amigable. En este momento no tengo acceso a tus datos financieros específicos, pero puedo ayudarte con:

- Consejos generales sobre finanzas personales
- Explicaciones sobre productos financieros
- Estrategias de ahorro e inversión
- Planificación financiera básica
- Respuestas a preguntas sobre banca y finanzas

Si necesitas información específica sobre tus cuentas o transacciones, necesitarás vincular tus cuentas bancarias primero."""
        
        # Calcular balance total y preparar resumen de cuentas
        accounts = financial_context.get('accounts', [])
        total_balance = 0.0
        accounts_summary = []
        for account in accounts:
            if isinstance(account, dict):
                # Usar current_balance si existe, sino available_balance
                balance = account.get('current_balance')
                if balance is None:
                    balance = account.get('available_balance')
                if balance is not None:
                    total_balance += float(balance)
                account_info = f"- {account.get('name', 'Cuenta')} ({account.get('mask', 'XXXX')}): ${balance:.2f}"
                if account.get('type'):
                    account_info += f" (Tipo: {account.get('type')})"
                accounts_summary.append(account_info)
        
        # Construir resumen de transacciones (máximo 10)
        transactions_summary = []
        recent_transactions = financial_context.get('transactions', [])[:10]
        for transaction in recent_transactions:
            if isinstance(transaction, dict):
                amount = transaction.get('amount', 0)
                date = transaction.get('date', 'Fecha desconocida')
                merchant = transaction.get('merchant_name') or transaction.get('name', 'Transacción')
                transactions_summary.append(f"- {merchant}: ${amount:.2f} el {date}")
        
        accounts_text = "\n".join(accounts_summary) if accounts_summary else "No hay cuentas disponibles"
        transactions_text = "\n".join(transactions_summary) if transactions_summary else "No hay transacciones recientes"
        
        return f"""Eres un asistente financiero inteligente con acceso a los datos financieros actuales del usuario.

### Información Disponible:
**Fecha de consulta:** {financial_context.get('timestamp', datetime.utcnow().isoformat())}

**Balance total en todas las cuentas:** ${total_balance:.2f}

**Cuentas Bancarias:**
{accounts_text}

**Transacciones Recientes:**
{transactions_text}

### Instrucciones:
- Proporciona respuestas precisas y útiles basadas en esta información
- Si el usuario pregunta por su balance total, responde con el monto calculado
- Si no tienes suficiente información para responder algo específico, indícalo claramente
- Mantén un tono profesional pero amigable
- Ofrece insights y consejos financieros cuando sea apropiado
- NO uses formato markdown con asteriscos (**texto**)
- NO uses saltos de línea ni caracteres especiales
- Usa un formato completamente simple y directo
- Siempre incluye los montos en formato de moneda ($X.XX)
- Responde de forma clara y concisa
- Si muestras listas, usa comas o puntos para separar elementos"""

    def get_chat_response(
        self,
        message: str,
        financial_context: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene una respuesta de IA basada en el mensaje y contexto proporcionados.
        
        Args:
            message (str): Mensaje del usuario
            financial_context (Dict[str, Any]): Contexto financiero preparado
            chat_history (List[Dict[str, str]]): Historial de chat formateado
            
        Returns:
            Dict[str, Any]: Respuesta de IA y contexto usado
            
        Raises:
            APIConnectionError: Si hay error en la conexión con OpenAI
        """
        try:
            # Construir prompt del sistema
            system_prompt = self._build_system_prompt(financial_context)
            
            # Preparar mensajes para OpenAI
            messages = [{"role": "system", "content": system_prompt}]
            
            # Agregar historial de chat si existe
            if chat_history:
                messages.extend(chat_history)
            
            # Agregar mensaje actual del usuario
            messages.append({"role": "user", "content": message})
            
            # Llamada a OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extraer contenido de la respuesta
            response_content = response.choices[0].message.content
            
            # Devolver respuesta con contexto usado
            return {
                "response": response_content,
                "context": financial_context
            }
            
        except Exception as e:
            logger.error(f"Error en AIService: {str(e)}")
            raise APIConnectionError("Error en el servicio de IA", str(e))
