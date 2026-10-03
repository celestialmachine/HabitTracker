# TODO: move basemodels into their own files
# TODO: write API test scripts using requests library?

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, habits

# creates an empty instance of FastAPI app which will hold all the routes
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows requests from any origin (fine for local dev)
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "welcome! habit tracker is alive"}


app.include_router(users.router)
app.include_router(habits.router)
