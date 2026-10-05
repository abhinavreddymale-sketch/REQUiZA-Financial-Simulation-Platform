"""Reference FastAPI service mirroring the engine's deterministic calculators.
Run: pip install -r requirements.txt && uvicorn main:app --reload"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from auth import router as auth_router

app = FastAPI(title="REQUiZA reference API (educational scenarios, not advice)")
app.include_router(auth_router)

class Sip(BaseModel):
    monthly: float = Field(ge=100, le=1_000_000)
    years: int = Field(ge=1, le=40)
    annual_return_pct: float = Field(ge=-20, le=50)

class Emi(BaseModel):
    principal: float = Field(ge=1000, le=100_000_000)
    annual_rate_pct: float = Field(ge=0, le=40)
    months: int = Field(ge=1, le=480)

@app.post("/sip")
def sip(b: Sip):
    r, n = b.annual_return_pct / 1200, b.years * 12
    fv = b.monthly * n if r == 0 else b.monthly * (((1 + r) ** n - 1) / r) * (1 + r)
    return {"invested": b.monthly * n, "future_value": fv, "note": "Scenario under stated assumptions, not a prediction."}

@app.post("/emi")
def emi(b: Emi):
    r, n = b.annual_rate_pct / 1200, b.months
    e = b.principal / n if r == 0 else b.principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return {"emi": e, "total_repayment": e * n, "total_interest": e * n - b.principal}
