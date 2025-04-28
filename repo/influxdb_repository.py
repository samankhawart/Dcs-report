import math
import sys
from typing import List
from datetime import datetime

import numpy as np
import pandas as pd
from influxdb_client import InfluxDBClient
from Database.db_connector import DBConnection
 # Ensure configs.py contains INFLUXDB_BUCKET


class InfluxdbRepository:
    def __init__(self):
        """Initialize the InfluxDB connection using DBConnection."""
        self.db_connection = DBConnection()
        self.query_api = self.db_connection.query_api  # Ensure this is set in DBConnection
        self.bucket="Dcs_db"
        # self.query_api1 = self.client.query_api()

    def get_total_pin_value(self, device_ips: List[str], start_date: datetime, end_date: datetime,
                            duration_str: str) -> float:
        start_time = start_date.isoformat() + 'Z'
        end_time = end_date.isoformat() + 'Z'
        aggregate_window = "1h" if duration_str == "24 hours" else "1d"
        total_pin = 0
        for ip in device_ips:
            query = f'''
           from(bucket: "{self.bucketT}")
           |> range(start: {start_time}, stop: {end_time})
           |> filter(fn: (r) => r["_measurement"] == "DevicePSU" and r["ApicController_IP"] == "{ip}")
           |> filter(fn: (r) => r["_field"] == "total_PIn" or r["_field"] == "total_POut")
           |> aggregateWindow(every: {aggregate_window}, fn: mean, createEmpty: false)
           |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
       '''

            result = self.query_api.query_data_frame(query)

            if not result.empty:
                total_pin +=result['total_PIn'].sum() if 'total_PIn' in result else 0.0

        return total_pin

    def get_consumption_percentages(self, start_date: datetime, end_date: datetime, duration_str: str) -> dict:
        start_time = start_date.isoformat() + 'Z'
        end_time = end_date.isoformat() + 'Z'
        aggregate_window = "1h" if duration_str == "24 hours" else "1d"
        zone = "AE"

        query = f'''
            from(bucket: "Dcs_db")
            |> range(start: {start_time}, stop: {end_time})
            |> filter(fn: (r) => r["_measurement"] == "electricitymap_power" and r["zone"] == "{zone}")
            |> filter(fn: (r) => 
                r["_field"] == "nuclear_consumption" or 
                r["_field"] == "geothermal_consumption" or 
                r["_field"] == "biomass_consumption" or 
                r["_field"] == "coal_consumption" or 
                r["_field"] == "wind_consumption" or 
                r["_field"] == "solar_consumption" or 
                r["_field"] == "hydro_consumption" or 
                r["_field"] == "gas_consumption" or 
                r["_field"] == "oil_consumption" or 
                r["_field"] == "unknown_consumption" or 
                r["_field"] == "battery_discharge_consumption")
            |> aggregateWindow(every: {aggregate_window}, fn: sum, createEmpty: false)
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        result = self.query_api.query_data_frame(query)
        print("RESULT", result, file=sys.stderr)

        # Initialize the consumption totals dictionary with specific fields.
        consumption_totals = {
            "nuclear": 0, "geothermal": 0, "biomass": 0, "coal": 0, "wind": 0,
            "solar": 0, "hydro": 0, "gas": 0, "oil": 0, "unknown": 0, "battery_discharge": 0
        }

        if not result.empty:
            # Extract the sums from the query result for each field.
            for field in consumption_totals.keys():
                field_name = f"{field}_consumption"
                if field_name in result.columns:
                    consumption_totals[field] = result[field_name].sum()

        # Calculate the total power consumption from the retrieved data.
        powerConsumptionTotal = sum(consumption_totals.values())

        # Compute the percentage of total power consumption for each field.
        percentages = {field: math.floor((value / powerConsumptionTotal) * 100) if powerConsumptionTotal > 0 else 0
                       for field, value in consumption_totals.items()}

        return percentages


    def get_carbon_intensity(self, start_date: datetime, end_date: datetime, duration_str: str) -> float:
        start_time = start_date.isoformat() + 'Z'
        end_time = end_date.isoformat() + 'Z'
        # Determine the appropriate aggregate window based on the duration
        if duration_str == "24 hours":
            aggregate_window = "1h"
            aggregation_function = "max()"  # For 24 hours, take the maximum value
        elif duration_str in ["7 Days", "Current Month", "Last Month"]:
            aggregate_window = "1d"
            aggregation_function = "sum()"  # Sum for longer durations
        else:
            aggregate_window = "1m"
            aggregation_function = "sum()"

        zone = "AE"

        # InfluxDB query to fetch the carbon intensity
        query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: {start_time}, stop: {end_time})
                |> filter(fn: (r) => r["_measurement"] == "electricitymap_carbonIntensity" and r["zone"] == "{zone}")
                |> filter(fn: (r) => r["_field"] == "carbonIntensity")
                |> aggregateWindow(every: {aggregate_window}, fn: max, createEmpty: false)
                |> {aggregation_function}  
            '''
        result = self.query_api.query_data_frame(query)
        print("RESULT", result, file=sys.stderr)
        carbon_intensity = result['_value'] if not result.empty else 0
        print("carbon_intensity", carbon_intensity, file=sys.stderr)

        return carbon_intensity
    def get_energy_consumption_metrics_with_filter(self, device_ips: List[str], start_date: datetime,
                                                   end_date: datetime, duration_str: str) -> List[dict]:
        total_power_metrics = []
        start_time = start_date.isoformat() + 'Z'
        end_time = end_date.isoformat() + 'Z'

        # Define the aggregate window and time format based on the duration string
        if duration_str in ["24 hours"]:
            aggregate_window = "1h"
            time_format = '%Y-%m-%d %H:00'
        elif duration_str in ["7 Days", "Current Month", "Last Month"]:
            aggregate_window = "1d"
            time_format = '%Y-%m-%d'
        else:  # For "last 6 months", "last year", "current year",
            aggregate_window = "1m"
            time_format = '%Y-%m'

        for ip in device_ips:
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: {start_time}, stop: {end_time})
                |> filter(fn: (r) => r["_measurement"] == "DevicePSU" and r["ApicController_IP"] == "{ip}")
                |> filter(fn: (r) => r["_field"] == "total_PIn" or r["_field"] == "total_POut")
                |> aggregateWindow(every: {aggregate_window}, fn: mean, createEmpty: true)
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
            result = self.query_api.query_data_frame(query)

            if not result.empty:
                result['_time'] = pd.to_datetime(result['_time']).dt.strftime(time_format)
                numeric_cols = result.select_dtypes(include=[np.number]).columns.tolist()
                if '_time' in result.columns and numeric_cols:
                    grouped = result.groupby('_time')[numeric_cols].mean().reset_index()
                    grouped['_time'] = pd.to_datetime(grouped['_time'])
                    grouped.set_index('_time', inplace=True)

                    all_times = pd.date_range(start=start_date, end=end_date, freq=aggregate_window.upper()).strftime(
                        time_format)
                    grouped = grouped.reindex(all_times).fillna(0).reset_index()

                    for _, row in grouped.iterrows():
                        pin = row['total_PIn']
                        pout = row['total_POut']

                        energy_consumption = pout / pin if pin > 0 else 0
                        power_efficiency = ((pin / pout) ) if pout > 0 else 0

                        total_power_metrics.append({
                            "time": row['index'],
                            "energy_efficiency": round(energy_consumption, 2),
                            "total_POut": round(pout, 2),
                            "total_PIn": round(pin, 2),
                            "power_efficiency": round(power_efficiency, 2)
                        })

        df = pd.DataFrame(total_power_metrics).drop_duplicates(subset='time').to_dict(orient='records')
        return df


    def determine_aggregate_window(self, duration_str: str) -> tuple:
        if duration_str == "24 hours":
            return "1h", '%Y-%m-%d %H:00'
        elif duration_str in ["7 Days", "Current Month", "Last Month"]:
            return "1d", '%Y-%m-%d'
        else:  # For "last 6 months", "last year", "current year"
            return "1m", '%Y-%m'

    def fetch_device_power_consumption(self, ip, start_time, end_time, aggregate_window):
        query = f'''
               from(bucket: "{self.bucket}")
                 |> range(start: {start_time}, stop: {end_time})
                 |> filter(fn: (r) => r["ApicController_IP"] == "{ip}")
                 |> filter(fn: (r) => r["_measurement"] == "DevicePSU" and r["_field"] == "total_PIn")
                 |> aggregateWindow(every: {aggregate_window}, fn: sum, createEmpty: false)
           '''

        try:
            result = self.query_api.query_data_frame(query)
            print(result)
            if isinstance(result, pd.DataFrame) and not result.empty:
                total_power = result['_value'].sum()
            else:
                total_power = 0
        except Exception as e:
            print(f"Error fetching power consumption: {e}")
            total_power = None

        return total_power

    def fetch_bandwidth_and_traffic(self, ip, start_time, end_time, aggregate_window):
        query = f'''
              from(bucket: "{self.bucket}")
                |> range(start: {start_time}, stop: {end_time})
                |> filter(fn: (r) => r["_measurement"] == "DeviceEngreeTraffic")
                |> filter(fn: (r) => r["ApicController_IP"] == "{ip}")
                |> filter(fn: (r) => r["_field"] == "bandwidth" or r["_field"] == "total_bytesRateLast")
                |> aggregateWindow(every: {aggregate_window}, fn: mean, createEmpty: false)
          '''

        try:
            result = self.query_api.query_data_frame(query)
            print(result)
            if isinstance(result, pd.DataFrame) and not result.empty:
                bandwidth = result.loc[result['_field'] == 'bandwidth', '_value'].mean() / 1000  # Convert Kbps to Mbps
                traffic_speed = result.loc[result[
                                               '_field'] == 'total_bytesRateLast', '_value'].mean() * 8 / 1e6  # Convert bytes/sec to Mbps
                # bandwidth_utilization = min((traffic_speed / bandwidth) * 100, 100) if bandwidth else 0
                bandwidth_utilization = (traffic_speed / bandwidth) * 100 if bandwidth else 0
            else:
                bandwidth = traffic_speed = bandwidth_utilization = 0
        except Exception as e:
            print(f"Error fetching bandwidth and traffic: {e}")
            bandwidth = traffic_speed = bandwidth_utilization = None

        return bandwidth, traffic_speed, bandwidth_utilization

    def convert_and_add_unit(self, total_power, bandwidth, traffic_speed, bandwidth_utilization, co2em):
        # Convert and round total power to kW if greater than 1000W (1 kW)
        if total_power > 1000:  # Convert to kW if power is greater than 1000W
            total_power = round(total_power / 1000, 2)  # Convert from W to kW
            power_unit = 'kW'
        else:
            total_power = round(total_power, 2)
            power_unit = 'W'

        # Convert and round bandwidth
        if bandwidth > 1000:  # Convert to GPS if bandwidth is greater than 1000 Mbps (1 Gbps)
            bandwidth = round(bandwidth / 1000, 2)  # Convert from Mbps to GPS
            bandwidth_unit = 'GPS'
        else:
            bandwidth = round(bandwidth, 2)
            bandwidth_unit = 'Mbps'

        # Convert and round traffic speed
        if traffic_speed > 1000:  # Convert to GPS if traffic speed is greater than 1000 Mbps (1 Gbps)
            traffic_speed = round(traffic_speed / 1000, 2)  # Convert from Mbps to GPS
            traffic_speed_unit = 'GPS'
        else:
            traffic_speed = round(traffic_speed, 2)
            traffic_speed_unit = 'Mbps'

        # Convert and round bandwidth utilization
        bandwidth_utilization = round(bandwidth_utilization, 2)

        # Convert and round CO2 emissions: if greater than 1000 grams (1 kg), convert to tons
        if co2em >= 1000:  # Convert to tons if CO2 emissions are greater than or equal to 1000 grams
            co2em = round(co2em / 1000, 3)  # Convert from grams to tons
            co2em_unit = 'tons'
        else:
            co2em = round(co2em, 2)  # Round to 2 decimal places if less than 1 kg
            co2em_unit = 'kgs'

        return {
            'total_power': f"{total_power} {power_unit}",
            'bandwidth': f"{bandwidth} {bandwidth_unit}",
            'traffic_speed': f"{traffic_speed} {traffic_speed_unit}",
            'bandwidth_utilization': f"{bandwidth_utilization} ",
            'co2emissions': f"{co2em} {co2em_unit}"
        }

    def get_top_5_devices(self,device_inventory, device_ips: List[str], start_date: datetime, end_date: datetime, duration_str: str) -> \
    List[dict]:
        top_devices = []

        start_time = start_date.isoformat() + 'Z'
        end_time = end_date.isoformat() + 'Z'

        aggregate_window, time_format = self.determine_aggregate_window(duration_str)

        for ip in device_ips:
            # Fetch data

            total_power = self.fetch_device_power_consumption(ip, start_time, end_time, aggregate_window)
            print("ip, start_time, end_time,aggregate_window",ip, start_time, end_time,aggregate_window)
            bandwidth_mps, traffic_speed_mps, bandwidth_utilization = self.fetch_bandwidth_and_traffic(ip, start_time, end_time,
                                                                                               aggregate_window)
            bandwidth_gps=bandwidth_mps/1000
            traffic_gbps = traffic_speed_mps / 1000  # Convert Mbps to Gbps
            pcr = round(total_power / traffic_gbps, 2) if traffic_gbps else None  # PCR in W/Gbps
            print(total_power,"dsajfdkjdkjd")
            print(traffic_gbps,"sd;f;sdl;fl;gls")
            co2em=(total_power/1000) *0.4041
            print("co2emissions ", co2em)
            print(pcr,"PCR")


            # Convert and format the data with units
            converted_data = self.convert_and_add_unit(total_power, bandwidth_mps, traffic_speed_mps, bandwidth_utilization,
                                                       co2em)

            # Example logic to populate id and device_name (replace with actual data source if available)
            # device_name = f"Device_{ip}"  # Replace with real device name logic
            # device_id = hash(ip)  # Replace with actual ID logic
            device_info = next((device for device in device_inventory if device['ip_address'] == ip), None)
            print(device_info)
            print("pcr ", pcr)
            print("co2emissions ", co2em)
            print(total_power,"")
            # print(" bandwidth, traffic_speed, bandwidth_utilization ", bandwidth, traffic_speed, bandwidth_utilization )
            if device_info:
                device_id = device_info['id']
                device_name = device_info['device_name']

            top_devices.append({
                'id': device_id,
                'device_name': device_name,
                'total_power': converted_data['total_power'],
                'total_bandwidth': converted_data['bandwidth'],
                'traffic_speed': converted_data['traffic_speed'],
                'bandwidth_utilization': converted_data['bandwidth_utilization'],
                'pcr': round(pcr, 4) if pcr else 0,
                'co2emmissions': converted_data['co2emissions'],
                'ip_address': ip
            })

        # Sort and get the top 5 devices
        top_devices = sorted(top_devices, key=lambda x: x['pcr'], reverse=True)[:5]
        return top_devices


    def get_24hrack_power(self,apic_ips, rack_id,start_date: datetime, end_date: datetime, duration_str: str)-> List[dict]:
        apic_ip_list = [ip[0] for ip in apic_ips if ip[0]]
        print(apic_ip_list)
        if not apic_ip_list:
            return []
        start_time = start_date.isoformat() + 'Z'
        end_time = end_date.isoformat() + 'Z'

        # Define the aggregate window and time format based on the duration string
        if duration_str in ["24 hours"]:
            aggregate_window = "1h"
            time_format = '%Y-%m-%d %H:00'
        elif duration_str in ["7 Days", "Current Month", "Last Month"]:
            aggregate_window = "1d"
            time_format = '%Y-%m-%d'
        else:  # For "last 6 months", "last year", "current year",
            aggregate_window = "1m"
            time_format = '%Y-%m'


        rack_data = []
        total_drawn, total_supplied = 0, 0

        for apic_ip in apic_ip_list:
            print(apic_ip)
            query = f'''from(bucket: "Dcs_db")
                  |> range(start: {start_time}, stop: {end_time})
                  |> filter(fn: (r) => r["_measurement"] == "DevicePSU")
                  |> filter(fn: (r) => r["ApicController_IP"] == "{apic_ip}")
                  |> sum()
                  |> yield(name: "total_sum")'''
            try:
                result = self.query_api.query(query)

                drawnAvg, suppliedAvg = None, None

                for table in result:
                    for record in table.records:
                        if record.get_field() == "total_POut":
                            drawnAvg = record.get_value()
                        elif record.get_field() == "total_PIn":
                            suppliedAvg = record.get_value()

                        if drawnAvg is not None and suppliedAvg is not None:
                            total_drawn += drawnAvg
                            total_supplied += suppliedAvg

                power_utilization = None
                pue = None
                if total_supplied > 0:
                    power_utilization = (total_drawn / total_supplied)
                if total_drawn > 0:
                    pue = ((total_supplied / total_drawn) - 1)

                rack_data.append({
                    "rack_id": rack_id,
                    "power_utilization": round(power_utilization, 2) if power_utilization is not None else 0,
                    "power_input": total_supplied,
                    "power_output": total_drawn,
                    "pue": round(pue, 2) if pue is not None else 0,

                })

            except Exception as e:
                print(f"Error querying InfluxDB for {apic_ip}: {e}")

        return rack_data

    def get_24h_rack_datatraffic(self,apic_ips, rack_id,start_date,end_date, duration) -> List[dict]:
        apic_ip_list = [ip[0] for ip in apic_ips if ip[0]]
        print(apic_ip_list)
        if not apic_ip_list:
            return []
        start_time = start_date.isoformat() + 'Z'
        end_time = end_date.isoformat() + 'Z'

        # Define the aggregate window and time format based on the duration string
        if duration in ["24 hours"]:
            aggregate_window = "1h"
            time_format = '%Y-%m-%d %H:00'
        elif duration in ["7 Days", "Current Month", "Last Month"]:
            aggregate_window = "1d"
            time_format = '%Y-%m-%d'
        else:  # For "last 6 months", "last year", "current year",
            aggregate_window = "1m"
            time_format = '%Y-%m'
        start_range = "-24h"
        Traffic_rack_data = []
        total_byterate = 0

        for apic_ip in apic_ip_list:
            print(apic_ip)
            query = f'''from(bucket: "Dcs_db")
                  |> range(start: {start_time}, stop: {end_time})
                  |> filter(fn: (r) => r["_measurement"] == "DeviceEngreeTraffic")
                  |> filter(fn: (r) => r["ApicController_IP"] == "{apic_ip}")
                  |> sum()
                  |> yield(name: "total_sum")'''
            try:
                result = self.query_api.query(query)
                byterate = None

                for table in result:
                    for record in table.records:
                        if record.get_field() == "total_bytesRateLast":
                            byterate = record.get_value()
                        else:
                            byterate = 0
                        total_byterate += byterate
                print(total_byterate, "total_bytesRateLast")

                Traffic_rack_data.append({
                    "rack_id": rack_id,
                    "traffic_through": total_byterate})
            except Exception as e:
                print(f"Error querying InfluxDB for {apic_ip}: {e}")

        return Traffic_rack_data
    def get_energy_consumption_metrics_with_filter17(self, device_ips: List[str], start_date: datetime,
                                                     end_date: datetime, duration_str: str) -> List[dict]:
        total_power_metrics = []
        start_time = start_date.isoformat() + 'Z'
        end_time = end_date.isoformat() + 'Z'

        print(f"Start Time: {start_time}, End Time: {end_time}", file=sys.stderr)

        # Define the aggregate window and time format based on the duration string
        if duration_str in ["24 hours"]:
            aggregate_window = "1h"
            time_format = '%Y-%m-%d %H:00'
        elif duration_str in ["7 Days", "Current Month", "Last Month"]:
            aggregate_window = "1d"
            time_format = '%Y-%m-%d'
        else:  # For "last 6 months", "last year", "current year"
            aggregate_window = "1m"
            time_format = '%Y-%m'
        powerin,powerout=0,0
        total_pout, total_pin=0,0

        for ip in device_ips:
            print(f"Querying metrics for IP: {ip}", file=sys.stderr)
            query = f'''
                           from(bucket: "{self.bucket}")
                           |> range(start: {start_time}, stop: {end_time})
                           |> filter(fn: (r) => r["_measurement"] == "DevicePSU" and r["ApicController_IP"] == "{ip}")
                           |> filter(fn: (r) => r["_field"] == "total_PIn" or r["_field"] == "total_POut")
                           |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
                           |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                       '''

            result = self.query_api.query(query)

            # Proper way to check for empty results
            # if not result or len(result) == 0:
            #     print("No results returned from InfluxDB query")



            metrics = []


            # Process each table in the result
            for table in result:
                for record in table.records:
                    # Get values with proper null checks
                    pin = record.values.get("total_PIn", 0) or 0
                    pout = record.values.get("total_POut", 0) or 0

                    total_pin += pin
                    total_pout += pout
        print(total_pin)

        energy_consumption = (total_pout / total_pin)  if total_pin > 0 else 0
        power_efficiency = (total_pin / total_pout) if total_pout > 0 else 0
        total_power_metrics.append({
                            "energy_consumption": round(energy_consumption, 2),
                            "total_POut_kw": round(total_pout/1000, 2),
                            "total_PIn_kw": round(total_pin/1000, 2),
                            "power_efficiency": round(power_efficiency, 2)
                        })
        print(total_pin,total_pout)


        df = pd.DataFrame(total_power_metrics).to_dict(orient='records')
        print(df)
        print(f"Final metrics: {df}", file=sys.stderr)
        return df

