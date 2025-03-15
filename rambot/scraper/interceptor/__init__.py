import time
import subprocess
import tempfile
import os

temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", dir=os.getcwd())

def start_mitmproxy(proxy_port: str = "8080"):
    """
    Démarre mitmproxy dans un thread pour ne pas bloquer l'exécution principale.
    """
    def run_mitmproxy():
        mitmproxy_command = [
            "mitmdump", "-s", "rambot/rambot/scraper/interceptor/interceptor.py", "--listen-port", proxy_port, "--quiet"
        ]
        subprocess.Popen(mitmproxy_command)
        time.sleep(2)
    run_mitmproxy()

def stop_mitmproxy():
    """
    Arrêter mitmproxy
    """
    subprocess.call(['pkill', 'mitmdump'])
    # os.remove("captured_requests.json")