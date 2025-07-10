from typing import Dict, Any, List, Optional
from openai import OpenAI
from datetime import datetime
from app.config import Config
from openai import APIConnectionError
import logging
from dotenv import load_dotenv
import re

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
        # Check if OpenAI API key is available
        if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'sk-your-openai-api-key-here':
            self.client = None
            self.model = None
            self.max_tokens = None
            self.temperature = None
        else:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.OPENAI_MODEL
            self.max_tokens = Config.OPENAI_MAX_TOKENS
            self.temperature = Config.OPENAI_TEMPERATURE
    
    def _clean_ai_response(self, response: str) -> str:
        """
        Limpia y normaliza la respuesta del AI para mejorar la presentación.
        
        Args:
            response (str): Respuesta cruda del AI
            
        Returns:
            str: Respuesta limpia y normalizada
        """
        if not response:
            return ""
        
        # Normalizar saltos de línea (convertir \n\n\n a \n\n)
        response = re.sub(r'\n{3,}', '\n\n', response)
        
        # Eliminar espacios en blanco al inicio y final
        response = response.strip()
        
        # Reemplazar caracteres especiales problemáticos
        response = response.replace('**', '')  # Eliminar markdown bold
        response = response.replace('*', '')   # Eliminar markdown italic
        response = response.replace('`', '')   # Eliminar markdown code
        response = response.replace('_', '')   # Eliminar markdown underline
        
        # Normalizar espacios múltiples
        response = re.sub(r' +', ' ', response)
        
        # Asegurar que no haya líneas vacías al inicio o final
        lines = response.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        response = '\n'.join(lines)
        
        return response
    
    def _build_system_prompt(self, financial_context: Dict[str, Any]) -> str:
        """
        Construye el prompt del sistema basado en el contexto financiero.
        
        Args:
            financial_context (Dict[str, Any]): Contexto financiero preparado
            
        Returns:
            str: Prompt del sistema para OpenAI
        """
        # LOG de depuración para verificar el contexto recibido
        logger.info(f"Construyendo prompt con contexto: {financial_context.keys()}")
        logger.info(f"Cuentas en contexto: {len(financial_context.get('accounts', []))}")
        logger.info(f"Transacciones en contexto: {len(financial_context.get('transactions', []))}")
        
        # Si no hay acceso a datos financieros
        if financial_context.get("note"):
            logger.info("Usando prompt sin datos financieros (note presente)")
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
        total_credit_balance = 0.0
        accounts_summary = []
        
        logger.info(f"Procesando {len(accounts)} cuentas")
        
        for account in accounts:
            if isinstance(account, dict):
                account_type = account.get('type', '').lower()
                balances = account.get('balances', {})
                
                logger.info(f"Procesando cuenta: {account.get('name')} - Tipo: {account_type} - Balances: {balances}")
                
                # Manejar diferentes tipos de cuentas
                if account_type == 'credit':
                    # Para cuentas de crédito, usar el balance actual (deuda)
                    balance = balances.get('current', 0)
                    if balance is not None:
                        total_credit_balance += float(balance)
                        balance_str = f"${float(balance):.2f} (deuda)"
                    else:
                        balance_str = "N/A"
                else:
                    # Para cuentas de depósito, usar available balance
                    balance = balances.get('available')
                    if balance is None:
                        balance = balances.get('current', 0)
                    if balance is not None:
                        total_balance += float(balance)
                        balance_str = f"${float(balance):.2f}"
                    else:
                        balance_str = "N/A"
                
                account_info = f"- {account.get('name', 'Cuenta')} ({account.get('mask', 'XXXX')}): {balance_str}"
                if account.get('type'):
                    account_info += f" (Tipo: {account.get('type')})"
                accounts_summary.append(account_info)
        
        logger.info(f"Balance total depósito: ${total_balance:.2f}, Balance crédito: ${total_credit_balance:.2f}")
        
        # Construir resumen de transacciones (ordenadas por fecha, más recientes primero)
        transactions_summary = []
        all_transactions = financial_context.get('transactions', [])
        
        logger.info(f"Procesando {len(all_transactions)} transacciones")
        
        # Ordenar transacciones por fecha (más recientes primero)
        sorted_transactions = sorted(
            all_transactions, 
            key=lambda x: x.get('date', ''), 
            reverse=True
        )  # Quitar el límite de 10
        
        for transaction in sorted_transactions:
            if isinstance(transaction, dict):
                amount = transaction.get('amount', 0)
                date = transaction.get('date', 'Fecha desconocida')
                merchant = transaction.get('merchant_name') or transaction.get('name', 'Transacción')
                # Limpiar caracteres especiales al final del nombre
                merchant = re.sub(r'[*/: ]+$', '', merchant)
                transactions_summary.append(f"- {merchant}: ${amount:.2f} el {date}")
        
        accounts_text = "\n".join(accounts_summary) if accounts_summary else "No hay cuentas disponibles"
        transactions_text = "\n".join(transactions_summary) if transactions_summary else "No hay transacciones recientes"
        
        # Construir resumen de balances
        balance_summary = f"Balance total en cuentas de depósito: ${total_balance:.2f}"
        if total_credit_balance > 0:
            balance_summary += f"\nDeuda total en tarjetas de crédito: ${total_credit_balance:.2f}"
            net_worth = total_balance - total_credit_balance
            balance_summary += f"\nPatrimonio neto: ${net_worth:.2f}"

        # INSTRUCCIÓN ESPECIAL SI SOLO HAY UNA CUENTA
        single_account_instruction = ""
        if len(accounts) == 1:
            single_account_instruction = "\n\nIMPORTANTE: Solo hay una cuenta en el contexto. Si el usuario pregunta por su balance, responde únicamente el balance de esa cuenta, no el balance total de todas las cuentas."

        logger.info("Prompt construido exitosamente")
        
        return f"""Eres un asistente financiero inteligente con acceso a los datos financieros actuales del usuario.

### Información Disponible:
**Fecha de consulta:** {financial_context.get('timestamp', datetime.utcnow().isoformat())}

**{balance_summary}**

**Cuentas Bancarias:**
{accounts_text}

**Transacciones Recientes (últimas 10):**
{transactions_text}

### Instrucciones:
- Proporciona respuestas precisas y útiles basadas en esta información
- Si el usuario pregunta por su balance total, responde con el monto calculado
- Distingue entre cuentas de depósito (dinero disponible) y tarjetas de crédito (deuda)
- Si no tienes suficiente información para responder algo específico, indícalo claramente
- Mantén un tono profesional pero amigable
- Ofrece insights y consejos financieros cuando sea apropiado
- NO uses formato markdown con asteriscos (**texto**)
- NO uses saltos de línea ni caracteres especiales
- Usa un formato completamente simple y directo
- Siempre incluye los montos en formato de moneda ($X.XX)
- Responde de forma clara y concisa
- Si muestras listas, usa comas o puntos para separar elementos{single_account_instruction}"""

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
            logger.info(f"Procesando mensaje: '{message[:50]}...'")
            logger.info(f"Contexto recibido con keys: {list(financial_context.keys())}")
            logger.info(f"Historial de chat: {len(chat_history) if chat_history else 0} mensajes")
            
            # Si no hay cliente de OpenAI configurado, usar respuesta de prueba
            if not self.client:
                logger.warning("Cliente OpenAI no configurado, usando respuesta de prueba")
                return {
                    "response": f"Hola! Recibí tu mensaje: '{message}'. Esta es una respuesta de prueba ya que no tengo configurada la API de OpenAI. Para usar la funcionalidad completa de IA, necesitas configurar tu OPENAI_API_KEY en el archivo .env",
                    "context": financial_context
                }
            
            # Construir prompt del sistema
            logger.info("Construyendo prompt del sistema...")
            system_prompt = self._build_system_prompt(financial_context)
            
            # Preparar mensajes para OpenAI
            messages = [{"role": "system", "content": system_prompt}]
            
            # Agregar historial de chat si existe
            if chat_history:
                messages.extend(chat_history)
            
            # Agregar mensaje actual del usuario
            messages.append({"role": "user", "content": message})
            
            logger.info(f"Enviando {len(messages)} mensajes a OpenAI...")
            
            # Llamada a OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extraer contenido de la respuesta
            response_content = response.choices[0].message.content
            
            logger.info(f"Respuesta recibida de OpenAI: {len(response_content)} caracteres")
            
            # Limpiar y normalizar la respuesta
            cleaned_response = self._clean_ai_response(response_content)
            
            logger.info("Respuesta procesada exitosamente")
            
            # Devolver respuesta con contexto usado
            return {
                "response": cleaned_response,
                "context": financial_context
            }
            
        except Exception as e:
            logger.error(f"Error en AIService: {str(e)}")
            raise APIConnectionError(f"Error en el servicio de IA: {str(e)}")
