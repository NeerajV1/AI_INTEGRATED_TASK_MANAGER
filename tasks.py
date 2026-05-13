#crud operations tasks
from fastapi import APIRouter,Request,HTTPException
from auth_utils import decode_data,getUserid
from databaseConnection import connect
from pydantic import BaseModel
from datetime import date,datetime
from enum import Enum
from pydantic import BaseModel,field_validator
from ai_agent import get_clean_json_task
from typing import Literal
class TaskTitle(BaseModel):
    title: str
class Priority(str, Enum):
    High = "high"
    medium = "medium"
    low = "low"
class Status(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
class task(BaseModel):
    title:str
    description:str
    deadline:date
    priority:Priority
    status:Status
    @field_validator('priority', 'status', mode='before')
    @classmethod
    def lowercase_strings(cls, v: str) -> str:
        return v.lower() if isinstance(v, str) else v
class textData(BaseModel):
    text: str
router=APIRouter()
@router.post("/gettaskid")
def getTaskId(request:Request,client:TaskTitle):
    tokenised = request.cookies.get("access_token")
    if tokenised is None:
        raise HTTPException(404,detail="login first!")
    token=decode_data(request.cookies.get("access_token"))
    userid=token.get("userid")
    conn=connect()
    cur=conn.cursor()
    query="select taskid from tasks where userid=%s and title=%s ;"
    result=-1
    try:
        cur.execute(query,(userid,client.title))
        conn.commit()
        result=cur.fetchone()
    except Exception as e:
        conn.rollback()
        print(f"error:{e}")
        raise HTTPException(400,detail="please send right data!")
    finally:
        cur.close()
        conn.close()
    if result is None:
        # Instead of crashing, return a clear message or 404
        print(f"Task titled '{client.title}' not found for user {userid}")
        return {"taskid": None}
    return {"taskid":result[0]}
@router.get("/alltasks")
def tasks(request:Request):
    tokenised = request.cookies.get("access_token")
    if tokenised is None:
        raise HTTPException(404,detail="login first!")
    token=decode_data(request.cookies.get("access_token"))
    userid=token.get("userid")
    conn=connect()
    cur=conn.cursor()
    query="select * from tasks where userid=%s"
    cur.execute(query,(userid,))
    results=cur.fetchall()
    data=[]
    for i in results:
        data.append({
            "taskid":i[0],
            "title":i[2],
            "description":i[3],
            "deadline":str(i[4]),
            "status":i[5],
            "priority":str(i[6]),
            "created_at":str(i[7]),
            "updated_at":str(i[8])
        })
    return data
@router.post("/sendtask")
def createTask(request:Request,client:task):
    tokenised=request.cookies.get("access_token")
    if tokenised is None:
        raise HTTPException(404,detail="login first")
    token=decode_data(tokenised)
    userid=token.get("userid")
    conn=connect()
    cur=conn.cursor()
    query="insert into tasks(title,task_description,deadline,priority,userid,status) values(%s,%s,%s,%s,%s,%s);"
    try:
        cur.execute(query,(client.title,client.description,client.deadline,client.priority,userid,client.status))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"error:{e}")
        raise HTTPException(400,detail="please send right data!")
    finally:
        
        cur.close()
        conn.close()
    return {"message":"task created successfully"}

@router.put("/update_task/{task_id}")
def update(task_id: int, request: Request, client: task):
    tokenised = request.cookies.get("access_token")
    if not tokenised:
        raise HTTPException(401, detail="login first")
    
    userid = decode_data(tokenised).get("userid")
    conn = connect()
    cur = conn.cursor()
    
    try:
        # 1. Update the main tasks table first
        # Note: Using task_description to match your DB screenshot
        query = """
            UPDATE tasks 
            SET title=%s, task_description=%s, deadline=%s, priority=%s, status=%s 
            WHERE taskid=%s AND userid=%s 
            RETURNING status, taskid;
        """
        cur.execute(query, (client.title, client.description, client.deadline, 
                            client.priority, client.status, task_id, userid))
        res = cur.fetchone()
        conn.commit()

        if res:
            new_status = res[0]
            tid = res[1]

            # 2. Handle moving to COMPLETED_TASKS
            if new_status == "completed":
                # Pull all data from 'tasks' and push to 'completed_tasks' in one shot
                archive_query = """
                    INSERT INTO completed_tasks (taskid, userid, title, task_description, deadline, status, completed_at)
                    SELECT taskid, userid, title, task_description, deadline, status, NOW()
                    FROM tasks WHERE taskid=%s;
                """
                cur.execute(archive_query, (tid,))
                cur.execute("DELETE FROM tasks WHERE taskid=%s", (tid,))
                conn.commit()
                return {"message": "Task completed and archived"}

            # 3. Handle moving to FAILED_TASKS
            elif new_status == "failed":
                fail_query = """
                    INSERT INTO failed_tasks (taskid, userid, title, task_description, deadline, status, failed_at)
                    SELECT taskid, userid, title, task_description, deadline, status, NOW()
                    FROM tasks WHERE taskid=%s;
                """
                cur.execute(fail_query, (tid,))
                cur.execute("DELETE FROM tasks WHERE taskid=%s", (tid,))
                conn.commit()
                return {"message": "Task moved to failed tasks"}

        return {"message": "Task updated successfully"}

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise HTTPException(400, detail="Update failed")
    finally:
        cur.close()
        conn.close()
