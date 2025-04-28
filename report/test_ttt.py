import logging
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import matplotlib

matplotlib.use('Agg')  # Set the backend to Agg for non-interactive plotting


class DynamicDCReportGenerator:
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

    def create_energy_trend_chart(self, energy_data):
        """Create a line chart showing energy efficiency trends"""
        df = pd.DataFrame(energy_data)
        df['time'] = pd.to_datetime(df['time'])

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df['time'], df['power_efficiency'], label='PUE', color=self.primary_color, marker='o')
        ax.plot(df['time'], df['energy_efficiency'], label='Energy Efficiency', color=self.secondary_color, marker='x')

        # Formatting
        ax.set_title('Energy Efficiency Trends', fontsize=14)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Efficiency Ratio', fontsize=12)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        fig.autofmt_xdate()

        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf

    def create_power_consumption_chart(self, consumption_data):
        """Create a bar chart showing power consumption breakdown"""
        labels = ['IT Equipment', 'Facility Overhead']
        values = [consumption_data['total_POut_kw'],
                  consumption_data['total_PIn_kw'] - consumption_data['total_POut_kw']]

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, values, color=[self.primary_color, self.secondary_color])

        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.2f} kW',
                    ha='center', va='bottom')

        # Formatting
        ax.set_title('Power Consumption Breakdown', fontsize=14)
        ax.set_ylabel('Power (kW)', fontsize=12)
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)

        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf

    def create_top_devices_table(self, devices, title):
        """Create a table for top/bottom devices"""
        device_data = [['Device Name', 'Power (kW)', 'CO2 Emissions']]
        for device in devices[:5]:  # Show top 5
            device_data.append([
                device['device_name'],
                device['total_power'],
                device['co2emmissions']
            ])

        return Table(device_data, colWidths=[200, 100, 100])

    def generate_report(self, input_data, output_file):
        site_name = input_data['site_name']
        duration = input_data['duration']
        consumption_details = input_data['overall_consumption']
        energy_data = input_data['energy_data']
        top_devices = input_data['devices']['top']
        bottom_devices = input_data['devices']['bottom']
        inventory = input_data['inventory']

        # Create PDF Document
        doc = SimpleDocTemplate(output_file, pagesize=letter)
        elements = []

        # Cover Page
        elements.append(Paragraph("Data Center Energy Performance Report", self.title_style))
        elements.append(Paragraph(f"Site: {site_name}", self.header_style))
        elements.append(Paragraph(f"Reporting Period: {duration}", self.subheader_style))
        elements.append(Spacer(1, 60))

        # Key Findings Section
        elements.append(Paragraph("<b>KEY FINDINGS</b>", self.header_style))
        elements.append(Spacer(1, 15))

        # Calculate metrics
        avg_pue = consumption_details['power_efficiency']
        avg_eer = consumption_details['energy_consumption']
        total_power = consumption_details['total_PIn_kw']
        it_power = consumption_details['total_POut_kw']
        energy_loss = total_power - it_power
        loss_percent = (energy_loss / total_power) * 100
        co2_emissions = consumption_details['co2emmsion'][1]

        # Key findings summary
        findings_content = f"""
        <b>🔍 Key Observations:</b><br/>
        - Average PUE: <b>{avg_pue:.2f}</b> (IT power is {it_power:.2f} kW, facility overhead is {energy_loss:.2f} kW)<br/>
        - Energy Efficiency Ratio: <b>{avg_eer:.2f}</b><br/>
        - CO2 Emissions: <b>{co2_emissions:.2f} kg</b> during reporting period<br/>
        - Inventory: <b>{inventory['onboarded_devices']}/{inventory['total_devices']}</b> devices onboarded from <b>{inventory['total_vendors']}</b> vendors<br/><br/>

        <b>📊 Efficiency Analysis:</b><br/>
        - Facility overhead accounts for <b>{loss_percent:.1f}%</b> of total power consumption<br/>
        - The data center is operating with <b>{'good' if avg_pue < 1.5 else 'moderate'}</b> energy efficiency<br/><br/>
        """
        elements.append(Paragraph(findings_content, self.desc_style))
        elements.append(Spacer(1, 20))

        # Energy Trends Section
        elements.append(Paragraph("<b>ENERGY TRENDS</b>", self.header_style))
        elements.append(Spacer(1, 15))

        # Generate and add energy trend chart
        trend_chart = self.create_energy_trend_chart(energy_data)
        elements.append(Image(trend_chart, width=400, height=200))
        elements.append(Spacer(1, 15))

        # Chart explanation
        chart_explanation = """
        <b>Trend Analysis:</b><br/>
        The chart above shows the variation in Power Usage Effectiveness (PUE) and Energy Efficiency Ratio over time.<br/>
        - <b>PUE</b> (blue line) measures total facility power divided by IT equipment power (ideal = 1.0)<br/>
        - <b>Energy Efficiency</b> (orange line) shows the ratio of useful cooling to energy consumed<br/><br/>
        """
        elements.append(Paragraph(chart_explanation, self.desc_style))
        elements.append(Spacer(1, 20))

        # Power Consumption Breakdown
        elements.append(Paragraph("<b>POWER CONSUMPTION BREAKDOWN</b>", self.header_style))
        elements.append(Spacer(1, 15))

        # Generate and add power consumption chart
        power_chart = self.create_power_consumption_chart(consumption_details)
        elements.append(Image(power_chart, width=350, height=200))
        elements.append(Spacer(1, 15))

        # Power consumption explanation
        power_explanation = f"""
        <b>Consumption Analysis:</b><br/>
        - IT Equipment consumes <b>{it_power:.2f} kW</b> ({100 - loss_percent:.1f}% of total)<br/>
        - Facility overhead (cooling, power distribution, etc.) consumes <b>{energy_loss:.2f} kW</b><br/>
        - Total facility power draw is <b>{total_power:.2f} kW</b><br/><br/>
        """
        elements.append(Paragraph(power_explanation, self.desc_style))
        elements.append(Spacer(1, 20))

        # Top Power-Consuming Devices
        elements.append(Paragraph("<b>TOP POWER-CONSUMING DEVICES</b>", self.header_style))
        elements.append(Spacer(1, 15))

        top_devices_table = self.create_top_devices_table(top_devices, "Top Power Consumers")
        top_devices_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.primary_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F9FF')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(self.secondary_color)),
        ]))
        elements.append(top_devices_table)
        elements.append(Spacer(1, 15))

        devices_analysis = """
        <b>Device Analysis:</b><br/>
        The table above shows the devices with highest power consumption. These devices typically offer<br/>
        the greatest opportunities for optimization through:<br/>
        - Right-sizing or virtualization<br/>
        - Firmware updates for power management features<br/>
        - Potential replacement with more efficient models<br/><br/>
        """
        elements.append(Paragraph(devices_analysis, self.desc_style))
        elements.append(Spacer(1, 20))

        # Recommendations Section
        elements.append(Paragraph("<b>RECOMMENDATIONS</b>", self.header_style))
        elements.append(Spacer(1, 15))

        recommendations = f"""
        <b>1. Cooling System Optimization:</b><br/>
        - Implement hot/cold aisle containment (potential 5-15% savings)<br/>
        - Adjust cooling setpoints upward where possible (1°C ≈ 3% savings)<br/><br/>

        <b>2. Power Management:</b><br/>
        - Install smart PDUs for granular power monitoring<br/>
        - Consider high-efficiency UPS systems (>97% efficiency)<br/><br/>

        <b>3. IT Equipment:</b><br/>
        - Conduct server virtualization assessment<br/>
        - Implement power management policies on all devices<br/>
        - Replace oldest {min(3, len(top_devices))} high-consumption devices in next refresh cycle<br/><br/>

        <b>4. Monitoring & Benchmarking:</b><br/>
        - Implement continuous PUE monitoring with alerts<br/>
        - Benchmark against similar facilities quarterly<br/><br/>
        """
        elements.append(Paragraph(recommendations, self.desc_style))
        elements.append(Spacer(1, 20))

        # Final Assessment
        elements.append(Paragraph("<b>FINAL ASSESSMENT</b>", self.header_style))
        elements.append(Spacer(1, 15))

        assessment = f"""
        <b>Overall Assessment:</b><br/>
        The {site_name} data center shows {'good' if avg_pue < 1.5 else 'moderate'} energy efficiency with a PUE of {avg_pue:.2f}.<br/>
        Key opportunities exist in cooling optimization and power management that could reduce<br/>
        energy overhead by an estimated 10-20%.<br/><br/>

        <b>Next Steps:</b><br/>
        1. Conduct detailed thermal assessment within next 30 days<br/>
        2. Develop implementation plan for containment strategies<br/>
        3. Schedule review of top {min(5, len(top_devices))} power-consuming devices<br/><br/>

        <b>Estimated Potential Savings:</b><br/>
        - Energy costs: ${(energy_loss * 0.15 * 24 * 365 * 0.12):.0f}/year (15% reduction at $0.12/kWh)<br/>
        - CO2 emissions: {(co2_emissions * 0.15):.1f} kg/year reduction<br/><br/>
        """
        elements.append(Paragraph(assessment, self.highlight_style))
        elements.append(Spacer(1, 20))

        # Footer
        elements.append(Paragraph(f"Report generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                  self.footer_style))

        # Build the PDF
        doc.build(elements)


# Example usage:
