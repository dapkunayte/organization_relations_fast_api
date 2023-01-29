from fastapi import FastAPI, Depends
import models, pydantic_models
import attach_logic as al
from database import SessionLocal, engine
from sqlalchemy.orm import Session
import uvicorn


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def index():
    return {"hello": "world"}


@app.get("/organizations/{organization_id}", response_model=pydantic_models.Organization)
def get_organization(organization_id, db: Session = Depends(get_db)):
    return al.get_organization(db=db, organization_id=organization_id)


@app.post("/organizations/", response_model=pydantic_models.OrganizationBase)
def create_organization(organization: pydantic_models.OrganizationBase, db: Session = Depends(get_db)):
    return al.create_organization(db=db, organization=organization)


@app.get("/devices/{device_id}", response_model=pydantic_models.Device)
def get_device(device_id: str, db: Session = Depends(get_db)):
    return al.get_device(db=db, device_id=device_id)


@app.post("/devices/", response_model=pydantic_models.DeviceCreate)
def create_device(device: pydantic_models.DeviceCreate, db: Session = Depends(get_db)):
    return al.create_device(db=db, device=device)


@app.put("/devices/{device_id}", response_model=pydantic_models.DeviceCreate)
def update_device(device_id: str, device: pydantic_models.DeviceUpdate, db: Session = Depends(get_db)):
    return al.update_device(db=db, device_id=device_id, device=device)


@app.get("/users/{user_id}", response_model=pydantic_models.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return al.get_user(db=db, user_id=user_id)


@app.post("/users/", response_model=pydantic_models.User)
def create_user(user: pydantic_models.UserCreate, db: Session = Depends(get_db)):
    return al.create_user(db=db, user=user)


@app.put("/users/{user_id}", response_model=pydantic_models.User)
def update_user(user_id: int, user: pydantic_models.UserUpdate, db: Session = Depends(get_db)):
    return al.update_user(db=db, user_id=user_id, user=user)


@app.get("/organizations/", response_model=list[pydantic_models.Organization])
def get_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    organizations = al.get_organizations(db, skip=skip, limit=limit)
    return organizations


@app.get("/devices/", response_model=list[pydantic_models.Device])
def get_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    devices = al.get_devices(db, skip=skip, limit=limit)
    return devices


@app.get("/users/", response_model=list[pydantic_models.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = al.get_users(db, skip=skip, limit=limit)
    return users


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)