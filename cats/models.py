from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Achievement(models.Model):
    """
    Модель для хранения достижений.
    Каждый объект представляет отдельное достижение с уникальным именем.
    """
    name = models.CharField(max_length=64, verbose_name="Название достижения")

    def __str__(self):
        """
        Возвращает строковое представление объекта.
        """
        return self.name


class Breed(models.Model):
    """
    Модель для хранения информации о породах кошек.
    Каждая порода имеет уникальное имя.
    """
    name = models.CharField(max_length=100, verbose_name="Название породы")

    def __str__(self):
        """
        Возвращает строковое представление объекта.
        """
        return self.name


class Cat(models.Model):
    """
    Модель для хранения информации о котах.
    Каждый кот связан с пользователем (владелец) и породой.
    """
    name = models.CharField(max_length=16, verbose_name="Имя кота")
    color = models.CharField(max_length=16, verbose_name="Цвет кота")
    age = models.IntegerField(
        verbose_name="Возраст кота",
        validators=[MinValueValidator(0)],
        help_text="Возраст кота в месяцах")
    owner = models.ForeignKey(
        User, related_name='cats',
        on_delete=models.CASCADE,
        verbose_name="Владелец кота"
        )
    achievements = models.ManyToManyField(
        Achievement, through='AchievementCat',
        verbose_name="Достижения кота", blank=True)
    description = models.TextField(verbose_name="Описание кота")
    breed = models.ForeignKey(
        Breed, on_delete=models.CASCADE, related_name='kittens',
        verbose_name="Порода кота")
    image = models.ImageField(
        upload_to='cats/images/',
        null=True,
        default=None,
        verbose_name="Фото кота"
        )

    def __str__(self):
        return self.name


class AchievementCat(models.Model):
    """
    Промежуточная модель, связывающая кота и его достижения.
    Каждая запись связывает одно достижение с одним котом.
    """
    achievement = models.ForeignKey(
        Achievement, on_delete=models.CASCADE, verbose_name="Достижение")
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, verbose_name="Кот")

    def __str__(self):
        return f'{self.achievement} {self.cat}'


class Rating(models.Model):
    """
    Модель для хранения оценок котов пользователями.
    Каждый пользователь может поставить оценку коту от 1 до 5.
    """
    kitten = models.ForeignKey(
        Cat,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name="Кот")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name="Пользователь")
    score = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка", help_text="Оценка от 1 до 5"
        )
