# coding=utf-8

from fastapi import APIRouter, Request


router = APIRouter(
    tags=["default"],
    responses={
        404: dict(description="Not found"),
    },
)


@router.get("/")
async def default(request: Request):
    templates = request.app.jinja_templates
    return templates.TemplateResponse(
        "page.html", dict(request=request, main="default/main.js")
    )
