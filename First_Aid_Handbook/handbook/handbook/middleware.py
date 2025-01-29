import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            try:
                # Попытка декодировать как UTF-8
                request_body = request.body.decode('utf-8')
            except UnicodeDecodeError:
                # Если декодирование не удалось, выводим сырые байты
                request_body = repr(request.body)

            logger.error(f"Request body: {request_body}")
            logger.error(f"Request headers: {request.headers}")

        response = self.get_response(request)

        if response.status_code >= 400:  # Логируем только ошибки
            logger.error(f"Response status: {response.status_code}")
            try:
                response_content = response.content.decode('utf-8')
            except UnicodeDecodeError:
                response_content = repr(response.content)
            logger.error(f"Response content: {response_content}")

        return response