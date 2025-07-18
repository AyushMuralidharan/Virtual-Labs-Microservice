from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import requests
import os

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# API endpoints
API_GATEWAY = "http://localhost:8080/api"
BUG_SERVICE = "http://localhost:8000"
CODE_REVIEW_SERVICE = "http://localhost:8001"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        response = requests.post(
            f"{API_GATEWAY}/auth/login",
            json={"email": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json()["token"]
            response = RedirectResponse(url="/dashboard")
            response.set_cookie(key="token", value=token)
            return response
        else:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid credentials"}
            )
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": str(e)}
        )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/")
    
    # Fetch bugs and reviews
    headers = {"Authorization": f"Bearer {token}"}
    try:
        bugs = requests.get(f"{BUG_SERVICE}/client/bugs", headers=headers).json()
        reviews = requests.get(f"{CODE_REVIEW_SERVICE}/reviews", headers=headers).json()
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "bugs": bugs,
                "reviews": reviews
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)}
        )

@app.post("/bugs/create")
async def create_bug(
    request: Request,
    title: str = Form(...),
    description: str = Form(...)
):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/")
    
    try:
        response = requests.post(
            f"{BUG_SERVICE}/client/bugs/create",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": title, "description": description}
        )
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)}
        )

@app.post("/reviews/create")
async def create_review(
    request: Request,
    title: str = Form(...),
    code: str = Form(...),
    description: str = Form(...)
):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/")
    
    try:
        response = requests.post(
            f"{CODE_REVIEW_SERVICE}/reviews",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": title,
                "code": code,
                "description": description
            }
        )
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)}
        )

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("token")
    return response