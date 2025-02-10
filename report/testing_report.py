import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from numpy.random import gumbel
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,Table as PlatypusTable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle


class PowerReport:
    def __init__(self, filename="Energy_Report.pdf"):
        self.filename = filename
        self.styles = getSampleStyleSheet()

    def generate_report(self, powerdata, cards, site_name,duration):
        self.data = pd.DataFrame(powerdata)
        self.data['time'] = pd.to_datetime(self.data['time'])
        self.final_colored_semi_gauge(self.data['power_efficiency'].mean(), 4, 'Power Usage Effectiveness',
                                      'Average PUE')
        self.final_colored_semi_gauge(self.data['energy_efficiency'].mean(), 2, 'Energy Efficiency Ratio',
                                      'Average EER')

        # Generate graphs
        self.generate_eer_graph()
        self.generate_pue_graph()


        # Create PDF Document
        doc = SimpleDocTemplate(self.filename, pagesize=landscape(letter))
        elements = []

        # Title Page
        title = Paragraph("<b>Energy Consumption Report</b>", self.styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 20))
        title = Paragraph(f"Duration : {duration}", self.styles["Heading1"])
        elements.append(title)
        elements.append(Spacer(1, 20))

        # Introduction
        intro = Paragraph(
            f"This report provides an analysis of energy consumption and efficiency trends for <b>{site_name}</b>.",
            self.styles["BodyText"])
        elements.append(intro)
        elements.append(Spacer(1, 20))

        # Card Summary Table
        def format_key(key):
            return key.replace('_', ' ').title()

        headers = [format_key(key) for key in cards.keys()]
        values =  [str(value) for value in cards.values()]

        table_data = [headers, values]
        col_widths = [150, 150, 150]  # Adjust as needed to increase width
        table = Table(table_data,col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.gray),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            # ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 2, colors.white),  # Thicker grid lines to simulate spacing
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Insert Gauges
        elements.append(Paragraph("<b>Average Metrics</b>", self.styles["Heading2"]))
        elements.append(Spacer(1, 10))
        gauge_images = [[Image("Power Usage Effectiveness.png", width=300, height=200),
                         Image("Energy Efficiency Ratio.png", width=300, height=200)]]
        gauge_table = PlatypusTable(gauge_images)
        elements.append(gauge_table)
        elements.append(Spacer(1, 10))

        # Explanation of Metrics
        elements.append(Paragraph("<b>Energy Efficiency and Power Usage Over Time</b>", self.styles["Heading2"]))
        elements.append(Spacer(1, 10))
        metrics_intro = Paragraph(
            "This section highlights performance metrics that provide insights into the efficiency and effectiveness of power utilization within the data center.",
            self.styles["BodyText"])
        elements.append(metrics_intro)
        elements.append(Spacer(1, 10))

        # Definitions of EER and PUE
        eer_definition = Paragraph(
            "<b>Energy Efficiency Ratio (EER):</b> EER is the ratio of the cooling output to the total electrical energy input (in watts). A higher EER indicates better energy efficiency.",
            self.styles["BodyText"])
        pue_definition = Paragraph(
            "<b>Power Usage Effectiveness (PUE):</b> PUE is a metric used to determine the energy efficiency of a data center by comparing the total amount of energy used by the facility to the energy used by the IT equipment alone. Lower PUE values indicate higher efficiency.",
            self.styles["BodyText"])

        elements.append(eer_definition)
        elements.append(Spacer(1, 10))
        elements.append(pue_definition)
        elements.append(Spacer(1, 20))


        # Insert Efficiency Charts
        elements.append(Image("eer_chart.png", width=500, height=200))
        elements.append(Spacer(1, 20))
        elements.append(Image("pue_chart.png", width=500, height=200))
        elements.append(Spacer(1, 20))

        # Conclusion
        avg_eer = self.data['energy_efficiency'].mean()
        logging.info(f"Average EER: {avg_eer}")
        conclusion_text = "Overall site is performing up to mark." if avg_eer >= 1 else "Overall site is NOT performing up to mark."
        conclusion = Paragraph(f"<b>Conclusion:</b> {conclusion_text}", self.styles["Heading2"])
        elements.append(conclusion)

        # Define styles
        styles = getSampleStyleSheet()

        header_style = ParagraphStyle(name='Title', parent=styles['Heading1'], fontSize=14, alignment=1, spaceAfter=12)
        stat_style = ParagraphStyle(name='Number', parent=styles['Title'], fontSize=24, textColor=colors.darkblue,
                                      alignment=1)
        desc_style = ParagraphStyle(name='Description', parent=styles['BodyText'], fontSize=10, alignment=1,
                                    textColor=colors.black)

        title = Paragraph("UNITED NATIONS HELPS TO TACKLE COVID-19 AND REACH SUSTAINABLE DEVELOPMENT GOALS",
                          header_style)
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Table Data (Each cell has a statistic and description)
        data = [
            [Paragraph("<b>162</b>", stat_style), Paragraph("<b>$17B</b>", stat_style),
             Paragraph("<b>77M</b>", stat_style)],
            [Paragraph("countries and territories supported to rescue the Goals", desc_style),
             Paragraph("delivered in operational activities for development", desc_style),
             Paragraph("tons of CO₂ emissions prevented through clean energy initiatives with UN support", desc_style)],

            [Paragraph("<b>$95M</b>", stat_style), Paragraph("<b>138M</b>", stat_style),
             Paragraph("<b>183M</b>", stat_style)],
            [Paragraph("in trade investment deals facilitated by support to South-South agreements", desc_style),
             Paragraph("workers protected from work-related deaths, injuries, and disease", desc_style),
             Paragraph("children supported with access to remote learning", desc_style)]
        ]

        # Define column widths to spread them evenly
        col_widths = [180, 180, 180]

        # Create the table
        table = Table(data, colWidths=col_widths)

        # Apply styles
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightblue),  # Second row header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),  # Header text color
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.darkblue),  # Second row header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical center alignment
            ('FONTSIZE', (0, 0), (-1, -1), 12),  # Set font size
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Add space inside cells
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Optional grid lines
        ]))

        # Add the table to the elements
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], fontSize=14, alignment=1, spaceAfter=12)
        number_style = ParagraphStyle(name='Number', parent=styles['Title'], fontSize=24, textColor=colors.darkblue,
                                      alignment=1)
        desc_style = ParagraphStyle(name='Description', parent=styles['BodyText'], fontSize=10, alignment=1,
                                    textColor=colors.black)

        # Add Title
        title = Paragraph("UNITED NATIONS HELPS TO TACKLE COVID-19 AND REACH SUSTAINABLE DEVELOPMENT GOALS",
                          title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))

        # Table data: two rows, three columns
        data = [
            [
                Paragraph("<b>162</b>", number_style),
                Paragraph("<b>$17B</b>", number_style),
                Paragraph("<b>77M</b>", number_style)
            ],
            [
                Paragraph("countries and territories supported to rescue the Goals", desc_style),
                Paragraph("delivered in operational activities for development", desc_style),
                Paragraph(
                    "tons of CO₂ emissions prevented through clean energy initiatives with United Nations support",
                    desc_style)
            ],
            [
                Paragraph("<b>$95M</b>", number_style),
                Paragraph("<b>138M</b>", number_style),
                Paragraph("<b>183M</b>", number_style)
            ],
            [
                Paragraph("in trade investment deals facilitated by support to South-South agreements", desc_style),
                Paragraph("workers protected from work-related deaths, injuries and disease", desc_style),
                Paragraph("children supported with access to remote learning", desc_style)
            ]
        ]

        # Define column widths
        col_widths = [170, 170, 170]

        # Create the table
        table = Table(data, colWidths=col_widths, hAlign='CENTER')

        # Apply table styling
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),  # Light background for entire table
            ('TEXTCOLOR', (0, 0), (-1, 1), colors.darkblue),  # Blue text for numbers
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align text
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically center text
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Padding for spacing
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            # Remove grid lines to match the clean look
        ]))

        # Add table to elements
        elements.append(table)
        elements.append(Spacer(1, 20))
        # Save PDF
        doc.build(elements)
        print("Report generated successfully: ", self.filename)

    def generate_pie_charts(self):
        avg_eer = self.data['energy_efficiency'].mean()
        max_pue = 4.0
        avg_pue = self.data['power_efficiency'].mean()
        # avg_power = self.data[['total_POut', 'total_PIn']].mean().mean()

        # Ensure values are non-negative
        avg_eer = max(avg_eer, 0)
        avg_pue = max(avg_pue, 0)
        # avg_power = max(avg_power, 0)

        # Define the segments and their labels
        sections = {
            "Efficient": (0, 1.5, '#70cf86'),
            "Moderate": (1.5, 2.0, '#1678b5'),
            "Inefficient": (2.0, max_pue, '#f5113b')
        }

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': 'polar'})
        ax.set_theta_offset(np.pi)  # Rotate to start from left
        ax.set_theta_direction(-1)  # Counter-clockwise

        # Remove grid and y-ticks
        ax.set_axis_off()

        # Draw sections
        for label, (start, end, color) in sections.items():
            theta1 = np.pi * (start / max_pue)
            theta2 = np.pi * (end / max_pue)
            ax.barh(1, theta2 - theta1, left=theta1, height=0.5, color=color, edgecolor='white')

            # Place section labels
            angle = (theta1 + theta2) / 2
            ax.text(angle, 1.3, label, ha='center', va='center', fontsize=10,
                    rotation=np.degrees(angle - np.pi / 2))

        # Draw the needle
        needle_angle = np.pi * (avg_pue / max_pue)
        ax.arrow(needle_angle, 0, 0, 0.8, width=0.02, head_width=0.08, head_length=0.1, fc='black', ec='black')

        # Display the PUE value in the center
        ax.text(0, -0.2, f'{avg_pue:.1f}', ha='center', va='center', fontsize=22, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))

        # Title
        plt.title('Power Usage Effectiveness (PUE)', fontsize=16, fontweight='bold', pad=20)

        plt.show()

    def generate_eer_graph(self):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_xlabel("Duration")
        ax.set_ylabel("EER (PowerOut/PowerIn)", color='tab:blue')
        ax.plot(self.data['time'], self.data['energy_efficiency'], marker='o', color='tab:blue', label='EER')
        ax.tick_params(axis='y', labelcolor='tab:blue')
        ax.set_ylim(0, 2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if self.data['time'].dt.time.nunique() == 1 and self.data['time'].dt.time.iloc[0] == pd.Timestamp(
                '00:00:00').time():
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        plt.title("Energy Efficiency Over Time")
        fig.tight_layout()
        plt.grid(False)
        plt.savefig("eer_chart.png", dpi=300, bbox_inches='tight', pad_inches=0.1)
        plt.close()

    def generate_pue_graph(self):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_xlabel("Duration")
        ax.set_ylabel("PUE (PowerOut/PowerIn)", color='tab:green')
        ax.plot(self.data['time'], self.data['power_efficiency'], marker='o', color='tab:green', label='PUE')
        ax.tick_params(axis='y', labelcolor='tab:green')
        ax.set_ylim(0, 2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if self.data['time'].dt.time.nunique() == 1 and self.data['time'].dt.time.iloc[0] == pd.Timestamp(
                '00:00:00').time():
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        plt.title("Power Usage Effectiveness Over Time")
        fig.tight_layout()
        plt.grid(False)
        plt.savefig("pue_chart.png", dpi=300, bbox_inches='tight', pad_inches=0.1)
        plt.close()

    def generate_pie_charts(self):
        avg_eer = self.data['energy_efficiency'].mean()
        max_pue = 4.0
        avg_pue = self.data['power_efficiency'].mean()

        # Ensure values are non-negative
        avg_eer = max(avg_eer, 0)
        avg_pue = max(avg_pue, 0)

        # Define the segments and their labels
        sections = {
            "Efficient": (0, 1.5, '#70cf86'),
            "Moderate": (1.5, 2.0, '#1678b5'),
            "Inefficient": (2.0, max_pue, '#f5113b')
        }

        # Create semi-gauge chart
        fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': 'polar'})
        ax.set_theta_offset(np.pi)  # Rotate to start from left
        ax.set_theta_direction(-1)  # Counter-clockwise
        ax.set_axis_off()  # Remove grid and ticks


        # Draw sections
        for label, (start, end, color) in sections.items():
            theta1 = np.pi * (start / max_pue)
            theta2 = np.pi * (end / max_pue)
            ax.barh(1, theta2 - theta1, left=theta1, height=0.5, color=color, edgecolor='white')

        # Determine color based on avg_pue
        if avg_pue <= 1.5:
            gauge_color = '#70cf86'  # Green
        elif 1.5 < avg_pue <= 2.0:
            gauge_color = '#1678b5'  # Blue
        else:
            gauge_color = '#f5113b'  # Red

        # Draw the filled arc for avg_pue
        needle_angle = np.pi * (avg_pue / max_pue)
        ax.barh(1, needle_angle, left=0, height=0.5, color=gauge_color)
        ax.barh(1, np.pi - needle_angle, left=needle_angle, height=0.5, color='lightgrey')

        # Display the PUE value in the center
        ax.text(0, 0, f'{avg_pue:.1f}', ha='center', va='center', fontsize=28, fontweight='bold')
        ax.text(0, -0.3, 'Average', ha='center', va='center', fontsize=10, color='grey')

        # Title
        plt.title('Power Usage Effectiveness (PUE)', fontsize=16, fontweight='bold', pad=20)
        plt.show()

    def generate_eer_graph(self):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_xlabel("Duration")
        ax.set_ylabel("EER (PowerOut/PowerIn)", color='tab:blue')
        ax.plot(self.data['time'], self.data['energy_efficiency'], marker='o', color='tab:blue', label='EER')
        ax.tick_params(axis='y', labelcolor='tab:blue')
        ax.set_ylim(0, 2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if self.data['time'].dt.time.nunique() == 1 and self.data['time'].dt.time.iloc[0] == pd.Timestamp(
                '00:00:00').time():
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        plt.title("Energy Efficiency Over Time")
        fig.tight_layout()
        plt.grid(False)
        plt.savefig("eer_chart.png", dpi=300, bbox_inches='tight', pad_inches=0.1)
        plt.close()

    def generate_pue_graph(self):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_xlabel("Duration")
        ax.set_ylabel("PUE (PowerOut/PowerIn)", color='tab:green')
        ax.plot(self.data['time'], self.data['power_efficiency'], marker='o', color='tab:green', label='PUE')
        ax.tick_params(axis='y', labelcolor='tab:green')
        ax.set_ylim(0, 2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if self.data['time'].dt.time.nunique() == 1 and self.data['time'].dt.time.iloc[0] == pd.Timestamp(
                '00:00:00').time():
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        plt.title("Power Usage Effectiveness Over Time")
        fig.tight_layout()
        plt.grid(False)
        plt.savefig("pue_chart.png", dpi=300, bbox_inches='tight', pad_inches=0.1)
        plt.close()

    def final_colored_semi_gauge(self, value, max_value, title, unit_label):
        if value <= 1.5:
            gauge_color = '#70cf86'  # Green
        elif 1.5 < value <= 2.0:
            gauge_color = '#1678b5'  # Blue
        else:
            gauge_color = '#f5113b'  # Red

        fig, ax = plt.subplots(figsize=(6, 4), subplot_kw={'projection': 'polar'})
        ax.set_theta_offset(np.pi)
        ax.set_theta_direction(-1)
        ax.set_axis_off()

        angle = np.pi * (value / max_value)
        ax.barh(1, angle, left=0, height=0.3, color=gauge_color)
        ax.barh(1, np.pi - angle, left=angle, height=0.3, color='lightgrey')

        ax.text(0.5, 0, f'{value:.1f}', ha='center', va='center', fontsize=32, fontweight='bold')
        # ax.text(0, -0.3, unit_label, ha='center', va='center', fontsize=12, color='grey')

        plt.title(title, fontsize=14, color='grey', pad=20)
        # ax.text(-np.pi / 2, 1.2, '0', ha='center', va='center', fontsize=10, color='grey')
        # ax.text(np.pi / 2, 1.2, f'{int(max_value)}', ha='center', va='center', fontsize=10, color='grey')

        plt.tight_layout()
        plt.savefig(f"{title}.png")
        plt.close()
        # plt.show()
