import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk

from qr_coder import generate_qr

WIDTH, HEIGHT = 800, 900

# ---------------- App + Canvas ----------------
root = tk.Tk()
root.title("QR Generator")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.resizable(True, True)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, highlightthickness=0)
canvas.pack()

# ---------------- State ----------------
current_color = "#D7AF28"
current_logo = None
current_qr_image = None
preview_tk = None
logo_tk = None

# ---------------- Background ----------------
canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#616161", outline="")
canvas.create_rectangle(0, 214, WIDTH, HEIGHT, fill="#D9D9D9", outline="")

# ---------------- Title ----------------
canvas.create_text(
    WIDTH // 2, 100,
    text="Type URL or sentence!",
    fill="white",
    font=("Arial", 20, "bold")
)

# ---------------- Search ----------------
search_entry = tk.Entry(root, bd=0, justify="center", font=("Arial", 14))
search_entry.place(x=165, y=123, width=471, height=43)

# ---------------- Color Picker ----------------
canvas.create_text(194, 232, text="Color :", font=("Arial", 14))

color_preview = canvas.create_oval(
    169, 251, 218, 300,
    fill=current_color, outline=""
)

def pick_color(event=None):
    global current_color
    c = colorchooser.askcolor()[1]
    if c:
        current_color = c
        canvas.itemconfig(color_preview, fill=c)

canvas.tag_bind(color_preview, "<Button-1>", pick_color)

def reset_color():
    global current_color
    current_color = "#000000"
    canvas.itemconfig(color_preview, fill=current_color)

tk.Button(root, text="reset", command=reset_color,
          bg="#646464", fg="white", bd=0).place(x=163, y=309, width=60, height=23)

# ---------------- Logo Picker ----------------
canvas.create_text(399, 232, text="Inside logo :", font=("Arial", 14))

default_logo = Image.new("RGB", (50, 50), "#cccccc")
default_logo_tk = ImageTk.PhotoImage(default_logo)

logo_preview = canvas.create_image(399, 276, image=default_logo_tk)

def pick_logo(event=None):
    global current_logo, logo_tk
    path = filedialog.askopenfilename(
        filetypes=[("Images", "*.png *.jpg *.jpeg")]
    )
    if not path:
        return

    current_logo = path
    img = Image.open(path).resize((50, 50))
    logo_tk = ImageTk.PhotoImage(img)
    canvas.itemconfig(logo_preview, image=logo_tk)

canvas.tag_bind(logo_preview, "<Button-1>", pick_logo)

def reset_logo():
    global current_logo
    current_logo = None
    canvas.itemconfig(logo_preview, image=default_logo_tk)

tk.Button(root, text="reset", command=reset_logo,
          bg="#646464", fg="white", bd=0).place(x=369, y=311, width=60, height=23)

# ---------------- Logo Size ----------------
canvas.create_text(609, 232, text="Logo size :", font=("Arial", 14))

logo_size = tk.IntVar(value=22)

slider = tk.Scale(
    root, from_=10, to=40,
    orient="horizontal", variable=logo_size,
    showvalue=False, length=110, bg="#D9D9D9"
)
slider.place(x=554, y=262)

size_label = canvas.create_text(609, 305, text="22%", font=("Arial", 14, "bold"))

def update_size(val):
    canvas.itemconfig(size_label, text=f"{val}%")

slider.config(command=update_size)

# ---------------- QR Preview ----------------
canvas.create_rectangle(301, 452, 498, 649, fill="white", outline="")
qr_preview_id = canvas.create_image(WIDTH // 2, 550)

# ---------------- Generate ----------------
def on_generate_click():
    global current_qr_image, preview_tk

    data = search_entry.get().strip()
    if not data:
        return

    current_qr_image = generate_qr(
        data=data,
        qr_color=current_color,
        bg_color="white",
        logo_path=current_logo,
        logo_percent=logo_size.get()
    )

    preview = current_qr_image.resize((197, 197))
    preview_tk = ImageTk.PhotoImage(preview)
    canvas.itemconfig(qr_preview_id, image=preview_tk)

tk.Button(root, text="Generate!", bg="#6B3030", fg="white",
          bd=0, command=on_generate_click).place(x=268, y=383, width=265, height=34)

# ---------------- Save ----------------
def on_save_click():
    if not current_qr_image:
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")]
    )
    if path:
        current_qr_image.save(path)

tk.Button(root, text="Save!", bg="#6B3030", fg="white",
          bd=0, command=on_save_click).place(x=268, y=698, width=265, height=34)
