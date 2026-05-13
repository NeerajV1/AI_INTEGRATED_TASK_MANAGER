from fastapi import HTTPException,Request,APIRouter
from pydantic import BaseModel,EmailStr
from fastapi.templating import Jinja2Templates
from databaseConnection import connect
from security import hash_password
router=APIRouter()
templates=Jinja2Templates(directory="templates")
class User(BaseModel):
    username:str
    email:EmailStr
    password:str
    phoneno:str
@router.post("/signup")
async def signup(request:Request,client:User):
    name=client.username
    email=client.email
    phoneno=client.phoneno
    password=hash_password(client.password)
    conn=connect()
    cur=conn.cursor()
    query = "INSERT INTO users (name, email, password, phoneno) VALUES (%s, %s, %s, %s) RETURNING name"
    try:
        cur.execute(query, (name, email, password, phoneno))
        conn.commit() # CRITICAL: Changes won't save without this!
        result = cur.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

    return templates.TemplateResponse(request=request, name="startup.html")
@router.get("/signup2")
def signup_page(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="signup.html",
    context={"request": request}
)