"""
Helper API endpoints for the section to course application.
"""

from django.utils.translation import gettext as _
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from ..compat import course_exists, get_course_outline, modulestore
from ..models import SectionToCourseLink


class CourseAutocomplete(APIView):
    """
    Autocomplete API endpoint for courses.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        Get all courses and match a search term against them.
        """
        self.check_permissions(request)
        section_courses = set(SectionToCourseLink.objects.values_list('destination_course_id', flat=True))
        all_courses = [
            {'id': str(course.id), 'text': f'{course.display_name} ({course.id})'}
            for course in modulestore().get_courses()
            if course.id not in section_courses
        ]
        term = request.GET.get('term', '').lower()
        courses = [
            entry for entry in all_courses
            if entry['id'].lower().startswith(term) or entry['text'].lower().startswith(term)
        ]
        return Response(data={'results': courses}, status=status.HTTP_200_OK)


class SectionAutocomplete(APIView):
    """
    Autocomplete API endpoint for course sections.
    """

    permission_classes = [IsAdminUser]

    def get(self, request, course_id):
        """
        Get a listing of all sections in a course, matching a search term against them.
        """
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            return Response(
                data={'details': _("{course_key} is not a valid course key.").format(course_key=course_id)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        term = request.GET.get('term', '').lower()
        if not course_exists(course_key):
            return Response(
                data={'details': _("Course {course_key} does not exist.").format(course_key=course_key)},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Don't allow this section to be created into more than one mini-course.
        existing_keys = set(
            SectionToCourseLink.objects.filter(
                source_course_id=course_key,
            ).values_list('source_section_id', flat=True)
        )
        sections = [
            {'text': child.title, 'id': str(child.usage_key)} for child in get_course_outline(course_key).sections
            if child.usage_key not in existing_keys
            and (child.title.lower().startswith(term) or str(child.usage_key).lower().startswith(term))
        ]
        return Response(data={'results': sections}, status=status.HTTP_200_OK)
