# coding=utf-8

import subprocess
import json
import hmac
import signal
import datetime
import time
from xmlrpc.client import ServerProxy

import psutil
from fastapi import APIRouter, Request
from fastapi import BackgroundTasks


router = APIRouter(
    prefix="/api/webhooks",
    tags=["webhooks"],
    responses={
        404: dict(description="Not found"),
    },
)

REPOSITORY = "repository_name"

def run_script(script_name):
    cwd = f"/tmp/{REPOSITORY}/deploy/scripts"
    proc = subprocess.Popen(f"bash {script_name}.sh", shell=True, cwd=cwd)
    proc.wait()
    return proc.returncode


def restart_processes():
    time.sleep(1)
    server = ServerProxy('http://127.0.0.1:9001/RPC2')
    for process in server.supervisor.getAllProcessInfo():
        server.supervisor.signalProcess(process["name"], signal.SIGKILL.value)


@router.post("/github/postreceive")
async def github_postreceive(request: Request, background_tasks: BackgroundTasks = None):
    body = await request.body()
    body = body.decode()

    secret = "github_webhook_secret"
    h = hmac.new(secret.encode(), body.encode(), digestmod="SHA256")
    computed_signature = h.hexdigest()
    header_signature = request.headers.get("X-Hub-Signature-256", "")
    if not header_signature.startswith("sha256=") or header_signature[len("sha256=") :] != computed_signature:
        return dict(err=1, msg="Invalid Signature")

    payload = json.loads(body)
    branch_name = payload["ref"].split("/")[-1]
    repository_name = payload["repository"]["name"]
    if branch_name != "master":
        return dict(err=1, msg=f"Skip branch {branch_name}")
    if repository_name != REPOSITORY:
        return dict(err=1, msg=f"Skip repository {repository_name}")

    background_tasks.add_task(run_script, "git_pull")

    return dict(err=0, data={
        "repository": {
            "name": REPOSITORY,
            "ref": payload["ref"],
        },
        "commits": {
            "before": payload["before"],
            "after": payload["after"],
        },
        "mode": {
            "created": payload["created"],
            "deleted": payload["deleted"],
            "forced": payload["forced"],
        },
        "pusher": payload["pusher"],
        "delivery": request.headers["X-GitHub-Delivery"],
    })


@router.get("/git/pull")
async def git_pull(request: Request):
    err = run_script("git_pull")
    if err:
        return dict(err=1, msg="同步失败")
    return dict(err=0, msg="同步成功")


@router.get("/npm/build")
async def npm_build(request: Request):
    err = run_script("npm_build")
    if err:
        return dict(err=1, msg="构建失败")
    return dict(err=0, msg="构建成功")


@router.get("/supervisor/restart")
async def supervisor_restart(request: Request, background_tasks: BackgroundTasks = None):
    background_tasks.add_task(restart_processes)
    return dict(err=0, msg="重启已触发")


@router.get("/supervisor/status")
async def supervisor_status(request: Request):
    server = ServerProxy('http://127.0.0.1:9001/RPC2')
    processes = []
    for process in server.supervisor.getAllProcessInfo():
        processes.append({
            "name": process["name"],
            "state": process["statename"],
            "description": process["description"],
        })
    return dict(err=0, msg="", data=processes)


@router.get("/system/ps")
async def system_ps(request: Request):
    processes = []
    for pid in psutil.pids():
        process = psutil.Process(pid)
        cpuTime = process.cpu_times()
        timedelta = datetime.timedelta(seconds=cpuTime.user+cpuTime.system)
        days = timedelta.days
        hours = timedelta.seconds // 60 // 60
        minutes = timedelta.seconds // 60 % 60
        seconds = timedelta.seconds % 60
        processes.append({
            "pid": pid,
            "ppid": process.ppid(),
            "cmdline": ' '.join(process.cmdline()),
            "cwd": process.cwd(),
            "status": process.status(),
            "uid": process.username(),
            "createTime": datetime.datetime.fromtimestamp(process.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
            "cpuTime": f"{days} days, {str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}",
        })

    return dict(err=0, msg="", data=processes)
