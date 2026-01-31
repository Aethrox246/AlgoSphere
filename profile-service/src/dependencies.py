try:
    from db.database import SessionLocal
except Exception:
    import db as _db_module
    SessionLocal = getattr(_db_module, "SessionLocal")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
