
try:
    from models import db
    print("Import successful")
except Exception as e:
    import traceback
    traceback.print_exc()
