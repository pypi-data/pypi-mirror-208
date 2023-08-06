"""
Tweaks the platform settings to enable support for section_to_course.
"""


def plugin_settings(settings):
    """Add django_object_actions to the installed apps so that its templates are loaded."""
    settings.INSTALLED_APPS += (
        'django_object_actions',
    )
