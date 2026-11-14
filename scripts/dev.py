"""Start the complete local development stack without Docker. Ctrl+C stops it."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
def main():
    port=int(os.getenv('PORT','8080'))
    for number in [port,8001,8002,8003,8004]:
        with socket.socket() as sock:
            try:sock.bind(('127.0.0.1',number))
            except OSError:raise SystemExit(f'Port {number} is occupied. Stop the existing service first or change PORT for the frontend.')
    node=shutil.which('node')
    if not node or not (ROOT/'frontend/node_modules/vite/bin/vite.js').exists():raise SystemExit('Run npm ci in frontend before starting.')
    runtime=ROOT/'.runtime';runtime.mkdir(exist_ok=True)
    env=os.environ.copy();env['CATALOG_URL']='http://127.0.0.1:8001';env['MEASUREMENTS_URL']='http://127.0.0.1:8003';env['SIMILARITY_URL']='http://127.0.0.1:8002';env['DATA_DIR']=str(ROOT/'data');env['DOCS_DIR']=str(ROOT/'docs');env.pop('ROOT_PATH',None)
    reload_args=['--reload'] if '--reload' in sys.argv else []
    commands=[(name,[sys.executable,'-m','uvicorn',f'services.{name}.app.main:app','--host','127.0.0.1','--port',str(number),*reload_args],ROOT) for name,number in [('catalog',8001),('measurements',8003),('similarity',8002),('planning',8004)]]
    commands.append(('frontend',[node,str(ROOT/'frontend/node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port',str(port),'--strictPort'],ROOT/'frontend'))
    processes=[];logs=[]
    try:
        for name,command,cwd in commands:
            log=(runtime/f'{name}.log').open('w',encoding='utf-8');logs.append(log)
            process=subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name=='nt' else 0)
            processes.append(process)
        for _ in range(60):
            if any(p.poll() is not None for p in processes):raise RuntimeError('A service exited; inspect .runtime/*.log')
            try:
                for url in [f'http://127.0.0.1:{number}/health' for number in [port,8001,8003,8002,8004]]:
                    with urllib.request.urlopen(url,timeout=2) as r:assert r.status==200
                break
            except Exception:time.sleep(.5)
        else:raise RuntimeError('Startup timed out; inspect .runtime/*.log')
        print(f'\nEarth Analog Finder: http://localhost:{port}',flush=True)
        for service in ['catalog','measurements','similarity','planning']:print(f'{service} docs: http://localhost:{port}/api/{service}/docs',flush=True)
        print('Ctrl+C stops all services. Logs: .runtime/\n',flush=True)
        while all(p.poll() is None for p in processes):time.sleep(1)
    except KeyboardInterrupt:pass
    finally:
        for p in reversed(processes):
            if p.poll() is None:
                if os.name=='nt':
                    import signal
                    p.send_signal(signal.CTRL_BREAK_EVENT)
                else:p.terminate()
        for p in reversed(processes):
            try:p.wait(timeout=8)
            except subprocess.TimeoutExpired:p.kill()
        for log in logs:log.close()

if __name__=='__main__':main()
