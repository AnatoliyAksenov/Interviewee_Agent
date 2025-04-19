from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse

from app.api.evaluation import router as evaluation_router
from app.api.interview import router as interview_router
from app.api.resume import router as resume_router
from app.api.recruiter_training import router as recruiter_training_router
from app.api.intermediate_evaluation import router as intermediate_evaluation_router

app = FastAPI()

# Инициализируем роутеры для API
app.include_router(evaluation_router)
app.include_router(interview_router)
app.include_router(resume_router)
app.include_router(recruiter_training_router)
app.include_router(intermediate_evaluation_router)

# Templates for frontend
templates = Jinja2Templates(directory="app/frontend")

# Роуты для отображения HTML страницы
@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/select-persona", response_class=HTMLResponse)
async def select_persona_page(request: Request):
    return templates.TemplateResponse("select-candidate.html", {"request": request})

@app.get("/select-profile", response_class=HTMLResponse)
async def select_persona_page(request: Request):
    return templates.TemplateResponse("select-profile.html", {"request": request})

@app.get("/interview", response_class=HTMLResponse)
async def interview_page(request: Request):
    return templates.TemplateResponse("interview.html", {"request": request})

@app.get("/interview_profile", response_class=HTMLResponse)
async def interview_page(request: Request):
    return templates.TemplateResponse("interview_profile.html", {"request": request})

@app.get("/evaluation", response_class=HTMLResponse)
async def evaluation_page(request: Request):
    return templates.TemplateResponse("evaluation.html", {"request": request})

@app.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})

@app.get("/resume-analysis", response_class=HTMLResponse)
async def resume_analysis_page(request: Request):
    return templates.TemplateResponse("resume-analysis.html", {"request": request})

@app.get("/recruiter-training", response_class=HTMLResponse)
async def recruiter_training_page(request: Request):
    return templates.TemplateResponse("recruiter-training.html", {"request": request})

@app.get("/recruiter-training-session")
async def recruiter_training_session(
    request: Request,
    position: str,
    personality: str,
    experience: str,
    honesty: str
):
    return templates.TemplateResponse(
        "recruiter-training-session.html",
        {
            "request": request,
            "position": position,
            "personality": personality,
            "experience": experience,
            "honesty": honesty
        }
    )

@app.get("/recruiter-training-check")
async def get_recruiter_training_check():
    return FileResponse("app/frontend/recruiter-training-check.html")

@app.get("/recruiter-training-check-results")
async def get_recruiter_training_check_results():
    """
    Страница с результатами оценки кандидата.
    """
    return FileResponse("app/frontend/recruiter-training-check-results.html")
