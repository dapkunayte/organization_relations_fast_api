from sqlalchemy.orm import Session, joinedload
import models
import pydantic_models
from fastapi import HTTPException
import uuid as uuid_lib


def is_valid_uuid(val):
    try:
        uuid_lib.UUID(str(val))
        return True
    except ValueError:
        return False


def get_organization(db: Session, organization_id: int):
    db_organization = db.query(models.Organization).filter(models.Organization.inn == organization_id).first()
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization


def create_organization(db: Session, organization: pydantic_models.Organization):
    if len(str(organization.inn)) != 10:
        raise HTTPException(status_code=415, detail="Incorrect inn")

    db_organization_inn = db.query(models.Organization).filter(models.Organization.inn == organization.inn).first()
    db_organization_name = db.query(models.Organization).filter(
        models.Organization.organization_name == organization.organization_name).first()

    if db_organization_inn is not None or db_organization_name is not None:
        raise HTTPException(status_code=400, detail="Organization already exists")

    db_organization = models.Organization(inn=organization.inn, organization_name=organization.organization_name)
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def get_device(db: Session, device_id: str):
    db_device = db.query(models.Device).filter(models.Device.uuid == device_id).first()
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device


def create_device(db: Session, device: pydantic_models.DeviceCreate):
    db_device_uuid = db.query(models.Device).filter(models.Device.uuid == device.uuid).first()
    db_device_name = db.query(models.Device).filter(models.Device.device_name == device.device_name).first()
    if db_device_uuid is not None or db_device_name is not None:
        raise HTTPException(status_code=400, detail="Device already exists")
    if not is_valid_uuid(device.uuid):
        raise HTTPException(status_code=415, detail="Incorrect uuid")
    get_organization(db, device.organization_id)  # проверка, чтобы привязка была только к существующей организации
    db_device = models.Device(uuid=device.uuid, device_name=device.device_name, organization_id=device.organization_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def create_device_with_organization(db: Session, device: pydantic_models.DeviceCreateWithOrganization):
    db_device_uuid = db.query(models.Device).filter(models.Device.uuid == device.uuid).first()
    db_device_name = db.query(models.Device).filter(models.Device.device_name == device.device_name).first()
    if db_device_uuid is not None or db_device_name is not None:
        raise HTTPException(status_code=400, detail="Device already exists")
    if not is_valid_uuid(device.uuid):
        raise HTTPException(status_code=415, detail="Incorrect uuid")
    create_organization(db, device.organization)
    db_device = models.Device(uuid=device.uuid, device_name=device.device_name, organization_id=device.organization.inn)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def update_device(db: Session, device_id: str, device: pydantic_models.DeviceUpdate):
    db_device = db.query(models.Device).filter(models.Device.uuid == device_id).first()
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.organization_id is not None:
        get_organization(db, device.organization_id)  # проверка, чтобы привязка была только к существующей организации
        if len(str(device.organization_id)) != 10:
            raise HTTPException(status_code=415, detail="Incorrect inn")
    db_device.organization_id = device.organization_id
    db.commit()
    return db_device


def get_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def create_user(db: Session, user: pydantic_models.UserCreate):
    if not is_valid_uuid(user.device_id):
        raise HTTPException(status_code=415, detail="Incorrect uuid")
    if user.device_id is not None:
        get_device(db, user.device_id)  # проверка, чтобы привязка была только к существующей организации

    db_user = models.User(user_name=user.user_name, device_id=user.device_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: pydantic_models.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.device_id is not None:
        get_device(db, user.device_id)  # проверка, чтобы привязка была только к существующей организации
        if not is_valid_uuid(user.device_id):
            raise HTTPException(status_code=415, detail="Incorrect uuid")
    db_user.device_id = user.device_id
    db.commit()
    return db_user


def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    db_organizations = db.query(models.Organization).offset(skip).limit(limit).all()
    if db_organizations is None or db_organizations == []:
        raise HTTPException(status_code=404, detail="Organization\'s list is empty")
    return db_organizations


def get_devices(db: Session, skip: int = 0, limit: int = 100):
    db_devices = db.query(models.Device).offset(skip).limit(limit).all()
    if len(db_devices) == 0:
        raise HTTPException(status_code=404, detail="Device\'s list is empty")
    return db_devices


def get_users(db: Session, skip: int = 0, limit: int = 100):
    db_users = db.query(models.User).offset(skip).limit(limit).all()
    if len(db_users) == 0:
        raise HTTPException(status_code=404, detail="User\'s list is empty")
    return db_users


def delete_organization(db: Session, organization_id: int):
    db_organization = db.query(models.Organization).filter(models.Organization.inn == organization_id).first()
    if db_organization is None:
        raise HTTPException(status_code=400, detail="Organization doesn't exist")
    if len(db_organization.devices) != 0:
        raise HTTPException(status_code=400, detail="Delete or detach devices first")
    db.delete(db_organization)
    db.commit()
    return get_organizations(db)


def delete_device(db: Session, device_id: str):
    db_device = db.query(models.Device).filter(models.Device.uuid == device_id).first()
    if db_device is None:
        raise HTTPException(status_code=400, detail="Device doesn't exist")
    if len(db_device.users) != 0:
        raise HTTPException(status_code=400, detail="Delete or detach users first")
    db.delete(db_device)
    db.commit()
    return get_devices(db)


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="User doesn't exist")
    db.delete(db_user)
    db.commit()
    return get_users(db)
