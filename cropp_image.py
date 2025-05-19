import cv2
import os
import glob

# Configuración inicial
scale_percent = 50  # % de reducción
input_folder = "files/Inv-plant/"
output_cropped = "files/cropped/"
output_rectangles = "files/rect_img/"

# Crear directorios de salida si no existen
os.makedirs(output_cropped, exist_ok=True)
os.makedirs(output_rectangles, exist_ok=True)

# Obtener lista de imágenes a procesar
image_files = glob.glob(os.path.join(input_folder, "*.jpg")) + glob.glob(os.path.join(input_folder, "*.png")) + glob.glob(os.path.join(input_folder, "*.jpeg")) + glob.glob(os.path.join(input_folder, "*.JPG"))

for image_path in image_files:
    # Cargar y redimensionar imagen
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error al cargar {image_path}, saltando...")
        continue
    
    base_name = os.path.basename(image_path)
    file_name, file_ext = os.path.splitext(base_name)
    
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    resized_image = cv2.resize(image, (width, height))
    clone = resized_image.copy()

    # Lista para almacenar todos los ROIs
    rois = []
    current_roi = []
    temp_clone = clone.copy()

    def select_roi(event, x, y, flags, param):
        global clone, temp_clone, current_roi, rois
        
        if event == cv2.EVENT_LBUTTONDOWN:
            current_roi = [(x, y)]
            
        elif event == cv2.EVENT_MOUSEMOVE and len(current_roi) == 1:
            # Dibuja el rectángulo temporal mientras arrastras
            temp_clone = clone.copy()
            cv2.rectangle(temp_clone, current_roi[0], (x, y), (0, 255, 0), 2)
            for r in rois:
                cv2.rectangle(temp_clone, r[0], r[1], (0, 255, 0), 2)
            cv2.imshow(f"Selecciona ROI - {base_name}", temp_clone)
            
        elif event == cv2.EVENT_LBUTTONUP:
            current_roi.append((x, y))
            rois.append(current_roi.copy())
            clone = temp_clone.copy()
            current_roi = []

    # Configurar ventana
    cv2.namedWindow(f"Selecciona ROI - {base_name}", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"Selecciona ROI - {base_name}", width, height)
    cv2.setMouseCallback(f"Selecciona ROI - {base_name}", select_roi)

    print(f"\nProcesando: {base_name}")
    print("Instrucciones:")
    print(" - Click izquierdo + arrastrar: Dibujar rectángulo")
    print(" - 'd': Eliminar último rectángulo")
    print(" - 'r': Reiniciar todos los rectángulos")
    print(" - 'c': Confirmar y guardar")
    print(" - 'q': Saltar esta imagen sin guardar")
    print(" - 'x': Salir del programa")

    while True:
        cv2.imshow(f"Selecciona ROI - {base_name}", clone)
        key = cv2.waitKey(1) & 0xFF
        
        # Tecla 'c' - Confirmar y guardar todos los recortes
        if key == ord("c") and rois:
            # Crear una copia de la imagen original con los rectángulos
            original_with_rectangles = image.copy()
            
            for i, roi in enumerate(rois):
                # Ajustar coordenadas al tamaño original
                x1 = int(roi[0][0] * (image.shape[1] / width))
                y1 = int(roi[0][1] * (image.shape[0] / height))
                x2 = int(roi[1][0] * (image.shape[1] / width))
                y2 = int(roi[1][1] * (image.shape[0] / height))
                
                # Dibujar rectángulos en la imagen original
                cv2.rectangle(original_with_rectangles, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Guardar recortes individuales
                cropped = image[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
                cv2.imwrite(f"{output_cropped}{file_name}_recorte_{i+1}{file_ext}", cropped)
            
            # Guardar imagen original con los rectángulos
            cv2.imwrite(f"{output_rectangles}{file_name}_con_rectangulos{file_ext}", original_with_rectangles)
            print(f"Recortes de {base_name} guardados exitosamente!")

            # Guardar las coordenadas de los rectángulos en un archivo de texto
            with open(f"files/rect_coords/{file_name}_coordenadas.txt", "w") as f:
                for roi in rois:
                    x1 = int(roi[0][0] * (image.shape[1] / width))
                    y1 = int(roi[0][1] * (image.shape[0] / height))
                    x2 = int(roi[1][0] * (image.shape[1] / width))
                    y2 = int(roi[1][1] * (image.shape[0] / height))
                    f.write(f"{x1},{y1},{x2},{y2}\n")
            print(f"Coordenadas de {base_name} guardadas exitosamente!")

            # Cerrar archivo de texto
            f.close()

            # Eliminar la imagen original
            if os.path.exists(image_path):
                print(f"Eliminando {image_path}...")
                os.remove(image_path)

            break
        
        # Tecla 'd' - Eliminar último rectángulo
        elif key == ord("d") and rois:
            rois.pop()
            clone = resized_image.copy()
            for r in rois:
                cv2.rectangle(clone, r[0], r[1], (0, 255, 0), 2)
        
        # Tecla 'r' - Reiniciar todos los rectángulos
        elif key == ord("r"):
            rois = []
            clone = resized_image.copy()
        
        # Tecla 'q' - Saltar esta imagen sin guardar
        elif key == ord("q"):
            print(f"Saltando {base_name} sin guardar...")
            break
        
        # Tecla 'x' - Salir del programa completamente
        elif key == ord("x"):
            cv2.destroyAllWindows()
            exit()

    cv2.destroyAllWindows()

print("\nProcesamiento completado!")
