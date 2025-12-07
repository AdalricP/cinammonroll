try:
    import pipecat
    print("Pipecat imported successfully")
except ImportError as e:
    print(f"Pipecat import failed: {e}")
except Exception as e:
    print(f"Pipecat crashed: {e}")
