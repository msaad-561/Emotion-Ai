try:
    import fer
    print(f"FER location: {fer.__file__}")
    from fer import FER
    print("Import Successful")
except Exception as e:
    import traceback
    traceback.print_exc()
