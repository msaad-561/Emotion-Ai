try:
    print("Attempting to import tensorflow...")
    import tensorflow
    print("Tensorflow imported.")
except ImportError as e:
    print(f"Tensorflow failed: {e}")

try:
    print("Attempting to import FER from fer.fer...")
    from fer.fer import FER
    print("FER imported from fer.fer successfully!")
    detector = FER(mtcnn=False)
    print("FER initialized.")
except Exception as e:
    print(f"FER import failed: {e}")
    import traceback
    traceback.print_exc()
