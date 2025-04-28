from typing import List, Dict
from Database.db_connector import DBConnection
from Models.model import Device, DeviceInventory, Site
from sqlalchemy.orm import joinedload
class SiteRepository:
    def __init__(self):
        self.db_connection = DBConnection()

    def get_devices_by_site_id(self, site_id: int):
        """Fetch devices using eager loading to prevent session detachment issues"""
        with self.db_connection.session_scope() as session:
            devices = (
                session.query(Device)
                .filter(Device.site_id == site_id)
                .options(joinedload(Device.site))  # Ensures related objects are loaded
                .all()
            )
            print(devices)
            return devices

    def get_device_inventory_by_site_id(self, site_id: int) -> List[Dict[str, any]]:
        with self.db_connection.session_scope() as session:
            device_inventory_data = (
                session.query(
                    DeviceInventory.id,
                    DeviceInventory.device_name,
                    Device.ip_address.label('ip_address'),
                    Site.site_name,
                    DeviceInventory.hardware_version,
                    DeviceInventory.manufacturer,
                    DeviceInventory.pn_code,
                    DeviceInventory.serial_number,
                    DeviceInventory.software_version,
                    DeviceInventory.status
                )
                .join(Device,
                      DeviceInventory.apic_controller_id == Device.id)
                .join(Site, DeviceInventory.site_id == Site.id)
                .filter(DeviceInventory.site_id == site_id)
                .all()
            )

            device_inventory_dicts = []
            for data in device_inventory_data:
                device_info = {
                    "id": data.id,
                    "device_name": data.device_name,
                    "ip_address": data.ip_address,
                    "site_name": data.site_name,
                    "hardware_version": data.hardware_version,
                    "manufacturer": data.manufacturer,
                    "pn_code": data.pn_code,
                    "serial_number": data.serial_number,
                    "software_version": data.software_version,
                    "status": data.status,
                }
                device_inventory_dicts.append(device_info)

            return device_inventory_dicts
