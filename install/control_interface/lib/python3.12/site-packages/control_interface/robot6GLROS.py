import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import serial.tools.list_ports
import time

# ========================
# Conexión con Arduino (detección automática)
# ========================
def conectar_arduino():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if 'ttyUSB' in p.device or 'ttyACM' in p.device:
            try:
                arduino = serial.Serial(p.device, 9600, timeout=1)
                time.sleep(2)
                print(f"✅ Conectado al Arduino en {p.device}")
                return arduino
            except Exception as e:
                print(f"❌ Fallo al conectar en {p.device}: {e}")
    print("⚠️ No se encontró Arduino conectado.")
    return None

arduino = conectar_arduino()

# ========================
# Variables globales
# ========================
trajectory = []

# ========================
# Cinemática directa
# ========================
def forward_kinematics(theta):
    l = [0.1] * 6
    x, y, z = [0], [0], [0]
    T = np.eye(4)
    for i in range(6):
        Ti = np.array([
            [np.cos(theta[i]), -np.sin(theta[i]), 0, l[i] * np.cos(theta[i])],
            [np.sin(theta[i]),  np.cos(theta[i]), 0, l[i] * np.sin(theta[i])],
            [0,                0,                1, 0],
            [0,                0,                0, 1]
        ])
        T = T @ Ti
        x.append(T[0, 3])
        y.append(T[1, 3])
        z.append(T[2, 3])
    return x, y, z

# ========================
# Enviar datos al Arduino
# ========================
def send_to_arduino():
    if arduino:
        angles = [int(max(0, var.get())) for var in theta_values]
        data = ",".join(map(str, angles)) + "\n"
        try:
            arduino.write(data.encode("utf-8"))
        except Exception as e:
            print(f"Error al enviar datos al Arduino: {e}")
    else:
        print("⚠️ Arduino no conectado.")

# ========================
# Actualizar robot
# ========================
def update_robot(*args):
    global trajectory
    theta = [max(0, var.get()) * np.pi / 180 for var in theta_values]
    x, y, z = forward_kinematics(theta)
    ax.clear()
    ax.set_xlim([-0.6, 0.6])
    ax.set_ylim([-0.6, 0.6])
    ax.set_zlim([0, 0.6])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.plot(x, y, z, marker='o', markersize=6, color='b')
    trajectory.append([x[-1], y[-1], z[-1]])
    if trajectory:
        traj_x, traj_y, traj_z = zip(*trajectory)
        traj_line.set_data(traj_x, traj_y)
        traj_line.set_3d_properties(traj_z)
    for i in range(6):
        angle_labels[i].config(text=f"{theta_values[i].get():.1f}°")
    canvas.draw()
    send_to_arduino()

# ========================
# Resetear trayectoria
# ========================
def reset_traj():
    global trajectory
    trajectory = []
    traj_line.set_data([], [])
    traj_line.set_3d_properties([])
    for var in theta_values:
        var.set(0)
    update_robot()

# ========================
# Interfaz gráfica
# ========================
root = tk.Tk()
root.title("Control Robot 6DOF")
root.configure(bg="#2C3E50")
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)

control_frame = tk.Frame(root, bg="#2C3E50")
control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

tk.Label(control_frame, text="Controles del Robot", bg="#2C3E50", fg="white", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10))

theta_values = [tk.DoubleVar(value=0) for _ in range(6)]
angle_labels = []
angle_sliders = []

for i in range(6):
    def make_update_fn(j):
        def on_change(value):
            update_robot()
        return on_change

    tk.Label(control_frame, text=f"Ángulo {i+1}:", bg="#2C3E50", fg="white", font=("Arial", 10)).grid(row=i+1, column=0, sticky="w", padx=5, pady=5)
    slider = ttk.Scale(control_frame, from_=0, to=180, variable=theta_values[i], orient="horizontal", length=200, command=make_update_fn(i))
    slider.grid(row=i+1, column=1, padx=5, pady=5)
    angle_sliders.append(slider)
    label = tk.Label(control_frame, text="0.0°", bg="#34495E", fg="white", font=("Arial", 10), width=6)
    label.grid(row=i+1, column=2, padx=5, pady=5)
    angle_labels.append(label)

ttk.Button(control_frame, text="Resetear Trayectoria", command=reset_traj).grid(row=7, column=0, columnspan=3, pady=10)

plot_frame = tk.Frame(root, bg="#2C3E50")
plot_frame.grid(row=0, column=1, padx=10, pady=10)

fig = plt.figure(figsize=(5, 4), facecolor="#2C3E50")
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor("#ecf0f1")
traj_line, = ax.plot([], [], [], 'r', label="Trayectoria")
ax.set_xlim([-0.6, 0.6])
ax.set_ylim([-0.6, 0.6])
ax.set_zlim([0, 0.6])
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.legend()

canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack()

update_robot()
root.mainloop()