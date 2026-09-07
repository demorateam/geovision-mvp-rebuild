"use client";

import { useEffect,useState } from "react";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { AgencyIncidentsManager } from "@/components/dashboard/AgencyIncidentsManager";
import { apiFetch } from "@/lib/api";
import type { SessionUser } from "@/types";

export default function AgencyIncidentsPage(){
 const [user,setUser]=useState<SessionUser|null>(null); const [incidents,setIncidents]=useState<any[]|null>(null);
 useEffect(()=>{(async()=>{const m=await (await apiFetch("/api/auth/me")).json(); if(!m.user||m.user.role!=="AGENCY"){window.location.href="/dashboard";return;} setUser(m.user); const r=await apiFetch("/api/incidents"); setIncidents((await r.json()).incidents??[]);})().catch(()=>setIncidents([]));},[]);
 if(!user||!incidents)return <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">در حال بارگذاری...</div>;
 return <DashboardShell user={user}><AgencyIncidentsManager incidents={incidents} agencyName={user.agency??""}/></DashboardShell>;
}