@router.delete("/delete/{taskid}")
def deletetask(taskid:int,request:Request):
    tokenised = request.cookies.get("access_token")
    if not tokenised:
        raise HTTPException(401, detail="login first")
    
    userid = decode_data(tokenised).get("userid")
    conn=connect()
    cur=conn.cursor()
    query="delete from tasks where userid=%s and taskid=%s"
    try:
        cur.execute(query,(userid,taskid))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"error:{e}")
        raise HTTPException(400,detail="please send right data!")
    finally:
        
        cur.close()
        conn.close()
    return {"message":"task deleted successfully"}
#task completed:1 task failed :-1 failed to fetch:-10 due but not failed:0
@router.post("/check/{taskid}")
def check(request:Request,client:task,taskid:int):
    token=request.cookies.get("access_token")
    if not token:
        raise HTTPException(400,detail="login first!")
    userid=getUserid(token) #made a new function 
    conn=connect()
    cur=conn.cursor()
    query="select deadline,created_at from tasks where userid=%s and taskid=%s;"
    result=-1
    try:
        cur.execute(query,(userid,taskid))
        conn.commit()
        result=cur.fetchone()
    except Exception as e:
        conn.rollback()
        print(f"error:{e}")
    finally:
        cur.close()
        conn.close()
    if result is None:
        return {"result":-10}
    due_date = result[0]#%d is getting highlighted in vs code
    if isinstance(due_date, str): 
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    if (due_date<datetime.now().date()):
        conn=connect()
        cur=conn.cursor()
        query1="insert into failed_tasks values (%s,%s,%s,%s,%s,%s,%s,%s)" #how will someone put if there were 100 attributes?
        query2="delete from tasks where userid=%s and taskid=%s"
        try:
            cur.execute(query1,(taskid,userid,client.title,client.description,client.deadline,client.status,result[1],datetime.now().date()))
            cur.execute(query2,(userid,taskid))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"error:{e}")
        finally :
            cur.close() #can conn be directly closed without writing cur.close()?
            conn.close()
        
        return {"result":-1}
    elif( client.status=="completed"):
        conn=connect()
        cur=conn.cursor()
        query1="insert into completed_tasks values (%s,%s,%s,%s,%s,%s,%s)" #how will someone put if there were 100 attributes?
        query2="delete from tasks where userid=%s and taskid=%s"
        try:
            cur.execute(query1,(taskid,userid,client.title,client.description,client.deadline,client.status,datetime.now().date()))
            cur.execute(query2,(userid,taskid))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"error:{e}")
        finally :
            cur.close() #can conn be directly closed without writing cur.close()?
            conn.close()
        return {"result":1}
    else:
        return {"result":0}
@router.post("/createTaskViaAI")
def create_task(request: Request, client_input: textData):
    # Authentication check
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, detail="Please login first!")
    
    userid = getUserid(token)
    
    # Call the AI function with the text from your Pydantic model
    task_dict = get_clean_json_task(client_input.text)
    
    if not task_dict:
        # Raise 422 if AI fails or quota is exhausted
        raise HTTPException(422, detail="AI could not parse the task. Please try again later.")

    conn = connect()
    cur = conn.cursor()
    
    query = """
        INSERT INTO tasks (title, task_description, deadline, priority, userid, status) 
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    
    try:
        # Extracting data using dictionary .get() for safety
        cur.execute(query, (
            task_dict.get("title"),
            task_dict.get("description"),
            task_dict.get("deadline"),
            task_dict.get("priority").lower(),
            userid,
            task_dict.get("status").lower()
        ))
        print(f"DEBUG: Inserting into DB. Row count: {cur.rowcount}")
        conn.commit()
        print("!!! COMMIT COMMAND EXECUTED SUCCESSFULLY !!!")
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        raise HTTPException(500, detail="Database insertion failed.")
    finally:
        cur.close()
        conn.close()
        
    return {"message": "Task created successfully", "task": task_dict}

