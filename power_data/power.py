import logging
import sys
from datetime import timedelta, datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from sqlalchemy import func

from Database.db_connector import DBConnection

from Models.model import Device, Rack, Building,rack_building_association,DeviceInventory,Site
from repo.site_repository import SiteRepository

from repo.influxdb_repository import InfluxdbRepository  # Assuming InfluxdbRepository is defined elsewhere
import logging
logger = logging.getLogger(__name__)

class PowerData:
    def __init__(self):
        self.site_repository = SiteRepository()
        self.db_connection = DBConnection()
        self.influxdb_repository = InfluxdbRepository()  # Assuming InfluxdbRepository is defined elsewhere

    def calculate_start_end_dates(self, duration_str: str) -> (datetime, datetime):
        today = datetime.today()

        if duration_str == "First Quarter":
            duration_str = "Last 3 Months"
        elif duration_str == "Second Quarter":
            duration_str = "Last 6 Months"
        elif duration_str == "Third Quarter":
            duration_str = "Last 9 Months"

        if duration_str == "Last 9 Months":
            start_date = (today - timedelta(days=270)).replace(day=1)
            end_date = today
        elif duration_str == "Last 6 Months":
            start_date = (today - timedelta(days=180)).replace(day=1)
            end_date = today
        elif duration_str == "Last 3 Months":
            start_date = (today - timedelta(days=90)).replace(day=1)
            end_date = today
        elif duration_str == "Last Year":
            start_date = (today.replace(day=1, month=1) - timedelta(days=365)).replace(day=1)
            end_date = start_date.replace(month=12, day=31)
        elif duration_str == "Current Year":
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif duration_str == "Current Month":
            start_date = today.replace(day=1)
            end_date = today
        elif duration_str == "Last Month":
            start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = (today.replace(day=1) - timedelta(days=1))
        elif duration_str == "7 Days":
            start_date = today - timedelta(days=7)
            end_date = today
        elif duration_str == "24 hours":
            start_date = today - timedelta(days=1)
            end_date = today
        else:
            raise ValueError("Unsupported duration format")

        return start_date, end_date
    def get_ips(self,site_id):
        with self.db_connection.session_scope() as session:
            devices = self.site_repository.get_devices_by_site_id(site_id)

            # Attach to session
            devices = [session.merge(device) for device in devices]

            device_ips = [device.ip_address for device in devices if device.ip_address]
            return device_ips

    def get_unit(self,carbon_emission_KG):
         if carbon_emission_KG < 1000:
             return "kg",round(carbon_emission_KG,4)
         else:
             carbon_emission=round((carbon_emission_KG / 1000), 4)
             return "ton",carbon_emission
    def calculate_carbon_car(self, carbon_emission_KG):

        car_trips = carbon_emission_KG * 1.39

        base_distance = 1000
        distance_per_trip = base_distance + (carbon_emission_KG * 10)
        unit, carbon_emission = self.get_unit(carbon_emission_KG)

        return f"{carbon_emission}{unit} is Equivalent of {int(car_trips)} car trips of {int(distance_per_trip)} km each in a gas-powered passenger vehicle"

    def calculate_carbon_solution(self, carbon_emission_KG):
        trees_needed = carbon_emission_KG / 0.021 / 12
        return {
            "plant_trees": f"Planting about {int(trees_needed)} trees can help offset carbon emissions. Trees absorb CO2 from the atmosphere, making this a natural way to balance out emissions.",
            "consolidation": "Regularly assess server usage, decommission outdated or underutilized servers, and consolidate workloads to optimize resource usage.",
            "high_efficiency": "Use power supplies with high-efficiency ratings (e.g., 80 PLUS Platinum or Titanium).",
            "regular_maintenance": "Conduct regular maintenance of IT equipment and cooling systems to ensure optimal performance."
        }

    def calculate_carbon_flight(self, carbon_emission_KG):
        flight_hours = carbon_emission_KG * 0.11 * 5.5
        hours = int(flight_hours)
        minutes = int((flight_hours - hours) * 60)
        unit, carbon_emission = self.get_unit(carbon_emission_KG)
        return f"{carbon_emission}{unit} is equivalent to {hours} hours and {minutes} minutes of flight time."

    def calculate_total_power_consumption(self, site_id: int, duration_str: str):
        start_date, end_date = self.calculate_start_end_dates(duration_str)
        device_ips = self.get_ips(site_id)

        results = {}

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.influxdb_repository.get_total_pin_value, device_ips, start_date, end_date,
                                duration_str): "total_pin",
                executor.submit(self.influxdb_repository.get_consumption_percentages, start_date, end_date,
                                duration_str): "consumption_percentages"
            }

            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    print(f"Error in {key}: {e}")  # You can replace this with logging

        total_pin_value = results.get("total_pin", 0)  # Default to 0 if there's an error
        consumption_percentages = results.get("consumption_percentages", {})
        logging.info(f"total_pin_value {total_pin_value}")
        logging.info(f"consumption_percentages {consumption_percentages}")
        if total_pin_value == 0 or not consumption_percentages:
            print("Warning: Some values are missing due to errors.")

        total_pin_value_KW = total_pin_value / 1000

        totalpin_kws = {field: round((percentage / 100) * total_pin_value_KW, 2) for field, percentage in
                        consumption_percentages.items()}

        return {
            "total_PIn": total_pin_value_KW,
            "consumption_percentages": consumption_percentages,
            "totalpin_kws": totalpin_kws
        }
    def calculate_average_energy_consumption_by_site_id(self, site_id: int, duration_str: str) -> dict:
        start_date, end_date = self.calculate_start_end_dates(duration_str)


        print('datatata')
        device_ips = self.get_ips(site_id)



        if not device_ips:
            logger.warning("Empty device_ips list provided")
            return {"time": f"{start_date} - {end_date}"}

        metrics = self.influxdb_repository.get_energy_consumption_metrics_with_filter17(device_ips, start_date, end_date, duration_str)

        print(metrics)
        if not metrics:
            return {"time": f"{start_date} - {end_date}"}

        total_energy_consumption = sum(metric.get('energy_consumption', 0) for metric in metrics)
        total_POut_kw = sum(metric.get('total_POut_kw', 0) for metric in metrics)
        total_PIn_kw = sum(metric.get('total_PIn_kw', 0) for metric in metrics)
        total_power_efficiency = sum(metric.get('power_efficiency', 0) for metric in metrics)
        count = len(metrics)

        co2emmsion=self.get_unit(total_PIn_kw*0.4041)


        return {
            "time": f"{start_date} - {end_date}",
            "energy_consumption":total_energy_consumption,
            "total_POut_kw": round(total_POut_kw, 2) if count > 0 else None,
            "total_PIn_kw": round(total_PIn_kw, 2) if count > 0 else None,
            "power_efficiency": total_power_efficiency,
            "co2emmsion":co2emmsion
        }

    def calculate_carbon_emission(self, site_id: int, duration_str: str) -> (float, float, str, str):

        start_date, end_date = self.calculate_start_end_dates(duration_str)
        device_ips=self.get_ips(site_id)

        # total_pin_value = self.influxdb_repository.get_total_pin_value(device_ips, start_date, end_date, duration_str)
        # carbon_intensity = self.influxdb_repository.get_carbon_intensity(start_date, end_date, duration_str)

        results = {}
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.influxdb_repository.get_total_pin_value, device_ips, start_date, end_date,
                                duration_str): "total_pin",
                executor.submit(self.influxdb_repository.get_carbon_intensity, start_date, end_date,
                                duration_str): "consumption_intensity"
            }

            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    print(f"Error in {key}: {e}")  # You can replace this with logging
        total_pin_value = results.get("total_pin", 0)  # Default to 0 if there's an error
        carbon_intensity = results.get("consumption_intensity", 0)

        total_pin_value_KW = total_pin_value / 1000
        carbon_emission = float(total_pin_value_KW) * float(carbon_intensity)
        print("Emisssionsssssss", carbon_emission, file=sys.stderr)
        carbon_emission_KG = round(carbon_emission / 1000, 2)
        print("KGGGGGGGGGGGG", carbon_emission_KG, file=sys.stderr)

        carbon_car = self.calculate_carbon_car(carbon_emission_KG)
        carbon_flight = self.calculate_carbon_flight(carbon_emission_KG)
        carbon_solution = self.calculate_carbon_solution(carbon_emission_KG)

        if carbon_emission < 1000:
            carbon_ems = str(round(carbon_emission, 3)) + ' kg'
        else:
            carbon_ems = str(round(carbon_emission / 1000, 3)) + ' Tons'

        data={
                "total_PIn": float(total_pin_value_KW),
                "carbon_emission": carbon_ems,
                "carbon_effect_car": carbon_car,
                "carbon_effect_flight": carbon_flight,
                "carbon_solution": carbon_solution
            }
        return data

    def calculate_energy_consumption_by_id_with_filter(self, site_id: int, duration_str: str) -> List[
        dict]:

        start_date, end_date = self.calculate_start_end_dates(duration_str)
        device_ips = self.get_ips(site_id)
        if not device_ips:
            return []

        energy_metrics = self.influxdb_repository.get_energy_consumption_metrics_with_filter(device_ips, start_date,
                                                                                             end_date,
                                                                                             duration_str)
        print("ENERGY_METRIC_OF_KPIIIIIIIIIII", energy_metrics, file=sys.stderr)
        return energy_metrics


    def get_device_inventory(self, site_id):
        with self.db_connection.session_scope() as session:
            # Fetch all devices for the given site ID
            onboarded_devices = session.query(Device).filter(
                (Device.site_id == site_id) &
                (Device.OnBoardingStatus == True)
            ).all()
            devices = session.query(Device).filter(
                (Device.site_id == site_id)
            ).all()

            # Count distinct vendors for the given site ID
            total_vendors = (
                session.query(func.count(Device.vendor_id.distinct()))
                .filter(
                    (Device.site_id == site_id) &
                    (Device.OnBoardingStatus == True)
                )
                .scalar()
            )

            # Fetch all racks for the given site ID
            racks = session.query(Rack).filter(Rack.site_id == site_id).all()

            # Calculate onboarded devices
            # onboarded_devices = sum(1 for device in devices if device.OnBoardingStatus)
            return {
                "onboarded_devices": len(onboarded_devices),
                "total_devices": len(devices),
                "total_vendors": total_vendors,
                "total_racks": len(racks)
            }

    def get_top_5_power_devices_with_filter(self, site_id: int, duration_str: str):
        start_date, end_date = self.calculate_start_end_dates(duration_str)

        device_inventory = self.site_repository.get_device_inventory_by_site_id(site_id)
        device_ips = [device['ip_address'] for device in device_inventory]
        print("DEVIIIIIIIIIIIIIIIIIIIIIIIIIIIII", device_ips, file=sys.stderr)

        top_devices_data_raw = self.influxdb_repository.get_top_5_devices(device_inventory, device_ips, start_date,
                                                                          end_date, duration_str)
        # top_devices_data = []
        # processed_ips = set()
        #
        # for device_data in top_devices_data_raw:
        #     ip = device_data['ip']
        #     if ip in processed_ips:
        #         continue
        #
        #     device_info = next((device for device in device_inventory if device['ip_address'] == ip), None)
        #     if device_info:
        #         cost_of_power = device_data['cost_of_power']
        #         average_power = device_data['average_PIn']
        #
        #         top_devices_data.append(DevicePowerConsumption(
        #             id=device_info['id'],
        #             device_name=device_info['device_name'],
        #             ip_address=device_info['ip_address'],
        #             total_power=round(device_data['total_PIn'] / 1000, 2),
        #             average_power=round(average_power, 2),
        #             cost_of_power=round(cost_of_power, 2)
        #         ))
        #
        #         processed_ips.add(ip)

        return top_devices_data_raw

    def get_all_racks(self, site_id,duration):
        with self.db_connection.session_scope()  as session:
            start_date, end_date = self.calculate_start_end_dates(duration)
            rack_list=[]
            if site_id:
                racks = session.query(Rack).filter(Rack.site_id == site_id).all()

            else:
                racks = session.query(Rack).all()
            print("length",len(racks))

            for rack in racks:

                building = (
                    session.query(Building.building_name)
                    .join(rack_building_association, Building.id == rack_building_association.c.building_id)
                    .filter(rack_building_association.c.rack_id == rack.id)
                    .first()
                )
                rack.building_name = building[0] if building else None

                apic_ips = session.query(Device.ip_address).filter(
                    rack.id == DeviceInventory.rack_id, Device.id == DeviceInventory.apic_controller_id
                ).distinct().all()

                site_result = session.query(Site.site_name).filter(Site.id == rack.site_id).first()
                rack.site_name = site_result[0] if site_result else None

                num_devices = session.query(func.count(Device.id)).filter(Device.rack_id == rack.id).scalar()
                rack.num_devices = num_devices
                print("Num devices", rack.num_devices)

                rack_power_data = self.influxdb_repository.get_24hrack_power(apic_ips, rack.id,start_date,
                                                                          end_date, duration)
                print(rack_power_data)

                rack_traffic_data = self.influxdb_repository.get_24h_rack_datatraffic(apic_ips, rack.id,start_date,
                                                                          end_date, duration)

                if rack_power_data:
                    power_utilization_values = [data.get('power_utilization', 0) for data in rack_power_data]
                    total_power_utilization = sum(power_utilization_values)
                    average_power_utilization = total_power_utilization / len(power_utilization_values)
                    rack.power_utilization = round(average_power_utilization, 2)

                    pue_values = [data.get('pue', 0) for data in rack_power_data]
                    total_pue = sum(pue_values)
                    average_pue = total_pue / len(pue_values)
                    rack.pue = round(average_pue, 2)

                    power_input_values = [data.get('power_input', 0) for data in rack_power_data]
                    total_power_input = sum(power_input_values)
                    rack.power_input = round(total_power_input / 1000, 2)

                    power_output_values = [data.get('power_output', 0) for data in rack_power_data]
                    total_power_output = sum(power_output_values)
                    rack.power_output = round(total_power_output / 1000, 2)
                else:
                    rack.power_utilization = 0
                    rack.pue = 0
                    rack.power_input = 0
                    rack.power_output = 0

                if rack_traffic_data:
                    traffic_throughput_values = [data.get('traffic_through', 0) for data in rack_traffic_data]
                    total_traffic_throughput = sum(traffic_throughput_values)
                    rack.datatraffic = round(total_traffic_throughput / (1024 ** 3), 2)
                else:
                    rack.datatraffic = 0

                rack_list.append({

                    "Rack Name": rack.rack_name,
                    "Building": rack.building_name,
                    "Site Name": rack.site_name,
                    "Number of Devices": rack.num_devices,
                    "EER": rack.power_utilization,
                    "PUE": rack.pue,
                    "Power Input (kW)": rack.power_input,
                    "Power Output(kW)": rack.power_output,
                    "Data Traffic (GB)": rack.datatraffic,
                    "Co2":round((rack.power_input *0.471),4),
                    "PCR":round((rack.power_input*1000)/rack.datatraffic,4) if rack.datatraffic > 0 else 0

                })
            return rack_list

