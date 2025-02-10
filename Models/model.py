from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Date, Text, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Association table for Rack and Building
rack_building_association = Table(
    'rack_building',
    Base.metadata,
    Column('rack_id', Integer, ForeignKey('rack.id'), primary_key=True),
    Column('building_id', Integer, ForeignKey('building.id'), primary_key=True)
)


class Site(Base):
    __tablename__ = 'site'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=True, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
    site_name = Column(String(255), nullable=True)
    site_type = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    latitude = Column(String(255), nullable=True)
    longitude = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    total_devices = Column(String(255), nullable=True)

    # Relationships
    reports = relationship("Reports", back_populates="site")
    racks = relationship("Rack", back_populates="site")
    device_inventory = relationship("DeviceInventory", back_populates="site")


class PasswordGroup(Base):
    __tablename__ = 'password_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    password_group_name = Column(String(255))
    password_group_type = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class Reports(Base):
    __tablename__ = 'Reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_title = Column(String(300), nullable=False)
    site_id = Column(Integer, ForeignKey('site.id'), nullable=True)
    report_type = Column(String(200), nullable=True)
    duration = Column(String(500), nullable=False)
    path = Column(String(300), nullable=False)
    entered_on = Column(DateTime, nullable=True)
    Status = Column(Boolean, nullable=True)
    message = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationship
    site = relationship("Site", back_populates="reports")


class Device(Base):
    __tablename__ = 'Devices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(255), unique=False, index=True)
    device_type = Column(String(200), nullable=True)
    device_name = Column(String(200), nullable=True)
    device_nature = Column(String(200), nullable=True)
    OnBoardingStatus = Column(Boolean, nullable=True, default=False)
    site_id = Column(Integer, ForeignKey('site.id'), nullable=True)
    rack_id = Column(Integer, ForeignKey('rack.id'), nullable=True)
    rack_unit = Column(Integer, nullable=True)
    credential_id = Column(Integer, nullable=True)
    password_group_id = Column(Integer, ForeignKey('password_groups.id'), nullable=True)
    node_id = Column(Integer, nullable=True)
    messages = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    vendor_id = Column(Integer, ForeignKey('vendor.id'), nullable=True)



    # Relationships
    site = relationship("Site")
    rack = relationship("Rack", back_populates="devices")
    password_group = relationship("PasswordGroup")
    vendor = relationship("Vendor", back_populates="devices")



class APICController(Base):
    __tablename__ = 'apic_controllers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    ip_address = Column(String(255), nullable=False)


class DeviceInventory(Base):
    __tablename__ = 'deviceInventory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cisco_domain = Column(String(255), nullable=True)
    created_by = Column(String(255), nullable=True)
    criticality = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    device_id = Column(Integer, nullable=True)
    device_name = Column(String(255), nullable=True)
    device_ru = Column(Integer, nullable=True)
    domain = Column(String(255), nullable=True)
    hardware_version = Column(String(255), nullable=True)
    item_desc = Column(Text, nullable=True)
    manufacturer_date = Column(Date, nullable=True)
    manufacturer = Column(String(255), nullable=True)
    modified_by = Column(String(255), nullable=True)
    apic_controller_id = Column(Integer, ForeignKey('apic_controllers.id'), nullable=False)
    pn_code = Column(String(255), nullable=True)
    rack_id = Column(Integer, ForeignKey('rack.id'), nullable=True)
    rfs_date = Column(Date, nullable=True)
    section = Column(String(255), nullable=True)
    serial_number = Column(String(255), nullable=True)
    site_id = Column(Integer, ForeignKey('site.id'), nullable=True)
    software_version = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    tag_id = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)

    # Define relationships
    apic_controller = relationship("APICController", backref="device_inventory")
    rack = relationship("Rack", backref="device_inventory")
    site = relationship("Site", back_populates="device_inventory")


class Rack(Base):
    __tablename__ = "rack"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rack_name = Column(String(255), nullable=False)
    site_id = Column(Integer, ForeignKey('site.id'), nullable=False)
    manufacture_date = Column(Date, nullable=True)
    rack_model = Column(String(255), nullable=True)
    rfs = Column(String(255), nullable=True)
    height = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    depth = Column(Integer, nullable=True)
    status = Column(String(255), nullable=True)

    # Relationships
    site = relationship("Site", back_populates="racks")
    devices = relationship("Device", back_populates="rack")
    buildings = relationship("Building", secondary=rack_building_association, back_populates="racks")


class Building(Base):
    __tablename__ = 'building'

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_name = Column(String(255), nullable=False)
    racks = relationship("Rack", secondary=rack_building_association, back_populates="buildings")




class Vendor(Base):
    __tablename__ = "vendor"
    id = Column(Integer, primary_key=True)
    vendor_name = Column(String(200), nullable=True)
    devices = relationship("Device", back_populates="vendor")