import psutil

def find_process_by_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        for conn in proc.info.get('connections', []):
            if conn.laddr.port == port:
                return proc.pid
    return None

def kill_process(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        print(f"Process with PID {pid} terminated successfully.")
    except psutil.NoSuchProcess:
        print(f"No such process with PID {pid}.")
    except psutil.AccessDenied:
        print(f"Access denied. Unable to terminate process with PID {pid}.")
    except Exception as e:
        print(f"Error occurred while terminating process with PID {pid}: {e}")

if __name__ == "__main__":
    port = 5000
    pid = find_process_by_port(port)
    if pid:
        kill_process(pid)
    else:
        print(f"No process found using port {port}.")
