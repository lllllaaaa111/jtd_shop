import logging


class ProductsDebugMiddleware:
    """Log request details for paths starting with /products/.

    Logs method, path, selected headers, query params, and a short body preview.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("request_debug")

    def __call__(self, request):
        try:
            path = request.path or ""
            if path.startswith("/products/"):
                headers = {
                    "Host": request.META.get("HTTP_HOST", ""),
                    "Origin": request.META.get("HTTP_ORIGIN", ""),
                    "Referer": request.META.get("HTTP_REFERER", ""),
                    "User-Agent": request.META.get("HTTP_USER_AGENT", ""),
                    "Content-Type": request.META.get("CONTENT_TYPE", ""),
                    "Content-Length": request.META.get("CONTENT_LENGTH", ""),
                    "Authorization": request.META.get("HTTP_AUTHORIZATION", ""),
                    "Cookie": request.META.get("HTTP_COOKIE", ""),
                    "X-Forwarded-For": request.META.get("HTTP_X_FORWARDED_FOR", ""),
                }

                # Safe body preview (won't consume stream in Django)
                try:
                    raw_body = request.body or b""
                except Exception:
                    raw_body = b""
                max_preview = 1024
                body_preview = raw_body[:max_preview]
                if raw_body and len(raw_body) > max_preview:
                    body_note = f" (truncated {len(raw_body) - max_preview} bytes)"
                else:
                    body_note = ""

                self.logger.debug(
                    "products debug | %s %s | headers=%s | GET=%s | body=%s%s",
                    request.method,
                    path,
                    headers,
                    dict(request.GET.lists()),
                    body_preview.decode(errors="replace"),
                    body_note,
                )
        except Exception as exc:
            # Never break requests due to logging
            logging.getLogger("request_debug").warning("debug middleware error: %s", exc)

        response = self.get_response(request)
        return response



