from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template


class Response:
    def __init__(self, request):
        self.request = request
        self.template_name = None
        self.context = None
        self.frame = None

    def from_template(self, template_name, context=None, frame=None):
        self.template_name = template_name
        self.context = context or {}
        self.frame = frame
        return self

    def to_200(self):
        data = get_template(self.template_name, using='samon').render(context=self.context, request=self.request, frame=self.frame)
        resp = HttpResponse(data)
        return resp

    def to_201(self):
        data = get_template(self.template_name, using='samon').render(context=self.context, request=self.request, frame=self.frame, to='js_template')
        resp = HttpResponse('html`' + data + '`')
        resp.status_code = 201
        return resp

    def to_403(self):
        data = get_template(self.template_name, using='samon').render(context=self.context, request=self.request, frame=self.frame, to='js_template')
        resp = HttpResponse('html`' + data + '`')
        resp.status_code = 403
        return resp

    def to_340(self, redirect_to):
        resp = HttpResponseRedirect(redirect_to=redirect_to)
        resp.status_code = 340
        return resp

    def to_ajax_redirect(self, redirect_to):
        self.to_340(redirect_to)


def response(request):
    return Response(request)
