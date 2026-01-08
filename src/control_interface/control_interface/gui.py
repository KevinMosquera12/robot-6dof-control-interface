import tkinter as tk
from tkinter import ttk
from control_interface.interface import RobotArmController
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

controller = RobotArmController()

root = tk.Tk()
root.title("Control Robot 6DOF")
root.configure(bg="#2C3E50")

theta_values = [tk.DoubleVar(value=0) for _ in range(6)]
angle_labels = []

# ========================
# Cinemática directa
# ========================
def forward_kinematics(theta):
    l = [0.1] * 6
    x, y, z = [0], [0], [0]
    T = np.eye(4)
    positions = [T[:3, 3].tolist()]
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
        positions.append(T[:3, 3].tolist())
    return x, y, z, positions

# ========================
# Dibujar un bloque 3D como eslabón
# ========================
def draw_block(ax, p1, p2, width=0.02):
    p1 = np.array(p1)
    p2 = np.array(p2)
    v = p2 - p1
    v_len = np.linalg.norm(v)
    if v_len == 0:
        return
    v = v / v_len
    not_v = np.array([1, 0, 0]) if abs(np.dot(v, [1, 0, 0])) < 0.99 else np.array([0, 1, 0])
    n1 = np.cross(v, not_v)
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(v, n1)
    n2 /= np.linalg.norm(n2)
    corners = []
    for dx in [-width/2, width/2]:
        for dy in [-width/2, width/2]:
            corners.append(p1 + dx * n1 + dy * n2)
            corners.append(p2 + dx * n1 + dy * n2)
    faces = [
        [corners[i] for i in [0,1,3,2]],
        [corners[i] for i in [4,5,7,6]],
        [corners[i] for i in [0,1,5,4]],
        [corners[i] for i in [2,3,7,6]],
        [corners[i] for i in [1,3,7,5]],
        [corners[i] for i in [0,2,6,4]],
    ]
    ax.add_collection3d(Poly3DCollection(faces, color='blue', alpha=0.7))

# ========================
# Enviar comando y actualizar visual
# ========================
def send_command(servo_id, scale):
    angle = int(scale.get())
    controller.move_servo(servo_id, angle)
    update_plot()

# ========================
# Interfaz de controles
# ========================
control_frame = tk.Frame(root, bg="#2C3E50")
control_frame.grid(row=0, column=0, padx=10, pady=10)

for i in range(6):
    label = tk.Label(control_frame, text=f"Servo {i}", bg="#2C3E50", fg="white")
    label.grid(row=i, column=0, padx=5, pady=5)

    scale = tk.Scale(control_frame, from_=0, to=180, orient=tk.HORIZONTAL, variable=theta_values[i], length=200)
    scale.grid(row=i, column=1, padx=5, pady=5)
    scale.bind("<ButtonRelease-1>", lambda e, i=i, s=scale: send_command(i, s))

    value_label = tk.Label(control_frame, textvariable=theta_values[i], bg="#2C3E50", fg="white")
    value_label.grid(row=i, column=2, padx=5)

    angle_labels.append(value_label)

# ========================
# Botón para reiniciar robot
# ========================
def reset_robot():
    global trajectory
    trajectory = []
    for i in range(6):
        theta_values[i].set(0)
        controller.move_servo(i, 0)
    update_plot()

reset_button = ttk.Button(control_frame, text="Reiniciar Robot", command=reset_robot)
reset_button.grid(row=7, column=0, columnspan=3, pady=10)

# ========================
# Panel gráfico 3D
# ========================
plot_frame = tk.Frame(root, bg="#2C3E50")
plot_frame.grid(row=0, column=1, padx=10, pady=10)

fig = plt.figure(figsize=(5, 5), facecolor="#2C3E50")
ax = fig.add_subplot(111, projection='3d')
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack()

trajectory = []
traj_line, = ax.plot([], [], [], 'r', label="Trayectoria")

# ========================
# Actualizar visual del robot
# ========================
def update_plot():
    angles = [theta.get() * np.pi / 180 for theta in theta_values]
    x, y, z, positions = forward_kinematics(angles)
    ax.clear()
    ax.set_facecolor("#ecf0f1")
    ax.set_xlim([-0.6, 0.6])
    ax.set_ylim([-0.6, 0.6])
    ax.set_zlim([0, 0.6])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    for i in range(len(positions)-1):
        draw_block(ax, positions[i], positions[i+1], width=0.03)

    trajectory.append(positions[-1])
    if trajectory:
        traj_x, traj_y, traj_z = zip(*trajectory)
        traj_line.set_data(traj_x, traj_y)
        traj_line.set_3d_properties(traj_z)

    ax.legend()
    canvas.draw()

update_plot()
root.mainloop()