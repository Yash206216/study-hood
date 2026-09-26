import csv
import io
from datetime import datetime

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Application, College
from app.auth import require_admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Study Hood")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/apply", response_class=HTMLResponse)
def apply_form(request: Request, college: str = "", db: Session = Depends(get_db)):
    data = {}
    if college:
        match = db.query(College).filter(College.slug == college).first()
        if match:
            data["preferred_college"] = match.name
            data["source_college"] = match.slug
    return templates.TemplateResponse(request, "apply.html", {"errors": None, "data": data})


@app.post("/apply")
def submit_application(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    city: str = Form(...),
    course_interested: str = Form(...),
    preferred_college: str = Form(...),
    intake_year: str = Form(""),
    twelfth_percentage: str = Form(""),
    message: str = Form(""),
    consent: str = Form(None),
    source_college: str = Form(""),
    db: Session = Depends(get_db),
):
    errors = []
    if "@" not in email or "." not in email:
        errors.append("Enter a valid email address.")
    if not phone.strip().isdigit() or len(phone.strip()) < 10:
        errors.append("Enter a valid 10-digit phone number.")
    if not consent:
        errors.append("You must consent to data processing to submit this form.")

    if errors:
        data = {
            "full_name": full_name, "email": email, "phone": phone, "city": city,
            "course_interested": course_interested, "preferred_college": preferred_college,
            "intake_year": intake_year, "source_college": source_college,
            "twelfth_percentage": twelfth_percentage, "message": message,
        }
        return templates.TemplateResponse(request, "apply.html", {"errors": errors, "data": data})

    record = Application(
        full_name=full_name.strip(),
        email=email.strip(),
        phone=phone.strip(),
        city=city.strip(),
        course_interested=course_interested.strip(),
        preferred_college=preferred_college.strip(),
        intake_year=intake_year.strip(),
        twelfth_percentage=twelfth_percentage.strip(),
        message=message.strip(),
        consent_given=True,
        source_college=source_college.strip() or None,
    )
    db.add(record)
    db.commit()
    return RedirectResponse(url="/thank-you", status_code=303)


@app.get("/thank-you", response_class=HTMLResponse)
def thank_you(request: Request):
    return templates.TemplateResponse(request, "thank_you.html", {})


@app.get("/college/{slug}", response_class=HTMLResponse)
def college_page(slug: str, request: Request, db: Session = Depends(get_db)):
    college = db.query(College).filter(College.slug == slug).first()
    if not college:
        raise HTTPException(status_code=404, detail="College page not found")
    return templates.TemplateResponse(request, "college_page.html", {"college": college})


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db), _=Depends(require_admin)):
    applications = db.query(Application).order_by(Application.created_at.desc()).all()
    return templates.TemplateResponse(request, "admin_dashboard.html", {"applications": applications})


@app.get("/admin/export")
def export_csv(db: Session = Depends(get_db), _=Depends(require_admin)):
    applications = db.query(Application).order_by(Application.created_at.desc()).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["ID", "Full Name", "Email", "Phone", "City", "Course Interested",
                      "Preferred College", "Intake Year", "Came From College Page", "12th %", "Message", "Consent", "Submitted At"])
    for a in applications:
        writer.writerow([a.id, a.full_name, a.email, a.phone, a.city, a.course_interested,
                          a.preferred_college, a.intake_year, a.source_college or "", a.twelfth_percentage, a.message,
                          a.consent_given, a.created_at])
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=applications_{datetime.utcnow().date()}.csv"},
    )


@app.delete("/admin/applications/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    record = db.query(Application).filter(Application.id == app_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(record)
    db.commit()
    return {"deleted": app_id}


def slugify(text: str) -> str:
    slug = "".join(c.lower() if c.isalnum() else "-" for c in text.strip())
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


@app.get("/admin/colleges", response_class=HTMLResponse)
def list_colleges(request: Request, db: Session = Depends(get_db), _=Depends(require_admin)):
    colleges = db.query(College).order_by(College.created_at.desc()).all()
    return templates.TemplateResponse(request, "admin_colleges.html", {"colleges": colleges, "error": None})


@app.post("/admin/colleges")
def create_college(
    request: Request,
    name: str = Form(...),
    city: str = Form(""),
    description: str = Form(""),
    courses_offered: str = Form(""),
    website: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    slug = slugify(name)
    if not slug:
        colleges = db.query(College).order_by(College.created_at.desc()).all()
        return templates.TemplateResponse(request, "admin_colleges.html",
                                           {"colleges": colleges, "error": "College name is required."})

    existing = db.query(College).filter(College.slug == slug).first()
    if existing:
        colleges = db.query(College).order_by(College.created_at.desc()).all()
        return templates.TemplateResponse(request, "admin_colleges.html", {
            "colleges": colleges,
            "error": f"A college with a similar name already exists (link: /college/{slug}).",
        })

    college = College(
        slug=slug, name=name.strip(), city=city.strip(),
        description=description.strip(), courses_offered=courses_offered.strip(),
        website=website.strip(),
    )
    db.add(college)
    db.commit()
    return RedirectResponse(url="/admin/colleges", status_code=303)


@app.delete("/admin/colleges/{college_id}")
def delete_college(college_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    record = db.query(College).filter(College.id == college_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(record)
    db.commit()
    return {"deleted": college_id}
