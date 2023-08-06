class DjangoProvider:

    def __init__(self, request):
        self.request = request

    @property
    def auth_token(self):
        return self.request.META.get('HTTP_AUTHORIZATION')

    @property
    def correlation_id(self):
        return self.request.META.get('HTTP_X_CORRELATION_ID')

    @property
    def locale(self):
        return self.request.META.get('HTTP_ACCEPT_LANGUAGE')
