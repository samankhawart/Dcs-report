
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
# import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class CreativeEnergyReport:
    def __init__(self):
        self.filename = ''
        self.styles = getSampleStyleSheet()
        self.prepare_styles()

    def prepare_styles(self):
        self.title_style = ParagraphStyle(name='Title', parent=self.styles['Heading1'], fontSize=18, alignment=1, spaceAfter=20)
        self.header_style = ParagraphStyle(name='Header', parent=self.styles['Heading2'], fontSize=14, alignment=0, spaceAfter=10)
        self.stat_style = ParagraphStyle(name='Stat', parent=self.styles['Title'], fontSize=28,  alignment=0)
        self.desc_style = ParagraphStyle(name='Description', parent=self.styles['BodyText'], fontSize=12, alignment=4)
        self.footer_style = ParagraphStyle(name='Footer', parent=self.styles['Normal'], fontSize=10, alignment=1, textColor=colors.HexColor('#808080'))


    def generate_report(self, powerdata, summary_cards, site_name, duration,top_devices,bottom_devices,rack_details,filenames):
        self.filename=filenames
        self.data = pd.DataFrame(powerdata)
        self.data['time'] = pd.to_datetime(self.data['time'])
        # Calculate Performance Score
        avg_eer = self.data['energy_efficiency'].mean()
        avg_pue = self.data['power_efficiency'].mean()
        performance_score = (avg_eer / avg_pue) * 100
        performance_summary = "The data center has demonstrated optimal energy efficiency with minimal wastage." if performance_score >= 75 else "The data center is operating at moderate efficiency, with room for improvements." if performance_score >= 50 else "The data center requires significant optimization efforts to improve efficiency."

        # Identify Zero Data Points
        zero_data_points = self.data[(self.data['power_efficiency'] == 0) | (self.data['energy_efficiency'] == 0)]

        # Generate charts and gauges
        self.create_gauge(self.data['power_efficiency'].mean(), 4, 'Power Usage Effectiveness', 'PUE')
        self.create_gauge(self.data['energy_efficiency'].mean(), 2, 'Energy Efficiency Ratio', 'EER')
        self.generate_eer_graph()
        self.generate_pue_graph()

        # Create PDF Document
        doc = SimpleDocTemplate(self.filename, pagesize=letter)
        elements = []

        # Cover Page
        elements.append(Paragraph(f"Energy Consumption Report for {site_name}", self.title_style))
        elements.append(Paragraph(f"Reporting Period: {duration}", self.header_style))
        elements.append(Spacer(1, 20))

        intro = Paragraph(
            f"This comprehensive report provides detailed insights into the energy consumption patterns and efficiency metrics for <b>{site_name}</b>. The data covers the specified reporting period, highlighting key performance indicators and offering actionable insights.",
            self.desc_style)
        elements.append(intro)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(performance_summary, self.desc_style))

        # Summary Section
        elements.append(Paragraph(f"Energy Consumption Report Summary for {site_name}", self.header_style))
        elements.append(Paragraph(f"Overall Performance Score: {performance_score:.2f}", self.desc_style))
        # elements.append(Paragraph("<b>Summary of Key Metrics</b>", self.header_style))
        # self.add_summary_table(elements, summary_cards)
        # Top Devices Utilization Section
        elements.append(Paragraph("<b>Top 5 Devices Utilization</b>", self.header_style))
        elements.append(Paragraph(
            "The table below highlights the top devices based on their power consumption, bandwidth utilization, and overall efficiency metrics. These devices play a critical role in the site's energy consumption profile, and understanding their performance can help identify areas for optimization and efficiency improvements.",
            self.desc_style))
        print("good tile hhere")
        elements.append(Spacer(1, 20))
        self.add_top_devices_table(elements, top_devices)



        # Top Devices Utilization Section
        elements.append(Paragraph("<b>Bottom 5 Devices Utilization</b>", self.header_style))
        elements.append(Paragraph(
            "The table below highlights the bottom devices based on their power consumption, bandwidth utilization, and overall efficiency metrics. These devices play a critical role in the site's energy consumption profile, and understanding their performance can help identify areas for optimization and efficiency improvements.",
            self.desc_style))
        print("good tile hhere")
        elements.append(Spacer(1, 20))
        self.add_top_devices_table(elements, bottom_devices)

        elements.append(Spacer(1, 90))


        # Average Metrics Gauges
        avg_eer = self.data['energy_efficiency'].mean()
        avg_pue = self.data['power_efficiency'].mean()
        elements.append(Paragraph("<b>Average Energy Efficiency Metrics</b>", self.header_style))
        elements.append(Spacer(1, 10))
        elements.append(self.create_image_table(["PUE.png", "EER.png"]))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("The above gauges represent the average Power Usage Effectiveness (PUE) and Energy Efficiency Ratio (EER) for the reporting period. These metrics are crucial indicators of overall site performance.", self.desc_style))
        elements.append(Spacer(1, 20))



        # Energy Efficiency Analysis
        elements.append(Paragraph("<b>Energy Efficiency Over Time</b>", self.header_style))
        elements.append(Paragraph("The Energy Efficiency Ratio (EER) indicates the ratio of cooling output to the electrical energy input. Higher EER values signify better energy efficiency. Below is the trend of EER over the reporting period:", self.desc_style))
        elements.append(Spacer(1, 10))
        elements.append(Image("eer_chart.png", width=400, height=200))
        elements.append(Spacer(1, 20))

        # EER Conclusion
        underperforming_points = self.data[self.data['energy_efficiency'] < 0.5]
        if not underperforming_points.empty:
            elements.append(Paragraph(
                f"Several data points showed low energy efficiency (EER < 0.5). Notable underperforming periods include:",
                self.desc_style))
            for _, row in underperforming_points.iterrows():
                elements.append(Paragraph(
                    f"-{row['time'].strftime('%Y-%m-%d %H:%M')} with an EER of {row['energy_efficiency']:.2f}",
                    self.desc_style))
        else:
            elements.append(Paragraph("No significant periods of low energy efficiency detected.", self.desc_style))
        eer_conclusion = "high energy efficiency throughout the period." if avg_eer >= 1.5 else "moderate energy efficiency with potential for improvement." if avg_eer >= 0.5 else "low energy efficiency, requiring significant optimization efforts."
        elements.append(Paragraph(f"The average EER of <font color='#1B98E0'>{avg_eer:.2f}</font> indicates <b><font color='#1B98E0'>{eer_conclusion}</font></b>", self.desc_style))

        # Power Utilization Analysis
        elements.append(Paragraph("<b>Power Utilization Over Time</b>", self.header_style))
        elements.append(Paragraph("Power Usage Effectiveness (PUE) measures the total energy consumption compared to the energy used solely by IT equipment. Lower PUE values represent more efficient energy use. The graph below shows the PUE trend over the reporting period:", self.desc_style))
        elements.append(Spacer(1, 10))
        elements.append(Image("pue_chart.png", width=400, height=200))
        elements.append(Spacer(1, 20))

        # PUE Conclusion
        underperforming_pue_points = self.data[self.data['power_efficiency'] > 2.0]
        if not underperforming_pue_points.empty:
            elements.append(Paragraph(
                f"Several data points showed poor power efficiency (PUE > 2.0). Notable underperforming periods include:",
                self.desc_style))
            for _, row in underperforming_pue_points.iterrows():
                elements.append(
                    Paragraph(f"- {row['time'].strftime('%Y-%m-%d %H:%M')} with a PUE of {row['power_efficiency']:.2f}",
                              self.desc_style))
        else:
            elements.append(Paragraph("No significant periods of poor power efficiency detected.", self.desc_style))

        pue_conclusion = "excellent energy efficiency." if avg_pue <= 1.5 else "moderate efficiency with room for improvement." if avg_pue <= 2.0 else "inefficient performance, necessitating immediate action."
        elements.append(Paragraph(f"<b>Conclusion:</b> The average PUE of <font color='#1678B5'>{avg_pue:.2f}</font> indicates <b><font color='#1678B5'>{pue_conclusion}</font></b>", self.desc_style))


        # Racks Utilization
        elements.append(Paragraph(f"<b>{site_name}'s Rack  wise Utilization</b>", self.header_style))
        elements.append(Paragraph(
            "The following table provides an overview of rack performance, showcasing power consumption, bandwidth utilization, and efficiency metrics. Understanding these parameters helps in identifying optimization opportunities and enhancing overall operational efficiency.",  self.desc_style))

        elements.append(Spacer(1, 20))
        self.add_rack_table(elements, rack_details)




        # Final Conclusion
        overall_conclusion = "The site has demonstrated optimal performance across the board." if avg_eer >= 0.5 else "There are noticeable inefficiencies that should be addressed to improve overall performance."
        elements.append(Paragraph(f"<b>Overall Conclusion:</b> <font color='#003366'>{overall_conclusion}</font>", self.header_style))
        elements.append(Spacer(1, 20))

        # Footer
        elements.append(Paragraph("Generated by <font color='#00509E'>Nets International</font> | 2025", self.footer_style))

        # Build PDF
        doc.build(elements)
        print(f"Report generated successfully: {self.filename}")

    def add_summary_table(self, elements, summary_cards):
        headers = [key.replace('_', ' ').title() for key in summary_cards.keys()]
        values = [str(value) for value in summary_cards.values()]

        data = [headers, values]
        table = Table(data, colWidths=[120, 120, 120])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#448c35')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#9cc993')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.white)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

    def create_image_table(self, image_paths):
        images = [Image(img, width=200, height=120) for img in image_paths]
        return Table([images], colWidths=[200, 200])

    def create_gauge(self, value, max_value, title, filename):
        color = '#448c35' if value <= 1.5 else '#1678b5' if value <= 2.0 else '#f5113b'
        fig, ax = plt.subplots(figsize=(4, 3), subplot_kw={'projection': 'polar'})
        ax.set_theta_offset(np.pi)
        ax.set_theta_direction(-1)
        ax.set_axis_off()
        angle = np.pi * (value / max_value)
        ax.barh(1, angle, left=0, height=0.3, color=color)
        ax.barh(1, np.pi - angle, left=angle, height=0.3, color='lightgrey')
        ax.text(0, 0, f'{value:.2f}', ha='center', va='center', fontsize=18, fontweight='bold')
        plt.title(title, fontsize=12, color='grey', pad=15)
        plt.savefig(f"{filename}.png")
        plt.close()

    def generate_eer_graph(self):
        self.generate_line_chart(self.data['time'], self.data['energy_efficiency'], 'EER', 'Energy Efficiency Over Time', 'eer_chart.png', 'tab:blue')

    def generate_pue_graph(self):
        self.generate_line_chart(self.data['time'], self.data['power_efficiency'], 'PUE', 'Power Usage Effectiveness Over Time', 'pue_chart.png', 'tab:green')

    def generate_line_chart(self, time_series, values, ylabel, title, filename, color):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_xlabel("Time")
        ax.set_ylabel(f"{ylabel} Ratio", color=color)
        ax.plot(time_series, values, marker='o', color=color)
        ax.tick_params(axis='y', labelcolor=color)
        ax.set_ylim(0, 2)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()

        plt.title(title)
        plt.tight_layout()
        plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
        plt.savefig(filename, dpi=300)
        plt.close()

    def add_top_devices_table(self, elements, top_devices):
        # 'data' should be your original JSON
        headers = ["Device Name","IP Address", "Total Power", "Traffic Speed", "PCR",
                   "CO2 Emissions"]
        print(headers)
        data = [headers] + [[
            device['device_name'],
            device['ip_address'],
            device['total_power'],
            device['traffic_speed'],
            device['pcr'],
            device['co2emmissions'],
        ] for device in top_devices]
        print("also good till here")

        table = Table(data, colWidths=[130, 70, 80, 80, 70, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#448c35')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        # Alternate row colors
        for i in range(1, len(data)):
            bg_color = colors.HexColor('#9cc993') if i % 2 == 0 else colors.white
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), bg_color)
            ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

    def add_rack_table(self, elements, racks):
        headers = ["Rack Name", "Building", "Site Name", "Number of Devices", "EER", "PUE",
                   "Power Input (kW)", "Data Traffic (GB)","PCR"]
        data = [headers] + [[
            rack["Rack Name"],
            rack["Building"],
            rack["Site Name"],
            rack["Number of Devices"],
            rack["EER"],
            rack["PUE"],
            rack["Power Input (kW)"],
            rack["Data Traffic (GB)"],
            rack["PCR"]

        ] for rack in racks]
        # col_widths = []  # Adjusted column widths
        table = Table(data, colWidths=[80, 60, 70, 50, 50, 50, 70, 70, 50])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#448c35')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        for i in range(1, len(data)):
            bg_color = colors.HexColor('#9cc993') if i % 2 == 0 else colors.white
            table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), bg_color)]))

        elements.append(table)
        elements.append(Spacer(1, 20))