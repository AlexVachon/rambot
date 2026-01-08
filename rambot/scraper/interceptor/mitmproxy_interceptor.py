import json
import os

from mitmproxy import ctx, http


class MITMProxyInterceptor:
    def __init__(self):
        self.requests_path = None

    def load(self, loader):
        self.requests_path = getattr(ctx.options, "requests_path", None) or os.getenv("REQUESTS_PATH")
        ctx.log.info(f"[Interceptor] requests_path = {self.requests_path}")

    def response(self, flow: http.HTTPFlow):
        if not self.requests_path or not flow.response:
            return

        flow.response.decode()

        content_type = flow.response.headers.get("Content-Type", "").lower()
        is_text = any(t in content_type for t in ["text", "json", "xml", "javascript"])

        if is_text:
            resp_body = flow.response.get_text(strict=False)
        else:
            resp_body = f"<Binary Data: {content_type}>"

        entry = {
            "request": {
                "method": flow.request.method,
                "url": flow.request.url,
                "headers": dict(flow.request.headers),
                "body": flow.request.get_text(strict=False)
            },
            "response": {
                "url": flow.request.url,
                "status_code": flow.response.status_code,
                "headers": dict(flow.response.headers),
                "body": resp_body
            }
        }

        try:
            with open(self.requests_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            ctx.log.warn(f"[Interceptor] Failed to log request/response: {e}")

addons = [MITMProxyInterceptor()]