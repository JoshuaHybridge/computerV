import time
from deepface import DeepFace


def analyze_emotion(image_path):
    """
    Analiza las emociones de una fotografía
    utilizando DeepFace.
    """

    start_time = time.time()

    try:

        analysis = DeepFace.analyze(
            img_path=image_path,
            actions=["emotion"],
            enforce_detection=True,
            detector_backend="opencv"
        )

        if isinstance(analysis, list):
            result = analysis[0]
        else:
            result = analysis

        emotions = result["emotion"]

        return {
            "success": True,

            "dominant_emotion": result["dominant_emotion"],

            "emotions": {
                key: round(float(value), 2)
                for key, value in emotions.items()
            },

            "box": result["region"],

            "inference_time_seconds": round(
                time.time() - start_time,
                3
            )
        }

    except Exception as error:

        raise ValueError(str(error))
