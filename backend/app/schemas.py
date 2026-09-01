from pydantic import BaseModel, Field, field_validator
from typing import Literal

AGENCY_LIST = ["شهرداری","نهادهای امنیتی","مخابرات","آب و فاضلاب","اداره برق","گاز","اورژانس","پلیس","آتش نشانی"]
Severity = Literal["Low","Medium","High","Critical"]
Status = Literal["PENDING","IN_PROGRESS","RESOLVED"]

class UserOut(BaseModel):
    id: str; name: str; phone: str; role: str; agency: str | None = None

class AuthRequest(BaseModel):
    action: Literal["request","verify"]
    portal: Literal["citizen","admin"] = "citizen"
    name: str | None = None
    phone: str = Field(pattern=r"^09\d{9}$")
    code: str | None = None

class IncidentCreate(BaseModel):
    imageUrl: str = Field(pattern=r"^/uploads/")
    description: str = Field(min_length=5, max_length=2000)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    region: str | None = Field(default=None, max_length=100)
    incidentType: str | None = Field(default=None, max_length=100)
    severity: Severity | None = None
    colorCode: str | None = None
    aiSummary: str | None = Field(default=None, max_length=1000)
    assignedAgencies: list[str] | None = None

    @field_validator("assignedAgencies")
    @classmethod
    def valid_agencies(cls, v):
        if v is not None and (len(v) > len(AGENCY_LIST) or any(x not in AGENCY_LIST for x in v)):
            raise ValueError("سازمان نامعتبر")
        return v

class IncidentStatusUpdate(BaseModel):
    status: Status | None = None

class AnalysisRequest(BaseModel):
    imageBase64: str | None = Field(default=None, max_length=18_000_000)
    description: str = Field(min_length=3, max_length=2000)
