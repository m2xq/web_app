from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, db
from .db import get_db

app = FastAPI(title="Fishing Fleet API")

# --- USERS ---
@app.post("/users")
def create_user(user: dict, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(username=user["username"]).first():
        raise HTTPException(400, "Пользователь уже существует")
    new_user = models.User(**user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "created"}

@app.get("/users/{username}")
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=username).first()
    if not user:
        raise HTTPException(404, "Не найдено")
    return {"username": user.username, "password_hash": user.password_hash, "role": user.role}

# --- VESSELS ---
@app.get("/vessels")
def get_vessels(db: Session = Depends(get_db)):
    return db.query(models.Vessel).all()

@app.post("/vessels")
def add_vessel(vessel: dict, db: Session = Depends(get_db)):
    new_v = models.Vessel(**vessel)
    db.add(new_v)
    db.commit()
    db.refresh(new_v)
    return new_v

# --- VOYAGES ---
@app.get("/voyages")
def get_voyages(db: Session = Depends(get_db)):
    return db.query(models.Voyage).all()

@app.post("/voyages")
def add_voyage(voyage: dict, db: Session = Depends(get_db)):
    new_v = models.Voyage(**voyage)
    db.add(new_v)
    db.commit()
    db.refresh(new_v)
    return new_v

# --- BANKS ---
@app.get("/banks")
def get_banks(db: Session = Depends(get_db)):
    return db.query(models.Bank).all()

@app.post("/banks")
def add_bank(bank: dict, db: Session = Depends(get_db)):
    new_b = models.Bank(**bank)
    db.add(new_b)
    db.commit()
    db.refresh(new_b)
    return new_b

# --- VISITS ---
@app.get("/visits")
def get_visits(db: Session = Depends(get_db)):
    return db.query(models.Visit).all()

@app.post("/visits")
def add_visit(visit: dict, db: Session = Depends(get_db)):
    new_v = models.Visit(**visit)
    db.add(new_v)
    db.commit()
    db.refresh(new_v)
    return new_v

# --- CATCHES ---
@app.get("/catches")
def get_catches(db: Session = Depends(get_db)):
    return db.query(models.Catch).all()

@app.post("/catches")
def add_catch(catch: dict, db: Session = Depends(get_db)):
    new_c = models.Catch(**catch)
    db.add(new_c)
    db.commit()
    db.refresh(new_c)
    return new_c

# --- REPORTS (пример) ---
@app.get("/reports/top-vessels")
def top_vessels(species: str = None, date_from: str = None, date_to: str = None, db: Session = Depends(get_db)):
    # Простейший пример: возвращает список катеров с суммарным уловом по виду рыбы
    from sqlalchemy import func
    query = db.query(models.Vessel.name.label("vessel"), func.sum(models.Catch.weight).label("total"))\
              .join(models.Voyage).join(models.Visit).join(models.Catch)
    if species:
        query = query.filter(models.Catch.species==species)
    result = query.group_by(models.Vessel.name).order_by(func.sum(models.Catch.weight).desc()).all()
    return [{"vessel": r.vessel, "total": r.total} for r in result]

