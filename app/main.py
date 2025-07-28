from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr
import asyncio
import shortuuid
import requests

# project files
from config import CLAUDE_API_KEY, CLAUDE_MODEL, CLAUDE_API_ROUTE, MAX_TOKENS, ANTHROPIC_VERSION
from config import SYSTEM_PROMPT
import database as db
from routers import auth, jobs
from routers.v1.api import router as api_v1


# =================== Hardcode Values =============================
MAX_CHAR_COUNT = 400
MIN_CHAR_COUNT = 15
TEST_USER = "1"

API_VERSION = "/api/v1"

# =================== APP SETUP =============================
app = FastAPI()

app.include_router(api_v1.router, prefix=["/api/v1"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# =================== Endpoint Security =============================
# TODO: JWT auth

# =================== Directories and Databases =============================
# see data.py


# =================== Classes =============================
class QueryRequest(BaseModel):
    message: constr(min_length=1, max_length=400)  # type: ignore

# =================== ENDPOINTS =============================


@app.post(f"{API_VERSION}/process_query/{{user_id}}")
async def process_query(request: Request,user_id: str, query: QueryRequest = None):
    """Accepts a query from a user, processes it using an ai model,
     and then returns the response.

    # TODO: add error handling: api request, connection loss, etc...
    # TODO: add logging, timing of requests, etc...
    """
    try:
        if not valid_user(user_id):
            raise Exception("Invalid user")
        # validate query
        if valid_query(query.message):
            job_id = await start_job(user_id, query.message)

            base_url = str(request.base_url)
            return_url = f"{base_url}{API_VERSION}/job_status/{job_id}"
            print(f"return URL: {return_url}")
            return {
                "status": "success",
                "job_id": job_id,
                "job_status_URL": return_url
            }
        else:
            print("Invalid Input")
            return {
                "status": "error",
                "message": "invalid input"
            }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            "status": "error",
            "message": f"Error processing request: {str(e)}"
        }


@app.get(f"{API_VERSION}/job_status/{{job_id}}")
async def job_status(job_id: str):
    """An endpoint to poll to check on job status.
    """
    try:
        print(f"Checking job status for job_id: {job_id}")
        if db.job_exists(job_id=job_id):
            print(f"Job {job_id} exists")
            result = db.get_result_text_by_job_id(job_id=job_id)
            print(f"Result: {result}")
            if result is None:
                status = "processing"
            else:
                status = "complete"
            return {
                "status": status,
                "results": result,
                "job_id": job_id
            }
        else:
            raise Exception
    except Exception as e:
        print(f"Error polling job status: {str(e)}")
        return {
            "status": "error",
            "message": f"Error polling job status: {str(e)}"
        }


def get_job_id():
    return str(shortuuid.uuid())


async def start_job(user_id: str, user_query: str):
    try:
        job_id = get_job_id()
        print(f"Job: {job_id} started")
        print(f"job id type: {type(job_id)}")
        full_prompt = f"{SYSTEM_PROMPT.strip()}\n\nHuman: {user_query.strip()}\n\nAssistant:"
        # start request to LLM
        asyncio.create_task(process_job(job_id, full_prompt))
        if db.create_job(job_id=job_id, user_id=user_id, input_text=full_prompt):
            print(f"Job: {job_id} started")
            return job_id
        else:
            raise Exception
    except Exception as e:
        print(f"Error starting new job: {str(e)}")
        return {
            "status": "error",
            "message": f"Error starting new job: {str(e)}"
        }


async def process_job(job_id: str, full_prompt: str):
    # format for anthropic/claude
    results = query_claude(full_prompt, CLAUDE_API_KEY)
    # db.write(table="jobs", job_id=job_id, status="complete", result=results)
    result_text = results["content"][0]["text"]
    db.update_job(job_id=job_id, result_text=result_text)


def query_claude(full_prompt: str, api_key: str):
    url = CLAUDE_API_ROUTE
    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json"
    }
    data = {
        "model": CLAUDE_MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "user", "content": full_prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error querying LLM {response.status_code}: {response.text}")
        response.raise_for_status()


def valid_user(user_id: str):
    return str(user_id) == str(1)
    # try:
    #     with get_connection() as conn:
    #         cur = conn.cursor()
    #         cur.execute("SELECT 1 FROM users WHERE id = ? LIMIT 1", (user_id))
    #         return cur.fetchone() is not None
    # except sqlite3.Error as e:
    #     print(f"Database error: {e}")
    #     return False

# data validation
def valid_query(query: str):
    if type(query) is not str:
        return False
    elif len(query) > MAX_CHAR_COUNT:
        return False
    elif len(query) < MIN_CHAR_COUNT:
        return False
    # TODO: Check for bad prompts, poor spelling, etc
    else:
        return True


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)