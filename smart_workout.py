import time
import datetime
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import pygame
import os
import json
import pyttsx3
from plyer import notification

# Workout plans
WORKOUT_PLANS = {
    "Beginner": """🔥 Beginner Workout 🔥
- 5 Squats
- 5 Push-ups
- 15s Plank
- 15s Jump Rope
- 2 min Jogging
Stay strong! 💪""",
    
    "Intermediate": """🔥 Intermediate Workout 🔥
- 10 Squats
- 8 Push-ups
- 30s Plank
- 30s Jump Rope
- 5 min Jogging
Stay strong! 💪""",
    
    "Advanced": """🔥 Advanced Workout 🔥
- 15 Squats
- 12 Push-ups
- 45s Plank
- 1 min Jump Rope
- 10 min Jogging
Stay strong! 💪"""
}

# Initialize pygame mixer for alarm sounds
pygame.mixer.init()

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)

# Files to store alarms and settings
ALARM_FILE = "alarms.json"
SETTINGS_FILE = "settings.json"

# Alarm times and settings
alarm_times = []
settings = {
    "alarm_sound": "default_alarm.mp3",  # Ensure this file exists or let user select
    "workout_plan": "Intermediate"
}

# Function to load stored alarms
def load_alarms():
    global alarm_times
    if os.path.exists(ALARM_FILE):
        try:
            with open(ALARM_FILE, "r") as f:
                alarm_times = json.load(f)
        except:
            alarm_times = []

# Function to save alarms
def save_alarms():
    with open(ALARM_FILE, "w") as f:
        json.dump(alarm_times, f)

# Function to load settings
def load_settings():
    global settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
        except:
            pass  # Use default settings

# Function to save settings
def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

# Function to play alarm sound
def play_alarm():
    try:
        if not os.path.exists(settings["alarm_sound"]):
            print(f"Alarm sound not found: {settings['alarm_sound']}")
            return
        pygame.mixer.music.load(settings["alarm_sound"])
        pygame.mixer.music.play(-1)  # Loop indefinitely
    except Exception as e:
        print(f"Error playing alarm: {e}")

# Function to stop alarm
def stop_alarm(popup):
    pygame.mixer.music.stop()
    popup.destroy()

# Function to snooze alarm (5 min)
def snooze_alarm(popup):
    pygame.mixer.music.stop()
    popup.destroy()
    snooze_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    alarm_times.append((snooze_time.hour, snooze_time.minute))
    save_alarms()
    print(f"Snoozed until {snooze_time.hour}:{snooze_time.minute}")

# Function to read workout plan aloud
def speak_workout():
    engine.say(WORKOUT_PLANS[settings["workout_plan"]])
    engine.runAndWait()

# Function to show workout reminder
def show_reminder():
    popup = tk.Toplevel()
    popup.title("Workout Reminder")
    popup.geometry("400x300")

    label = tk.Label(popup, text=WORKOUT_PLANS[settings["workout_plan"]], font=("Arial", 12), padx=10, pady=10)
    label.pack()

    btn_ok = tk.Button(popup, text="OK, Let's Go!", command=lambda: stop_alarm(popup), font=("Arial", 12))
    btn_ok.pack(pady=5)

    btn_snooze = tk.Button(popup, text="Snooze (5 min)", command=lambda: snooze_alarm(popup), font=("Arial", 12))
    btn_snooze.pack(pady=5)

    btn_speak = tk.Button(popup, text="🔊 Read Workout Plan", command=speak_workout, font=("Arial", 12))
    btn_speak.pack(pady=5)

    popup.mainloop()

# Function to check and trigger alarm
def schedule_alarm():
    while True:
        now = datetime.datetime.now()
        load_alarms()  # Ensure latest alarms are checked

        for alarm_hour, alarm_minute in alarm_times:
            if now.hour == alarm_hour and now.minute == alarm_minute:
                play_alarm()
                threading.Thread(target=show_reminder, daemon=True).start()
                notification.notify(title="Workout Reminder", message="Time to exercise!", timeout=10)
                time.sleep(60)  # Prevent multiple triggers in the same minute
        time.sleep(10)  # Check every 10 seconds

# Function to add an alarm
def add_alarm():
    try:
        hour = int(entry_hour.get())
        minute = int(entry_minute.get())
        if 0 <= hour < 24 and 0 <= minute < 60:
            alarm_times.append((hour, minute))
            save_alarms()
            listbox.insert(tk.END, f"{hour:02}:{minute:02}")
        else:
            messagebox.showerror("Invalid Time", "Enter a valid time (0-23 hours, 0-59 minutes).")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter numbers only.")

# Function to remove selected alarm
def remove_alarm():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        listbox.delete(index)
        del alarm_times[index]
        save_alarms()

# Function to select alarm sound
def select_alarm_sound():
    file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if file_path:
        settings["alarm_sound"] = file_path
        save_settings()
        messagebox.showinfo("Success", "Alarm sound updated!")

# Function to change workout plan
def change_workout_plan():
    settings["workout_plan"] = workout_var.get()
    save_settings()
    messagebox.showinfo("Success", "Workout plan updated!")

# GUI Setup
root = tk.Tk()
root.title("Workout Reminder")
root.geometry("400x450")

# Alarm input
tk.Label(root, text="Set Workout Alarm (24-hour format)", font=("Arial", 12)).pack(pady=5)

frame = tk.Frame(root)
frame.pack()

entry_hour = tk.Entry(frame, width=5)
entry_hour.pack(side=tk.LEFT)
tk.Label(frame, text=":").pack(side=tk.LEFT)
entry_minute = tk.Entry(frame, width=5)
entry_minute.pack(side=tk.LEFT)

btn_add = tk.Button(root, text="Add Alarm", command=add_alarm, font=("Arial", 10))
btn_add.pack(pady=5)

# Alarm list
listbox = tk.Listbox(root, width=20, height=5)
listbox.pack(pady=5)

btn_remove = tk.Button(root, text="Remove Selected Alarm", command=remove_alarm, font=("Arial", 10))
btn_remove.pack(pady=5)

# Alarm sound selection
btn_sound = tk.Button(root, text="Select Alarm Sound", command=select_alarm_sound, font=("Arial", 10))
btn_sound.pack(pady=5)

# Workout plan selection
workout_var = tk.StringVar(value=settings["workout_plan"])
tk.Label(root, text="Select Workout Plan:").pack()
tk.OptionMenu(root, workout_var, *WORKOUT_PLANS.keys(), command=lambda _: change_workout_plan()).pack()

# Load alarms and start checking
load_alarms()
load_settings()

for hour, minute in alarm_times:
    listbox.insert(tk.END, f"{hour:02}:{minute:02}")

thread = threading.Thread(target=schedule_alarm, daemon=True)
thread.start()

root.mainloop()
