
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class CreativeEnergyReport:
    def __init__(self, filename="saved_reports/Creative_Energy_Report4.pdf"):
        self.filename = filename
        self.styles = getSampleStyleSheet()
        self.prepare_styles()

    def prepare_styles(self):
        # Define styles with light grey text
        self.title_style = ParagraphStyle(
            name='Title',
            parent=self.styles['Heading1'],
            fontSize=18,
            alignment=1,
            spaceAfter=20,
            textColor=colors.HexColor('#003366')  # Fixed: Added missing closing parenthesis
        )
        self.header_style = ParagraphStyle(
            name='Header',
            parent=self.styles['Heading2'],
            fontSize=14,
            alignment=0,
            spaceAfter=10,
            textColor=colors.HexColor('#003366')
        )
        self.stat_style = ParagraphStyle(
            name='Stat',
            parent=self.styles['Title'],
            fontSize=28,
            alignment=0,
            textColor=colors.HexColor('#003366')
        )
        self.desc_style = ParagraphStyle(
            name='Description',
            parent=self.styles['BodyText'],
            fontSize=12,
            alignment=4,
            textColor=colors.HexColor('#555555')
        )
        self.footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=1,
            textColor=colors.HexColor('#808080')
        )
        self.link_style = ParagraphStyle(
            name='Link',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=0,
            textColor=colors.HexColor('#1B98E0'),
            underline=1
        )

    def generate_report(self, powerdata, summary_cards, site_name, duration, top_devices):
        self.data = pd.DataFrame(powerdata)
        self.data['time'] = pd.to_datetime(self.data['time'])

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

        # Summary Section
        elements.append(Paragraph("<b>Summary of Key Metrics</b>", self.header_style))
        self.add_summary_table(elements, summary_cards)

        # Top Devices Utilization Section
        elements.append(Paragraph("<b>Top Devices Utilization</b>", self.header_style))
        elements.append(Paragraph(
            "The table below highlights the top devices based on their power consumption, bandwidth utilization, and overall efficiency metrics. These devices play a critical role in the site's energy consumption profile, and understanding their performance can help identify areas for optimization and efficiency improvements.",
            self.desc_style))
        elements.append(Spacer(1, 20))
        self.add_top_devices_table(elements, top_devices)

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
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),  # Dark blue header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#D3D3D3')),  # Light grey for values
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.white)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

    def add_top_devices_table(self, elements, top_devices):
        top_devices = top_devices.get("top_devices", [])
        headers = ["Device Name", "IP Address", "Total Power", "Traffic Speed", "PCR", "CO2 Emissions"]
        data = [headers] + [[
            device['device_name'],
            device['ip_address'],
            device['total_power'],
            device['traffic_speed'],
            device['pcr'],
            device['co2emmissions'],
        ] for device in top_devices]

        table = Table(data, colWidths=[130, 70, 80, 80, 70, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),  # Dark blue header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        # Alternate row colors
        for i in range(1, len(data)):
            bg_color = colors.HexColor('#D3D3D3') if i % 2 == 0 else colors.white  # Light grey and white
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), bg_color)
            ]))

        elements.append(table)
        elements.append(Spacer(1, 20))
