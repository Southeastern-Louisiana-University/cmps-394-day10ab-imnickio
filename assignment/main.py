from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from keycloak import KeycloakOpenID
import os

app = FastAPI()
security = HTTPBearer()

keycloak_openid = KeycloakOpenID(
    server_url="http://keycloak:8080/",
    client_id="myclient",  
    realm_name="myrealm" 
)

models.Base.metadata.create_all(bind=engine)
API_INSTANCE = os.getenv('API_INSTANCE', 'Unknown')

class ItemBase(BaseModel):
    itemname: str
    quantity: int

def getdb():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(getdb)]

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token_info = keycloak_openid.decode_token(
            token.credentials
        )
        return token_info
    except Exception as e:
        print(f"Detailed Token Validation Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/items", status_code=status.HTTP_200_OK)
async def read_all_items(db: db_dependency):
    items = db.query(models.Item).all()
    return {"items": items, "instance": API_INSTANCE}

@app.post("/items", status_code=status.HTTP_201_CREATED)
async def add_item(item: ItemBase, db: db_dependency, user: dict = Depends(get_current_user)):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    return {"message": "Item added by " + user.get("preferred_username", "Unknown")}

@app.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item(item_id: int, db: db_dependency, user: dict = Depends(get_current_user)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail='Item not found.')
    db.delete(item)
    db.commit()
    return {"detail": "Deleted successfully"}