from openpyxl import Workbook

# Create a new workbook and select the active sheet
wb = Workbook()
ws = wb.active

# Define the data for the schedule
data = """
Class  8A
Subject - Time
Subject2 - Time2
Class  8B
Subject - Time
Subject2 - Time2
"""

# Split the data into lines
lines = data.strip().split('\n')

# Write the data to the worksheet
for i, line in enumerate(lines, start=1):
    ws.cell(row=i, column=1).value = line

# Save the workbook to an Excel file
wb.save("school_schedule_custom.xlsx")
