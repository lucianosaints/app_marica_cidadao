import google.generativeai as genai
from django.conf import settings
from decouple import config
import PIL.Image
import json

# Configuração da API Key
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')

def analisar_imagem_problema(image_path):
    """
    Usa o modelo Gemini 1.5 Flash para analisar a imagem e sugerir uma categoria.
    """
    if not GEMINI_API_KEY:
        return {"error": "API Key do Gemini não configurada no .env"}

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        img = PIL.Image.open(image_path)
        
        prompt = """
        Você é um especialista em zeladoria urbana da Prefeitura de Maricá.
        Analise a imagem e identifique qual categoria de problema de infraestrutura ela representa.
        As categorias possíveis são:
        1: Buraco na via
        2: Lâmpada Queimada
        3: Foco de Dengue
        4: Lixo Acumulado
        5: Vazamento de Água
        6: Calçada Danificada

        Responda APENAS em formato JSON com os seguintes campos:
        - "categoria_id": (ID numérico da categoria encontrada, ou null se não identificar)
        - "confianca": (0 a 100)
        - "justificativa": (Breve explicação técnica do que viu na foto)
        """

        response = model.generate_content([prompt, img])
        
        # Limpa a resposta para garantir que seja um JSON válido
        text_response = response.text.strip()
        if "```json" in text_response:
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        
        return json.loads(text_response)

    except Exception as e:
        print(f"Erro ao chamar Gemini: {e}")
        return {"error": str(e)}
