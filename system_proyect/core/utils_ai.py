# core/utils_ai.py

import openai
from django.conf import settings

def consultar_ia(mensajes, modelo=None, max_tokens=None, temperatura=0.7, timeout=None):
    """
    Llama a la API de OpenAI para obtener una respuesta de IA en formato chat.
    - mensajes: lista de diccionarios [{"role": "user"/"assistant"/"system", "content": "..."}]
    - modelo: modelo a usar (por defecto, el configurado en settings)
    - max_tokens: límite máximo de tokens (por defecto, el configurado en settings)
    - temperatura: creatividad (por defecto 0.7)
    - timeout: tiempo máximo de espera (por defecto, el configurado en settings)
    Retorna: string (respuesta de la IA) o None si hay error.
    """
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise Exception("No se ha configurado la API KEY de OpenAI.")

    # Valores por defecto desde settings si no se pasan
    modelo = modelo or getattr(settings, "OPENAI_MODEL_DEFAULT", "gpt-4-1-mini")
    max_tokens = max_tokens or getattr(settings, "OPENAI_MAX_TOKENS", 500)
    timeout = timeout or getattr(settings, "OPENAI_TIMEOUT", 20)

    openai.api_key = api_key

    try:
        respuesta = openai.chat.completions.create(
            model=modelo,
            messages=mensajes,
            max_tokens=max_tokens,
            temperature=temperatura,
            timeout=timeout
        )
        # Extraer el texto generado (OpenAI v1 API)
        contenido = respuesta.choices[0].message.content.strip()
        return contenido
    except Exception as e:
        print(f"[Error IA] {e}")
        return None

