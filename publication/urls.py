from django.urls import path

from .views import (get_publications_page, get_publication_page_by_slug, get_search_result_page_by_publication,
                    get_page_for_add_new_publication, delete_publication, get_page_for_edit_publication)

urlpatterns = [
    path("", get_publications_page, name="publications"),
    path("publication/<str:slug>/", get_publication_page_by_slug, name="publication_by_slug"),
    path("search/", get_search_result_page_by_publication, name="publication_search_result"),
    path('add_publication/', get_page_for_add_new_publication, name='add_publication'),
    path('delete_publication/', delete_publication, name='delete_publication'),
    path('edit_publication/<str:publication_slug>/', get_page_for_edit_publication, name='edit_publication'),
]
