from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# project files
from routers.v1 import api as api_v1
from routers.v1 import auth as auth_v1

# =================== Hardcode Values =============================
# see config.py

# =================== APP SETUP =============================
app = FastAPI()

app.include_router(api_v1.router, prefix="/api/v1", tags=["api"])
app.include_router(auth_v1.router, prefix="/auth/v1", tags=["auth"])

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# =================== Endpoint Security =============================
# see app/routers/v1/auth.py

# =================== Directories and Databases =============================
# see database.py and app/data/schema.sql

# =================== ENDPOINTS =============================
# see app/routers/v1/api.py

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)