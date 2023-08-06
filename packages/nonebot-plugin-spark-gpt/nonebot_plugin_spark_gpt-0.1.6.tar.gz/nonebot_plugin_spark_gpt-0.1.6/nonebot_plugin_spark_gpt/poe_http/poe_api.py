import asyncio
from .config import poe_persistor
from nonebot import logger
from concurrent.futures import ThreadPoolExecutor
import poe

if poe_persistor.poe_cookie:
    retry_count = 0
    while retry_count < 3:
        try:
            client = poe.Client(poe_persistor.poe_cookie)
            break
        except:
            retry_count += 1
            logger.warning("加载poe失败,正在尝试重试...")
    if retry_count >= 3:
        raise Exception("加载poe失败,请重试")
    
def poe_chat(truename, message):
    try:
        result = client.send_message(truename,message)
        for chunk in result:
            pass
        return chunk["text"]
    except Exception as e:
        logger.error(f"出错了:{e}")
        return f"Poe出错了:{e}"

def poe_create(truename, prompt, model_index):
    if model_index == 1:
        base_model = "chinchilla"
    else:
        base_model = "a2"
    try:
        client.create_bot(truename,prompt,base_model=base_model)
        return True
    except Exception as e:
        logger.error(f"出错了:{e}")
        return False

def poe_clear(truename):
    try:
        client.send_chat_break(truename)
        return True
    except Exception as e:
        logger.error(f"出错了:{e}")
        return False