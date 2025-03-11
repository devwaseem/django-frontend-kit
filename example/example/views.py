from django.http import HttpRequest, HttpResponse
from django.views import View
from frontend.pages.home import HomePage, HomePageProps


class HomeView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return HomePage(props=HomePageProps()).as_response(request=request)
