import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="qwerty",
    database="test"
)

def create_table_if_not_exists():
    # Create a table for BMI data if it does not exist
    with conn.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bmi_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                weight DOUBLE,
                height DOUBLE,
                bmi DOUBLE,
                category VARCHAR(255),
                timestamp DATETIME
            )
        ''')
    conn.commit()

# Call the function to create the table
create_table_if_not_exists()

def calculate_bmi():
    try:
        weight = weight_var.get()
        height = height_var.get()

        if not (0 < weight < 500) or not (0.5 < height < 2.5):
            raise ValueError("Weight and height must be within reasonable ranges.")

        bmi = weight / (height ** 2)
        category = classify_bmi(bmi)
        save_data(weight, height, bmi, category)
        show_bmi_result(bmi, category)
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def show_bmi_result(bmi, category):
    result_text = f"Your BMI is: {bmi:.2f}\nYou are classified as: {category}"
    messagebox.showinfo("BMI Result", result_text)

def classify_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"

def save_data(weight, height, bmi, category):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with conn.cursor() as cursor:
        cursor.execute('''
            INSERT INTO bmi_data (weight, height, bmi, category, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        ''', (weight, height, bmi, category, timestamp))
    conn.commit()

def view_history():
    with conn.cursor() as cursor:
        cursor.execute('''
            SELECT timestamp, weight, height, bmi, category
            FROM bmi_data
            ORDER BY timestamp DESC
        ''')
        data = cursor.fetchall()

    history_window = tk.Toplevel(root)
    history_window.title("BMI History")

    tree = ttk.Treeview(history_window)
    tree["columns"] = ("Timestamp", "Weight", "Height", "BMI", "Category")
    tree.heading("#0", text="ID")
    tree.column("#0", width=0, stretch=tk.NO)

    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)

    for row in data:
        tree.insert("", "end", values=row)

    tree.pack(expand=True, fill=tk.BOTH)

    trend_button = tk.Button(history_window, text="Show BMI Trend", command=lambda: show_bmi_trend(data, history_window))
    trend_button.pack(pady=10)

def show_bmi_trend(data, history_window):
    timestamps = [row[0] for row in data]
    bmis = [row[3] for row in data]

    fig, ax = plt.subplots()
    ax.bar(timestamps, bmis, color='blue', alpha=0.7)
    ax.set(xlabel='Timestamp', ylabel='BMI', title='BMI Trend Analysis')
    ax.grid()

    trend_frame = ttk.Frame(history_window)
    trend_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    canvas = FigureCanvasTkAgg(fig, master=trend_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    toolbar = tk.Frame(master=trend_frame)
    toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    toolbar_btn = tk.Button(master=toolbar, text="Quit", command=lambda: plt.close(fig))
    toolbar_btn.pack(side=tk.RIGHT)

if __name__ == "__main__":
    root = tk.Tk()

    weight_var = tk.DoubleVar()
    height_var = tk.DoubleVar()

    tk.Label(root, text="Weight (kg):").grid(row=0, column=0, padx=10, pady=10)
    tk.Entry(root, textvariable=weight_var).grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Height (m):").grid(row=1, column=0, padx=10, pady=10)
    tk.Entry(root, textvariable=height_var).grid(row=1, column=1, padx=10, pady=10)

    tk.Button(root, text="Calculate BMI", command=calculate_bmi).grid(row=2, column=0, columnspan=2, pady=10)
    tk.Button(root, text="View History", command=view_history).grid(row=3, column=0, columnspan=2, pady=10)

    root.mainloop()
