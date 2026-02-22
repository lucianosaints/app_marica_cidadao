from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RelatoZeladoriaViewSet

router = DefaultRouter()
# Cria as rotas: GET /api/relatos/ e POST /api/relatos/
router.register(r'relatos', RelatoZeladoriaViewSet, basename='relato')

urlpatterns = [
    path('api/', include(router.urls)),
]