from fastapi import FastAPI

app = FastAPI()

@app.get('/fastapi-test')
def read_root():
    return {"message": "FastAPI is working!"}