def agency(a):
    return {"id":a.id,"agencyName":a.agency_name,"assignedAt":a.assigned_at.isoformat()}

def incident(i, include_reporter=True, include_history=False):
    d={
      "id":i.id,"incidentNumber":i.incident_number,"reporterId":i.reporter_id,
      "imageUrl":i.image_url,"description":i.description,"latitude":i.latitude,"longitude":i.longitude,
      "region":i.region,"incidentType":i.incident_type,"severity":i.severity,"colorCode":i.color_code,
      "aiSummary":i.ai_summary,"status":i.status,"createdAt":i.created_at.isoformat(),"updatedAt":i.updated_at.isoformat(),
      "agencies":[agency(a) for a in i.agencies]
    }
    if include_reporter and i.reporter:
        d["reporter"]={"id":i.reporter.id,"name":i.reporter.name,"phone":i.reporter.phone}
    if include_history:
        d["statusHistory"]=[{"id":h.id,"oldStatus":h.old_status,"newStatus":h.new_status,"createdAt":h.created_at.isoformat()} for h in sorted(i.status_history,key=lambda x:x.created_at)]
    return d
