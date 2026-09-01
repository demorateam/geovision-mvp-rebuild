"use client";

import { useEffect,useState } from "react";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { AgencyIncidentDetail } from "@/components/dashboard/AgencyIncidentDetail";
import { apiFetch } from "@/lib/api";
import type { SessionUser } from "@/types";
import { useParams } from "next/navigation";

export default function AgencyIncidentDetailPage(){
 const params=useParams<{id:string}>(); const [user,setUser]=useState<SessionUser|null>(null); const [incident,setIncident]=useState<any|null>(null);
 useEffect(()=>{(async()=>{const m=await (await apiFetch("/api/auth/me")).json(); if(!m.user||m.user.role!=="AGENCY"){window.location.href="/dashboard";return;} setUser(m.user); const r=await apiFetch(`/api/incidents/${params.id}`); if(!r.ok){window.location.href="/agency/incidents";return;} setIncident((await r.json()).incident);})().catch(()=>{window.location.href="/agency/incidents";});},[params.id]);
 if(!user||!incident)return <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">در حال بارگذاری...</div>;
 return <DashboardShell user={user}><AgencyIncidentDetail incident={incident}/></DashboardShell>;
}
