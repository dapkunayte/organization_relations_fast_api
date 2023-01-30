from pydantic import BaseModel


class OrganizationBase(BaseModel):
    inn: int
    organization_name: str

    class Config:
        orm_mode = True


class DeviceBase(BaseModel):
    uuid: str
    device_name: str

    class Config:
        orm_mode = True


class DeviceCreate(DeviceBase):
    organization_id: int


class DeviceCreateWithOrganization(DeviceBase):
    organization: OrganizationBase


class UserBase(BaseModel):
    user_name: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    device_id: str | None


class User(UserCreate):
    id: int


class UserList(UserBase):
    id: int


class Device(DeviceCreate):
    users: list[UserList] = None


class Organization(OrganizationBase):
    devices: list[DeviceBase] = None


class UserUpdate(BaseModel):
    device_id: str | None


class DeviceUpdate(BaseModel):
    organization_id: int | None





