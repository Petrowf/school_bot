from openpyxl import Workbook

# Create a new workbook and select the active sheet
wb = Workbook()
ws = wb.active

# Define the data for the schedule
data = """
Класс 8A
Математика - 23:00-0:00
Русский - 0:00-3:00
Класс 8B
Математика - 22:00-0:00
Русский - 0:00-3:00
"""

# Split the data into lines
lines = data.strip().split('\n')

# Write the data to the worksheet
for i, line in enumerate(lines, start=1):
    ws.cell(row=i, column=1).value = line

# Save the workbook to an Excel file
wb.save("school_schedule_custom.xlsx")
