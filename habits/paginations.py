from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Кастомная пагинация для API.

    Attributes:
        page_size (int): Количество элементов на странице по умолчанию
        page_size_query_param (str): Параметр запроса для изменения размера страницы
        max_page_size (int): Максимально допустимый размер страницы
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10
