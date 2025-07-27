# Tech Support API

## Description
API supporting tech support app

## Setup

0. Start in tech-support-api/
    cd tech-support-api
1. navigate into VENV
    source venv/bin/activate
2. Install dependencies
    pip install -r app/requirements.txt
3. create new database
    sqlite3 app/data/data.db < app/data/schema.sql
4. run 
    python app/main.py
    or     
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)


### MVP
<!-- - integrate llm -->
- github/git host
- CI deploy to cloud instance
    - setup vm
    - container?
<!-- - input validation, screening, review -->
<!-- - error checking, handling -->
- secure for deploy - api key, auth (jwt)
- add database to track jobs

### improvements
- authentication/authorization
- full security review (fastapi docs, ai, etc...)
- agentic rag (review this)
- full database of previous jobs, add archives page to main app
- accept file upload

### Nice to haves
- voice to text 
- upload a photo w/ error message
- upload a voice message of issue

