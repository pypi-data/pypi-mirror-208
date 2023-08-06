"""
URLs for the section_to_course app.
"""

from django.urls import path

from . import views

app_name = 'section_to_course'
urlpatterns = [
    path('autocomplete/course/', views.CourseAutocomplete.as_view(), name='course_autocomplete'),
    path(
        'autocomplete/course/<str:course_id>/sections/',
        views.SectionAutocomplete.as_view(),
        name='section_autocomplete',
    )
]
