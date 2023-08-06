from elefantolib import context
from elefantolib.provider import django_provider


class DjangoPlatformContextMiddleware:

    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request, *args, **kwargs):
        pvr = django_provider.DjangoProvider(request=request)
        request.pfm = context.PlatformContext(pvr=pvr)
        request.pfm.validate()
        response = self._get_response(request)

        return response


class DjangoAsyncPlatformContextMiddleware:

    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request, *args, **kwargs):
        pvr = django_provider.DjangoProvider(request=request)
        request.aiopfm = context.AsyncPlatformContext(pvr=pvr)
        request.aiopfm.validate()
        response = self._get_response(request)

        return response
