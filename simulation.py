import math
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Connect to MySQL database
# conn = mysql.connector.connect(
#     host = "localhost",
#     user = "root",
#     passwd = "qwerty",
#     database = "simulation"
# )

# def create_table_if_not_exists():
#     # Create a table for BMI data if it does not exist
#     with conn.cursor() as cursor:
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS simulation (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 c DOUBLE, w DOUBLE, k DOUBLE, a DOUBLE,
#                 theta_f DOUBLE, beta DOUBLE,
#                 d DOUBLE, b DOUBLE,
#                 in_diam DOUBLE, out_diam DOUBLE,
#                 area DOUBLE, peak_pressure DOUBLE,
#                 x1 DOUBLE, x2 DOUBLE,
#                 temp1 DOUBLE, temp2 DOUBLE, temp3 DOUBLE
#             )
#         ''')
#     conn.commit()

# # Call the function to create the table
# create_table_if_not_exists()

# Gloabal variable
gamma = 1.26

# Calculating value of a
def calculate_a(charge_mass, seat_weight, chamber_vol):
    a = 6823 * (charge_mass/seat_weight)**0.5 * (27.68 * (charge_mass/chamber_vol))**((gamma-1)/2)
    return a

# Calculating value of b
def calculate_b(charge_mass, seat_weight, chamber_vol, form_factor, burning_rate, web_thickness):
    q = (1+form_factor) * (burning_rate/web_thickness)
    b = q * (1 - (27.68 * charge_mass/chamber_vol) / (1/17.6)) * (chamber_vol/seat_weight)**(2/3)
    return q, b

# Calculating velocity of seat
def calculate_v(self, distance):
    v = (self.a * distance) / (self.b + distance)
    return v

# Calculating area
def calculate_area(in_diam, out_diam):
    area = (math.pi)/8 * (in_diam**2 + out_diam**2)
    return area
    
# Calculating peak pressure
def calculate_peakpressure(self, seat_weight, g):
    peak_pressure = (4.48*seat_weight / (27*self.b)) * (self.a**2 / (g*self.area))
    peak_pressure *= 0.006895
    return peak_pressure

# Calculating peak rate of rise of acceleration
def calculate_peak_rate_of_rise_of_acceleration(self, seat_weight, g):
    x1 = (self.b/12) * (8+6.324)
    x2 = (self.b/12) * (8-6.324)

    # Calculating (dp/dt)max
    temp1 = (1.12*seat_weight*self.b/g) * (self.a**2/self.area)
    temp2 = (self.b*self.a*x2 - 2*self.a*(x2**2)) / (math.pow(self.b+x2,5))
    peak_rate_of_rise_of_acceleration = (temp1*temp2) / 32.2
    peak_rate_of_rise_of_acceleration *= 0.5078

    return x1, x2, peak_rate_of_rise_of_acceleration

class SimulationApp:
    def __init__(self, master):
        self.master = master
        self.master.title('Simulation App')

        custom_font = ('Arial', 11)

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill = 'both', expand = True)

        self.create_page_a(custom_font)
        self.create_page_b(custom_font)
        self.create_page_peak_rate_of_rise_of_acceleration(custom_font)

        self.a = None
        self.q = None
        self.b = None
        self.area = None

    def create_page_a(self, custom_font):
        page_a = ttk.Frame(self.notebook)
        self.notebook.add(page_a, text = "Calculation of a")

        tk.Label(page_a, text = "Enter charge mass (lb):", font = custom_font).pack(pady=10) #constant
        entry_charge_mass = tk.Entry(page_a)
        entry_charge_mass.pack(pady=10)

        tk.Label(page_a, text = "Enter weight of seat-man combination (kg):", font = custom_font).pack(pady=10) #constant
        entry_seat_weight = tk.Entry(page_a)
        entry_seat_weight.pack(pady=10)

        tk.Label(page_a, text = "Enter chamber volume in (m^3):", font = custom_font).pack(pady=10) #constant
        entry_chamber_vol = tk.Entry(page_a)
        entry_chamber_vol.pack(pady=10)

        tk.Label(page_a, text = "Enter distance travelled along the barrel at any time (m):", font = custom_font).pack(pady=10) #constant
        entry_distance = tk.Entry(page_a)
        entry_distance.pack(pady=10)

        button = tk.Button(page_a, text = "Calculate", font = custom_font, command = lambda:self.show_next_a(
            entry_charge_mass, entry_seat_weight, entry_chamber_vol, entry_distance))
        button.pack(pady=10)

    def show_next_a(self, entry_charge_mass, entry_seat_weight, entry_chamber_vol, entry_distance):
        self.charge_mass = float(entry_charge_mass.get())
        self.seat_weight = float(entry_seat_weight.get())
        self.chamber_vol = float(entry_chamber_vol.get())
        self.distance = float(entry_distance.get())

        self.a = calculate_a(self.charge_mass, self.seat_weight, self.chamber_vol)
        result_a = f"The calculated value of a is: {self.a}\n"
        messagebox.showinfo("Result", result_a)
        self.notebook.select(1)

    def create_page_b(self, custom_font):
        page_b = ttk.Frame(self.notebook)
        self.notebook.add(page_b, text = "Calculation of b")

        tk.Label(page_b, text = "Enter form factor of propellent grain:", font = custom_font).pack(pady=10) #constant
        entry_form_factor = tk.Entry(page_b)
        entry_form_factor.pack(pady=10)

        tk.Label(page_b, text = "Enter burning rate (mm/s):", font = custom_font).pack(pady=10) #constant
        entry_burning_rate = tk.Entry(page_b)
        entry_burning_rate.pack(pady=10)

        tk.Label(page_b, text = "Enter propellent web thickness (mm):", font = custom_font).pack(pady=10)
        entry_web_thickness = tk.Entry(page_b)
        entry_web_thickness.pack(pady=10)

        tk.Label(page_b, text = "Enter time (ms):", font = custom_font).pack(pady=10)
        entry_time = tk.Entry(page_b)
        entry_time.pack(pady=10)

        button = tk.Button(page_b, text = "Calculate", font = custom_font, command = lambda:self.show_next_b(
            entry_form_factor, entry_burning_rate, entry_web_thickness, entry_time))
        button.pack(pady=10)

    def show_next_b(self, entry_form_factor, entry_burning_rate, entry_web_thickness, entry_time):
        form_factor = float(entry_form_factor.get())
        burning_rate = float(entry_burning_rate.get())
        web_thickness = float(entry_web_thickness.get())
        time = float(entry_time.get())

        self.q, self.b = calculate_b(self.charge_mass, self.seat_weight, self.chamber_vol, form_factor, burning_rate, web_thickness)
        self.v = calculate_v(self, self.distance)
        result_b = f"The quickness of propellant is: {self.q}\n"
        result_b += f"The calculated value of b is: {self.b} ft\n"
        result_b += f"The velocity of seat at any instant of time is: {self.v} m/s"
        messagebox.showinfo("Result", result_b)
        self.notebook.select(2)

    def create_page_peak_rate_of_rise_of_acceleration(self, custom_font):
        page_area = ttk.Frame(self.notebook)
        self.notebook.add(page_area, text = "Calculation of Peak rate of rise of Acceleration")

        tk.Label(page_area, text = "Enter inner diameter of the tube (in):", font = custom_font).pack(pady=10)
        entry_in_diam = tk.Entry(page_area)
        entry_in_diam.pack(pady=10)

        tk.Label(page_area, text = "Enter outer diameter of the tube in (in):", font = custom_font).pack(pady=10)
        entry_out_diam = tk.Entry(page_area)
        entry_out_diam.pack(pady=10)

        tk.Label(page_area, text = "Enter mass fraction of propellant burnt:", font = custom_font).pack(pady=10)
        entry_mass_fraction = tk.Entry(page_area)
        entry_mass_fraction.pack(pady=10)

        tk.Label(page_area, text = "Enter value of g:", font = custom_font).pack(pady=10)
        entry_g = tk.Entry(page_area)
        entry_g.pack(pady=10)

        button = tk.Button(page_area, text = "Calculate", font = custom_font, 
                    command = lambda:self.show_next_peak_rate_of_rise_of_acceleration(entry_in_diam, entry_out_diam, 
                                                                    entry_mass_fraction, entry_g))
        button.pack(pady=10)

    def show_next_peak_rate_of_rise_of_acceleration(self, entry_in_diam, entry_out_diam, entry_mass_fraction, entry_g):
        in_diam = float(entry_in_diam.get())
        out_diam = float(entry_out_diam.get())
        mass_fraction = float(entry_mass_fraction.get())
        g = float(entry_g.get())

        self.area = calculate_area(in_diam, out_diam)
        self.peak_pressure = calculate_peakpressure(self, self.seat_weight, g)
        result_message = f"The calculated Area is: {self.area} sq. inch\n"
        result_message += f"The calculated Peak Pressure is: {self.peak_pressure} MPa"
        messagebox.showinfo("Result", result_message)

        x1, x2, peak_rate_of_rise_of_acceleration = calculate_peak_rate_of_rise_of_acceleration(self, self.seat_weight, g)
        result_x1_x2 = f"x1 = {x1} ft\n"
        result_x1_x2 += f"x2 = {x2} ft\n"
        result_x1_x2 += f"Peak rate of rise of Acceleration is: {peak_rate_of_rise_of_acceleration} g/s\n"
        messagebox.showinfo("Result", result_x1_x2)

        self.notebook.select(3)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x600")
    app = SimulationApp(root)
    root.mainloop()