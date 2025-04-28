import logging
from time import process_time_ns

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
        # ax.plot(df['time'], df['power_efficiency'], label='PUE', color=self.primary_color, marker='o')
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

    def create_power_trend_chart(self, energy_data):
        """Create a line chart showing energy efficiency trends"""
        df = pd.DataFrame(energy_data)
        df['time'] = pd.to_datetime(df['time'])

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df['time'], df['power_efficiency'], label='PUE', color=self.primary_color, marker='o')
        # ax.plot(df['time'], df['energy_efficiency'], label='Energy Efficiency', color=self.secondary_color, marker='x')

        # Formatting
        ax.set_title('Power Usage Trends', fontsize=14)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Power Usage Effectiveness', fontsize=12)
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
    def get_co2_assessment(self,total_co2_kg, it_power_kw, duration_days=1):
        """Realistic CO₂ assessment for data centers with scaling factors"""

        # Calculate daily CO₂ per kW of IT load (industry benchmarks)
        co2_per_kw_per_day = total_co2_kg / (it_power_kw * duration_days)

        # Evaluation thresholds (kg CO₂ per kW per day)
        if co2_per_kw_per_day < 0.2:  # ~0.5 kg/kW-day is typical for grid power
            return "Excellent"
        elif co2_per_kw_per_day < 0.5:
            return "Good"
        elif co2_per_kw_per_day < 1.0:
            return "Moderate"
        else:
            return "High"

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
        headers = ["Device Name", "IP Address", "Total Power", "Traffic Speed", "PCR",
                   "CO2 Emissions"]
        #print("headers")

        device_data = [headers] + [[
            device['device_name'],
            device['ip_address'],
            device['total_power'],
            device['traffic_speed'],
            device['pcr'],
            device['co2emmissions'],
        ] for device in devices]

        return Table(device_data, colWidths=[120, 100, 80, 80, 80, 100])


    def generate_power_consumption_conclusion(self,it_power, loss_power):
        total_power = it_power + loss_power
        if total_power == 0:
            return "No data available to generate conclusion."

        it_power_percentage = (it_power / total_power) * 100
        loss_power_percentage = (loss_power / total_power) * 100

        if it_power_percentage >= 85:
            conclusion = (
                f"The data center demonstrates strong energy prioritization toward IT operations "
                f"({it_power_percentage:.1f}% IT load), with minimal losses to facility overhead ({loss_power_percentage:.1f}%), "
                "reflecting efficient infrastructure design."
            )
        elif 70 <= it_power_percentage < 85:
            conclusion = (
                f"The data center maintains good IT energy prioritization ({it_power_percentage:.1f}% IT load), "
                f"though facility overhead ({loss_power_percentage:.1f}%) presents opportunities for further optimization."
            )
        else:
            conclusion = (
                f"The data center shows high facility overhead ({loss_power_percentage:.1f}%), indicating "
                "substantial opportunities to improve infrastructure efficiency and reduce non-IT energy consumption."
            )

        return conclusion

    def analyze_pue_trends(self, df):
        # print(df)
        try:
            df['time'] = pd.to_datetime(df['time'])
            #print("test it ")

            # Find minimum PUE (best performance)
            min_pue = df['power_efficiency'].min()
            min_time = df.loc[df['power_efficiency'].idxmin(), 'time'].strftime('%Y-%m-%d %H:%M')
            #print("test it 2 ")
            # Find maximum PUE (worst performance)
            max_pue = df['power_efficiency'].max()
            max_time = df.loc[df['power_efficiency'].idxmax(), 'time'].strftime('%Y-%m-%d %H:%M')
            #print("test it 3")
            # Find average PUE
            avg_pue = df['power_efficiency'].mean()
            #print("test it 4")
            # Stability analysis
            pue_range = max_pue - min_pue
            #print("pue_range",pue_range)
            #print("test it 5")
            if pue_range <= 0.1:
                trend_conclusion = "The PUE remained highly stable throughout the observation period, indicating efficient and consistent energy management."
            elif pue_range <= 0.3:
                trend_conclusion = "The PUE showed moderate fluctuations, suggesting minor operational variations impacting energy distribution."
            else:
                trend_conclusion = "Significant fluctuations were observed in PUE, highlighting potential inefficiencies or inconsistent infrastructure performance."
            #print(trend_conclusion)
            #print("test it 6")
            # Final report
            return f"""
        <b>PUE Analysis:</b><br/>
        - The lowest PUE recorded was <b>{min_pue:.2f}</b> at <b>{min_time}</b>.<br/>
        - The highest PUE recorded was <b>{max_pue:.2f}</b> at <b>{max_time}</b>.<br/>
        - The average PUE during the monitoring period was approximately <b>{avg_pue:.2f}</b>.<br/><br/>
        {trend_conclusion}
        """
        except Exception as e:
            logging.error(f"got error at {e}")

    def analyze_energy_trends(self, df):
        import pandas as pd

        df['time'] = pd.to_datetime(df['time'])

        # Find minimum efficiency
        min_eff = df['energy_efficiency'].min()
        min_time = df.loc[df['energy_efficiency'].idxmin(), 'time'].strftime('%Y-%m-%d %H:%M')

        # Find maximum efficiency
        max_eff = df['energy_efficiency'].max()
        max_time = df.loc[df['energy_efficiency'].idxmax(), 'time'].strftime('%Y-%m-%d %H:%M')

        # Find overall average efficiency
        avg_eff = df['energy_efficiency'].mean()

        # Overall conclusion based on efficiency stability
        efficiency_range = max_eff - min_eff

        if efficiency_range <= 0.1:
            trend_conclusion = "The energy efficiency remained stable throughout the observation period, indicating consistent operational performance."
        elif efficiency_range <= 0.2:
            trend_conclusion = "The energy efficiency showed moderate variation, suggesting minor fluctuations possibly linked to load or environmental changes."
        else:
            trend_conclusion = "The energy efficiency fluctuated significantly, indicating potential instability or system inefficiencies requiring further review."

        # Final formatted report
        return f"""
    <b>Energy Efficiency Analysis:</b><br/>
    - The lowest energy efficiency observed was <b>{min_eff:.2f}</b> at <b>{min_time}</b>.<br/>
    - The highest energy efficiency observed was <b>{max_eff:.2f}</b> at <b>{max_time}</b>.<br/>
    - The average energy efficiency across the period was approximately <b>{avg_eff:.2f}</b>.<br/><br/>
    {trend_conclusion}
    """

    def generate_report(self, input_data, output_file='test1-+++-'):
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
        elements.append(Spacer(1, 10))

        intro = Paragraph(f"This comprehensive report provides detailed insights into the energy consumption patterns and efficiency metrics for <b>{site_name}</b>,which comprises of {inventory['onboarded_devices']} onboarded devices, {inventory['total_vendors']} vendor, and {inventory['total_racks']} racks.The data covers the specified reporting period, highlighting key performance indicators and offering actionable insights.",
        self.desc_style)
        elements.append(intro)
        elements.append(Spacer(1, 10))


        # Calculate metrics
        avg_pue = consumption_details['power_efficiency']
        avg_eer = consumption_details['energy_consumption']
        total_power = consumption_details['total_PIn_kw']
        it_power = consumption_details['total_POut_kw']

        energy_loss = total_power - it_power
        loss_percent = (energy_loss / total_power) * 100
        co2_emissions = consumption_details['co2emmsion'][1]
        self.create_key_findings_section(
            pue=avg_pue,
            eer=avg_eer,
            co2=co2_emissions,
            total_power=total_power,
            it_power=it_power,
            elements=elements  # The report's elements list
        )
        # Key findings summary
        # findings_content = f"""
        # <b>🔍 Key Observations:</b><br/>
        # - Average PUE: <b>{avg_pue:.2f}</b> (IT power is {it_power:.2f} kW, facility overhead is {energy_loss:.2f} kW)<br/>
        # - Energy Efficiency Ratio: <b>{avg_eer:.2f}</b><br/>
        # - CO2 Emissions: <b>{co2_emissions:.2f} kg</b> during reporting period<br/>
        # - Inventory: <b>{inventory['onboarded_devices']}/{inventory['total_devices']}</b> devices onboarded from <b>{inventory['total_vendors']}</b> vendors<br/><br/>
        #
        # <b>📊 Efficiency Analysis:</b><br/>
        # - Facility overhead accounts for <b>{loss_percent:.1f}%</b> of total power consumption<br/>
        # - The data center is operating with <b>{'good' if avg_pue < 1.5 else 'moderate'}</b> energy efficiency<br/><br/>
        # """
        # elements.append(Paragraph(findings_content, self.desc_style))

        # Power Consumption Breakdown
        elements.append(Paragraph("<b>POWER CONSUMPTION BREAKDOWN</b>", self.header_style))
        elements.append(Spacer(1, 5))
        # Generate and add power consumption chart
        power_chart = self.create_power_consumption_chart(consumption_details)
        elements.append(Paragraph(
            "This analysis highlights the distribution of total power consumption between core IT operations and facility overhead."
            " It assesses how effectively the data center directs energy toward computing infrastructure versus ancillary systems like cooling,"
            " lighting, and power backup.",self.desc_style))
        elements.append(Spacer(1, 5))
        elements.append(Image(power_chart, width=350, height=200))
        elements.append(Spacer(1, 5))
        conclusion = self.generate_power_consumption_conclusion(it_power, energy_loss)
        # Power consumption explanation
        power_explanation = f"""
              <b>Consumption Analysis:</b><br/>
                - IT Equipment consumes <b>{it_power:.2f} kW</b><br/>
                - Facility overhead (cooling, power distribution, etc.) consumes <b>{energy_loss:.2f} kW</b><br/>
                - Total facility power draw is <b>{total_power:.2f} kW</b><br/>
                <b>{conclusion}</b><br/><br/>
               """
        elements.append(Paragraph(power_explanation, self.desc_style))
        elements.append(Spacer(1, 10))


        # Energy Trends Section
        elements.append(Paragraph("<b>Energy Efficiency Over Time</b>", self.header_style))

        elements.append(Spacer(1, 7))
        elements.append(Paragraph("The Energy Efficiency Ratio (EER) indicates the ratio of cooling output to the electrical energy input. Higher EER values signify better "
                                  "energy efficiency. Below is the trend of EER over the reporting period.",self.desc_style
))
        ##print("EER")

        # Generate and add energy trend chart
        trend_chart = self.create_energy_trend_chart(energy_data)
        energy_df = pd.DataFrame(energy_data)
        elements.append(Image(trend_chart, width=400, height=200))
        elements.append(Spacer(1, 5))
        trend_analysis = self.analyze_energy_trends(energy_df)
        elements.append(Paragraph(trend_analysis, self.desc_style))
        elements.append(Spacer(1, 5))

        # Energy Trends Section
        elements.append(Paragraph("<b>Power Usage Over Time</b>", self.header_style))

        elements.append(Spacer(1, 7))
        elements.append(Paragraph(
            f"Power Usage Effectiveness (PUE) measures the total energy consumption "
            f"compared to the energy used solely by IT equipment. Lower PUE values represent more efficient energy use. "
            f"The graph below shows the PUE trend over the reporting period{duration}:",self.desc_style))
        #print("PUE")
        # Generate and add energy trend chart
        trend_chart = self.create_power_trend_chart(energy_data)
        # energy_df = pd.DataFrame(energy_data)
        elements.append(Image(trend_chart, width=400, height=200))
        #print("PUE-Test 1")
        elements.append(Spacer(1, 5))
        trend_analysis = self.analyze_pue_trends(energy_df)
        elements.append(Paragraph(trend_analysis, self.desc_style))
        elements.append(Spacer(1, 5))
        #print("testing point 1 ")
        # Chart explanation
        # chart_explanation = """
        # <b>Trend Analysis:</b><br/>
        # The chart above shows the variation in Power Usage Effectiveness (PUE) and Energy Efficiency Ratio over time.<br/>
        # - <b>PUE</b> (blue line) measures total facility power divided by IT equipment power (ideal = 1.0)<br/>
        # - <b>Energy Efficiency</b> (orange line) shows the ratio of useful cooling to energy consumed<br/><br/>
        # """
        # elements.append(Paragraph(chart_explanation, self.desc_style))
        # elements.append(Spacer(1, 20))



        # Top Power-Consuming Devices
        elements.append(Paragraph("<b>TOP POWER-CONSUMING DEVICES</b>", self.header_style))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph("The table below highlights the top devices based on their power consumption,data traffic,Co2 emmission, and overall efficiency metrics. These devices play a critical role in the site's energy consumption profile, and understanding their performance can help identify areas for optimization and efficiency improvements.",self.desc_style))
        elements.append(Spacer(1, 5))
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
        elements.append(Spacer(1, 5))

        devices_analysis = """
        <b>Device Analysis:</b><br/>
        These devices typically offer the greatest opportunities for optimization through:<br/>
        - Right-sizing or virtualization<br/>
        - Firmware updates for power management features<br/>
        - Potential replacement with more efficient models<br/><br/>
        """
        elements.append(Paragraph(devices_analysis, self.desc_style))
        # Recommendations Section
        elements.append(Paragraph("<b>RECOMMENDATIONS</b>", self.header_style))
        elements.append(Spacer(1, 5))

        # recommendations = f"""
        # <b>1. Cooling System Optimization:</b><br/>
        # - Implement hot/cold aisle containment (potential 5-15% savings)<br/>
        # - Adjust cooling setpoints upward where possible (1°C ≈ 3% savings)<br/><br/>
        #
        # <b>2. Power Management:</b><br/>
        # - Install smart PDUs for granular power monitoring<br/>
        # - Consider high-efficiency UPS systems (>97% efficiency)<br/><br/>
        #
        # <b>3. IT Equipment:</b><br/>
        # - Conduct server virtualization assessment<br/>
        # - Implement power management policies on all devices<br/>
        # - Replace oldest {min(3, len(top_devices))} high-consumption devices in next refresh cycle<br/><br/>
        #
        # <b>4. Monitoring & Benchmarking:</b><br/>
        # - Implement continuous PUE monitoring with alerts<br/>
        # - Benchmark against similar facilities quarterly<br/><br/>
        # """
        dynamic_recommendations = self.generate_dynamic_recommendations(
            avg_pue, avg_eer, co2_emissions, top_devices, loss_percent
        )
        elements.append(Paragraph(dynamic_recommendations, self.desc_style))
        # elements.append(Paragraph(recommendations, self.desc_style))
        elements.append(Spacer(1, 5))

        # Final Assessment
        elements.append(Paragraph("<b>FINAL ASSESSMENT</b>", self.header_style))
        elements.append(Spacer(1, 5))

        # assessment = f"""
        # <b>Overall Assessment:</b><br/>
        # The {site_name} data center shows {'good' if avg_pue < 1.5 else 'moderate'} energy efficiency with a PUE of {avg_pue:.2f}.<br/>
        # Key opportunities exist in cooling optimization and power management that could reduce<br/>
        # energy overhead by an estimated 10-20%.<br/><br/>
        #
        # <b>Next Steps:</b><br/>
        # 1. Conduct detailed thermal assessment within next 30 days<br/>
        # 2. Develop implementation plan for containment strategies<br/>
        # 3. Schedule review of top {min(5, len(top_devices))} power-consuming devices<br/><br/>
        #
        # <b>Estimated Potential Savings:</b><br/>
        # - Energy costs: ${(energy_loss * 0.15 * 24 * 365 * 0.12):.0f}/year (15% reduction at $0.12/kWh)<br/>
        # - CO2 emissions: {(co2_emissions * 0.15):.1f} kg/year reduction<br/><br/>
        # """
        # elements.append(Paragraph(assessment, self.highlight_style))
        final_assessment = self.generate_final_assessment(
            site_name, avg_pue, avg_eer, co2_emissions, total_power, it_power, top_devices
        )
        elements.append(Paragraph(final_assessment, self.highlight_style))
        elements.append(Spacer(1, 5))

        # Footer
        elements.append(Paragraph(f"Report generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                  self.footer_style))

        # Build the PDF
        doc.build(elements)

    def generate_dynamic_recommendations(self, pue, eer, co2, top_devices, loss_percent):
        """Generate recommendations based on performance metrics"""
        recommendations = []

        # Cooling recommendations
        if pue >= 1.4:
            cooling_msg = (
                "<b>1. Cooling System Optimization (High Priority):</b><br/>"
                "- Implement hot/cold aisle containment (potential 10-20% cooling savings)<br/>"
                "- Upgrade to variable speed fans and pumps (5-15% savings)<br/>"
                "- Raise cooling setpoints by 1-2°C where possible (3-5% savings per °C)<br/><br/>"
            )
        elif pue >= 1.2:
            cooling_msg = (
                "<b>1. Cooling System Optimization:</b><br/>"
                "- Implement basic aisle containment (potential 5-10% savings)<br/>"
                "- Optimize airflow management with blanking panels<br/>"
                "- Review temperature setpoints for optimization opportunities<br/><br/>"
            )
        else:
            cooling_msg = (
                "<b>1. Cooling System Maintenance:</b><br/>"
                "- Perform routine maintenance on existing cooling systems<br/>"
                "- Monitor for subtle optimization opportunities<br/><br/>"
            )
        recommendations.append(cooling_msg)

        # Power management
        if loss_percent >= 25:
            power_msg = (
                "<b>2. Power Distribution Overhaul (Critical):</b><br/>"
                "- Replace legacy UPS systems with high-efficiency (>97%) models<br/>"
                "- Install smart PDUs for granular power monitoring<br/>"
                "- Consider DC power distribution where applicable<br/><br/>"
            )
        elif loss_percent >= 15:
            power_msg = (
                "<b>2. Power Management Improvements:</b><br/>"
                "- Implement power monitoring at all distribution levels<br/>"
                "- Schedule maintenance for existing power infrastructure<br/>"
                "- Consider UPS battery refresh if older than 3 years<br/><br/>"
            )
        else:
            power_msg = (
                "<b>2. Power System Maintenance:</b><br/>"
                "- Continue regular power system maintenance<br/>"
                "- Monitor for incremental improvement opportunities<br/><br/>"
            )
        recommendations.append(power_msg)

        # IT Equipment
        if len(top_devices) > 0:
            top_device_names = ", ".join([d['device_name'] for d in top_devices[:3]])
            it_msg = (
                f"<b>3. IT Equipment Optimization:</b><br/>"
                f"- Target top consumers first: {top_device_names}<br/>"
                "- Conduct virtualization assessment (potential 5:1 consolidation)<br/>"
                "- Implement power management policies on all devices<br/>"
                "- Schedule refresh of oldest 3-5 high-consumption devices<br/><br/>"
            )
        else:
            it_msg = (
                "<b>3. IT Equipment Maintenance:</b><br/>"
                "- Review all devices for power management compliance<br/>"
                "- Monitor for aging equipment replacement opportunities<br/><br/>"
            )
        recommendations.append(it_msg)

        # Monitoring
        monitoring_msg = (
            "<b>4. Enhanced Monitoring:</b><br/>"
            "- Implement real-time PUE monitoring with alerts<br/>"
            "- Establish quarterly benchmarking against similar facilities<br/>"
            "- Create automated reports for key efficiency metrics<br/><br/>"
        )
        recommendations.append(monitoring_msg)

        return "".join(recommendations)

    def generate_final_assessment(self, site_name, pue, eer, co2, total_power, it_power, top_devices):
        """Generate dynamic final assessment based on performance"""
        # Calculate key metrics
        energy_loss = total_power - it_power
        loss_percent = (energy_loss / total_power) * 100
        daily_savings_potential = energy_loss * 0.15 * 24  # 15% reduction
        annual_savings = daily_savings_potential * 365 * 0.12  # $0.12/kWh

        # Determine assessment level
        if pue < 1.2 and eer > 1.2:
            assessment_level = "excellent"
        elif pue < 1.4 and eer > 0.8:
            assessment_level = "good"
        else:
            assessment_level = "needs improvement"

        # Generate appropriate assessment
        if assessment_level == "excellent":
            assessment = (
                f"<b>Overall Assessment:</b><br/>"
                f"The {site_name} data center demonstrates <font color='{self.secondary_color}'><b>excellent</b></font> energy efficiency "
                f"with a PUE of {pue:.2f} and EER of {eer:.2f}. The facility operates at industry-leading standards with "
                "minimal opportunities for major improvements.<br/><br/>"

                "<b>Maintenance Recommendations:</b><br/>"
                "- Continue current best practices in cooling and power management<br/>"
                "- Monitor for gradual optimization opportunities<br/>"
                "- Consider piloting innovative efficiency technologies<br/><br/>"
            )
        elif assessment_level == "good":
            assessment = (
                f"<b>Overall Assessment:</b><br/>"
                f"The {site_name} data center shows <font color='{self.secondary_color}'><b>good</b></font> energy efficiency "
                f"with a PUE of {pue:.2f} and EER of {eer:.2f}. The facility performs well with identified "
                "opportunities for targeted improvements.<br/><br/>"

                "<b>Optimization Priorities:</b><br/>"
                f"- Address the {loss_percent:.1f}% facility overhead through cooling and power improvements<br/>"
                f"- Focus on top {min(3, len(top_devices))} energy-consuming devices<br/>"
                "- Implement monitoring enhancements for continuous improvement<br/><br/>"
            )
        else:
            assessment = (
                f"<b>Overall Assessment:</b><br/>"
                f"The {site_name} data center <font color='{self.secondary_color}'><b>requires improvement</b></font> in energy efficiency "
                f"(PUE: {pue:.2f}, EER: {eer:.2f}). Significant opportunities exist to reduce operational costs "
                "and environmental impact.<br/><br/>"

                "<b>Critical Actions:</b><br/>"
                f"- Immediate attention to the {loss_percent:.1f}% facility overhead (potential ${annual_savings:,.0f}/year savings)<br/>"
                f"- Urgent review of top {min(5, len(top_devices))} energy-consuming devices<br/>"
                "- Comprehensive cooling system assessment within 30 days<br/><br/>"
            )

        # Add next steps
        assessment += (
            "<b>Next Steps:</b><br/>"
            "1. Conduct detailed thermal assessment within next 30 days<br/>"
            "2. Develop implementation plan for priority recommendations<br/>"
            "3. Schedule executive review of energy efficiency program<br/><br/>"

            f"<b>Estimated Potential Savings:</b><br/>"
            f"- Energy costs: <font color='{self.secondary_color}'><b>${annual_savings:,.0f}/year</b></font> (15% overhead reduction at $0.12/kWh)<br/>"
            f"- CO2 emissions: <font color='{self.secondary_color}'><b>{(co2 * 0.15):.1f} kg/year</b></font> reduction potential<br/>"
        )

        return assessment

    def evaluate_data_center(self,pue, eer, co2,total_power):
        # Individual evaluations
        pue_eval = "Excellent" if pue < 1.2 else "Good" if pue < 1.5 else "Needs Improvement"
        eer_eval = "Excellent" if eer > 1.5 else "Good" if eer > 1.0 else "Needs Improvement"
        co2_eval =self.get_co2_assessment(co2, total_power, 1)

        # Overall performance classification
        if pue_eval == "Excellent" and (eer_eval in ["Excellent", "Good"]) and co2_eval == "Excellent":
            overall_status = "Excellent"
        elif pue_eval in ["Excellent", "Good"] and (eer_eval in ["Excellent", "Good"]) and co2_eval in ["Excellent", "Good", "Moderate"]:
            overall_status = "Good"
        else:
            overall_status = "Needs Improvement"

        # Detailed reasoning
        details = []

        if pue_eval == "Excellent":
            details.append(f"The datacenter PUE(Power Usage Effectiveness) is <font color='{self.secondary_color}'><b>{pue:.2f}</b></font>, classified as Excellent based on industry benchmarks.")
        elif pue_eval == "Good":
            details.append(f"The datacenter PUE(Power Usage Effectiveness) is <font color='{self.secondary_color}'><b>{pue:.2f}</b></font>, classified as Good with potential for further optimization.")
        else:
            details.append(f"The datacenter PUE(Power Usage Effectiveness) is <font color='{self.secondary_color}'><b>{pue:.2f}</b></font>, indicating the need for major energy efficiency improvements.")

        if eer_eval == "Excellent":
            details.append(f"The EER(Energy Efficiency Ratio) is <font color='{self.secondary_color}'><b>{eer:.2f}</b></font>, reflecting excellent energy reuse efficiency.")
        elif eer_eval == "Good":
            details.append(f"The EER(Energy Efficiency Ratio) is <font color='{self.secondary_color}'><b>{eer:.2f}</b></font>, reflecting reasonable but improvable energy reuse.")
        else:
            details.append(
                f"The EER(Energy Efficiency Ratio) is <font color='{self.secondary_color}'><b>{eer:.2f}</b></font>, indicating underutilization of recovered energy and improvement opportunities.")

        if co2_eval == "Low":
            details.append(
                f"Daily CO2 emissions are low at <font color='{self.secondary_color}'><b>{co2:.2f}</b></font> kg/day, indicating a strong environmental profile.")
        elif co2_eval == "Moderate":
            details.append(
                f"Daily CO2 emissions are moderate at <font color='{self.secondary_color}'><b>{co2:.2f}</b></font> kg/day, suggesting partial reliance on non-renewables.")
        else:
            details.append(
                f"Daily CO2 emissions are high at <font color='{self.secondary_color}'><b>{co2:.2f}</b></font> kg/day, raising concerns about carbon footprint.")

        # Final conclusion
        if overall_status == "Excellent":
            conclusion = "The data center is performing at an excellent standard with strong energy efficiency and a sustainable environmental impact."
        elif overall_status == "Good":
            conclusion = "The data center performs well overall, with minor areas identified for energy optimization and sustainability improvements."
        else:
            conclusion = "While the data center demonstrates strengths in certain areas, targeted improvements, especially in energy reuse, are needed to enhance overall performance."

        return overall_status, details, conclusion

    def create_key_findings_section(self, pue, eer, co2, total_power, it_power, elements):
        """Enhanced Key Findings section combining executive summary with interactive elements"""

        # Calculate metrics
        loss = total_power - it_power
        loss_pct = (loss / total_power) * 100

        # Evaluation categories
        overall_status, details, conclusion = self.evaluate_data_center(pue, eer, co2, total_power)
        full_paragraph = " ".join(details + [conclusion])
        #print("Test parGR")

        # --- Executive Summary ---
        summary_content = [
            Paragraph("<b>EXECUTIVE SUMMARY</b>", self.header_style),
            Spacer(1, 5),
            Paragraph(full_paragraph,self.desc_style)
            # Paragraph(
            #     f"The data center demonstrates usage efficiency,with a PUE of  <b>{pue:.2f}</b>,, classified as font> against global benchmarks."
            #     f"(industry benchmark: 1.0-1.2=Excellent, 1.2-1.5=Good).The EER stands at <b>{eer:.2f}</b>, reflecting <font color='{self.secondary_color}'><b>{eer_eval}</b></font> energy efficiency "
            #     f"(optimal > 1.5 for most facilities).CO2 emissions are <b>{co2:.2f} kg/day</b>, classified as <font color='{self.secondary_color}'><b>{co2_eval}</b></font> "
            #     f"environmental impact.",
            #     self.desc_style
            # )


        ]

        # Power Loss Breakdown Table
        breakdown_data = [
            ['Category', 'Power (kW)', 'Percentage'],
            ['IT Equipment', f"{it_power:.2f}", f"{(it_power / total_power * 100):.1f}%"],
            ['Total Facility', f"{total_power:.2f}", "100%"]
        ]

        breakdown_table = Table(breakdown_data, colWidths=[150, 100, 100])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.primary_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F9FF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.secondary_color)),
        ]))

        # --- Interactive Elements ---
        interactive_content = [
            Spacer(1, 15),
            Paragraph("<b>QUICK ASSESSMENT</b>", self.subheader_style),
            Spacer(1, 5),
            Paragraph(
                f"<b>Operational Status:</b> {'✅ Optimal' if pue < 1.3 else '⚠️ Needs Attention'} | "
                f"<b>Savings Potential:</b> ${(loss * 0.15 * 24 * 365 * 0.12):.0f}/year with 15% overhead reduction",
                self.highlight_style
            ),
            Spacer(1, 10),
            Paragraph("<b>Efficiency Score</b>", self.subheader_style),
            self.create_efficiency_gauge((1 / pue + eer) * 50),  # Custom gauge method
            Paragraph(
                "<b>Scoring:</b> 90+ = Industry Leader | 80-89 = Good | <80 = Needs Improvement",
                self.desc_style
            )
        ]

        # Combine all elements
        elements.extend(summary_content)
        # elements.append(breakdown_table)
        # elements.extend(interactive_content)


    def create_efficiency_gauge(self, score):
        """Create visual gauge for efficiency score"""
        # For PDF we simulate a gauge with text and bars
        gauge_visual = [
            ["0", "=" * int(score / 5), f"{score:.1f}", "=" * int((100 - score) / 5), "100"],
            ["", "Current Score", "", "", ""]
        ]

        gauge_table = Table(gauge_visual, colWidths=[30, 100, 40, 100, 30])
        gauge_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('TEXTCOLOR', (2, 0), (2, 0), colors.HexColor(self.secondary_color)),
            ('FONTSIZE', (2, 0), (2, 0), 14),
            ('ALIGN', (1, 1), (3, 1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        return gauge_table