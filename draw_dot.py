import os
import cv2

# Folders
IMAGES_DIR = 'files/cropped'
IMAGES_OUT_DIR = 'files/image_dots'
DOT_DIR = 'files/dots'

# Create output directory if it doesn't exist
os.makedirs(IMAGES_OUT_DIR, exist_ok=True)

# Image list
image_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Global state
circles = []  # (x, y, radius)

def draw_circle(event, x, y, flags, param):
    global drawing, radius, circles, img, original

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        circles.append((x, y, radius))
        redraw_image()

def redraw_image():
    global img, original, circles
    img = original.copy()
    for (x, y, r) in circles:
        cv2.circle(img, (x, y), r, (255, 0, 0), -1)

def nothing(x):
    pass

for image_file in image_files:
    img_path = os.path.join(IMAGES_DIR, image_file)
    original = cv2.imread(img_path)
    if original is None:
        continue

    drawing = False
    radius = 5
    circles = []

    img = original.copy()

    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('image', draw_circle)
    cv2.createTrackbar('Radius', 'image', radius, 100, nothing)

    while True:
        cv2.imshow('image', img)
        radius = cv2.getTrackbarPos('Radius', 'image')
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            # Save image
            black_img = original.copy()
            black_img[:] = 0
            for (x, y, r) in circles:
                cv2.circle(black_img, (x, y), r, (255, 255, 255), -1)
            
            output_image_path = os.path.join(IMAGES_OUT_DIR, f"dot_{image_file}")
            cv2.imwrite(output_image_path, black_img)
            os.remove(img_path)
            print(f"Deleted: {img_path}")

            # Save coordinates
            txt_name = os.path.splitext(image_file)[0] + ".txt"
            output_txt_path = os.path.join(DOT_DIR, f"dot_{txt_name}")
            with open(output_txt_path, 'w') as f:
                for (x, y, r) in circles:
                    f.write(f"{x} {y} {r}\n")
            print(f"Saved: {output_image_path} and {output_txt_path}")
            break

        elif key == ord('n'):
            break
        elif key == ord('d') and circles:
            circles.pop()
            redraw_image()
        elif key == 27:  # ESC
            exit()

    cv2.destroyAllWindows()
