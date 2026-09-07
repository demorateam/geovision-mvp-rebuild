import random
from datetime import datetime, timedelta
from uuid import uuid4
from .db import Base, engine, SessionLocal
from .models import User, Incident, IncidentAgency, IncidentStatusHistory

TEMPLATES=[
("نشتی گاز","بوی گاز شدیدی از لوله بیرون می‌آید. خطرناک است.",["گاز","آتش نشانی","اورژانس"],"Critical"),
("حریق","آتش در یک ساختمان مسکونی گرفته و دود زیادی تولید می‌کند.",["آتش نشانی","اورژانس","پلیس"],"Critical"),
("تصادف","تصادف بین دو خودرو در تقاطع رخ داده و مسدود شده.",["پلیس","اورژانس"],"High"),
("خرابی آسفالت","چاله عمیقی در وسط خیابان ایجاد شده و خطر تصادف دارد.",["شهرداری"],"Medium"),
("مشکل آب و فاضلاب","لوله آب ترکیده و آب در خیابان جاری است.",["آب و فاضلاب","شهرداری"],"High"),
("مشکل برق","سیم برق قطع شده و روی زمین افتاده. خطر برق گرفتگی.",["اداره برق","شهرداری"],"High"),
("مشکل پسماند","زباله‌ها در خیابان انباشته و بوی بدی تولید می‌کنند.",["شهرداری"],"Low"),
("خرابی چراغ","چراغ خیابان سه روز است روشن نمی‌شود و شب تاریک است.",["شهرداری","اداره برق"],"Low"),
("خطر درخت","شاخه بزرگ درخت روی جاده افتاده و مسیر را بسته.",["شهرداری","اورژانس"],"Medium"),
("سرقت","دزدی از یک مغازه گزارش شده، مجرم فرار کرده.",["پلیس","نهادهای امنیتی"],"Medium"),
]
REGIONS=["منطقه ۱","منطقه ۳","منطقه ۵","منطقه ۶","منطقه ۷","منطقه ۸","منطقه ۱۰","منطقه ۱۲","منطقه ۱۴","منطقه ۱۵","منطقه ۱۷","منطقه ۱۹","منطقه ۲۰","منطقه ۲۲"]
COLORS={"Low":"Green","Medium":"Yellow","High":"Orange","Critical":"Red"}
STATUSES=["PENDING","IN_PROGRESS","RESOLVED"]

def seed():
    Base.metadata.create_all(engine)
    db=SessionLocal()
    try:
        db.query(IncidentStatusHistory).delete(); db.query(IncidentAgency).delete(); db.query(Incident).delete(); db.query(User).delete()
        users=[
            User(id=uuid4().hex,name="مدیر سیستم",phone="09120000001",role="ADMIN"),
            User(id=uuid4().hex,name="علی رضایی",phone="09120000002",role="CITIZEN"),
            User(id=uuid4().hex,name="مریم احمدی",phone="09120000003",role="CITIZEN"),
            User(id=uuid4().hex,name="اپراتور شهرداری",phone="09120000004",role="AGENCY",agency="شهرداری"),
            User(id=uuid4().hex,name="اپراتور آتش نشانی",phone="09120000005",role="AGENCY",agency="آتش نشانی")]
        db.add_all(users); db.commit(); citizens=users[1:3]
        for i in range(30):
            typ,desc,agencies,sev=random.choice(TEMPLATES); status=random.choice(STATUSES)
            created=datetime.utcnow()-timedelta(days=random.randint(0,30),hours=random.randint(0,23),minutes=random.randint(0,59))
            inc=Incident(id=uuid4().hex,incident_number=f"INC-{1000+i:04d}",reporter_id=random.choice(citizens).id,
                image_url="https://images.pexels.com/photos/3822622/?auto=compress&cs=tinysrgb&w=600",description=desc,
                latitude=random.uniform(35.55,35.82),longitude=random.uniform(51.2,51.6),region=random.choice(REGIONS),
                incident_type=typ,severity=sev,color_code=COLORS[sev],ai_summary=f"تحلیل خودکار: {typ}. {desc}",status=status,
                created_at=created,updated_at=created+timedelta(hours=1))
            db.add(inc); db.flush()
            for a in agencies: db.add(IncidentAgency(id=uuid4().hex,incident_id=inc.id,agency_name=a,assigned_at=created))
            order=["PENDING","IN_PROGRESS","RESOLVED"]; idx=order.index(status)
            for j in range(idx+1): db.add(IncidentStatusHistory(id=uuid4().hex,incident_id=inc.id,old_status=None if j==0 else order[j-1],new_status=order[j],created_at=created+timedelta(minutes=j*15)))
        db.commit()
    finally: db.close()

if __name__=="__main__": seed()
