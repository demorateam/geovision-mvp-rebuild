import json, re, random
import httpx
from .config import settings

AGENCY_LIST = ["شهرداری","نهادهای امنیتی","مخابرات","آب و فاضلاب","اداره برق","گاز","اورژانس","پلیس","آتش نشانی"]
COLORS = {"Low":"Green","Medium":"Yellow","High":"Orange","Critical":"Red"}
REGIONS = [f"منطقه {i}" for i in range(1,23)]
SYSTEM_PROMPT = f'''You are an expert municipal emergency dispatcher.
Analyze the urban incident image and description. Return ONLY JSON with:
incident_type, severity, color_code, assigned_agencies, region, summary_fa.
Severity: Low, Medium, High, Critical. Colors: Green, Yellow, Orange, Red.
Organizations: {", ".join(AGENCY_LIST)}.
Region should be a Tehran district. summary_fa is a short Persian sentence.'''

RULES = [
(["گاز","نشتی","بوی گاز","لوله گاز"],"نشتی گاز","Critical",["گاز","آتش نشانی","اورژانس"],"احتمال نشتی گاز گزارش شده. تیم اورژانس گاز و آتش نشانی فورا اعزام شوند."),
(["آتش","حریق","شعله","سوختن","دود","سوختگی"],"حریق","Critical",["آتش نشانی","اورژانس","پلیس"],"گزارش حریق. آتش نشانی و اورژانس با اولویت بالا اعزام شوند."),
(["تصادف","حادثه","ضربه"],"تصادف","High",["پلیس","اورژانس","نهادهای امنیتی"],"تصادف رخ داده. پلیس و اورژانس برای کنترل صحنه اعزام شوند."),
(["چاله","گودال","چال","سوراخ","فرورفتگی","آسفالت"],"خرابی آسفالت","Medium",["شهرداری"],"چاله یا خرابی آسفالت در مسیر. تیم شهرداری برای ترمیم اعزام شود."),
(["آب","نشتی آب","لوله آب","سیل","آب گرفتگی","سیلاب"],"مشکل آب و فاضلاب","High",["آب و فاضلاب","شهرداری"],"مشکل شبکه آب و فاضلاب. اداره آب برای رفع نشتی اعزام شود."),
(["برق","قطع برق","سیم","تیر برق"],"مشکل برق","High",["اداره برق","شهرداری"],"مشکل شبکه برق. اداره برق برای بررسی و رفع خطر اعزام شود."),
(["سرقت","دزدی","یاغی"],"سرقت","Medium",["پلیس","نهادهای امنیتی"],"گزارش سرقت. پلیس برای بررسی اعزام شود."),
(["زباله","پسماند","کثیف","آلودگی","زباله دان"],"مشکل پسماند","Low",["شهرداری"],"انباشت زباله. شهرداری برای جمع‌آوری اعزام شود."),
(["چراغ","نور","روشنایی","چراغ خیابان"],"خرابی چراغ","Low",["شهرداری","اداره برق"],"خرابی چراغ خیابان. شهرداری برای تعمیر اعزام شود."),
(["درخت","شاخه","افتاد","درخت افتاده"],"خطر درخت","Medium",["شهرداری","اورژانس"],"درخت یا شاخه خطرناک. شهرداری برای پاکسازی اعزام شود."),
(["درگیری","دعوا","نزاع","ناآرامی","اغتشاش","درگیری خیابانی"],"رخداد امنیتی","High",["نهادهای امنیتی","پلیس","اورژانس"],"رخداد امنیتی گزارش شده. نیروهای امنیتی و پلیس برای بررسی و کنترل وضعیت اعزام شوند."),
(["انفجار","صدای انفجار","منفجر","ترکش","انفجار شدید"],"انفجار","Critical",["نهادهای امنیتی","آتش نشانی","اورژانس","پلیس"],"انفجار گزارش شده. نیروهای امنیتی، آتش‌نشانی و اورژانس با اولویت بسیار بالا اعزام شوند."),
(["موشک","بمب","اصابت موشک","اصابت بمب","حمله موشکی","محل اصابت"],"محل اصابت موشک یا بمب","Critical",["نهادهای امنیتی","آتش نشانی","اورژانس","پلیس"],"محل اصابت موشک یا بمب گزارش شده. نیروهای امنیتی و امدادی برای ایمن‌سازی و امدادرسانی اعزام شوند."),
(["بسته مشکوک","شیء مشکوک","خودرو مشکوک","کیف مشکوک","چمدان مشکوک","مورد مشکوک"],"موارد مشکوک","High",["نهادهای امنیتی","پلیس"],"مورد مشکوک گزارش شده. نیروهای امنیتی برای بررسی و ایمن‌سازی محل اعزام شوند.")
]

def fallback(description):
    text = description.lower()
    for keys, typ, sev, agencies, summary in RULES:
        if any(k in text for k in keys):
            return {"incident_type":typ,"severity":sev,"color_code":COLORS[sev],"assigned_agencies":agencies,"region":random.choice(REGIONS),"summary_fa":summary}
    return {"incident_type":"مشکل عمومی شهری","severity":"Medium","color_code":"Yellow","assigned_agencies":["شهرداری"],"region":random.choice(REGIONS),"summary_fa":"رخداد عمومی شهری گزارش شد. شهرداری برای بررسی اعزام شود."}

async def analyze(image_base64: str | None, description: str):
    if settings.openai_api_key:
        model = settings.vision_model if image_base64 else settings.llm_model
        content = [{"type":"text","text":description or "تحلیل این رخداد شهری را انجام دهید."}]
        if image_base64:
            content.append({"type":"image_url","image_url":{"url": image_base64 if image_base64.startswith("data:") else f"data:image/jpeg;base64,{image_base64}"}})
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    f"{settings.openai_base_url.rstrip('/')}/chat/completions",
                    headers={"Authorization":f"Bearer {settings.openai_api_key}"},
                    json={"model":model,"messages":[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":content}],"max_tokens":400,"temperature":0.2},
                )
                r.raise_for_status()
                raw = r.json().get("choices",[{}])[0].get("message",{}).get("content","")
                m = re.search(r"\{[\s\S]*\}", raw)
                obj = json.loads(m.group(0) if m else raw)
                sev = obj.get("severity") if obj.get("severity") in COLORS else "Medium"
                return {"incident_type":obj.get("incident_type") or "نامشخص","severity":sev,"color_code":COLORS[sev],
                        "assigned_agencies":[a for a in obj.get("assigned_agencies",[]) if a in AGENCY_LIST],
                        "region":obj.get("region") or "نامشخص","summary_fa":obj.get("summary_fa") or "تحلیل خودکار انجام شد."}, "openai"
        except Exception:
            pass
    return fallback(description), "fallback"
