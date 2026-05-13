from jose import jwt
from datetime import datetime,timedelta,timezone
secret_key="super_secret_key"
algo="HS256"
def create_data_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(hours=24)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,secret_key,algorithm=algo)
def decode_data(token:str):
    try:
        return jwt.decode(token,secret_key,algorithms=[algo])
    except:
        return None
def getUserid(token:str):
    tokenised=decode_data(token).get("userid")
    return tokenised
