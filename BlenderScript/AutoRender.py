import bpy
import logging
import os

# Define the log file and ensure the directory exists
log_file = r"E:\Blender Addons\CrashHandler\render_logV2.txt"
log_dir = os.path.dirname(log_file)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up logging with immediate flushing
logging.basicConfig(filename=log_file,
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    force=True)  # Overwrites previous logging setups

logging.info("Logging initialized.")

# Function to get the last rendered frame
def get_last_rendered_frame(log_file_path):
    if not os.path.exists(log_file_path):
        return 1
    try:
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()
            for line in reversed(lines):
                if "Rendered Frame:" in line:
                    return int(line.split("Rendered Frame:")[1].strip())
    except Exception as e:
        logging.error(f"Error reading log file: {e}")
        return 1
    return 1

# Function to log rendered frames
def log_and_start_render(scene):
    frame = scene.frame_current
    logging.info(f"Rendered Frame: {frame}")

# Function to start rendering from the specified frame
def start_rendering():
    last_frame = get_last_rendered_frame(log_file)
    logging.info(f"Resuming rendering from frame: {last_frame}")
    bpy.context.scene.frame_start = last_frame
    bpy.ops.render.render('INVOKE_DEFAULT', animation=True)

# Handler to log frames during rendering
def render_update_handler(scene):
    log_and_start_render(scene)

# Function to initialize rendering after file load
def render_on_load(dummy):
    bpy.app.handlers.render_post.clear()
    bpy.app.handlers.render_post.append(render_update_handler)
    bpy.app.timers.register(start_rendering)

# Register the handler for file load event
bpy.app.handlers.load_post.clear()
bpy.app.handlers.load_post.append(render_on_load)

# Debug to ensure file path is working
print(f"Logging to: {log_file}")
