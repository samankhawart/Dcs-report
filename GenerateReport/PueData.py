from concurrent.futures import ThreadPoolExecutor, as_completed
from power_data.power import PowerData
import logging
from report.pue_report import DynamicDCReportGenerator
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ReportData.log',
    filemode='a'
)


class PueData:
    def __init__(self):
        self.power = PowerData()
        self.powerreport = DynamicDCReportGenerator()

    def get_results(self, report, site_name, filename):
        duration = report.duration
        site_id = report.site_id
        logging.info(f"Generating report for {site_name}")

        try:
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Concurrent data fetching
                futures = {
                    "overall_consumption": executor.submit(
                        self.power.calculate_average_energy_consumption_by_site_id,
                        site_id, duration
                    ),
                    "inventory": executor.submit(
                        self.power.get_device_inventory,
                        site_id
                    ),
                    "top_devices": executor.submit(
                        self.power.get_top_5_power_devices_with_filter,
                        site_id, duration
                    ),
                    "bottom_devices": executor.submit(
                        self.power.get_top_5_power_devices_with_filter,
                        site_id, duration
                    ),
                    "racks": executor.submit(
                        self.power.get_all_racks,
                        site_id, duration
                    )
                }


                # Collect results
                results = {}
                for key, future in futures.items():
                    try:
                        results[key] = future.result()
                        logging.debug(f"Retrieved {key} data successfully")
                    except Exception as e:
                        logging.error(f"Failed to get {key}: {str(e)}")
                        results[key] = None
            print(results)


            # Validate critical data
            if not results["overall_consumption"]:
                raise ValueError("No  data available for report")
            if not results["inventory"]:
                logging.warning("No inventory data available")
            energy_data = [{'time': '2025-04-22 22:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0,
                            'power_efficiency': 0.0},
                           {'time': '2025-04-22 23:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0,
                            'power_efficiency': 0.0},
                           {'time': '2025-04-23 00:00', 'energy_efficiency': 0.93, 'total_POut': 174.0,
                            'total_PIn': 187.0, 'power_efficiency': 1.07},
                           {'time': '2025-04-23 01:00', 'energy_efficiency': 0.92, 'total_POut': 174.5,
                            'total_PIn': 190.5, 'power_efficiency': 1.09},
                           {'time': '2025-04-23 02:00', 'energy_efficiency': 0.85, 'total_POut': 171.0,
                            'total_PIn': 200.0, 'power_efficiency': 1.17},
                           {'time': '2025-04-23 03:00', 'energy_efficiency': 0.86, 'total_POut': 169.5,
                            'total_PIn': 198.0, 'power_efficiency': 1.17},
                           {'time': '2025-04-23 04:00', 'energy_efficiency': 0.87, 'total_POut': 171.0,
                            'total_PIn': 197.5, 'power_efficiency': 1.15},
                           {'time': '2025-04-23 05:00', 'energy_efficiency': 0.93, 'total_POut': 170.5,
                            'total_PIn': 183.5, 'power_efficiency': 1.08},
                           {'time': '2025-04-23 06:00', 'energy_efficiency': 0.9, 'total_POut': 171.0, 'total_PIn'
                           : 190.5, 'power_efficiency': 1.11},
                           {'time': '2025-04-23 07:00', 'energy_efficiency': 0.82, 'total_POut': 163.0,
                            'total_PIn': 199.0, 'power_efficiency': 1.22},
                           {'time': '2025-04-23 08:00', 'energy_efficiency': 0.93, 'total_POut': 179.0,
                            'total_PIn': 193.0, 'power_efficiency': 1.08},
                           {'time': '2025-04-23 09:00', 'energy_efficiency': 0.84, 'total_POut': 164.0,
                            'total_PIn': 194.5, 'power_efficiency': 1.19},
                           {'time': '2025-04-23 10:00', 'energy_efficiency': 0.91, 'total_POut': 173.0,
                            'total_PIn': 190.0, 'power_efficiency': 1.1}, {'time':
                                                                               '2025-04-23 11:00',
                                                                           'energy_efficiency': 0.92,
                                                                           'total_POut': 169.0, 'total_PIn': 184.0,
                                                                           'power_efficiency': 1.09},
                           {'time': '2025-04-23 12:00', 'energy_efficiency': 0.89, 'total_POut': 174.0,
                            'total_PIn': 195.5, 'power_efficiency': 1.12},
                           {'time': '2025-04-23 13:00', 'energy_efficiency': 0.81, 'total_POut': 164.5,
                            'total_PIn': 202.0, 'power_efficiency': 1.23
                            }, {'time': '2025-04-23 14:00', 'energy_efficiency': 0.86, 'total_POut': 173.0,
                                'total_PIn': 200.5, 'power_efficiency': 1.16},
                           {'time': '2025-04-23 15:00', 'energy_efficiency': 0.94, 'total_POut': 174.5,
                            'total_PIn': 185.5, 'power_efficiency': 1.06},
                           {'time': '2025-04-23 16:00', 'energy_efficiency': 0.91, 'total_POut': 176.5,
                            'total_PIn': 193.5, 'power_efficiency': 1.1},
                           {'time': '2025-04-23 17:00', 'energy_efficiency': 0.87, 'total_POut': 171.0,
                            'total_PIn': 195.5, 'power_efficiency': 1.14},
                           {'time': '2025-04-23 18:00', 'energy_efficiency': 0.84, 'total_POut': 163.0,
                            'total_PIn': 193.5, 'power_efficiency': 1.19},
                           {'time': '2025-04-23 19:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0,
                            'power_efficiency': 0.0},
                           {'time': '2025-04-23 20:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0,
                            'power_efficiency': 0.0},
                           {'time': '2025-04-23 21:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0,
                            'power_efficiency': 0.0},
                           {'time': '2025-04-23 22:00', 'energy_efficiency': 0.0, 'total_POut': 0.0, 'total_PIn': 0.0,
                            'power_efficiency': 0.0}]

            # Create input data dict for processing
            input_data = {
                "overall_consumption": results["overall_consumption"],
                "energy_data":energy_data,
                "inventory": results["inventory"] or {},
                "devices": {
                    "top": results["top_devices"] or [],
                    "bottom": results["bottom_devices"] or [],
                    "all": (results["top_devices"] or []) + (results["bottom_devices"] or [])
                },
                "racks": results["racks"] or [],
                "site_name": site_name,
                "duration": duration
            }

            # Generate the report
            self.powerreport.generate_report(input_data=input_data, output_file=filename)

        except Exception as e:
            logging.error(f"Report generation failed for {site_name}: {str(e)}")
            raise RuntimeError(f"Could not generate report: {str(e)}")

    # def get_results(self,report, site_name,filename):
    #     #site_name=report.site_name
    #     duration=report.duration
    #     site_id=report.site_id
    #     logging.info(f"{site_name} data fetching")
    #     results = {}
    #
    #     try:
    #         with ThreadPoolExecutor() as executor:
    #             futures = {
    #                 executor.submit(self.power.calculate_average_energy_consumption_by_site_id, site_id,
    #                                 duration): "consumption_details",
    #                 executor.submit(self.power.get_device_inventory, site_id): "card",
    #                 executor.submit(self.power.calculate_energy_consumption_by_id_with_filter, site_id,
    #                                                      duration) :"energy-effienciy",
    #                 future_cards_data = executor.submit(self.power.get_device_inventory, site_id)
    #                 future_top_devices = executor.submit(self.power.get_top_5_power_devices_with_filter, site_id, duration)
    #
    #                 future_rack_data = executor.submit(self.power.get_all_racks, site_id,duration)
    #             }
    #
    #             for future in as_completed(futures):
    #                 key = futures[future]
    #                 try:
    #                     results[key] = future.result()
    #                     logging.debug(f"Successfully retrieved {key} for {site_name}")
    #                 except Exception as e:
    #                     logging.error(f"Error retrieving {key} for {site_name}: {str(e)}")
    #                     results[key] = None
    #
    #         logging.info(f"Data retrieval completed for {site_name}")
    #         # logging.debug(f"Consumption details: {results.get('consumption_details')}")
    #         logging.debug(f"Card data: {results.get('card')}")
    #
    #         print(results)
    #         cards_data=results.get('card')
    #         consumption_details=results.get('consumption_details')
    #
    #
    #
    #         self.powerreport.generate_report(consumption_details, cards_data, site_name,top_devices,bottom_devices, top_racks,duration,  filename)
    #
    #
    #
    #     except Exception as e:
    #         logging.error(f"Error in get_results for {site_name}: {str(e)}")
    #         raise
    #
    #