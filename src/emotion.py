from deepface import DeepFace


def analyze_emotion(frame):
    """
    Analiza las emociones detectadas en una imagen.

    Retorna la emoción dominante y sus porcentajes.
    """

    try:
        analysis = DeepFace.analyze(
            img_path=frame,
            actions=["emotion"],
            detector_backend="opencv",
            enforce_detection=True
        )

        if isinstance(analysis, list):
            result = analysis[0]
        else:
            result = analysis

        emotions = {
            key: round(float(value), 2)
            for key, value in result["emotion"].items()
        }

        return {
            "dominant_emotion": result["dominant_emotion"],
            "emotions": emotions,
            "box": result["region"]
        }

    except Exception as error:
        print(f"Error analizando emociones: {error}")
        return None
