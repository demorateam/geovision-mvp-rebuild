"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { CitizenDashboard } from "@/components/dashboard/CitizenDashboard";
import { AdminDashboard } from "@/components/dashboard/AdminDashboard";
import { AgencyDashboard } from "@/components/dashboard/AgencyDashboard";
import { apiFetch } from "@/lib/api";
import type { SessionUser } from "@/types";

export default function DashboardPage() {
  const [user,setUser]=useState<SessionUser|null>(null);
  const [data,setData]=useState<any>(null);
  const [error,setError]=useState(false);

  useEffect(()=>{ (async()=>{
    try {
      const me=await apiFetch("/api/auth/me"); const m=await me.json();
      if(!m.user){ window.location.href="/login?redirect=/dashboard"; return; }
      setUser(m.user);
      if(m.user.role==="ADMIN"){
        const r=await apiFetch("/api/stats"); if(!r.ok) throw new Error(); setData({stats:await r.json()});
      } else {
        const r=await apiFetch("/api/incidents"); if(!r.ok) throw new Error(); setData({incidents:(await r.json()).incidents});
      }
    } catch { setError(true); }
  })(); },[]);

  if(error) return <div className="flex min-h-screen items-center justify-center">خطا در دریافت اطلاعات سامانه</div>;
  if(!user || !data) return <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">در حال بارگذاری...</div>;

  return <DashboardShell user={user}>
    {user.role==="ADMIN" ? <AdminDashboard stats={data.stats}/> :
     user.role==="AGENCY" ? <AgencyDashboard incidents={data.incidents} agencyName={user.agency ?? ""}/> :
     <CitizenDashboard incidents={data.incidents} userName={user.name}/>}
  </DashboardShell>;
}
