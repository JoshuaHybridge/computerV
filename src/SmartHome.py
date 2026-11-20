import os
import pygame


# =====================================================
# CONFIGURACIÓN
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MUSIC_DIR = os.path.join(
    BASE_DIR,
    "music"
)

MUSIC_FILE = os.path.join(
    MUSIC_DIR,
    "track1.mp3"
)


# =====================================================
# INICIALIZAR REPRODUCTOR
# =====================================================

pygame.mixer.init()


# =====================================================
# REPRODUCIR MÚSICA
# =====================================================

def play_music():

    if not os.path.exists(MUSIC_FILE):
        print("No se encontró el archivo de música.")

        return False

    try:

        pygame.mixer.music.load(MUSIC_FILE)

        # Reproducir en bucle
        pygame.mixer.music.play(loops=-1)

        print("Música reproduciéndose.")

        return True

    except Exception as error:

        print("Error al reproducir música:", error)

        return False


# =====================================================
# AUTOMATIZACIÓN SMART HOME
# =====================================================

def activate_smart_home(user_id):

    print("\n================================")
    print("       SMART HOME ACTIVADO")
    print("================================")

    print("Usuario reconocido:", user_id)

    # Simulación de iluminación
    brightness = 80

    print("Iluminación configurada:", brightness, "%")

    # Simulación de temperatura
    temperature = 22

    print("Temperatura configurada:", temperature, "°C")

    # Reproducir música
    music_playing = play_music()

    return {
        "success": True,
        "music_playing": music_playing,
        "brightness": brightness,
        "temperature": temperature
    }
