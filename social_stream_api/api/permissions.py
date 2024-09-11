from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Устанавливаем разрешение на редактирование только авторам.
    Разрешает чтение всем пользователям, а изменение только автору объекта.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь разрешение на выполнение запроса.
        Разрешает доступ, если метод запроса безопасный (например, GET, HEAD или OPTIONS)
        или если пользователь аутентифицирован.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь разрешение на выполнение запроса с объектом.
        Разрешает доступ, если метод запроса безопасный (например, GET, HEAD или OPTIONS)
        или если пользователь является автором объекта.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
