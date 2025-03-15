import json
from mitmproxy import http

from . import temp_file
print(f"tempfile: {temp_file}")

requests = []


def request(flow: http.HTTPFlow) -> None:
    """
    Fonction appelée à chaque requête interceptée par mitmproxy.
    """
    request_data = {
        'method': flow.request.method,
        'url': flow.request.url,
        'status_code': flow.response.status_code if flow.response else 'No Response',
        'headers': dict(flow.request.headers),
        'body': flow.request.get_text() if flow.request.content else None,
        "response": {
            'status_code': flow.response.status_code if flow.response else 'No Response',
            'headers': dict(flow.response.headers) if flow.response else None,
            'body': flow.response.get_text() if flow.response and flow.response.content else None
        }
    }

    requests.append(request_data)
    temp_file.write("hi\n")

    save_requests_to_file()


def save_requests_to_file():
    """
    Sauvegarde les requêtes dans un fichier JSON
    """
    with open('captured_requests.json', 'w') as file:
        json.dump(requests, file, indent=4)

def get_requests():
    """
    Retourne toutes les requêtes capturées à partir du fichier JSON.
    """
    try:
        with open('captured_requests.json', 'r') as file:
            requests = json.load(file)
        return requests
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []