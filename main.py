import logging
import os
import time

from dotenv import load_dotenv

from Database.db_connector import DBConnection
from Models.model import Reports, Site
from GenerateReport.PueData import PueData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ReportData.log',
    filemode='a'
)
load_dotenv()
report_dir = os.getenv('dir_path')
logging.info(f"directory already exists at: {report_dir}")

class Reporting:
    def __init__(self):
        self.db_connection = DBConnection()
        self.generate_report = PueData()

    def get_pending_reports(self):
        report_result=0
        with self.db_connection.session_scope() as session:
            logging.info("Retrieving pending reports")
            try:
                reports_path = os.path.join(report_dir, "reports")
                if not os.path.exists(reports_path):
                    os.makedirs(reports_path)
                    logging.info(f"'reports' directory created at: {reports_path}")
                else:
                    logging.info(f"'reports' directory already exists at: {reports_path}")
                results = []
                pending_reports = session.query(Reports).filter(Reports.Status == False).all()
                if pending_reports:
                    for report in pending_reports:
                        site_id = report.site_id
                        report_id = report.id
                        duration = report.duration
                        report_type=report.report_type
                        print("repoert",report_type)
                        site_name = session.query(Site.site_name).filter(Site.id == site_id).first()[0]
                        clean_duration = duration.replace(" ", "_").replace(":", "-")
                        file_name = f"report_{report_id}_{clean_duration}.pdf"
                        file_path = os.path.join(reports_path, file_name)

                        print(file_path)
                        logging.info(f"Processing report ID {report.id} with site_id {site_id} and duration {duration}")
                        if report_type in ('Energy Consumption Report', 'PUE Report'):
                            print(report_type)
                            report_result = self.generate_report.get_results(report,site_name, file_path)


                        if report_result:
                            report.path = file_name  # Save only the filename in the database
                            report.Status = True  # Mark the report as processed
                            report.message="Report Generated Successfully"
                            session.commit()  # Commit changes to the database
                            logging.info(f"Report ID {report_id} saved successfully at '{file_name}'")
                        else:
                            logging.warning(f"Report ID {report_id} generation failed.")
                    else:
                        print("No report is pending to generated")
                        # results.append(report_result)

            except Exception as e:
                logging.error(f"An error occurred while fetching pending reports: {e}")
                return []

if __name__ == "__main__":
    reporting = Reporting()
    try:
        # while True:
            reporting.get_pending_reports()
            logging.info("Waiting 1 minutes before next check...")
            # time.sleep(60)  # Wait for 2 minutes
    except KeyboardInterrupt:
        logging.info("Report generation stopped by user.")
