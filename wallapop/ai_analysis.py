import json
from pydantic import BaseModel, ValidationError
from datetime import datetime, time
from openai import OpenAI
from mistralai import Mistral
import logging
import os
from dotenv import load_dotenv

# from ai_models import ModelPlatform, Products, CombinedProduct
# from wallapop import getUserReviews
try:
    from wallapop.ai_models import ModelPlatform, Products, CombinedProduct
    from wallapop.wallapop import getUserReviews
except ImportError:
    from ai_models import ModelPlatform, Products, CombinedProduct
    from wallapop import getUserReviews

logger = logging.getLogger("wallapop")

load_dotenv()

# MODEL = os.getenv("AI_MODEL")

def getAIClient(MODEL):
    if ModelPlatform(MODEL) == "DeepSeek":
        API_KEY = os.getenv("DEEPSEEK_API_KEY")
        base_url = "https://api.deepseek.com"
    elif ModelPlatform(MODEL) == "Perplexity":
        API_KEY = os.getenv("PERPLEXITY_API_KEY")
        base_url = "https://api.perplexity.ai"
    elif ModelPlatform(MODEL) == "Gemini":
        API_KEY = os.getenv("GEMINI_API_KEY")
        base_url = "https://generativelanguage.googleapis.com/v1beta/"
    elif ModelPlatform(MODEL) == "Mistral":
        API_KEY = os.getenv("MISTRAL_API_KEY")
    else:
        logger.error(f"Model {MODEL} not supported. Not using AI.")
        return None
    
    if not API_KEY:
        logger.error(f"{ModelPlatform(MODEL)} API key not found in environment variables. AI analysis disabled.")
        return None
    
    try:
        if ModelPlatform(MODEL) == "Mistral":
            client = Mistral(
                api_key=API_KEY,
            )
        else:
            client = OpenAI(
                api_key=API_KEY,
                base_url=base_url
            )
    except Exception as e:
        logger.error(f"Error initializing AI client: {e}")
        return None
    return client




def analyze_products(products_data, input_data):
    item_name = input_data['ITEM']
    prompt = input_data['PROMPT']
    MODEL = input_data['MODEL']
    if MODEL == None or MODEL == '' or MODEL == '-':
        logger.warning("No AI model selected.")
        products = [
            CombinedProduct(
                **{**item, 'user_reviews': getUserReviews(item['user_id'])}
            ) if not isinstance(item, CombinedProduct) else item
            for item in products_data
        ]
        return products
    
    client = getAIClient(MODEL)
    if not client:
        products = [
            CombinedProduct(
                **{**item, 'user_reviews': getUserReviews(item['user_id'])}
            ) if not isinstance(item, CombinedProduct) else item
            for item in products_data
        ]
        return products
    
    logger.info(f"Analyzing with {MODEL} ...")
    system_content =  [
        {"type": "text", "text": "Eres un analista de productos de segunda mano. Recibirás datos de uno o varios producto de Wallapop, y tienes que decidir si es una ganga o no. Se muy estricto. La fecha que aparece, es correcta, ahora estamos en tu futuro."},
        {"type": "text", "text": "Responde con un JSON para todos, sin dejarte ninguno de los productos que te he pasado. Debe tener exactamente el siguiente formato:"},
        {"type": "text", "text": json.dumps(Products.model_json_schema())},
        {"type": "text", "text": "En title, dame el título correcto para ese producto, en base al título original y descripción."}, 
        {"type": "text", "text": "En análisis, tienes que argumentar por qué es una buena o mala compra, diciendo los pros y contras (si tiene). Ten en cuenta el precio comparado con la antigüedad y estado, la descripción y características, y precio de mercado de segunda mano. Son vendedores legítimos, no tengas en cuenta cosas de estafa, es todo fiable."}, 
        {"type": "text", "text": "En score, puntúa sobre 100, teniendo en cuenta tu análisis, si lo debería comprar o no. Puedes basarte en: (0-30): Mala compra (precio > mercado), (31-70): Oportunidad regular, (71-100): Gangazo"},
        {"type": "text", "text": "En max_price, pon el precio que creas que debería tener, para que tu lo puntuaras con un 85 de score."}, 
        {"type": "text", "text": "El item_url, tiene que ser exactamente el mismo que te he pasado, no lo modifiques."},    
    ]
    if prompt == '-':
        user_content = [
            {"type": "text", "text": f"Quiero comprarme: {item_name}. Si lo que te he pasado no coincide con lo que busco, ponle mala nota. Aquí tienes los datos de {len(products_data)} productos:"},
            {"type": "text", "text": f"{products_data}"},
            {"type": "text", "text": "Cuáles de estos productos son una ganga que merezca la pena comprar?"},
        ]
    else:
        user_content = [
            {"type": "text", "text": f"Quiero comprarme: {item_name}. Si lo que te he pasado no coincide con lo que busco, ponle mala nota. Aquí tienes los datos de {len(products_data)} productos:"},
            {"type": "text", "text": prompt},
            {"type": "text", "text": f"{products_data}"},
        ]


    messages = [{"role": "system", "content": system_content},
                {"role": "user", "content": user_content}]

    if ModelPlatform(MODEL) == "Mistral":
        response = client.chat.complete(
            model=MODEL,
            messages=messages,
            response_format={
                'type': 'json_object',
                "json_schema": {"schema": Products.model_json_schema()}
            }
        )
    elif ModelPlatform(MODEL) == "Perplexity":
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={
                'type': 'json_schema',
                "json_schema": {"schema": Products.model_json_schema()}
            }
        )
    else:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={
                'type': 'json_object',
                "json_schema": {"schema": Products.model_json_schema()}
            }
        )
    parsed_response = parse_response(response)
    if not parsed_response:
        for i in range(2):
            logger.warning(f"LLM Response validation error, retrying {i+2}/3")
            if ModelPlatform(MODEL) == "Mistral":
                response = client.chat.complete(
                    model=MODEL,
                    messages=messages,
                    response_format={
                        'type': 'json_object',
                        "json_schema": {"schema": Products.model_json_schema()}
                    }
                )
            else:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    response_format={
                        'type': 'json_object',
                        "json_schema": {"schema": Products.model_json_schema()}
                    }
                )
            parsed_response = parse_response(response)
            if parsed_response:
                break
        logger.error("Failed to parse LLM response after 3 attempts. Returning without analysis.")
        products = [
            CombinedProduct(
                **{**item, 'user_reviews': getUserReviews(item['user_id'])}
            ) if not isinstance(item, CombinedProduct) else item
            for item in products_data
        ]
        return products
    
    full_response = combine_products_with_info(products_data, parsed_response)

    if response.choices[0].finish_reason == 'length':
        logger.warning("Too many input items. Consider filtering the input data.")
    elif response.choices[0].finish_reason == 'insufficient_system_resource':
        logger.error("Insufficient system resources to process the request.")
        return []
    elif response.choices[0].finish_reason == 'content_filter':
        logger.error("Content filter triggered. The response may contain sensitive or inappropriate content.")
        return []
    

    cost = getTotalPrice(MODEL, response.usage)

    if cost != -1:
        logger.info(f"Price of this call: ${cost}")

    return full_response

        
