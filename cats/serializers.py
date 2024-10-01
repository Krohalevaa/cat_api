import base64
import webcolors
import datetime as dt

from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import Achievement, AchievementCat, Cat, User, Breed, Rating


class BreedSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели породы кошек (Breed).
    Описывает поля, которые будут отображены для каждой породы.
    """
    class Meta:
        model = Breed
        fields = ['id', 'name']


class RatingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели оценки (Rating).
    Преобразует данные оценок котов в JSON формат.
    """
    class Meta:
        model = Rating
        fields = ['id', 'cat', 'user', 'score']


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели пользователя (User).
    Включает в ответе связанные с пользователем коты.
    """
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'cats')
        ref_name = 'ReadOnlyUsers'


class Hex2NameColor(serializers.Field):
    """
    Кастомное поле сериализации для преобразования HEX-кода цвета в имя цвета.
    Использует библиотеку webcolors для преобразования.
    """
    def to_representation(self, value):
        """
        Возвращает представление цвета в виде строки HEX-кода.
        """
        return value

    def to_internal_value(self, data):
        """
        Преобразует входящие данные (HEX-код) в имя цвета.
        """
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class AchievementSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели достижения (Achievement).
    Преобразует данные достижений в JSON формат.
    """
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class Base64ImageField(serializers.ImageField):
    """
    Кастомное поле для сериализации изображений в формате Base64.
    Поддерживает преобразование изображений, закодированных в base64, в файлы.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CatSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели кота (Cat).
    Осуществляет преобразование данных котов в JSON формат,
    включая связанные достижения и изображения.
    """
    achievements = AchievementSerializer(required=False, many=True)
    color = Hex2NameColor()
    age = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    breed = BreedSerializer(read_only=True)

    class Meta:
        model = Cat
        fields = (
            'id', 'name', 'color', 'age', 'achievements',
            'owner', 'age', 'image', 'description', 'breed'
            )
        read_only_fields = ('owner',)

    def get_age(self, obj):
        """
        Вычисляет возраст кота на основе года его рождения.
        """
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        """
        Создает объект кота, включая его достижения, если они указаны.
        """
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat
        else:
            achievements = validated_data.pop('achievements')
            cat = Cat.objects.create(**validated_data)
            for achievement in achievements:
                current_achievement, status = (
                    Achievement.objects.get_or_create(**achievement))
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=cat
                    )
            return cat

    def update(self, instance, validated_data):
        """
        Обновляет информацию о коте, включая достижения и изображение.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.color = validated_data.get('color', instance.color)
        instance.birth_year = validated_data.get(
            'birth_year', instance.birth_year
            )
        instance.image = validated_data.get('image', instance.image)
        if 'achievements' in validated_data:
            achievements_data = validated_data.pop('achievements')
            lst = []
            for achievement in achievements_data:
                current_achievement, status = (
                    Achievement.objects.get_or_create(**achievement))
                lst.append(current_achievement)
            instance.achievements.set(lst)

        instance.save()
        return instance
