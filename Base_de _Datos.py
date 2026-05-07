import cv2
import threading
import win32gui
import win32con
import os
import numpy as np
from datetime import datetime

class CameraStream:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
        self.ret, self.frame = False, None
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.cap.read()

    def get_frame(self):
        if self.ret and self.frame is not None:
            return cv2.resize(self.frame, (420, 420))
        return None

# --- FUNCIONES DE PROCESAMIENTO (Lógica de tu MATLAB) ---
def procesar_y_guardar(frame, color_folder):
    # Crear estructura de subcarpetas
    subcarpetas = ['original', 'rotada90', 'rotada270', 'espejo', 'marco', 'gris', 'binaria', 'all']
    for sub in subcarpetas:
        os.makedirs(os.path.join(color_folder, sub), exist_ok=True)
    
    timestamp = datetime.now().strftime("%H%M%S")
    
    # 1. Original
    orig_path = os.path.join(color_folder, 'original', f'orig_{timestamp}.jpg')
    cv2.imwrite(orig_path, frame)
    cv2.imwrite(os.path.join(color_folder, 'all', f'orig_{timestamp}.jpg'), frame)

    # 2. Rotaciones (MATLAB imrotate)
    yy = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    cv2.imwrite(os.path.join(color_folder, 'rotada90', f'rot90_{timestamp}.jpg'), yy)
    cv2.imwrite(os.path.join(color_folder, 'all', f'rot90_{timestamp}.jpg'), yy)

    yz = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imwrite(os.path.join(color_folder, 'rotada270', f'rot270_{timestamp}.jpg'), yz)
    cv2.imwrite(os.path.join(color_folder, 'all', f'rot270_{timestamp}.jpg'), yz)

    # 3. Espejo (MATLAB fliplr)
    sp = cv2.flip(frame, 1)
    cv2.imwrite(os.path.join(color_folder, 'espejo', f'esp_{timestamp}.jpg'), sp)
    cv2.imwrite(os.path.join(color_folder, 'all', f'esp_{timestamp}.jpg'), sp)

    # 4. Borde (MATLAB padarray)
    borde = cv2.copyMakeBorder(frame, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[0,0,0])
    borde = cv2.resize(borde, (420, 420)) # Re-ajustar a 420x420 tras el borde
    cv2.imwrite(os.path.join(color_folder, 'marco', f'marco_{timestamp}.jpg'), borde)
    cv2.imwrite(os.path.join(color_folder, 'all', f'marco_{timestamp}.jpg'), borde)

    # 5. Gris (MATLAB rgb2gray)
    zz = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(os.path.join(color_folder, 'gris', f'gris_{timestamp}.jpg'), zz)
    cv2.imwrite(os.path.join(color_folder, 'all', f'gris_{timestamp}.jpg'), zz)

    # 6. Binaria (MATLAB imbinarize)
    _, xx = cv2.threshold(zz, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite(os.path.join(color_folder, 'binaria', f'bin_{timestamp}.jpg'), xx)
    cv2.imwrite(os.path.join(color_folder, 'all', f'bin_{timestamp}.jpg'), xx)

    print(f"¡Capturas guardadas en {color_folder}!")

# --- CONFIGURACIÓN ---
IP_CELULAR = "http://192.168.1.5:8080/video" 
TITULO_VENTANA = "Camara_Virtual_1"
TITULO_LABVIEW = "Camara1"

cam1 = CameraStream(IP_CELULAR).start()
cv2.namedWindow(TITULO_VENTANA, cv2.WINDOW_NORMAL)
cv2.resizeWindow(TITULO_VENTANA, 420, 420)

# Opcional: Quitar bordes (win32gui)
hwnd_py = win32gui.FindWindow(None, TITULO_VENTANA)
if hwnd_py:
    style = win32gui.GetWindowLong(hwnd_py, win32con.GWL_STYLE)
    style = style & ~win32con.WS_CAPTION & ~win32con.WS_THICKFRAME
    win32gui.SetWindowLong(hwnd_py, win32con.GWL_STYLE, style)

while True:
    frame = cam1.get_frame()
    if frame is not None:
        cv2.imshow(TITULO_VENTANA, frame)

        # Inyectar en LabVIEW si está abierto
        hwnd_lv = win32gui.FindWindow(None, TITULO_LABVIEW)
        if hwnd_lv:
            win32gui.SetParent(hwnd_py, hwnd_lv)
            win32gui.SetWindowPos(hwnd_py, None, 0, 0, 420, 420, win32con.SWP_NOZORDER)

    key = cv2.waitKey(1) & 0xFF
    
    # Lógica de teclado
    if key == ord('m'): # Morado
        procesar_y_guardar(frame, 'Camara1/morado')
    elif key == ord('v'): # Verde
        procesar_y_guardar(frame, 'Camara1/verde')
    elif key == ord('r'): # Rosado
        procesar_y_guardar(frame, 'Camara1/rosado')
    elif key == ord('q'):
        break

cv2.destroyAllWindows()
