import cv2


def abrir_camera(indice=0):
    """Abre a webcam. No Windows, o backend DSHOW costuma abrir mais rápido."""
    camera = cv2.VideoCapture(indice, cv2.CAP_DSHOW)
    return camera


def camera_esta_aberta(camera):
    return camera.isOpened()


def ler_frame(camera):
    """Lê um frame da câmera. Retorna (sucesso, frame)."""
    sucesso, frame = camera.read()
    return sucesso, frame


def fechar_camera(camera):
    camera.release()
    cv2.destroyAllWindows()