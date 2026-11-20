def execute_action(emotion):

    actions = {
        "happy": "Mostrando ambiente alegre.",
        "sad": "Activando ambiente relajante.",
        "angry": "Activando iluminación tenue.",
        "surprise": "Activando iluminación dinámica.",
        "fear": "Activando ambiente tranquilo.",
        "disgust": "Manteniendo configuración normal.",
        "neutral": "Manteniendo configuración normal."
    }

    message = actions.get(
        emotion,
        "Sin acciones configuradas."
    )

    print(message)

    return message
