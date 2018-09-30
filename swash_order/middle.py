from django.http import Http404
from django.utils.deprecation import MiddlewareMixin


class FilterIPMiddleware(MiddlewareMixin):

    def process_request(self, request):
        allowed_ips = ['192.168.1.1', '123.123.123.123', '127.0.0.1']
        ip = request.META.get('REMOTE_ADDR')
        if ip not in allowed_ips:
            raise Http404

        return None
