from fastapi import HTTPException,Request,APIRouter
from pydantic import BaseModel,EmailStr
from fastapi.templating import Jinja2Templates
from databaseConnection import connect
from security import verifyPassword
from auth_utils import create_data_token,decode_data
from fastapi.responses import RedirectResponse
router=APIRouter()
templates=Jinja2Templates(directory="templates")

class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    phoneno: str


@router.post("/login")
def loginPage(request:Request ,client:User):
    name=client.username
    password=client.password
    email=client.email
    conn=connect()
    cur=conn.cursor()
    query="select name,password,userid from users where  email=%s"
    cur.execute(query,(email,))
    result=cur.fetchone()
    cur.close()
    conn.close()
    if result is None:
                return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={"username":name}
        )
    if(result[0]==name and verifyPassword(password,result[1])):
        #return html,css,javascript file
        token=create_data_token({"userid":result[2]})
        response= templates.TemplateResponse(
            
                request=request,
                name="hello.html",
                context={"username": name}
                
            
        )
        response.set_cookie(key="access_token",value=token,httponly=True,max_age=86400,samesite="lax")
        return response
    else:
          raise HTTPException(401,detail=f"Unauthorized access name:{result[0]},password:{verifyPassword(password,result[1])}")
    
@router.post("/logout")
def logOut(request:Request):
      response=RedirectResponse(url="/login")
      response.delete_cookie("access_token", samesite="lax")
      return response