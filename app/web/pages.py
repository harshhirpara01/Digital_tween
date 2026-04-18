import os
import pathlib

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates

module_path = str(pathlib.Path(__file__).resolve().parent.parent.parent)
templates = Jinja2Templates(directory=os.path.join(module_path, "templates"))

web = APIRouter()


@web.get("/")
def root():
    return RedirectResponse(url="/login", status_code=302)


@web.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "title": "Login — Digital Tween"},
    )


@web.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "title": "Register — Digital Tween"},
    )


@web.get("/home")
def home_page(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "title": "Home — Digital Tween"},
    )


@web.get("/logs")
def logs_page(request: Request):
    return templates.TemplateResponse(
        "logs.html",
        {"request": request, "title": "Behavior logs — Digital Tween"},
    )


@web.get("/account")
def account_page(request: Request):
    return templates.TemplateResponse(
        "account.html",
        {"request": request, "title": "Account — Digital Tween"},
    )
