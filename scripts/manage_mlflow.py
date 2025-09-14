import os
import platform
import subprocess
import time
from pathlib import Path

import psutil
import typer
from typing_extensions import Annotated

# --- 설정 ---
PORT = 5000
HOST = "127.0.0.1"
PID_DIR = Path(os.path.expanduser("~/.tmp/pids"))
PID_FILE = PID_DIR / "mlflow_server.pid"


# 애플리케이션 생성
app = typer.Typer(
    help="MLflow 서버를 관리하는 CLI 도구",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def find_proc_and_kill(port: int):
    """지정된 포트를 사용하는 프로세스와 그 자식들을 찾아 종료합니다."""
    current_pid = os.getpid()
    parent_pid = os.getppid()

    listening_proc = None
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.pid in (current_pid, parent_pid):
            continue
        try:
            for conn in proc.net_connections(kind="inet"):
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    listening_proc = proc
                    break
            if listening_proc:
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if listening_proc:
        try:
            procs_to_kill = [listening_proc] + listening_proc.children(recursive=True)
            typer.echo(
                f"✅ 포트 {port}에서 실행 중인 프로세스(PID: {listening_proc.pid})와 자식들을 종료합니다: {[p.pid for p in procs_to_kill]}"
            )

            for p in reversed(procs_to_kill):
                p.terminate()

            gone, alive = psutil.wait_procs(procs_to_kill, timeout=10)

            if alive:
                typer.echo(f"❗️ 강제 종료: {[p.pid for p in alive]}")
                for p in alive:
                    p.kill()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return False


@app.command(name="start", help="MLflow 서버를 시작합니다.")
def start_server(
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="서버가 이미 실행 중인 경우 강제로 재시작합니다.",
        ),
    ] = False,
    store_path: Annotated[
        str,
        typer.Option(
            "--store-path",
            help="MLflow 백엔드 스토어 및 아티팩트 루트 경로. 기본값: ./mlruns",
        ),
    ] = "./mlruns",
):
    """
    MLflow 서버를 백그라운드에서 시작합니다.
    """
    # PID 파일 디렉터리 생성
    PID_DIR.mkdir(parents=True, exist_ok=True)

    if PID_FILE.exists():
        pid = int(PID_FILE.read_text())
        if psutil.pid_exists(pid):
            if not force:
                typer.echo(
                    f"🤷‍♂️ MLflow 서버가 이미 PID {pid}로 실행 중입니다. 중지 후 다시 시도하거나 --force 옵션을 사용하세요."
                )
                raise typer.Exit(1)
            else:
                typer.echo("🚀 --force 옵션이 감지되었습니다. 기존 서버를 종료합니다.")
                find_proc_and_kill(PORT)
        else:
            # PID 파일은 있지만 프로세스가 없는 경우 (비정상 종료)
            PID_FILE.unlink()

    # 포트 충돌 방지를 위해 한 번 더 확인 및 정리
    if find_proc_and_kill(PORT):
        time.sleep(1)  # 포트가 완전히 해제될 때까지 잠시 대기

    typer.echo(f"✨ 새로운 MLflow 서버를 포트 {PORT}에서 시작합니다.")
    typer.echo(f"🗂️  스토어 경로: {store_path}")

    mlflow_server_command = (
        f"mlflow server --host {HOST} --port {PORT} "
        f"--backend-store-uri {store_path} --default-artifact-root {store_path}"
    )

    # --- Cross-platform background process startup ---
    popen_kwargs = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if platform.system() == "Windows":
        # Windows에서는 DETACHED_PROCESS 플래그를 사용하여 새 콘솔에서 실행
        popen_kwargs["creationflags"] = subprocess.DETACHED_PROCESS
    else:
        # Unix 계열에서는 setsid를 사용하여 세션을 분리
        popen_kwargs["preexec_fn"] = os.setsid
    # -------------------------------------------------

    server_process = subprocess.Popen(
        mlflow_server_command.split(),
        **popen_kwargs,
    )

    # PID 파일 작성
    PID_FILE.write_text(str(server_process.pid))

    typer.echo(
        f"✅ MLflow 서버가 성공적으로 시작되었습니다. (PID: {server_process.pid})"
    )
    typer.echo(f"🔗 주소: http://{HOST}:{PORT}")


