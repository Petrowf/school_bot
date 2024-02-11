import pandas as pd

# Read the Excel file
df = pd.read_excel('school_schedule_custom.xlsx', engine='openpyxl', header=None)


# Function to get the subjects and times by class
def get_subjects_and_times_by_class(df, class_name):
    # Find the rows where the class name appears
    class_rows = df[df[0].str.contains(class_name, na=False)].index

    # Extract the subjects and times for the class
    class_schedule = []
    for row in class_rows:
        next_row = row + 1
        while next_row < len(df) and not df.iloc[next_row][0].startswith('Класс'):
            subject_time = df.iloc[next_row][0].split(' - ')
            class_schedule.append({
                'Урок': subject_time[0],
                'Время': subject_time[1]
            })
            next_row += 1

    # Convert the list of dictionaries to a DataFrame
    class_schedule_df = pd.DataFrame(class_schedule)
    return class_schedule_df


# Example usage: Get the subjects and times for Class  8A
timetable = get_subjects_and_times_by_class(df, "Класс 8A")
print(timetable)
