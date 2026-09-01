"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { MyReportsList } from "@/components/dashboard/MyReportsList";
import { apiFetch } from "@/lib/api";
import type { SessionUser } from "@/types";

export default function MyReportsPage() {
  const [user,setUser]=useState<SessionUser|null>(null); const [incidents,setIncidents]=useState<any[]|null>(null);
  useEffect(()=>{(async()=>{const me=await apiFetch("/api/auth/me"); const m=await me.json(); if(!m.user){window.location.href="/login?redirect=/my-reports";return;} if(m.user.role!=="CITIZEN"){window.location.href="/dashboard";return;} setUser(m.user); const r=await apiFetch("/api/incidents"); setIncidents((await r.json()).incidents??[]);})().catch(()=>setIncidents([]));},[]);
  if(!user||!incidents)return <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">در حال بارگذاری...</div>;
  return <DashboardShell user={user}><MyReportsList incidents={incidents}/></DashboardShell>;
}
