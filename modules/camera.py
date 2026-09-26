import cv2

from modules.database import registrar_log_terminal


def abrir_camera(indice=0):
    """Abre a webcam e registra falhas sem derrubar o terminal."""
    try:
        camera = cv2.VideoCapture(
            indice,
            cv2.CAP_DSHOW,
        )

        if not camera.isOpened():
            registrar_log_terminal(
                "ERROR",
                "CAMERA_OPEN_ERROR",
                f"Nao foi possivel abrir a camera de indice {indice}",
            )

        return camera

    except Exception as erro:
        registrar_log_terminal(
            "ERROR",
            "CAMERA_OPEN_ERROR",
            f"Erro ao abrir camera: {type(erro).__name__}: {erro}",
        )

        return None


def camera_esta_aberta(camera):
    """Verifica se a camera existe e esta aberta."""
    if camera is None:
        return False

    try:
        return camera.isOpened()

    except Exception:
        return False


def ler_frame(camera):
    """Le um frame da camera. Retorna (sucesso, frame)."""
    if not camera_esta_aberta(camera):
        return False, None

    try:
        sucesso, frame = camera.read()

        if not sucesso:
            return False, None

        return True, frame

    except Exception as erro:
        registrar_log_terminal(
            "ERROR",
            "CAMERA_READ_ERROR",
            f"Erro ao ler frame: {type(erro).__name__}: {erro}",
        )

        return False, None


def fechar_camera(camera):
    """Fecha a camera com seguranca."""
    if camera is not None:
        try:
            camera.release()

        except Exception as erro:
            registrar_log_terminal(
                "WARNING",
                "CAMERA_CLOSE_ERROR",
                f"Erro ao fechar camera: {type(erro).__name__}: {erro}",
            )

    cv2.destroyAllWindows()