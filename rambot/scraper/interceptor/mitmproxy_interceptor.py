from mitmproxy import ctx, http
import json
import os


class MITMProxyInterceptor:
    
    def __init__(self):
        self.requests_path = None

    def load(self, loader):
        self.requests_path = getattr(ctx.options, "requests_path", None)

        if not self.requests_path:
            self.requests_path = os.getenv("REQUESTS_PATH")

        ctx.log.info(f"[Interceptor] requests_path = {self.requests_path}")

    def request(self, flow: http.HTTPFlow):
        if not self.requests_path:
            return

        entry = {
            "url": flow.request.pretty_url,
            "method": flow.request.method,
            "headers": dict(flow.request.headers),
            "timestamp": flow.request.timestamp_start,
        }

        try:
            with open(self.requests_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            ctx.log.warn(f"[Interceptor] Failed to log request: {e}")


addons = [
    MITMProxyInterceptor()
]
