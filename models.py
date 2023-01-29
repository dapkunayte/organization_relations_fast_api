from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from database import Base


class Organization(Base):
    __tablename__ = "organizations_table"

    inn = Column(BigInteger, primary_key=True, index=False)
    organization_name = Column(String, nullable=False, unique=True)

    devices = relationship("Device", backref="organizations_table")


class Device(Base):
    __tablename__ = "devices_table"

    uuid = Column(String, primary_key=True, index=False)
    device_name = Column(String, nullable=False, unique=True)
    organization_id = Column(BigInteger, ForeignKey("organizations_table.inn"), nullable=True)

    users = relationship("User", backref="devices_table")


class User(Base):
    __tablename__ = "users_table"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False, unique=False)
    device_id = Column(String, ForeignKey("devices_table.uuid"), nullable=True)