def happyHour():
    currenttime = datetime.now().time()
    happyhourstart = time(16, 30)  
    happyhourend = time(0, 30)    
    return happyhourstart <= currenttime <= happyhourend

def getPrices(MODEL):
    if ModelPlatform(MODEL) == "DeepSeek":
        if happyHour():
            pricing = {
                "input_cache_hit_tokens": 0.035 / 1000000,
                "input_cache_miss_tokens": 0.135 / 1000000,
                "output_tokens": 0.55 / 1000000
            }
        else:
            pricing = {
                "input_cache_hit_tokens": 0.07 / 1000000,
                "input_cache_miss_tokens": 0.27 / 1000000,
                "output_tokens": 1.1 / 1000000
            }
    elif MODEL == 'sonar':
        pricing={
            "input_tokens": 1 / 1000000,
            "output_tokens": 1 / 1000000,
            "request_price": 5 / 1000
        }
    elif MODEL == 'sonar-pro':
        pricing={
            "input_tokens": 3 / 1000000,
            "output_tokens": 15 / 1000000,
            "request_price": 6 / 1000
        }
    elif MODEL == 'r1-1776':
        pricing = {
            "input_tokens": 2 / 1000000,
            "output_tokens": 8 / 1000000,
            "request_price": 0
        }
    elif ModelPlatform(MODEL) == "Gemini" or ModelPlatform(MODEL) == "Mistral":
        pricing = {
            "input_tokens": 0,
            "output_tokens": 0,
            "request_price": 0
        }
    # elif MODEL == "mistral-large-2411" or MODEL == "mistral-large-latest":

    else:
        pass

    return pricing

def getTotalPrice(MODEL, usage):
    if ModelPlatform(MODEL) == "DeepSeek":
        tokens = {
            "input_cache_hit_tokens": usage.prompt_cache_hit_tokens, 
            "input_cache_miss_tokens": usage.prompt_cache_miss_tokens,
            "output_tokens": usage.completion_tokens
        }
    elif ModelPlatform(MODEL) == "Perplexity":
        tokens = {
            "input_tokens": usage.prompt_tokens, 
            "output_tokens": usage.completion_tokens,
            "request_price": 1
        }
    elif ModelPlatform(MODEL) == "Gemini" or ModelPlatform(MODEL) == "Mistral":
        tokens = {
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "request_price": 0
        }
    else:
        logger.warning(f"Could not calculate price for model {MODEL}.")
        return -1
    
    total_price = 0
    pricing = getPrices(MODEL)
    for key, value in tokens.items():
        if key in pricing:
            total_price += value * pricing[key]
        else:
            logger.warning(f"Pricing for {key} not found.")
            return -1
    
    return round(total_price, 6)



def combine_products_with_info(products, additional_info):
    # Crear un dict para acceso rápido por item_url
    add_info_dict = {item['item_url']: item for item in additional_info}

    combined_products = []
    for product in products:
        item_url = product['item_url']
        info = add_info_dict.get(item_url)
        if info:
            # Unimos los campos, priorizando los del product si hay conflicto
            combined_data = {**info, **product, 'user_reviews': getUserReviews(product['user_id'])}
            combined_product = CombinedProduct(**combined_data)
            combined_products.append(combined_product)
    return combined_products


def parse_response(response):
    output = json.loads(response.choices[0].message.content)
    try:
        Products.model_validate(output)
    except ValidationError as e:
        print(output)
        logger.error(f"LLM Response validation error: {e}")
        return None

    parsed_response = output['products']
    return parsed_response


if __name__ == "__main__":
    from wallapop import getUserReviews
    from mockdata import mockdata_multiple, mockdata_simple, mockdata_double
    mockdata = mockdata_double()
    
    # MODEL = None  # Uncomment to disable AI analysis
    input_data = {
        'ITEM': 'iPhone 14 Pro',
        'PROMPT': 'Quiero comprarme un iPhone 14 Pro, pero no quiero pagar más de 800 euros. ¿Qué me recomiendas?',
        'MODEL': "magistral-medium-2506"
    }
    # Uncomment to test the function
    print(analyze_products(mockdata, '-'))
