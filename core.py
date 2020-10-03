import os
import json
import tweepy
import logging

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(filename="logOutline.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger("Logger") # Logger básico

API_KEY = os.getenv("API_KEY") # Informações de ambiente
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

with open("./info.json", "r") as f:
    infos = json.loads(f.read()) # Carrega usuários cadastrados

MAX_TWEETS = 50 # Máxima quantidade de tweets por execução (variável dependendo da frequência de execuções)
OUTLINE_URL = "https://outline.com/"

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)
if not api.verify_credentials():
    logger.warning("Error verifying credentials")
    exit(1)
logger.info("Credentials verified") # Inicializa API

updatedIds = [] # Atualiza ids para evitar repetição (bloqueada pela API, porém ocupa tempo de execução)
for user, lastId in zip(infos["users"], infos["last_ids"]): # Itera sequencialmente pela lista de usuários para diminuir o fluxo de requests
    tweets = api.user_timeline(
        id = user,
        count = MAX_TWEETS,
        include_rts = False,
        since_id = None if lastId == -1 else lastId,
        tweet_mode = 'extended'
    ) # Retorna tweets de cada conta
    updatedIds.append(tweets[0].id) # Atualiza para cada usuário o último tweet respondido
    for tweet in tweets: # Para cada tweet responde com o outline da notícia e loga possíveis erros
        try:
            outline = OUTLINE_URL + tweet._json["entities"]["urls"][0]["expanded_url"]
            api.update_status(status=f"Outline da notícia (sem paywall e distrações) [mensagem automática @{user}]: {outline}", in_reply_to_status_id=tweet.id)
        except Exception as e:
            logger.warning(f"REPLY ERROR! {str(e)}")

infos["last_ids"] = updatedIds
with open("./info.json", "w+") as f:
    json.dump(infos, f) # Atualiza arquivo json
    