@app.command(name="stop", help="MLflow 서버를 중지합니다.")
def stop_server():
    """
    실행 중인 MLflow 서버를 중지합니다.
    """
    killed_something = False

    # 1. Find and kill the process listening on the port
    listening_proc = None
    # find_proc_and_kill과 로직이 중복되지만, stop에서는 kill전에 메시지를 출력하는 등
    # 세부 동작이 달라 별도로 구현
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        # 자기 자신과 부모 프로세스는 건너뛰기
        if proc.pid in (os.getpid(), os.getppid()):
            continue
        try:
            # Check if it's an mlflow or related process
            cmd = proc.cmdline()
            if not any("mlflow" in s or "gunicorn" in s or "uvicorn" in s for s in cmd):
                continue

            for conn in proc.net_connections(kind="inet"):
                if conn.laddr.port == PORT and conn.status == psutil.CONN_LISTEN:
                    listening_proc = proc
                    break
            if listening_proc:
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if listening_proc:
        typer.echo(
            f"🔍 포트 {PORT}에서 리스닝 중인 서버 프로세스(PID: {listening_proc.pid})를 종료합니다."
        )
        try:
            procs_to_kill = [listening_proc] + listening_proc.children(recursive=True)
            for p in reversed(procs_to_kill):
                p.terminate()
            gone, alive = psutil.wait_procs(procs_to_kill, timeout=5)
            if alive:
                for p in alive:
                    p.kill()
            killed_something = True
        except psutil.NoSuchProcess:
            pass  # Already gone

    # 2. Clean up the manager process from the PID file
    if PID_FILE.exists():
        pid_from_file = int(PID_FILE.read_text())
        # 방금 위에서 리스닝 프로세스를 죽였다면, 그 PID와 파일의 PID가 같은지 확인
        if listening_proc and pid_from_file == listening_proc.pid:
            pass
        else:
            try:
                manager_proc = psutil.Process(pid_from_file)
                typer.echo(
                    f"🔍 PID 파일의 관리 프로세스(PID: {pid_from_file})를 추가로 종료합니다."
                )
                procs_to_kill = [manager_proc] + manager_proc.children(recursive=True)
                for p in reversed(procs_to_kill):
                    p.terminate()
                gone, alive = psutil.wait_procs(procs_to_kill, timeout=5)
                if alive:
                    for p in alive:
                        p.kill()
                killed_something = True
            except psutil.NoSuchProcess:
                # Manager process was already gone, that's fine
                pass
        PID_FILE.unlink()

    if killed_something:
        typer.echo("✅ MLflow 서버 종료 절차를 완료했습니다.")
    else:
        typer.echo("🤷‍♂️ 현재 실행 중인 MLflow 서버를 찾을 수 없습니다.")


@app.command(name="status", help="MLflow 서버의 실행 상태를 확인합니다.")
def server_status():
    """
    MLflow 서버의 현재 실행 상태를 확인합니다.
    """
    listening_proc = None
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            # Check if it's an mlflow or related process
            cmd = proc.cmdline()
            if not any("mlflow" in s or "gunicorn" in s or "uvicorn" in s for s in cmd):
                continue

            for conn in proc.net_connections(kind="inet"):
                if conn.laddr.port == PORT and conn.status == psutil.CONN_LISTEN:
                    listening_proc = proc
                    break
            if listening_proc:
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if listening_proc:
        typer.echo("✅ MLflow 서버가 실행 중입니다.")
        typer.echo(f"  - 서비스 PID: {listening_proc.pid} (포트 리스닝)")
        typer.echo(f"  - 주소: http://{HOST}:{PORT}")

        if PID_FILE.exists():
            pid_from_file = int(PID_FILE.read_text())
            # mlflow server는 관리 프로세스와 실제 서빙 프로세스가 다를 수 있습니다.
            # PID 파일에는 관리 프로세스 PID가 저장됩니다.
            if pid_from_file != listening_proc.pid:
                typer.echo(f"  - 관리 PID: {pid_from_file} (중지 시 사용)")
                try:
                    manager_proc = psutil.Process(pid_from_file)
                    typer.echo(
                        f"  - 시작 시간: {time.ctime(manager_proc.create_time())}"
                    )
                except psutil.NoSuchProcess:
                    typer.echo(
                        "  - 경고: 관리 프로세스를 찾을 수 없습니다. 'stop' 명령이 실패할 수 있습니다."
                    )
            else:  # PID가 같은 경우 (드묾)
                try:
                    proc_from_file = psutil.Process(pid_from_file)
                    typer.echo(
                        f"  - 시작 시간: {time.ctime(proc_from_file.create_time())}"
                    )
                except psutil.NoSuchProcess:
                    pass  # 이미 위에서 확인했지만 안전장치
        else:
            typer.echo(
                "  - 참고: PID 파일이 없습니다. 'stop' 명령이 정확히 동작하지 않을 수 있습니다."
            )
        return

    # 수신 대기 중인 프로세스가 없는 경우
    typer.echo("❌ MLflow 서버가 실행되고 있지 않습니다.")
    if PID_FILE.exists():
        pid_from_file = int(PID_FILE.read_text())
        if not psutil.pid_exists(pid_from_file):
            typer.echo("🗑️ 오래된 PID 파일을 삭제합니다.")
            PID_FILE.unlink()


if __name__ == "__main__":
    app()
