from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import subprocess
import time
import platform

PORT = 8848
PROC_TITLE = 'gcli_multiproc_procnum'
CHILD_PROC_ENV_IDENTIFIER = 'GCLI_CHILD_PROC_NUM'
PROCS = {}

""" 
def kill(proc_title, proc):
    proc_pid = proc.pid
    if platform.system() == 'Windows':
        subprocess.run(
            f'TASKKILL /F /T /FI "WINDOWTITLE eq {proc_title}*"', shell=True)
    elif platform.system() == 'Linux':
        os.killpg(proc_pid, signal.SIGINT)
 """


def spawn_gcli_terminal(proc_num, service_code, params):
    params_str = json.dumps(params, separators=[',', ':'])
    '''
    win_title = f'{PROC_TITLE}_{proc_num}'
    if platform.system() == 'Windows':
        cmd = f'start "{win_title}" cmd /k "sleep 1 && echo {service_code} && sleep 15 && echo {params_str}"'
        proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        PROCS[win_title] = proc
    elif platform.system() == 'Linux':
    '''

    win_title = f'{proc_num}.gcli'
    output_logs_dir = os.path.join(os.path.expanduser('~'), '.grepsr-experiments', 'multi_proc')
    os.makedirs(output_logs_dir, exist_ok=True)
    # turn multiprocess flag off to prevent infinite recursion.
    cmds = ["gcli", "crawler", "test", "-m", "0", "-s", service_code, "-p", params_str]
    # if platform.system() == 'Windows':
    #     cmds[0] = 'C:\\Users\\DELL\\bin\\gcli.cmd'
    with open(os.path.join(output_logs_dir, f'{win_title}.mp.out'), 'w') as fd:
        # this env var tells that the current crawler is a child process initiated by main parent.
        # this information might be needed somewhere
        os.environ[CHILD_PROC_ENV_IDENTIFIER] = str(proc_num)
        proc = subprocess.Popen(cmds, stdin=subprocess.PIPE, stdout=fd, stderr=subprocess.STDOUT)
        # wait a little so that there is less chance of race condition when gcli starts processing.
        time.sleep(2)
        PROCS[win_title] = proc


class ProcessHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = None
        respo = {'success': False, 'message': ''}
        try:
            content_length = int(self.headers['content-length'])
        except TypeError:
            respo = {'success': False,
                     'message': 'Could not convert content-length header to integer'}
        if content_length is not None:
            if self.headers['content-type'].split(';')[0] == 'application/json':
                body = self.rfile.read(content_length).decode('UTF-8')
                try:
                    data = json.loads(body)
                    service_code = data.get('service_code')
                    params = data.get('params')
                    proc_num = data.get('proc_num')
                    if (service_code is None) or (params is None) or (proc_num is None):
                        respo = {
                            'success': False, 'message': 'No service code or params or proc number found'}
                    else:
                        spawn_gcli_terminal(proc_num, service_code, params)
                        respo = {'success': True, 'data': {'message': 'Spawned a process successfully!'}}
                except json.JSONDecodeError:
                    respo = {'success': False,
                             'message': 'request body is not JSON.'}

        self.send_response(200)
        self.send_header('content-type', 'application/json')
        self.end_headers()

        self.wfile.write(bytes(json.dumps(respo), "utf8"))

def start():
    with HTTPServer(('127.0.0.1', PORT), ProcessHandler) as server:
        try:
            print('C&C: MultiProcess facillitation Python Server started', flush=True)
            server.serve_forever()
        except (Exception, KeyboardInterrupt) as e:
            if not isinstance(e, KeyboardInterrupt):
                print('\n', flush=True)
                print(f'Do not Panic. Caught Exception. `{e}`', flush=True)
            # print('', flush=True)
            # print('Force Exit. Cleaning server and child processes.', flush=True)
            server.server_close()

    for i, proc in PROCS.items():
        # print('Terminating Child process:: ', i, flush=True)
        proc.terminate()
        proc.communicate()
        proc.kill()
        print('Terminated Child process:: ', i, flush=True)
        # kill(i, proc)


    # outs, errs = proc.communicate(signal.CTRL_BREAK_EVENT)
    # outs, errs = proc.communicate(signal.CTRL_C_EVENT)

    # if hasattr(signal, 'CTRL_C_EVENT'):
    #     # windows. Need CTRL_C_EVENT to raise the signal in the whole process group
    #     print('using win method to kill whole process group', flush=True)
    #     os.kill(os.getpid(), signal.CTRL_C_EVENT)
    #     # os.kill(os.getpid(), signal.CTRL_BREAK_EVENT)
    # else:
    #     print('using unix method to kill whole process group', flush=True)
    #     # unix.
    #     pgid = os.getpgid(os.getpid())
    #     if pgid == 1:
    #         os.kill(os.getpid(), signal.SIGINT)
    #     else:
    #         os.killpg(os.getpgid(os.getpid()), signal.SIGINT)

if __name__ == '__main__':
    pass