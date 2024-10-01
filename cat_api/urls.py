from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView)
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from cats.views import (
    AchievementViewSet, CatViewSet, UserViewSet, BreedViewSet, RatingViewSet)

# Настройка схемы для Swagger-документации
schema_view = get_schema_view(
   openapi.Info(
      title="Kitten API",
      default_version='v1',
      description="API для онлайн выставки котят",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'cats', CatViewSet)
router.register(r'breeds', BreedViewSet)
router.register(r'users', UserViewSet)
router.register(r'achievements', AchievementViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path(
        'api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(
        'api/token/refresh/', TokenRefreshView.as_view(), name='tkn_refresh'),
    path('swagger/', schema_view.with_ui(
        'swagger', cache_timeout=0), name='schema-swagger-ui'),
]
