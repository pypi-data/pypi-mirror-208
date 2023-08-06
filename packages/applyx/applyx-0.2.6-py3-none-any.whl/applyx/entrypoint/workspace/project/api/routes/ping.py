# coding=utf-8

from fastapi import APIRouter, Request

from applyx.utils import get_store_dir


STORE_DIR = get_store_dir()

router = APIRouter(
    prefix="/api/ping",
    tags=["ping"],
    responses={
        404: dict(description="Not found"),
    },
)


@router.get("")
async def ping_pong(request: Request):
    return dict(
        ip=request.state.real_ip,
        agent=request.headers.get("user-agent"),
    )
