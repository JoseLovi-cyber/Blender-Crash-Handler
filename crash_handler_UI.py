import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import psutil
import subprocess

# Global flags
monitoring = False
frame_logging = False
recent_paths_file = "recent_paths.json"

# Save recent paths
def save_recent_paths(paths):
    try:
        with open(recent_paths_file, "w") as f:
            json.dump(paths, f)
    except Exception as e:
        log_message(f"Error saving recent paths: {e}")

# Load recent paths
def load_recent_paths():
    try:
        if os.path.exists(recent_paths_file):
            with open(recent_paths_file, "r") as f:
                return json.load(f)
    except Exception as e:
        log_message(f"Error loading recent paths: {e}")
    return {"blender_path": "", "blend_file": "", "log_file": ""}

# Update recent paths
def update_recent_paths(field, value):
    recent_paths[field] = value
    save_recent_paths(recent_paths)

# Check if Blender is running
def is_blender_running():
    for proc in psutil.process_iter(['name']):
        if "blender" in proc.info['name'].lower():
            return True
    return False

# Start Blender
def start_blender(blender_path, blend_file):
    subprocess.Popen([blender_path, blend_file])

# Monitor Blender process
def monitor_blender_process(blender_path, blend_file):
    global monitoring
    while monitoring:
        if not is_blender_running():
            log_message("Blender not running. Restarting Blender...")
            start_blender(blender_path, blend_file)
        time.sleep(10)

# Monitor rendered frames
def monitor_rendered_frames(log_file_path):
    global frame_logging
    already_logged_frames = set()

    while frame_logging:
        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r") as log_file:
                    lines = log_file.readlines()
                    for line in lines:
                        if "Rendered Frame:" in line:
                            frame = int(line.split("Rendered Frame:")[1].strip())
                            if frame not in already_logged_frames:
                                already_logged_frames.add(frame)
                                log_message(f"Rendered Frame: {frame}")
            except Exception as e:
                log_message(f"Error reading rendered frames: {e}")
        time.sleep(2)

# Log message to the UI
def log_message(message):
    log_box.insert(tk.END, f"{message}\n")
    log_box.see(tk.END)

# Start monitoring
def start_monitor():
    global monitoring, frame_logging
    if monitoring:
        log_message("Monitoring is already running!")
        return

    blender_path = blender_path_entry.get().strip()
    blend_file = blend_file_entry.get().strip()
    log_file = log_file_entry.get().strip()

    if not (os.path.exists(blender_path) and os.path.exists(blend_file) and os.path.exists(os.path.dirname(log_file))):
        messagebox.showerror("Error", "Invalid paths for Blender executable, .blend file, or log file.")
        return

    # Save paths to recent
    update_recent_paths("blender_path", blender_path)
    update_recent_paths("blend_file", blend_file)
    update_recent_paths("log_file", log_file)

    monitoring = True
    frame_logging = True
    log_message("Monitoring started.")

    threading.Thread(target=monitor_blender_process, args=(blender_path, blend_file), daemon=True).start()
    threading.Thread(target=monitor_rendered_frames, args=(log_file,), daemon=True).start()

# Stop monitoring
def stop_monitor():
    global monitoring, frame_logging
    if not monitoring:
        log_message("Monitoring is not running!")
        return

    monitoring = False
    frame_logging = False
    log_message("Monitoring stopped.")

# File dialog for selecting files
def browse_file(entry_widget, file_types, field):
    file_path = filedialog.askopenfilename(filetypes=file_types)
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)
        update_recent_paths(field, file_path)

# Directory dialog for the log file
def browse_log_file(entry_widget):
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)
        update_recent_paths("log_file", file_path)

# Load recent paths on startup
recent_paths = load_recent_paths()

# UI Setup
root = tk.Tk()
root.title("Blender Monitor")

# Title Section (Author and Version)
tool_title = tk.Label(root, text="Blender Crash Handler", font=("Helvetica", 16, "bold"))
tool_title.grid(row=0, column=0, columnspan=3, pady=5)

tool_version = tk.Label(root, text="Version: 1.0.0 | Author: Jose Lorenzo Soren", font=("Helvetica", 10, "italic"))
tool_version.grid(row=1, column=0, columnspan=3, pady=2)

# Blender executable path
tk.Label(root, text="Blender Executable:").grid(row=2, column=0, sticky="w")
blender_path_entry = tk.Entry(root, width=50)
blender_path_entry.grid(row=2, column=1, padx=5)
tk.Button(root, text="Browse", command=lambda: browse_file(blender_path_entry, [("Blender Executable", "*.exe")] if os.name == 'nt' else [], "blender_path")).grid(row=2, column=2)

# Blender file path
tk.Label(root, text="Blender File (.blend):").grid(row=3, column=0, sticky="w")
blend_file_entry = tk.Entry(root, width=50)
blend_file_entry.grid(row=3, column=1, padx=5)
tk.Button(root, text="Browse", command=lambda: browse_file(blend_file_entry, [("Blender Files", "*.blend")], "blend_file")).grid(row=3, column=2)

# Log file path
tk.Label(root, text="Log File Path:").grid(row=4, column=0, sticky="w")
log_file_entry = tk.Entry(root, width=50)
log_file_entry.grid(row=4, column=1, padx=5)
tk.Button(root, text="Browse", command=lambda: browse_log_file(log_file_entry)).grid(row=4, column=2)

# Start and Stop Buttons
tk.Button(root, text="Start", command=start_monitor, bg="green", fg="white").grid(row=5, column=1, sticky="w", pady=5)
tk.Button(root, text="Stop", command=stop_monitor, bg="red", fg="white").grid(row=5, column=1, sticky="e", pady=5)

# Log Box
tk.Label(root, text="Log:").grid(row=6, column=0, sticky="w", pady=5)
log_box = tk.Text(root, height=15, width=60, state=tk.NORMAL)
log_box.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

# Populate fields with recent paths
blender_path_entry.insert(0, recent_paths.get("blender_path", ""))
blend_file_entry.insert(0, recent_paths.get("blend_file", ""))
log_file_entry.insert(0, recent_paths.get("log_file", ""))

# Run the UI
root.mainloop()
