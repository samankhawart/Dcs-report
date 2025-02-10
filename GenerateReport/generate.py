from concurrent.futures import ThreadPoolExecutor
from power_data.power import PowerData
import pandas as pd

from report.Pue import CreativeEnergyReport

class GenerateReport:
    def __init__(self):
        self.power = PowerData()
        self.powerreport = CreativeEnergyReport()

    def get_results(self, site_id, duration,site_name,filename):

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks to be executed concurrently
            # future_pie_data = executor.submit(self.power.calculate_total_power_consumption, site_id, duration)
            # future_carbon_emission = executor.submit(self.power.calculate_carbon_emission, site_id, duration)
            future_energy_data = executor.submit(self.power.calculate_energy_consumption_by_id_with_filter, site_id,
                                                 duration)
            future_cards_data = executor.submit(self.power.get_device_inventory, site_id)
            future_top_devices = executor.submit(self.power.get_top_5_power_devices_with_filter, site_id, duration)

            # Retrieve results from the futures
            # pie_data = future_pie_data.result()
            # carbon_emission = future_carbon_emission.result()
            energy_data = future_energy_data.result()
            cards_data = future_cards_data.result()
            top_devices = future_top_devices.result()

        # # Print results for debugging
        # print("\n================================")
        # print("Power Consumption:")
        # print(pie_data)
        #
        # print("\n***********************************")
        # print("Carbon Emission:")
        # print(carbon_emission)

        print("\n***********************************")
        print("Energy Consumption Data:")
        print(energy_data)

        print("\n***********************************")
        print("Device Inventory (Cards Data):")
        print(cards_data)

        print("\n***********************************")
        print("Top 5 Power Devices:")
        print(top_devices)

        # Combine all data in a dictionary for further use
        results = {

            "energy_data": energy_data,
            "device_inventory": cards_data,
            "top_power_devices": top_devices
        }




        self.powerreport.generate_report(energy_data,cards_data,site_name,duration,top_devices,filename)
            # self.powerreport.create_pdf()

        return  True
