from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination

from .models import Achievement, Cat, User, Breed, Rating
from .serializers import (
    AchievementSerializer, CatSerializer,
    UserSerializer, BreedSerializer, RatingSerializer
)


class BreedViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления породами котов (Breed).
    Доступен для чтения всем пользователям, создание
    и редактирование - только аутентифицированным.
    """
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CatViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления котами (Cat).
    Поддерживает создание, обновление, удаление котов с
    проверкой на владельца.
    """
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """
        Возвращает список котов. Если передан параметр `breed`,
        возвращаются коты указанной породы.
        """
        breed_id = self.request.query_params.get('breed')
        if breed_id:
            return Cat.objects.filter(breed_id=breed_id)
        return Cat.objects.all()

    def perform_create(self, serializer):
        """
        Устанавливает текущего пользователя как владельца кота при создании.
        """
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        Обновляет информацию о коте, если текущий пользователь является
        владельцем кота.
        """
        if serializer.instance.owner == self.request.user:
            serializer.save()

    def perform_destroy(self, instance):
        """
        Удаляет кота, если текущий пользователь является его владельцем.
        """
        if instance.owner == self.request.user:
            instance.delete()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для отображения информации о пользователях (User).
    Предоставляет только возможность чтения.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления достижениями котов (Achievement).
    Полная функциональность CRUD.
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    pagination_class = None


class RatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления оценками котов (Rating).
    Доступен для чтения всем пользователям, создание и
    редактирование - только аутентифицированным.
    """
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
