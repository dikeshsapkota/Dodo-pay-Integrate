from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse({"ok": True, "service": "dodo-payments-demo"})


urlpatterns = [
    path("", health_check),
    path("admin/", admin.site.urls),
    path("api/", include("payments.urls")),
]
