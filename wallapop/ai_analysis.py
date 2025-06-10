import json
from pydantic import BaseModel, ValidationError
from datetime import datetime, time
from openai import OpenAI
import logging
import os
from dotenv import load_dotenv
from wallapop.wallapop import getUserReviews

# from wallapop import getUserReviews
# from mockdata import mockdata_multiple, mockdata_simple, mockdata_double
# mockdata = mockdata_double()


logger = logging.getLogger("wallapop")

load_dotenv()
API_KEY = os.getenv("AI_MODEL_API_KEY")
MODEL = 'deepseek-chat'

if MODEL == "deepseek-chat":
    base_url = "https://api.deepseek.com"
elif MODEL == "sonar" or MODEL == "r1-1776" or MODEL == "sonar-pro":
    base_url = "https://api.perplexity.ai"
else:
    logger.error(f"Model {MODEL} not supported. Using deepseek-chat model.")
    MODEL = 'deepseek-chat'
    base_url = "https://api.deepseek.com"


client = OpenAI(
    api_key=API_KEY,
    base_url=base_url
)

class Product(BaseModel):
    title: str
    max_price: int
    analysis: str
    score: int
    item_url: str

class CombinedProduct(BaseModel):
    title: str
    price: int
    max_price: int
    analysis: str
    description: str
    location: str
    date: datetime
    user_id: str
    user_rating: str 
    score: int
    item_url: int

class Products(BaseModel):
    products: list[Product]

def analyze_products(products_data):
    system_content =  [
        {"type": "text", "text": "Eres un analista de productos de segunda mano. Recibirás datos de uno o varios producto de Wallapop, y tienes que decidir si es una ganga o no. Se muy estricto. La fecha que aparece, es correcta, ahora estamos en tu futuro."},
        {"type": "text", "text": "Responde con un JSON para todos, sin dejarte ninguno de los productos que te he pasado. Debe tener exactamente el siguiente formato:"},
        {"type": "text", "text": json.dumps(Products.model_json_schema())},
        {"type": "text", "text": "En análisis, tienes que argumentar por qué es una buena o mala compra, diciendo los pros y contras (si tiene). Ten en cuenta el precio comparado con la antigüedad y estado, la descripción y características, y precio de mercado de segunda mano. Son vendedores legítimos, no tengas en cuenta cosas de estafa, es todo fiable."}, 
        {"type": "text", "text": "En score, puntúa sobre 100, teniendo en cuenta tu análisis, si lo debería comprar o no. Puedes basarte en: (0-30): Mala compra (precio > mercado), (31-70): Oportunidad regular, (71-100): Gangazo"},
        {"type": "text", "text": "En max_price, pon el precio que le des al menos un 85 de score."}, 
        {"type": "text", "text": "El item_url, tiene que ser exactamente el mismo que te he pasado, no lo modifiques."}, 
    ]

    user_content = [
                    {"type": "text", "text": "Analiza el siguiente producto de Wallapop:"},
                    {"type": "text", "text": f"{products_data}"},
                    {"type": "text", "text": "¿Es una buena compra?"},
                ]

    messages = [{"role": "system", "content": system_content},
                {"role": "user", "content": user_content}]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={
            'type': 'json_object',
            "json_schema": {"schema": Products.model_json_schema()}
        }
    )
    parsed_response = parse_response(response)
    full_response = combine_products_with_info(products_data, parsed_response)

    if response.choices[0].finish_reason == 'length':
        logger.warning("Too many input items. Consider filtering the input data.")
    elif response.choices[0].finish_reason == 'insufficient_system_resource':
        logger.error("Insufficient system resources to process the request.")
        return []
    elif response.choices[0].finish_reason == 'content_filter':
        logger.error("Content filter triggered. The response may contain sensitive or inappropriate content.")
        return []
    

    cost = getTotalPrice(response.usage)

    if cost != -1:
        logger.info(f"Cost: ${cost}")

    return parsed_response

        
def happyHour():
    currenttime = datetime.now().time()
    happyhourstart = time(16, 30)  
    happyhourend = time(0, 30)    
    return happyhourstart <= currenttime <= happyhourend

def getPrices():
    if MODEL == 'deepseek-chat':
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
    elif MODEL == 'r1-1776':
        pricing = {
            "input_tokens": 2 / 1000000,
            "output_tokens": 8 / 1000000,
            "request_price": 0
        }
    else:
        pass

    return pricing

def getTotalPrice(usage):
    if MODEL == 'deepseek-chat':
        tokens = {
            "input_cache_hit_tokens": usage.prompt_cache_hit_tokens, 
            "input_cache_miss_tokens": usage.prompt_cache_miss_tokens,
            "output_tokens": usage.completion_tokens
        }
    elif MODEL == 'sonar' or MODEL == 'r1-1776':
        tokens = {
            "input_tokens": usage.prompt_tokens, 
            "output_tokens": usage.completion_tokens,
            "request_price": 1
        }
    else:
        logger.warning(f"Could not calculate price for model {MODEL}.")
        return -1
    
    total_price = 0
    pricing = getPrices()
    for key, value in tokens.items():
        if key in pricing:
            total_price += value * pricing[key]
        else:
            logger.warning(f"Pricing for {key} not found.")
            return -1
    return total_price



def combine_products_with_info(products, additional_info):
    # Crear un dict para acceso rápido por item_url
    add_info_dict = {item['item_url']: item for item in additional_info}

    combined_products = []
    for product in products:
        item_url = product['item_url']
        info = add_info_dict.get(item_url)
        if info:
            # Unimos los campos, priorizando los del product si hay conflicto
            combined_data = {**info, **product, 'user_rating': getUserReviews(product['user_id'])}
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
    
    ## Aqué està posant un missatge que no està ben estructurat, de vegades falla i altres no.
    for product in output['products']:
        print(f"Product: {product['title']}")
        print(f"Max Price: {product['max_price']}")
        print(f"Description: {product.get('description', 'No description provided')}")
        print(f"Location: {product.get('location', 'No location provided')}")
        print(f"Date: {product.get('date', 'No date provided')}")
        print(f"User ID: {product.get('user_id', 'No user ID provided')}")
        print(f"User Rating: {product.get('user_rating', 'No user rating provided')}")
        print(f"Análisis: {product['analysis']}")
        print(f"Score: {product['score']}\n")
        print(f"Item URL: {product['item_url']}")
    # output = json.loads(response.choices[0].message.content)
    parsed_response = output['products']
    return parsed_response

# print(analyze_products(mockdata))