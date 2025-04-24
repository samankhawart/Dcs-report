from concurrent.futures import ThreadPoolExecutor
from power_data.power import PowerData
import numpy as np
import pandas as pd

from report.Pue import CreativeEnergyReport

class GenerateReport:
    def __init__(self):
        self.power = PowerData()
        self.powerreport = CreativeEnergyReport()

    def get_results(self, site_id, duration,site_name,filename):

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks to be executed concurrently
            # future_pie_data = executor.submit(self.power.calculate_total_power_consumption, site_id, duration)
            # future_carbon_emission = executor.submit(self.power.calculate_carbon_emission, site_id, duration)

            #
            #
            # future_energy_data = executor.submit(self.power.calculate_energy_consumption_by_id_with_filter, site_id,
            #                                      duration)
            # future_cards_data = executor.submit(self.power.get_device_inventory, site_id)
            # future_top_devices = executor.submit(self.power.get_top_5_power_devices_with_filter, site_id, duration)
            #
            # future_rack_data = executor.submit(self.power.get_all_racks, site_id,duration)
            #

            # Retrieve results from the futures
            # pie_data = future_pie_data.result()
            # carbon_emission = future_carbon_emission.result()
            # energy_data = future_energy_data.result()
            # cards_data = future_cards_data.result()
            # top_devices,bottom_devices = future_top_devices.result()
            # top_racks=future_rack_data.result()
            # print("Top", top_racks)
            # print("energy_data", energy_data)
            # print("cards_data",cards_data)
            # print("top_devices",top_devices)
            # print("bottom_devices",bottom_devices)
            energy_data=[{'time': '2025-04-22 22:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0, 'power_efficiency': 0.0}, {'time': '2025-04-22 23:00', 'energy_efficiency':0.0, 'total_POut': 0.0, 'total_PIn': 0.0, 'power_efficiency': 0.0}, {'time': '2025-04-23 00:00', 'energy_efficiency': 0.93, 'total_POut': 174.0, 'total_PIn': 187.0, 'power_efficiency': 1.07}, {'time': '2025-04-23 01:00', 'energy_efficiency': 0.92, 'total_POut': 174.5, 'total_PIn': 190.5, 'power_efficiency': 1.09}, {'time': '2025-04-23 02:00', 'energy_efficiency': 0.85, 'total_POut': 171.0, 'total_PIn': 200.0, 'power_efficiency': 1.17}, {'time': '2025-04-23 03:00', 'energy_efficiency': 0.86, 'total_POut': 169.5, 'total_PIn': 198.0, 'power_efficiency': 1.17}, {'time': '2025-04-23 04:00', 'energy_efficiency': 0.87, 'total_POut': 171.0, 'total_PIn': 197.5, 'power_efficiency': 1.15}, {'time': '2025-04-23 05:00', 'energy_efficiency': 0.93, 'total_POut': 170.5, 'total_PIn': 183.5, 'power_efficiency': 1.08}, {'time': '2025-04-23 06:00', 'energy_efficiency': 0.9, 'total_POut': 171.0, 'total_PIn'
                : 190.5, 'power_efficiency': 1.11}, {'time': '2025-04-23 07:00', 'energy_efficiency': 0.82, 'total_POut': 163.0, 'total_PIn': 199.0, 'power_efficiency': 1.22}, {'time': '2025-04-23 08:00', 'energy_efficiency': 0.93, 'total_POut': 179.0, 'total_PIn': 193.0, 'power_efficiency': 1.08}, {'time': '2025-04-23 09:00', 'energy_efficiency': 0.84, 'total_POut': 164.0,
                 'total_PIn': 194.5, 'power_efficiency': 1.19}, {'time': '2025-04-23 10:00', 'energy_efficiency': 0.91, 'total_POut': 173.0, 'total_PIn': 190.0, 'power_efficiency': 1.1}, {'time':
                '2025-04-23 11:00', 'energy_efficiency': 0.92, 'total_POut': 169.0, 'total_PIn': 184.0, 'power_efficiency': 1.09}, {'time': '2025-04-23 12:00', 'energy_efficiency': 0.89, 'total_POut': 174.0, 'total_PIn': 195.5, 'power_efficiency': 1.12}, {'time': '2025-04-23 13:00', 'energy_efficiency': 0.81, 'total_POut': 164.5, 'total_PIn': 202.0, 'power_efficiency': 1.23
                }, {'time': '2025-04-23 14:00', 'energy_efficiency': 0.86, 'total_POut': 173.0, 'total_PIn': 200.5, 'power_efficiency': 1.16}, {'time': '2025-04-23 15:00', 'energy_efficiency': 0.94, 'total_POut': 174.5, 'total_PIn': 185.5, 'power_efficiency': 1.06}, {'time': '2025-04-23 16:00', 'energy_efficiency': 0.91, 'total_POut': 176.5, 'total_PIn': 193.5, 'power_efficiency': 1.1}, {'time': '2025-04-23 17:00', 'energy_efficiency': 0.87, 'total_POut': 171.0, 'total_PIn': 195.5, 'power_efficiency': 1.14}, {'time': '2025-04-23 18:00', 'energy_efficiency': 0.84, 'total_POut': 163.0, 'total_PIn': 193.5, 'power_efficiency': 1.19}, {'time': '2025-04-23 19:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0, 'power_efficiency': 0.0}, {'time': '2025-04-23 20:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0, 'power_efficiency': 0.0}, {'time': '2025-04-23 21:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0, 'power_efficiency': 0.0}, {'time': '2025-04-23 22:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0, 'power_efficiency': 0.0}]

            cards_data={'onboarded_devices': 20, 'total_devices': 21, 'total_vendors': 2, 'total_racks': 1,'total_energy_consumption':56050}
            top_devices=[
            {'id': 1369, 'device_name': 'SULY-ELEF-CI-COM-415', 'total_power': '7.37 kW', 'total_bandwidth': '4.81 GPS',
             'traffic_speed': '786.08 GPS', 'bandwidth_utilization': '16344.31 ', 'pcr': np.float64(0.0094), 'co2emmissions': '2.98 kgs', 'ip_address': '172.8.160.70'}, {'id': 1370, 'device_name': 'SULY - ELEF - CI - COM - 304', 'total_power': '7.37 kW', 'total_bandwidth': '4.22 GPS', 'traffic_speed': '926.83 GPS', 'bandwidth_utilization': '21969.6 ', 'pcr': np.float64(0.008), 'co2emmissions': '2.98 kgs', 'ip_address': '172.8.144.81'},
             {'id': 1505, 'device_name': 'R_384', 'total_power': '7.36 kW', 'total_bandwidth': '4.54 GPS',
              'traffic_speed': '1018.69 GPS', 'bandwidth_utilization': '22417.49 ', 'pcr': np.float64(0.0072), 'co2emmissions': '2.98 kgs', 'ip_address': '169.254.2.2'}, {'id': 1346,
                                                                                      'device_name': 'SULY-ELEF-CI-COM-302',
                                                                                      'total_power': '7.35 kW',
                                                                                      'total_bandwidth': '6.26 GPS',
                                                                                      'traffic_speed': '1021.5 GPS',
                                                                                      'bandwidth_utilization': '16310.11 ',
                                                                                      'pcr': np.float64(0.0072),
                                                                                      'co2emmissions': '2.97 kgs',
                                                                                      'ip_address': '172.8.144.83'}, {'id': 1376, 'device_name': 'SULY - ELEF - CI - COM - 432', 'total_power': '7.34 kW', 'total_bandwidth': '5.13 GPS',
                                                                                                                      'traffic_speed': '1136.27 GPS', 'bandwidth_utilization': '22162.8 ', 'pcr': np.float64(0.0065), 'co2emmissions': '2.96 kgs',
                                                                                                                      'ip_address': '172.8.160.75'}]
            bottom_devices= [{'id': 1386, 'device_name': 'SULY-ELEF-CI-COM-429', 'total_power': '7.31 kW', 'total_bandwidth': '5.65 GPS', 'traffic_speed': '1069.12 GPS', 'bandwidth_utilization'
                : '18935.67 ', 'pcr': np.float64(0.0068), 'co2emmissions': '2.95 kgs', 'ip_address': '172.8.16.66'}, {'id': 1394, 'device_name': 'SULY-ELEF-CI-COM-402', 'total_power': '7.31 kW', 'total_bandwidth': '6.42 GPS', 'traffic_speed': '823.24 GPS', 'bandwidth_utilization': '12814.41 ', 'pcr': np.float64(0.0089), 'co2emmissions': '2.95 kgs', 'ip_address': '172.8.144.79'}, {'id': 1501, 'device_name': 'R_167_SW_01', 'total_power': '7.29 kW', 'total_bandwidth': '5.15 GPS', 'traffic_speed': '891.14 GPS', 'bandwidth_utilization': '17301.83 ', 'pcr'
                : np.float64(0.0082), 'co2emmissions': '2.95 kgs', 'ip_address': '10.200.97.72'}, {'id': 1374, 'device_name': 'SULY-ELEF-CI-COM-403', 'total_power': '7.27 kW', 'total_bandwidth': '6.36 GPS', 'traffic_speed': '969.19 GPS', 'bandwidth_utilization': '15248.56 ', 'pcr': np.float64(0.0075), 'co2emmissions': '2.94 kgs', 'ip_address': '172.8.144.77'}, {'id': 1397,
                'device_name': 'SULY-EAPC-CI-COM-003', 'total_power': '7.27 kW', 'total_bandwidth': '5.23 GPS', 'traffic_speed': '902.55 GPS', 'bandwidth_utilization': '17250.96 ', 'pcr': np.float64(0.0081), 'co2emmissions': '2.94 kgs', 'ip_address': '172.8.0.3'}]

            top_racks=[{'Rack Name': 'L0-AF-19', 'Building': None, 'Site Name': 'SULAY', 'Number of Devices': 21, 'EER': 0.88,
                 'PUE': 0.13, 'Power Input (kW)': 1391.9, 'Power Output(kW)': 1228.35, 'Data Traffic (GB)': 234383.22,
                 'Co2': 655.5849, 'PCR': 5.9386}]

            # future_bottom_devices=future_bottom_devices.result()



        self.powerreport.generate_report(energy_data,cards_data,site_name,duration,top_devices,bottom_devices,top_racks,filename)
            # self.powerreport.create_pdf()


        return  True
