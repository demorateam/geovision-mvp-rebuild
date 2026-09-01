"use client";

import { useEffect,useState } from "react";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { apiFetch } from "@/lib/api";
import type { SessionUser } from "@/types";
import { MapPin, Clock } from "lucide-react";
import { STATUS_LABELS, SEVERITY_LABELS } from "@/types";
import { useParams } from "next/navigation";

const ORGANIZATION_MAP: Record<string,string>={municipality:"شهرداری",security:"نهادهای امنیتی",telecom:"مخابرات",water:"آب و فاضلاب",electricity:"اداره برق",gas:"گاز",emergency:"اورژانس",police:"پلیس",fire:"آتش نشانی"};
const STATUS_COLOR:Record<string,string>={PENDING:"bg-orange-100 text-orange-700",IN_PROGRESS:"bg-blue-100 text-blue-700",RESOLVED:"bg-green-100 text-green-700"};
const SEVERITY_COLOR:Record<string,string>={Low:"bg-gray-100 text-gray-600",Medium:"bg-yellow-100 text-yellow-800",High:"bg-red-100 text-red-700",Critical:"bg-pink-200 text-pink-800"};

export default function OrganizationPage(){
 const params=useParams<{slug:string}>(); const [user,setUser]=useState<SessionUser|null>(null); const [incidents,setIncidents]=useState<any[]|null>(null);
 const agency=ORGANIZATION_MAP[params.slug];
 useEffect(()=>{(async()=>{if(!agency){window.location.href="/admin/incidents";return;} const m=await (await apiFetch("/api/auth/me")).json(); if(!m.user||m.user.role!=="ADMIN"){window.location.href="/dashboard";return;} setUser(m.user); const r=await apiFetch("/api/incidents"); const all=(await r.json()).incidents??[]; setIncidents(all.filter((i:any)=>i.agencies?.some((a:any)=>a.agencyName===agency)));})().catch(()=>setIncidents([]));},[agency]);
 if(!agency)return null;
 if(!user||!incidents)return <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">در حال بارگذاری...</div>;
 return <DashboardShell user={user}><div className="p-6"><h1 className="mb-4 text-xl font-semibold">{agency}</h1>{incidents.length===0?<p className="text-sm text-muted-foreground">حادثه‌ای یافت نشد.</p>:<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">{incidents.map((inc:any)=><div key={inc.id} className="overflow-hidden rounded-xl border bg-white shadow-sm"><div className="relative flex h-36 items-center justify-center bg-gray-100">{inc.imageUrl?<img src={inc.imageUrl} alt="" className="h-full w-full object-cover"/>:<span className="text-xs text-gray-400">بدون تصویر</span>}<span className={`absolute right-2 top-2 rounded-full px-2 py-0.5 text-xs ${STATUS_COLOR[inc.status]??"bg-gray-100 text-gray-600"}`}>{STATUS_LABELS[inc.status]??inc.status}</span><span className={`absolute left-2 top-2 rounded-full px-2 py-0.5 text-xs ${SEVERITY_COLOR[inc.severity]??"bg-gray-100 text-gray-600"}`}>{SEVERITY_LABELS[inc.severity]??inc.severity}</span></div><div className="space-y-2 p-3"><div className="flex items-center justify-between text-xs text-muted-foreground"><span className="flex items-center gap-1"><Clock className="h-3 w-3"/>{new Intl.DateTimeFormat("fa-IR").format(new Date(inc.createdAt))}</span><span className="font-mono">{inc.id.slice(0,6)}</span></div><p className="text-sm font-semibold">{inc.incidentType}</p><p className="line-clamp-3 text-sm text-muted-foreground">{inc.aiSummary||"تحلیلی ثبت نشده"}</p><div className="flex items-center gap-1 text-xs text-muted-foreground"><MapPin className="h-3 w-3"/><span>{inc.region||"—"}</span></div><p className="line-clamp-2 border-t pt-1 text-[11px] text-gray-400">{inc.description}</p></div></div>)}</div>}</div></DashboardShell>;
}
