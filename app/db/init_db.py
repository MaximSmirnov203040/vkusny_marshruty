from app.db.database import SessionLocal
from app.db.seed import seed_tours

def init_db():
    db = SessionLocal()
    try:
        seed_tours(db)
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating initial data")
    init_db()
    print("Initial data created") 