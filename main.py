import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Client

app = FastAPI(title="CRM Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helpers
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


def to_public(doc: dict) -> dict:
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d


# Models for updates
class ClientCreate(Client):
    pass

class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[dict] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    newsletter_subscribed: Optional[bool] = None
    contact_preferences: Optional[dict] = None
    lead_status: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "CRM Backend running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# CRUD Endpoints for clients
@app.get("/api/clients", response_model=List[dict])
def list_clients():
    items = get_documents("client", {}, limit=None)
    return [to_public(i) for i in items]


@app.post("/api/clients", status_code=201)
def create_client(client: ClientCreate):
    new_id = create_document("client", client)
    created = db["client"].find_one({"_id": ObjectId(new_id)})
    return to_public(created)


@app.get("/api/clients/{client_id}")
def get_client(client_id: str):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(404, "Client not found")
    doc = db["client"].find_one({"_id": ObjectId(client_id)})
    if not doc:
        raise HTTPException(404, "Client not found")
    return to_public(doc)


@app.put("/api/clients/{client_id}")
def update_client(client_id: str, payload: ClientUpdate):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(404, "Client not found")
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not updates:
        return get_client(client_id)
    updates["updated_at"] = __import__("datetime").datetime.utcnow()
    res = db["client"].update_one({"_id": ObjectId(client_id)}, {"$set": updates})
    if res.matched_count == 0:
        raise HTTPException(404, "Client not found")
    return get_client(client_id)


@app.delete("/api/clients/{client_id}", status_code=204)
def delete_client(client_id: str):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(404, "Client not found")
    res = db["client"].delete_one({"_id": ObjectId(client_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Client not found")
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
