
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
    def __init__(self):
        self.primary_color = '#003366'  # Dark blue
        self.secondary_color = '#1B98E0'  # Light blue
        self.accent_color = '#00509E'  # Medium blue
        self.text_color = '#555555'  # Dark grey
        self.styles = getSampleStyleSheet()
        self.prepare_styles()


    def prepare_styles(self):
        # Unified blue color scheme styles
        self.title_style = ParagraphStyle(
            name='Title',
            parent=self.styles['Heading1'],
            fontSize=22,
            alignment=1,
            spaceAfter=20,
            textColor=colors.HexColor(self.primary_color),
            fontName='Helvetica-Bold'
        )
        self.header_style = ParagraphStyle(
            name='Header',
            parent=self.styles['Heading2'],
            fontSize=16,
            alignment=0,
            spaceAfter=12,
            textColor=colors.HexColor(self.primary_color),
            fontName='Helvetica-Bold'
        )
        self.subheader_style = ParagraphStyle(
            name='Subheader',
            parent=self.styles['Heading3'],
            fontSize=14,
            alignment=0,
            spaceAfter=10,
            textColor=colors.HexColor(self.secondary_color),
            fontName='Helvetica-Bold'
        )
        self.stat_style = ParagraphStyle(
            name='Stat',
            parent=self.styles['Title'],
            fontSize=28,
            alignment=0,
            textColor=colors.HexColor(self.secondary_color),
            fontName='Helvetica-Bold'
        )
        self.desc_style = ParagraphStyle(
            name='Description',
            parent=self.styles['BodyText'],
            fontSize=12,
            alignment=4,
            textColor=colors.HexColor(self.text_color),
            leading=14
        )
        self.highlight_style = ParagraphStyle(
            name='Highlight',
            parent=self.styles['BodyText'],
            fontSize=12,
            alignment=4,
            textColor=colors.HexColor(self.secondary_color),
            backColor=colors.HexColor('#F0F8FF'),  # Very light blue
            borderPadding=(5, 5, 5, 5),
            leading=14
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
            textColor=colors.HexColor(self.secondary_color),
            underline=1
        )

    def generate_report(self, powerdata, summary_cards, site_name, duration, top_devices, bottom_devices, top_racks,
                        filename):
        self.data = pd.DataFrame(powerdata)
        self.data['time'] = pd.to_datetime(self.data['time'])

        # Generate charts and gauges
        self.create_gauge(self.data['power_efficiency'].mean(), 4, 'Power Usage Effectiveness', 'PUE')
        self.create_gauge(self.data['energy_efficiency'].mean(), 2, 'Energy Efficiency Ratio', 'EER')
        self.generate_eer_graph()
        self.generate_pue_graph()

        # Create PDF Document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []

        # Cover Page
        elements.append(Paragraph(f"Energy Consumption Report for {site_name}", self.title_style))
        elements.append(Paragraph(f"Reporting Period: {duration}", self.header_style))
        elements.append(Spacer(1, 40))

        # Key Findings Section (Detailed Executive Summary)
        elements.append(Paragraph("<b>KEY FINDINGS: EXECUTIVE SUMMARY</b>", self.header_style))
        elements.append(Spacer(1, 15))

        # Calculate key metrics
        avg_pue = self.data['power_efficiency'].mean()
        avg_eer = self.data['energy_efficiency'].mean()
        total_energy = float(summary_cards['total_energy_consumption'].split()[0])
        co2_savings = float(summary_cards['co2_savings'].split()[0]) if 'co2_savings' in summary_cards else 0

        # Create detailed findings
        findings = [
            f"<b>1. Energy Efficiency Performance:</b> The site achieved an average Power Usage Effectiveness (PUE) of <font color='{self.secondary_color}'><b>{avg_pue:.2f}</b></font> " +
            ("(excellent, meeting industry best practices)" if avg_pue <= 1.5 else
             "(good, with room for improvement)" if avg_pue <= 2.0 else
             "(needs significant improvement)"),

            f"<b>2. Cooling Efficiency:</b> The Energy Efficiency Ratio (EER) averaged <font color='{self.secondary_color}'><b>{avg_eer:.2f}</b></font> " +
            ("indicating highly efficient cooling systems" if avg_eer >= 1.5 else
             "showing moderate cooling efficiency" if avg_eer >= 0.5 else
             "suggesting cooling system inefficiencies"),

            f"<b>3. Energy Consumption:</b> Total energy consumption was <font color='{self.secondary_color}'><b>{total_energy:,} kWh</b></font> during the reporting period",

            f"<b>4. Top Performing Devices:</b> The highest efficiency devices achieved PCR (Power to Carbon Ratio) scores up to " +
            f"<font color='{self.secondary_color}'><b>{max(float(d['pcr']) for d in top_devices['top_devices']):.1f}</b></font>",

            f"<b>5. Environmental Impact:</b> Potential CO₂ savings of <font color='{self.secondary_color}'><b>{co2_savings:,} kg</b></font> could be achieved with optimization",

            f"<b>6. Peak Usage:</b> Highest power demand occurred at {self.data.loc[self.data['power_input'].idxmax()]['time'].strftime('%Y-%m-%d %H:%M')} " +
            f"reaching <font color='{self.secondary_color}'><b>{self.data['power_input'].max():.1f} kW</b></font>",

            f"<b>7. Efficiency Trends:</b> Daily PUE variance was <font color='{self.secondary_color}'><b>{self.data['power_efficiency'].std():.2f}</b></font> " +
            "indicating " + (
                "stable operations" if self.data['power_efficiency'].std() < 0.2 else "significant fluctuations")
        ]

        for finding in findings:
            elements.append(Paragraph(finding, self.desc_style))
            elements.append(Spacer(1, 8))

        elements.append(Spacer(1, 20))

        # Recommendation Highlights
        elements.append(Paragraph("<b>RECOMMENDATIONS</b>", self.subheader_style))
        recommendations = [
            "• Implement targeted efficiency improvements for devices with PCR below 1.0",
            "• Consider load balancing during peak usage periods",
            "• Schedule maintenance for cooling systems showing efficiency degradation",
            "• Evaluate virtualization opportunities for underutilized devices"
        ]

        for rec in recommendations:
            elements.append(Paragraph(rec, self.highlight_style))
            elements.append(Spacer(1, 5))

        elements.append(Spacer(1, 30))

        # Rest of the report continues with existing sections...
        # [Previous content sections would follow here]

        # Build PDF
        doc.build(elements)
        print(f"Report generated successfully: {filename}")

    # [Keep all other existing methods unchanged]
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

