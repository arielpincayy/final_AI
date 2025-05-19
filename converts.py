import os
import subprocess
import sys


if len(sys.argv) > 1:
    input_dir = sys.argv[1]
    
output_dir = sys.argv[2] + "_dots"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Valid input extensions
valid_exts = ('.jpg', '.jpeg', '.JPG', '.JPEG')

# Loop through input directory
for filename in os.listdir(input_dir):
    if filename.endswith(valid_exts):
        input_path = os.path.join(input_dir, filename)
        name_base = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, f"{name_base}.png")

        # Run ffmpeg command
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path, output_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"[✓] Converted: {filename} → {name_base}.png")
