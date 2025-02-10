import logging
import os
from dotenv import load_dotenv

from Database.db_connector import DBConnection
from Models.model import Reports, Site
from GenerateReport.generate import GenerateReport

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
        self.generate_report = GenerateReport()

    def get_pending_reports(self):
        with self.db_connection.session_scope() as session:
            logging.info("Retrieving pending reports")
            try:
                reports_path = os.path.join(report_dir, "reports")
                if not os.path.exists(reports_path):
                    os.makedirs(reports_path)
                    logging.info(f"'reports' directory created at: {reports_path}")
                else:
                    logging.info(f"'reports' directory already exists at: {reports_path}")

                pending_reports = session.query(Reports).filter(Reports.Status == False).all()
                results = []
                for report in pending_reports:
                    site_id = report.site_id
                    report_id = report.id
                    duration = report.duration
                    site_name =  session.query(Site.site_name).filter(Site.id == site_id).first()[0]
                    clean_duration = duration.replace(" ", "_").replace(":", "-")
                    file_name = f"report_{report_id}_{clean_duration}.pdf"
                    path = os.path.join(reports_path, file_name)
                    print(path)

                    logging.info(f"Processing report ID {report.id} with site_id {site_id} and duration {duration}")
                    report_result = self.generate_report.get_results(site_id, duration,site_name,path)
                    if report_result:
                        report.path = file_name  # Save only the filename in the database
                        report.Status = True  # Mark the report as processed
                        session.commit()  # Commit changes to the database
                        logging.info(f"Report ID {report_id} saved successfully at '{file_name}'")
                    else:
                        logging.warning(f"Report ID {report_id} generation failed.")



                    # results.append(report_result)


            except Exception as e:
                logging.error(f"An error occurred while fetching pending reports: {e}")
                return []

if __name__ == "__main__":
    reporting = Reporting()
    pending_reports = reporting.get_pending_reports()
