from fastapi import FastAPI
from models.analyzer import Analyzer

app = FastAPI()
analyzer = Analyzer("data/players.csv")

@app.get("/")
def home():
    return {"message": "Basketball Stats Analyzer API"}

@app.get("/top_scorer")
def top_scorer():
    return analyzer.top_scorer().to_dict()

@app.get("/mvp")
def mvp():
    return analyzer.mvp().to_dict()