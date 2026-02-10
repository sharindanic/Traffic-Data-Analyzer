import csv
import os
import tkinter as tk
from collections import defaultdict

# Task A: Input Validation
def validate_date_input():
    """
    Validates the user input for date, month, and year.
    Checks if the corresponding CSV file exists.
    """
    while True:
        try:
            date = int(input("Enter date between 1 to 31: "))
            if not (1 <= date <= 31):
                print("The entered date is out of range! Try again.")
                continue

            month = int(input("Enter a month (1 to 12): "))
            if not (1 <= month <= 12):
                print("The entered month is out of range! Try again.")
                continue

            year = int(input("Enter a year between 2000-2024: "))
            if not (2000 <= year <= 2024):
                print("The entered year is out of range! Try again.")
                continue

            file_path = f"traffic_data{date:02d}{month:02d}{year}.csv"
            if os.path.exists(file_path):
                print(f"File '{file_path}' found! Loading dataset...")
                return file_path
            else:
                print(f"File '{file_path}' does not exist! Try again.")
        except ValueError:
            print("Invalid input! Please try again.")

def validate_continue_input():
    """
    Asks the user if they want to continue with another dataset.
    """
    while True:
        user_input = input("Would you like to load another dataset (Y/N)? ").strip().upper()
        if user_input in ['Y', 'N']:
            return user_input
        print("Invalid input! Please enter 'Y' to continue or 'N' to stop.")

# Dynamically map CSV columns
def map_columns(headers, required_columns):
    """
    Dynamically maps CSV headers to required column names for flexibility.
    """
    mapped_columns = {}
    for req_col in required_columns:
        for header in headers:
            if header.lower().replace("_", "").replace(" ", "") == req_col.lower().replace("_", "").replace(" ", ""):
                mapped_columns[req_col] = header
                break
    return mapped_columns

