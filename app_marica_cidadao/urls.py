from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RelatoZeladoriaViewSet, RegisterUserView, CategoriaProblemaViewSet

router = DefaultRouter()
# Cria as rotas: GET /api/relatos/ e POST /api/relatos/
router.register(r'relatos', RelatoZeladoriaViewSet, basename='relato')
router.register(r'categorias', CategoriaProblemaViewSet, basename='categoria')

urlpatterns = [
    path('cadastro/', RegisterUserView.as_view(), name='registrar_usuario'),
    path('', include(router.urls)),
]