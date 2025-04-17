from concurrent.futures import ThreadPoolExecutor
from power_data.power import PowerData
import pandas as pd

from report.test_inter import CreativeEnergyReport

class GenerateReport:
    def __init__(self):
        self.power = PowerData()
        self.powerreport = CreativeEnergyReport()

    def get_results(self, site_id, duration,site_name,filename):

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks to be executed concurrently
            # future_pie_data = executor.submit(self.power.calculate_total_power_consumption, site_id, duration)
            # future_carbon_emission = executor.submit(self.power.calculate_carbon_emission, site_id, duration)
            future_energy_data = executor.submit(self.power.calculate_energy_consumption_by_id_with_filter, site_id,
                                                 duration)
            future_cards_data = executor.submit(self.power.get_device_inventory, site_id)
            future_top_devices = executor.submit(self.power.get_top_5_power_devices_with_filter, site_id, duration)

            future_rack_data = executor.submit(self.power.get_all_racks, site_id,duration)


            # Retrieve results from the futures
            # pie_data = future_pie_data.result()
            # carbon_emission = future_carbon_emission.result()
            energy_data = future_energy_data.result()
            cards_data = future_cards_data.result()
            top_devices,bottom_devices = future_top_devices.result()
            top_racks=future_rack_data.result()
            # future_bottom_devices=future_bottom_devices.result()

            print("Top",top_racks)

        self.powerreport.generate_report(energy_data,cards_data,site_name,duration,top_devices,bottom_devices,top_racks,filename)
            # self.powerreport.create_pdf()


        return  True
