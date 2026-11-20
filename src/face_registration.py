import os
import re
import tempfile
import cv2
import numpy as np

from deepface import DeepFace
from src.user import get_user


# =====================================================
# CONFIGURACIÓN DE RUTAS
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

FACES_DIR = os.path.join(
    BASE_DIR,
    "database",
    "personas",
    "faces"
)

MAX_IMAGE_SIZE = 5 * 1024 * 1024


# =====================================================
# OBTENER RUTA DE REFERENCIA
# =====================================================

def get_reference_path(user_id):
    """Obtiene la ruta de la fotografía de referencia."""

    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,30}", user_id):
        raise ValueError("ID de usuario inválido.")

    user_dir = os.path.join(FACES_DIR, user_id)

    # Aceptar ambas extensiones
    jpg_path = os.path.join(user_dir, "reference.jpg")
    jpeg_path = os.path.join(user_dir, "reference.jpeg")

    if os.path.exists(jpg_path):
        return jpg_path

    if os.path.exists(jpeg_path):
        return jpeg_path

    return jpg_path


# =====================================================
# VALIDAR IMAGEN
# =====================================================


def validate_image(image_bytes):
    """Valida y normaliza una imagen."""

    print("\n========== VALIDACIÓN DE IMAGEN ==========")

    print("Bytes recibidos:", len(image_bytes))
    print("Límite permitido:", MAX_IMAGE_SIZE)

    if not image_bytes:
        raise ValueError("No se recibió ninguna imagen.")

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError("La imagen supera el límite de 5 MB.")

    print("Comprobando conversión OpenCV...")

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    print("Array generado:", image_array.shape)

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            "OpenCV no pudo interpretar la imagen. "
            "Comprueba que el archivo sea JPEG o PNG válido."
        )

    height, width = image.shape[:2]

    print("Ancho:", width)
    print("Alto:", height)

    if width < 100 or height < 100:
        raise ValueError(
            "La imagen tiene una resolución demasiado pequeña."
        )

    if width > 4000 or height > 4000:
        raise ValueError(
            "La resolución de la imagen es demasiado grande."
        )

    print("Imagen validada correctamente.")
    print("==========================================\n")

    return image



# =====================================================
# DETECTAR ROSTRO
# =====================================================

def detect_single_face(image_path):
    """Comprueba que exista exactamente un rostro."""

    faces = DeepFace.extract_faces(
        img_path=image_path,
        detector_backend="opencv",
        enforce_detection=True,
        align=True
    )

    if len(faces) != 1:
        raise ValueError(
            "La imagen debe contener exactamente un rostro."
        )


# =====================================================
# REGISTRAR ROSTRO
# =====================================================

def register_face(user_id, image_bytes):
    """Registra una fotografía facial de referencia."""

    user = get_user(user_id)

    if user is None:
        raise ValueError("El usuario no está registrado.")

    reference_path = get_reference_path(user_id)

    print("\n========== REGISTRO FACIAL ==========")
    print("Usuario:", user_id)
    print("Ruta de referencia:", reference_path)
    print("Ya existe:", os.path.exists(reference_path))
    print("=====================================\n")

    if os.path.exists(reference_path):
        raise ValueError(
            "Este usuario ya tiene un rostro registrado."
        )

    image = validate_image(image_bytes)

    os.makedirs(
        os.path.dirname(reference_path),
        exist_ok=True
    )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False
        ) as temp_file:

            temp_path = temp_file.name

        if not cv2.imwrite(temp_path, image):
            raise ValueError("No se pudo procesar la fotografía.")

        detect_single_face(temp_path)

        # Guardar imagen de referencia
        os.replace(temp_path, reference_path)
        temp_path = None

        print("Rostro registrado correctamente.")
        print("Archivo:", reference_path)

        return {
            "success": True,
            "message": "Rostro registrado correctamente.",
            "user_id": user_id
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# =====================================================
# VERIFICAR ROSTRO
# =====================================================


def verify_face(user_id, image_bytes):
    """Compara una imagen nueva con el rostro registrado."""

    print("\n========== INICIO VERIFICACIÓN ==========")

    user = get_user(user_id)

    if user is None:
        raise ValueError("El usuario no está registrado.")

    reference_path = get_reference_path(user_id)

    print("Referencia:", reference_path)
    print("Existe:", os.path.exists(reference_path))

    if not os.path.exists(reference_path):
        raise ValueError(
            "El usuario todavía no tiene un rostro registrado."
        )

    # PASO 1: Validar imagen
    print("\nPASO 1: Validando imagen recibida...")

    image = validate_image(image_bytes)

    print("Imagen válida.")
    print("Dimensiones:", image.shape)

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False
        ) as temp_file:
            temp_path = temp_file.name

        # PASO 2: Guardar imagen temporal
        print("\nPASO 2: Guardando imagen temporal...")

        if not cv2.imwrite(temp_path, image):
            raise ValueError("No se pudo procesar la fotografía.")

        print("Imagen temporal guardada:", temp_path)

        # PASO 3: Detectar rostro
        print("\nPASO 3: Detectando rostro...")

        detect_single_face(temp_path)

        print("Rostro detectado correctamente.")

        # PASO 4: Comparar imágenes
        print("\nPASO 4: Ejecutando DeepFace.verify...")

        result = DeepFace.verify(
            img1_path=reference_path,
            img2_path=temp_path,
            model_name="Facenet512",
            detector_backend="opencv",
            distance_metric="cosine",
            enforce_detection=True
        )

        verified = bool(result["verified"])

        print("Comparación finalizada.")
        print("Resultado:", verified)
        print("Distancia:", result.get("distance"))

        return {
            "success": True,
            "verified": verified,
            "user_id": user_id,
            "name": user["name"],
            "message": (
                "Coincidencia facial."
                if verified
                else "No se pudo verificar la identidad."
            )
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
