import cv2
import time
import shutil
import psutil
import os

# Function to get available disks  
def get_disk_partitions():
    partitions = psutil.disk_partitions()
    drives = [partition.device for partition in partitions if 'cdrom' not in partition.opts and partition.fstype != '']
    return drives

# Function to get available disk space in GB
def get_available_disk_space_gb(path="."):
    total, used, free = shutil.disk_usage(path)
    return free / (2**30)  # Convert bytes to gigabytes

# Create an object to read from the camera
video = cv2.VideoCapture(0)

# Check if the camera is opened successfully
if not video.isOpened():
    print("Error reading video file")
    exit()

# Set resolutions
frame_width = int(video.get(3))
frame_height = int(video.get(4))
size = (frame_width, frame_height)

# VideoWriter object to save the video
video_writer = None

# Record until available disk space is less than 500MB
while True:
    # Find available disks
    disks = get_disk_partitions()

    # Set the default path to the local drive
    default_path = "."

    # Use the first external disk found, or default to the local drive
    if disks:
        external_disk_path = disks[1]
    else:
        external_disk_path = default_path

    # Create 'videos' directory if it doesn't exist
    videos_directory = os.path.join(external_disk_path, 'videos')
    if not os.path.exists(videos_directory):
        os.makedirs(videos_directory)

    # Capture video for 10 minutes
    end_time = time.time() + 600  # 10 minutes in seconds

    # Create a unique filename based on the current date and time
    current_time = time.localtime()
    formatted_time = time.strftime("%Y-%m-%d_%H-%M-%S", current_time)
    filename = f'{external_disk_path}/videos/{formatted_time}.mp4'

    print(f"Recording video to {filename}")

    # Create VideoWriter object with MP4 codec
    video_writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), 30, size)

    while time.time() <= end_time:
        ret, frame = video.read()

        if ret:
            # Write the frame into the video file
            video_writer.write(frame)

    # Release VideoWriter object
    video_writer.release()
    print("Video saved successfully")

    # Check available disk space in GB
    available_space_gb = get_available_disk_space_gb(external_disk_path)
    print(f"Available disk space on {external_disk_path}: {available_space_gb:.2f} GB")

    # Terminate the loop if available disk space is less than 500MB
    if available_space_gb < 0.5:  # 500MB in GB
        print("Insufficient disk space. Exiting.")
        break

# Release the video capture when the program is interrupted
video.release()
cv2.destroyAllWindows()
