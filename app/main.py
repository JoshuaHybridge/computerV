
import os
import base64
import tempfile
import re

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# =====================================================
# IMPORTACIONES DEL PROYECTO
# =====================================================

from src.SmartHome import activate_smart_home
from src.recognizer import analyze_emotion
from src.face_registration import register_face, verify_face
from src.user import register_user, get_all_users, get_user


# =====================================================
# CONFIGURACIÓN DE RUTAS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")


# =====================================================
# INICIALIZACIÓN DE FASTAPI
# =====================================================

app = FastAPI(
    title="MoodMeter",
    description="Sistema de análisis emocional, reconocimiento facial y automatización de hogares inteligentes mediante DeepFace",
    version="1.0.0"
)


# =====================================================
# ARCHIVOS ESTÁTICOS
# =====================================================

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# =====================================================
# MODELOS DE DATOS
# =====================================================

class MoodAnalysisRequest(BaseModel):
    image: str


class FaceRequest(BaseModel):
    image: str


class UserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=60)

    user_id: str = Field(
        min_length=1,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_-]+$"
    )


# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def decode_image(image_data):

    try:

        print("\n========== DEBUG IMAGEN ==========")

        print("Tipo recibido:", type(image_data))
        print("Longitud recibida:", len(image_data))

        if not image_data:
            raise ValueError("Imagen vacía.")

        # Eliminar encabezado Data URI si existe
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_data = image_data.strip()

        print("Longitud Base64:", len(image_data))
        print("Primeros caracteres:", repr(image_data[:50]))

        decoded_image = base64.b64decode(
            image_data,
            validate=True
        )

        print("Bytes decodificados:", len(decoded_image))

        print("==================================\n")

        if not decoded_image:
            raise ValueError("Imagen vacía.")

        return decoded_image

    except Exception as error:

        print("\nERROR AL DECODIFICAR:", repr(error))

        raise HTTPException(
            status_code=400,
            detail="La imagen enviada no es válida."
        )


def validate_user_id(user_id):

    if not re.fullmatch(
        r"[a-zA-Z0-9_-]{1,30}",
        user_id
    ):

        raise HTTPException(
            status_code=400,
            detail="ID de usuario inválido."
        )


def save_temp_image(image_bytes, suffix=".jpg"):

    with tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False
    ) as temp_file:

        temp_file.write(image_bytes)

        return temp_file.name


# =====================================================
# PÁGINA PRINCIPAL
# =====================================================

@app.get("/", response_class=HTMLResponse)
async def home():

    index_path = os.path.join(
        TEMPLATES_DIR,
        "index.html"
    )

    if not os.path.isfile(index_path):

        raise HTTPException(
            status_code=500,
            detail="No se encontró index.html."
        )

    with open(
        index_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# =====================================================
# ESTADO DEL SERVIDOR
# =====================================================

@app.get("/api/health")
async def health():

    return {
        "status": "online",
        "project": "MoodMeter"
    }


# =====================================================
# ANÁLISIS EMOCIONAL
# =====================================================

@app.post("/api/analyze-mood")
async def analyze_mood(payload: MoodAnalysisRequest):

    image_bytes = decode_image(payload.image)

    temp_path = None

    try:

        temp_path = save_temp_image(image_bytes)

        result = analyze_emotion(temp_path)

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar la imagen: {error}"
        )

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# =====================================================
# REGISTRO DE USUARIOS
# =====================================================

@app.post("/api/users")
async def create_user(payload: UserRequest):

    try:

        user = register_user(
            payload.name.strip(),
            payload.user_id.strip()
        )

        return {
            "success": True,
            "message": "Usuario registrado correctamente.",
            "user": user
        }

    except ValueError as error:

        raise HTTPException(
            status_code=409,
            detail=str(error)
        )


# =====================================================
# CONSULTAR TODOS LOS USUARIOS
# =====================================================

@app.get("/api/users")
async def list_users():

    return {
        "success": True,
        "users": get_all_users()
    }


# =====================================================
# CONSULTAR UN USUARIO POR ID
# =====================================================

@app.get("/api/users/{user_id}")
async def find_user(user_id: str):

    validate_user_id(user_id)

    user = get_user(user_id)

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado."
        )

    return {
        "success": True,
        "user": user
    }


# =====================================================
# REGISTRAR ROSTRO DE UN USUARIO
# =====================================================

@app.post("/api/users/{user_id}/face")
async def create_face(
    user_id: str,
    payload: FaceRequest
):

    validate_user_id(user_id)

    image_bytes = decode_image(payload.image)

    try:

        result = register_face(
            user_id,
            image_bytes
        )

        return {
            "success": True,
            "message": "Rostro registrado correctamente.",
            "result": result
        }

    except ValueError as error:

        message = str(error)

        if "ya tiene un rostro" in message:

            status_code = 409

        elif "no está registrado" in message:

            status_code = 404

        else:

            status_code = 422

        raise HTTPException(
            status_code=status_code,
            detail=message
        )


# =====================================================
# VERIFICAR IDENTIDAD FACIAL + SMART HOME
# =====================================================

@app.post("/api/verify-face/{user_id}")
async def check_face(
    user_id: str,
    payload: FaceRequest
):

    validate_user_id(user_id)

    image_bytes = decode_image(payload.image)

    try:

        # =============================================
        # PASO 1: VERIFICACIÓN FACIAL
        # =============================================

        print("\n====================================")
        print("       INICIANDO VERIFICACIÓN")
        print("====================================")

        result = verify_face(
            user_id,
            image_bytes
        )

        automation = None

        # =============================================
        # PASO 2: ACTIVAR SMART HOME
        # =============================================

        if result["verified"]:

            print("\n====================================")
            print("       IDENTIDAD VERIFICADA")
            print("====================================")

            print("Nombre:", result["name"])
            print("ID:", user_id)

            print("\nActivando Smart Home...")

            try:

                automation = activate_smart_home(
                    user_id
                )

            except Exception as error:

                print("ERROR SMART HOME:", str(error))

                automation = {
                    "success": False,
                    "message": "La identidad fue verificada, pero ocurrió un error en Smart Home."
                }

        else:

            print("\n====================================")
            print("       IDENTIDAD NO VERIFICADA")
            print("====================================")

            print("Automatización desactivada.")

        # =============================================
        # PASO 3: RESPUESTA FINAL
        # =============================================

        return {
            "success": True,
            "message": "Verificación facial procesada.",
            "verification": result,
            "smart_home": automation
        }

    except ValueError as error:

        message = str(error)

        if (
            "no está registrado" in message
            or "no tiene un rostro" in message
        ):

            status_code = 404

        else:

            status_code = 422

        raise HTTPException(
            status_code=status_code,
            detail=message
        )


# =====================================================
# FIN DE LA API
# =====================================================
