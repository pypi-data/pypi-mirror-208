class FastAPIProvider:
    def __init__(self, request):
        self.request = request

    @property
    def auth_token(self):
        return self.request.headers.get('Authorization')

    @property
    def correlation_id(self):
        return self.request.headers.get('X-Correlation-Id')

    @property
    def locale(self):
        return self.request.headers.get('Accept-Language')
