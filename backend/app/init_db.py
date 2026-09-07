from .db import Base, engine
from .models import User
from sqlalchemy.orm import Session
from .db import SessionLocal
from uuid import uuid4

def init():
    Base.metadata.create_all(engine)

def seed():
    init()
    with SessionLocal() as db:
        samples=[
            ("مدیر سامانه","09120000001","ADMIN",None),
            ("شهروند نمونه","09120000002","CITIZEN",None),
            ("شهروند دوم","09120000003","CITIZEN",None),
            ("اپراتور شهرداری","09120000004","AGENCY","شهرداری"),
            ("اپراتور آتش نشانی","09120000005","AGENCY","آتش نشانی"),
        ]
        for name,phone,role,agency in samples:
            if not db.query(User).filter(User.phone==phone).first():
                db.add(User(id=uuid4().hex,name=name,phone=phone,role=role,agency=agency))
        db.commit()
if __name__=="__main__": seed()
