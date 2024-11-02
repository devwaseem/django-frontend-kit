from django.views import View
from frontend.pages.home import HomePage, HomePageProps


class HomeView(View):
    def get(self, request):
        return HomePage(props=HomePageProps()).as_response()
