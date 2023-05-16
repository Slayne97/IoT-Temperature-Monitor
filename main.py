from tkinter import *
import ttkbootstrap as ttk
import paho.mqtt.client as paho
from ttkbootstrap.constants import *
import RPi.GPIO as GPIO
import pygame
from PIL import Image, ImageTk
pygame.mixer.init()
pygame.mixer.music.load("alarm.wav")
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Create Window
root = ttk.Window(title="Temperature GUI", size=(1200,720), themename="darkly")
root.attributes("-fullscreen", True)


# Variables
temperature_int = 0
temperature_text = StringVar()
shooting_its_shown = False
fire_its_shown = False
balazos = False
fuego = False

# Fullscreen behaviour
def end_fullscreen(event):
    root.attributes("-fullscreen", False)


def enable_fullscreen(event):
    root.attributes("-fullscreen", True)

def stop_audio():
    pygame.mixer.music.stop()
    
    # Destroy all toplevels
    for widget in root.winfo_children():
        if isinstance(widget, Toplevel):
            widget.destroy()
    
    

def show_shooting_warning():
    global shooting_its_shown
    shooting_its_shown = True
    root.attributes("-fullscreen", False)
    
    new_window = Toplevel()
    new_window.attributes("-fullscreen", True)

    pygame.mixer.music.play(loops=-1)
    
    image_shooting_warning = PhotoImage(file="DISPAROS.png")
    new_window_background = Label(new_window)
    new_window_background.configure(image=image_shooting_warning)
    new_window_background.image = image_shooting_warning
    new_window_background.pack()
    new_window.protocol("WM_DELETE_WINDOW", stop_audio)
    
def show_fire_warning():
    global fire_its_shown
    fire_its_shown = True
    root.attributes("-fullscreen", False)
    
    new_window = Toplevel()
    new_window.attributes("-fullscreen", True)
    
    pygame.mixer.music.play(loops=-1)
    
    image_shooting_warning = PhotoImage(file="FUEGO.png")
    new_window_background = Label(new_window)
    new_window_background.configure(image=image_shooting_warning)
    new_window_background.image = image_shooting_warning
    new_window_background.pack()
    new_window.protocol("WM_DELETE_WINDOW", stop_audio)


    
# MQTT
def on_message(mosq, obj, msg):
    global temperature_int
    temperature_int = float(msg.payload)


def on_publish(mosq, obj, mid):
    pass


def read_sensor():    
	# MQTT Message handling
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish
    client.connect("127.0.0.1", 1883, 60)
    client.subscribe("My_Topic", 0)
    client.loop_start()


def update_values():

    label_room1_temperature["text"] = "Temperatura: " + str(temperature_int) + "°C"
    widget_temperature_c["amountused"] = temperature_int
    widget_temperature_f["amountused"] = (temperature_int * 9 / 5) + 32


    # Button behaviour
    global balazos
    input_state = GPIO.input(17)
    if input_state == False:
        balazos = True
        
    global fuego
    input_state2 = GPIO.input(5)
    if input_state2 == False:
        fuego = True

    if balazos and not shooting_its_shown:
        
        show_shooting_warning()
        
    if fuego and not fire_its_shown:
        pygame.mixer.music.play(loops=-1)
        show_fire_warning()


    if temperature_int > 20:
        widget_temperature_c["bootstyle"] = "danger"
        widget_temperature_f["bootstyle"] = "danger"
        label_room1_temperature["bootstyle"] = "inverse-danger"
        label_temp_indicator["bootstyle"] = "inverse-danger"
        label_temp_indicator["text"] = "¡¡¡ TEMPERATURA ALTA !!!"
    else:
        widget_temperature_c["bootstyle"] = "success"
        widget_temperature_f["bootstyle"] = "success"
        label_room1_temperature["bootstyle"] = "inverse-success"
        label_temp_indicator["bootstyle"] = "inverse-success"
        label_temp_indicator["text"] = "Temperatura Normal"


def loop_function():
    read_sensor()
    update_values()
    root.update()
    root.after(3000, loop_function)


def show_room_1():
    global background_image
    background_image = PhotoImage(file="ejemplo.png")
    canvas.itemconfigure(picture, image=background_image)


# Create frames
frame_side_pane = ttk.Frame(root, bootstyle="dark")
frame_side_pane.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=2, pady=2)

frame_image_display = ttk.Frame(root)
frame_image_display.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=2, pady=2)

frame_bottom_pane = ttk.Frame(root)
frame_bottom_pane.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=2, pady=2)

# Configure row/column weight (proportions)
root.grid_rowconfigure(0, weight=3)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# Create Canvas
canvas = Canvas(frame_image_display, width=1024, height=768, bg="white")
canvas.pack()

# Image widget
background_image = PhotoImage(file="seleccione_habitación.png")
picture = canvas.create_image(10,10, anchor=NW, image=background_image)

# Side widgets (rooms)
frame_room1 = ttk.Frame(frame_side_pane)
frame_room1.grid(row=0, column=0, sticky="nesw")

label_room1 = ttk.Label(frame_room1, text="Habitacion 1", justify=LEFT,  bootstyle="inverse-primary")
label_room1.grid(row=0, column=0, sticky="nesw", ipadx=40, ipady=6)

label_room1_temperature = ttk.Label(
    frame_room1,
    text="Temperatura= ",
    bootstyle="inverse-dark",
    justify=LEFT)
label_room1_temperature.grid(row=1, column=0, sticky="nesw", ipadx=40, ipady=10)

button_room1 = ttk.Button(frame_room1, text="Mostrar", bootstyle="info", command=show_room_1) # , command=show_room1
button_room1.grid(row=0, column=1, rowspan=2, sticky="nesw")


# Bottom Widgets
widget_temperature_c = ttk.Meter(
        master=frame_bottom_pane,
        padding=20,
        amounttotal=100,
        arcrange=180,
        arcoffset=-180,
        amountused=temperature_int,
        metertype="semi",
        bootstyle="dark",
        textright='°C',
        subtext='Temperatura',
        interactive=False,

    )
widget_temperature_c.grid(row=1, column=0)

widget_temperature_f = ttk.Meter(
        master=frame_bottom_pane,
        padding=20,
        amounttotal=200,
        arcrange=180,
        arcoffset=-180,
        amountused=temperature_int,
        metertype="semi",
        bootstyle="dark",
        textright='°F',
        subtext='Temperatura',
        interactive=False
    )
widget_temperature_f.grid(row=1, column=1)


label_temp_indicator = ttk.Label(frame_bottom_pane, text="Temperatura Normal", bootstyle="inverse-success", width=15, wraplength=100, justify="center")
label_temp_indicator.grid(row=1, column=2, sticky="ew", ipady=50, padx=2)

label_shooting_indicator = ttk.Label(frame_bottom_pane, text="Sin señales de Disparos", bootstyle="inverse-success", width=15, wraplength=100, justify="center")
label_shooting_indicator.grid(row=1, column=3, sticky="ew", ipady=50, padx=2)

label_fire_indicator = ttk.Label(frame_bottom_pane, text="Sin señales de Fuego", bootstyle="inverse-success", width=15, wraplength=100, justify="center")
label_fire_indicator.grid(row=1, column=4, sticky="ew", ipady=50, padx=2)


# Window full screen behaviour
root.bind("<Escape>", end_fullscreen)
root.bind("<F11>", enable_fullscreen)
root.after_idle(loop_function)
root.mainloop()
