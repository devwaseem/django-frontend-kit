from django.http import HttpRequest, HttpResponse
from django.views import View
from frontend.pages.home import HomePage


class HomeView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return HomePage(name="User").as_response(request=request)
