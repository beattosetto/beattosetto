"""beattosetto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from beattosetto.settings import DEBUG

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('beatmap_collections.urls')),
    path('', include('users.urls')),
    path('', include('actions.urls'))
]

if DEBUG:
    def create_error_template_view(error_code):
        """
        Create a function that return view for an error code.

        This is for debugging purpose. Django will add templates automatically
        on production.
        """
        def error_template_view(request):
            """View for viewing error template on debug."""
            return render(request, f"{error_code}.html")
        return error_template_view
    for err in [400, 403, 404, 500]:
        urlpatterns.append(path(f"{err}/", create_error_template_view(err)))
