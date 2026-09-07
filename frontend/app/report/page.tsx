"use client";

import { useEffect,useState } from "react";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { IncidentReportForm } from "@/components/forms/IncidentReportForm";
import { apiFetch } from "@/lib/api";
import type { SessionUser } from "@/types";

export default function ReportPage(){
 const [user,setUser]=useState<SessionUser|null>(null);
 useEffect(()=>{apiFetch("/api/auth/me").then(r=>r.json()).then(m=>{if(!m.user||m.user.role!=="CITIZEN"){window.location.href="/login?redirect=/report";return;}setUser(m.user);}).catch(()=>{window.location.href="/login?redirect=/report";});},[]);
 if(!user)return <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">در حال بررسی دسترسی...</div>;
 return <DashboardShell user={user}><div className="mb-6"><h1 className="text-2xl font-bold">ثبت رخداد جدید</h1><p className="text-sm text-muted-foreground">مراحل ثبت رخداد را به ترتیب تکمیل کنید</p></div><IncidentReportForm/></DashboardShell>;
}
