import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import datetime
import os


class DynamicDCReportGenerator:
    def __init__(self):
        self.primary_color = '#003366'
        self.secondary_color = '#1B98E0'
        self.accent_color = '#00509E'
        self.text_color = '#333333'
        self.styles = getSampleStyleSheet()
        self.prepare_styles()

    def prepare_styles(self):
        self.title_style = ParagraphStyle(name='Title', parent=self.styles['Heading1'], fontSize=26, alignment=1,
                                          textColor=colors.HexColor(self.primary_color), spaceAfter=20,
                                          fontName='Helvetica-Bold')
        self.header_style = ParagraphStyle(name='Header', parent=self.styles['Heading2'], fontSize=18,
                                           textColor=colors.HexColor(self.primary_color), spaceAfter=12,
                                           fontName='Helvetica-Bold')
        self.subheader_style = ParagraphStyle(name='Subheader', parent=self.styles['Heading3'], fontSize=14,
                                              textColor=colors.HexColor(self.secondary_color), spaceAfter=10,
                                              fontName='Helvetica-Bold')
        self.observation_style = ParagraphStyle(name='Observation', parent=self.styles['BodyText'], fontSize=12,
                                                textColor=colors.HexColor(self.primary_color),
                                                backColor=colors.HexColor('#EEF7FF'), spaceAfter=10, leftIndent=10,
                                                rightIndent=10, borderPadding=5,
                                                borderColor=colors.HexColor(self.secondary_color), borderWidth=1,
                                                borderRadius=3, leading=14)
        self.recommendation_style = ParagraphStyle(name='Recommendation', parent=self.styles['BodyText'], fontSize=12,
                                                   textColor=colors.HexColor(self.secondary_color),
                                                   backColor=colors.HexColor('#F5FAFF'), spaceAfter=10, leftIndent=10,
                                                   rightIndent=10, borderPadding=5,
                                                   borderColor=colors.HexColor(self.secondary_color), borderWidth=1,
                                                   borderRadius=3, leading=14)
        self.footer_style = ParagraphStyle(name='Footer', parent=self.styles['Normal'], fontSize=10, alignment=1,
                                           textColor=colors.HexColor('#999999'))

    def generate_report(self, input_data, output_file):
        site_name = input_data['site_name']
        duration = input_data['duration']
        consumption_details = input_data['overall_consumption']
        energy_data = input_data['energy_data']
        top_devices = input_data['devices']['top']

        doc = SimpleDocTemplate(output_file, pagesize=letter)
        elements = []

        # Cover Page
        elements.append(Paragraph("📊 Data Center Energy & Efficiency Report", self.title_style))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"📍 Site: {site_name}", self.header_style))
        elements.append(Paragraph(f"🗓️ Reporting Period: {duration}", self.subheader_style))
        elements.append(Spacer(1, 40))

        # Executive Summary
        avg_pue = consumption_details['power_efficiency']
        avg_eer = consumption_details['energy_consumption']
        total_power = consumption_details['total_PIn_kw']
        it_power = consumption_details['total_POut_kw']
        co2_emission = consumption_details['co2emmsion'][1]

        elements.append(Paragraph("Executive Summary", self.header_style))
        summary_text = self.create_executive_summary(avg_pue, avg_eer, co2_emission, total_power, it_power)
        elements.append(Paragraph(summary_text, self.observation_style))


        # Energy Trends
        energy_df = pd.DataFrame(energy_data)
        self.plot_energy_trends(energy_df)
        elements.append(Paragraph("Energy Performance Trends", self.header_style))
        elements.append(Image("energy_trends.png", width=400, height=250))
        elements.append(Spacer(1, 20))
        trend_analysis = self.analyze_energy_trends(energy_df)
        elements.append(Paragraph(trend_analysis, self.observation_style))


        # CO2 Emissions
        self.plot_co2_pie(it_power, total_power - it_power)
        elements.append(Paragraph("CO₂ Emissions Analysis", self.header_style))
        elements.append(Image("co2_pie.png", width=400, height=250))
        elements.append(Spacer(1, 20))
        co2_analysis = self.analyze_co2_emissions(co2_emission)
        elements.append(Paragraph(co2_analysis, self.observation_style))


        # Top Devices
        device_table = [['Device Name', 'Power (kW)', 'CO₂ Emissions', 'IP Address']]
        for device in top_devices:
            device_table.append([
                device['device_name'],
                device['total_power'],
                device['co2emmissions'],
                device['ip_address']
            ])

        table = Table(device_table)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.primary_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F9FF')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(self.secondary_color))
        ]))

        elements.append(Paragraph("Top Monitored Cisco Network Devices", self.header_style))
        elements.append(table)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(
            "The monitored network devices demonstrate a well-balanced energy profile without any single device showing unusually high consumption.",
            self.observation_style))
        elements.append(PageBreak())

        # Final Conclusion
        final_summary = self.create_final_conclusion(avg_pue, avg_eer, co2_emission)
        elements.append(Paragraph("Final Summary and Recommendations", self.header_style))
        elements.append(Paragraph(final_summary, self.recommendation_style))

        elements.append(Spacer(1, 40))
        elements.append(Paragraph(f"📄 Report generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                  self.footer_style))

        doc.build(elements)

    def create_executive_summary(self, pue, eer, co2, total_power, it_power):
        loss = total_power - it_power
        loss_pct = (loss / total_power) * 100

        pue_eval = "Excellent" if pue < 1.2 else "Good" if pue < 1.5 else "Needs Improvement"
        eer_eval = "Excellent" if eer > 1 else "Good" if eer > 1.0 else "Needs Improvement"
        co2_eval = "Low" if co2 < 10 else "Moderate" if co2 < 20 else "High"

        return f"""
        The data center's PUE is {pue:.2f}, categorized as <b>{pue_eval}</b> based on global benchmarks.(industry benchmark: 1.0-1.2=Excellent, 1.2-1.5=Good)
        The EER stands at {eer:.2f}, reflecting <b>{eer_eval}</b> usage efficiency.
        Daily CO₂ emissions are around {co2:.2f} kg/day, classified as <b>{co2_eval}</b> footprint.

        A power loss of {loss_pct:.1f}% was observed, mostly attributable to facility overheads like cooling and UPS inefficiencies.
        Overall, the infrastructure demonstrates a stable and efficient operational profile with room for fine-tuning in overhead energy management.
        """

    def analyze_energy_trends(self, df):
        df['time'] = pd.to_datetime(df['time'])
        min_eff = df['energy_efficiency'].min()
        min_time = df.loc[df['energy_efficiency'].idxmin()]['time'].strftime('%Y-%m-%d %H:%M')

        return f"""
        The energy efficiency remained stable between 0.85 and 0.94 across most hours.
        The lowest observed efficiency was {min_eff:.2f} recorded at {min_time}, indicating a slight increase in energy overhead during that period.

        It is recommended to investigate HVAC system behavior and environmental conditions around early mornings to fine-tune cooling strategies.
        """

    def analyze_energy_trends(self, df):
        df['time'] = pd.to_datetime(df['time'])

        min_eff = df['energy_efficiency'].min()
        max_eff = df['energy_efficiency'].max()
        avg_eff = df['energy_efficiency'].mean()

        min_time = df.loc[df['energy_efficiency'].idxmin()]['time'].strftime('%Y-%m-%d %H:%M')
        max_time = df.loc[df['energy_efficiency'].idxmax()]['time'].strftime('%Y-%m-%d %H:%M')

        fluctuation = max_eff - min_eff

        trend_analysis = f"""
        During the reporting period, energy efficiency fluctuated between <b>{min_eff:.2f}</b> and <b>{max_eff:.2f}</b>, 
        with an average efficiency of <b>{avg_eff:.2f}</b>.

        The lowest energy efficiency was observed at <b>{min_time}</b> with a reading of <b>{min_eff:.2f}</b>, suggesting a potential 
        increase in overhead cooling load or underutilization during that period.

        The highest efficiency was recorded at <b>{max_time}</b>, where the data center operated near optimal conditions.

        Overall, the energy performance was {"very stable" if fluctuation < 0.1 else "moderately fluctuating"}, and it is 
        recommended to specifically monitor environmental control systems during the early morning hours to improve consistency further.
        """
        return trend_analysis

    def analyze_co2_emissions(self, co2_value):
        if co2_value < 10:
            return """
            The current carbon footprint is very low, reflecting excellent operational sustainability.
            No immediate actions are necessary; continue current practices and consider publishing sustainability metrics externally.
            """
        elif co2_value < 20:
            return """
            The carbon footprint is moderate. It is advisable to explore further optimizations in cooling and power distribution to reduce CO₂ emissions further.
            """
        else:
            return """
            The carbon footprint is high. Immediate review of facility cooling systems, UPS efficiency, and renewable energy sourcing is strongly recommended.
            """

    def create_final_conclusion(self, pue, eer, co2):
        conclusion = f"""
        In summary, the data center's operational performance aligns well with energy efficiency expectations for Cisco network-based infrastructures.
        Key strengths include a stable PUE of {pue:.2f} and a manageable CO₂ footprint of {co2:.2f} kg/day.

        Opportunities for improvement lie mainly in reducing energy losses attributed to cooling and facility overheads.
        It is suggested to perform a detailed thermal audit and evaluate options for higher-efficiency UPS deployments.

        With minor optimizations, the data center can achieve even stronger sustainability results and operational cost savings moving forward.
        """
        return conclusion

    def plot_energy_trends(self, df):
        plt.figure(figsize=(10, 6))
        df['time'] = pd.to_datetime(df['time'])
        plt.plot(df['time'], df['energy_efficiency'], label='Energy Efficiency', marker='o')
        plt.plot(df['time'], df['power_efficiency'], label='Power Efficiency', marker='x')
        plt.xlabel('Time')
        plt.ylabel('Efficiency Ratio')
        plt.title('Energy Performance Trends')
        plt.legend()
        plt.grid(True)
        plt.gcf().autofmt_xdate()
        plt.savefig('energy_trends.png')
        plt.close()

    def plot_co2_pie(self, it_power, overhead_power):
        plt.figure(figsize=(6, 6))
        labels = ['IT Load', 'Cooling & Overhead']
        sizes = [it_power, overhead_power]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=[self.secondary_color, self.accent_color],
                startangle=140)
        plt.axis('equal')
        plt.title('CO₂ Emissions Distribution')
        plt.savefig('co2_pie.png')
        plt.close()