# Task B: Process CSV Data
def process_csv_data(file_path):
    """
    Processes the CSV data and calculates outcomes.
    """
    try:
        with open(file_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            headers = csv_reader.fieldnames

            # Map required columns
            required_columns = ["JunctionName", "vehicleType", "travel_Direction_in", "travel_Direction_out",
                                "VehicleSpeed", "JunctionSpeedLimit", "elctricHybrid", "Weather_Conditions", "timeOfDay"]
            column_map = map_columns(headers, required_columns)
            if len(column_map) != len(required_columns):
                raise KeyError("Some required columns are missing in the CSV file!")

            # Initialize counters
            total_vehicles = total_trucks = total_electric_vehicles = 0
            total_two_wheeled = elm_rabbit_buses = 0
            no_turn_vehicles = over_speed = 0
            
            # count unique rainy hours 
            rainy_hours=set()
            #busiest hour per junction
            peak_hour_by_junction = defaultdict(lambda: defaultdict(int))
            

            for row in csv_reader:
                junction_name = row[column_map["JunctionName"]]
                vehicle_type = row[column_map["vehicleType"]].strip().lower()
                direction_in = row[column_map["travel_Direction_in"]].strip().lower()
                direction_out = row[column_map["travel_Direction_out"]].strip().lower()
                vehicle_speed = int(row[column_map["VehicleSpeed"]])
                junction_speed_limit = int(row[column_map["JunctionSpeedLimit"]])
                is_electric = row[column_map["elctricHybrid"]].strip().lower() == 'true'
                weather_condition = row[column_map["Weather_Conditions"]].strip().lower()
                time_of_day = row[column_map["timeOfDay"]]

                # Conditions
                total_vehicles += 1
                if vehicle_type == "truck":
                    total_trucks += 1
                if is_electric:
                    total_electric_vehicles += 1
                if vehicle_type in ['bicycle', 'scooter', 'motorcycle']:
                    total_two_wheeled += 1
                if direction_in == direction_out:
                    no_turn_vehicles += 1
                if vehicle_speed > junction_speed_limit:
                    over_speed += 1
                hour = time_of_day[:2]
                if "rain" in weather_condition:
                    rainy_hours.add(hour)

                peak_hour_by_junction[junction_name][hour] += 1
                
            hours_of_rain = len(rainy_hours)

            # Calculate busiest hours
            busiest_hours_by_junction = {}
            for junction, hour_counts in peak_hour_by_junction.items():
                if not hour_counts:
                    busiest_hours_by_junction[junction] = []
                    continue
                busiest_count = max(hour_counts.values())
                busiest_hours = [
                    f"between {h}:00 and {int(h)+1}:00"
                    for h, count in hour_counts.items()
                    if count == busiest_count
                ]
                busiest_hours_by_junction[junction] = busiest_hours


            outcomes = {
                "Total Vehicles": total_vehicles,
                "Total Trucks": total_trucks,
                "Total Electric Vehicles": total_electric_vehicles,
                "Total Two-Wheeled Vehicles": total_two_wheeled,
                "Vehicles Passing Without Turning": no_turn_vehicles,
                "Vehicles Over Speed Limit": over_speed,
                "Hours of Rain": hours_of_rain,
                "Busiest Hour(s) (Per Junction)": busiest_hours_by_junction,
            }
            display_results(outcomes)
            return outcomes
    except Exception as e:
        print(f"Error: {e}")
        return None

# Task B: Display Results
def display_results(outcomes):
    print("\nSummary of Results:")
    print("-" * 50)
    for key, value in outcomes.items():
        print(f"{key}: {value}")
    print("-" * 50)

# Task C: Save Results to File
def save_results_to_file(outcomes, file_name="results.txt"):
    with open(file_name, "a") as f:
        f.write("\nSummary of Results:\n")
        f.write("-" * 50 + "\n")
        for key, value in outcomes.items():
            f.write(f"{key}: {value}\n")
        f.write("-" * 50 + "\n")

# Task D: Histogram with Colors and Titles
class HistogramApp:
    def __init__(self, data, date):
        """
        Initializes the histogram application with traffic data and the selected date.
        """
        self.data = data
        self.date = date
        self.junction_data = {"Elm Avenue/Rabbit Road": defaultdict(int),
                              "Hanley Highway/Westway": defaultdict(int)}
        self.process_data()

    def process_data(self):
        """
        Processes the data to calculate vehicle counts by hour for each junction.
        Initializes all hours from 00:00 to 23:59 to ensure consistency.
        """
        # Initialize all 24 hours with 0 counts
        for hour in range(24):
            hour_str = f"{hour:02}"
            self.junction_data["Elm Avenue/Rabbit Road"][hour_str] = 0
            self.junction_data["Hanley Highway/Westway"][hour_str] = 0

        # Update counts from the CSV data
        for row in self.data:
            hour = row["timeOfDay"][:2]
            junction = row["JunctionName"]
            if junction in self.junction_data:
                self.junction_data[junction][hour] += 1

    def run(self):
        """
        Displays a graphical histogram using Tkinter Canvas with scrollbars for easy navigation.
        """
        root = tk.Tk()
        root.title(f"Traffic Volume Histogram - {self.date}")

        # Main frame and scrollbars
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=1)

        # Create canvas
        canvas = tk.Canvas(main_frame, bg="white")
        canvas.pack(side="left", fill="both", expand=1)

        # Add scrollbars
        v_scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
        h_scrollbar.pack(side="bottom", fill="x")

        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas
        chart_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=chart_frame, anchor="nw")

        # Chart settings
        bar_width = 20
        spacing = 10
        x_offset = 100
        y_offset = 50
        chart_height = 450
        max_count = max(max(j.values()) for j in self.junction_data.values())

        # Chart title
        tk.Label(chart_frame, text="Traffic Volume by Hour", font=("Arial", 16, "bold")).pack()

        # Create chart canvas
        chart_canvas = tk.Canvas(chart_frame, width=2400, height=chart_height + 100, bg="white")
        chart_canvas.pack()

        # Y-axis
        chart_canvas.create_line(x_offset, y_offset, x_offset, chart_height + y_offset, width=2)
        chart_canvas.create_text(x_offset - 30, chart_height // 2, text="Number of Vehicles", angle=90, font=("Arial", 12))

        # X-axis
        chart_canvas.create_line(x_offset, chart_height + y_offset, x_offset + 2500, chart_height + y_offset, width=2)
        chart_canvas.create_text(1300, chart_height + y_offset + 40, text="Hours of the Day", font=("Arial", 12))

        # Draw bars
        current_x = x_offset + spacing
        for hour in range(24):
            hour_str = f"{hour:02}"
            count_elm = self.junction_data["Elm Avenue/Rabbit Road"].get(hour_str, 0)
            count_hanley = self.junction_data["Hanley Highway/Westway"].get(hour_str, 0)

            # Scale bar height
            height_elm = (count_elm / max_count) * chart_height
            height_hanley = (count_hanley / max_count) * chart_height

            # Draw bars for each junction
            chart_canvas.create_rectangle(current_x, chart_height + y_offset - height_elm,
                                          current_x + bar_width, chart_height + y_offset,
                                          fill="blue", outline="blue")
            chart_canvas.create_rectangle(current_x + bar_width + spacing, chart_height + y_offset - height_hanley,
                                          current_x + 2 * bar_width + spacing, chart_height + y_offset,
                                          fill="green", outline="green")

            # Add hour labels
            chart_canvas.create_text(current_x + bar_width, chart_height + y_offset + 15, text=hour_str, font=("Arial", 8))

            # Increment x-position
            current_x += 2 * (bar_width + spacing)

        # Legend
        chart_canvas.create_text(2000, y_offset, text="Legend:", font=("Arial", 10, "bold"))
        chart_canvas.create_text(2100, y_offset, text="Elm Avenue/Rabbit Road: Blue", fill="blue", anchor="w")
        chart_canvas.create_text(2100, y_offset + 20, text="Hanley Highway/Westway: Green", fill="green", anchor="w")

        root.mainloop()

# Task E: Main Loop
def main():
    while True:
        file_path = validate_date_input()
        with open(file_path, "r") as file:
            data = list(csv.DictReader(file))
        outcomes = process_csv_data(file_path)
        if outcomes:
            save_results_to_file(outcomes)
            date = file_path.split("traffic_data")[-1].split(".csv")[0]
            HistogramApp(data, date).run()
        if validate_continue_input() == "N":
            print("Exiting... Goodbye!")
            break

if __name__ == "__main__":
    main()
