from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr
import asyncio
import shortuuid
import requests

# project files
from config import CLAUDE_API_KEY, CLAUDE_MODEL, CLAUDE_API_ROUTE, MAX_TOKENS, ANTHROPIC_VERSION
from config import API_VERSION, SYSTEM_PROMPT
import database as db

# =================== Hardcode Values =============================
MAX_CHAR_COUNT = 400
MIN_CHAR_COUNT = 15
TEST_USER = "1"

# =================== APP SETUP =============================
app = FastAPI()

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
async def process_query(user_id: str, request: QueryRequest = None):
    """Accepts a query from a user, processes it using an ai model,
     and then returns the response.

    # TODO: add error handling: api request, connection loss, etc...
    # TODO: add logging, timing of requests, etc...
    """
    try:
        # validate query
        if valid_query(request.message):
            job_id = start_job(user_id, request.message)

            base_url = "http://localhost:3000"
            return {
                "status": "success",
                "job_id": job_id,
                "job_status_URL": f"{base_url}{API_VERSION}/job_status/{job_id}"
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
        if db.job_exists(job_id=job_id):
            result = db.get_result_text_by_job_id(job_id=job_id)
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
        print(f"Error processing request: {str(e)}")
        return {
            "status": "error",
            "message": f"Error processing request: {str(e)}"
        }


def get_job_id():
    return str(shortuuid.uuid())


async def start_job(user_id: str, user_query: str):
    try:
        job_id = get_job_id()
        full_prompt = f"{SYSTEM_PROMPT.strip()}\n\nHuman: {user_query.strip()}\n\nAssistant:"
        # start request to LLM
        asyncio.create_task(process_job(job_id, full_prompt))
        job_id = db.create_job(job_id=job_id, user_id=user_id, input_text=full_prompt)
        print(f"Job: {job_id} started")
        return job_id
    except Exception as e:
        print(f"Error starting new job: {str(e)}")
        return {
            "status": "error",
            "message": f"Error processing request: {str(e)}"
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
        print(f"Error {response.status_code}: {response.text}")
        response.raise_for_status()


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