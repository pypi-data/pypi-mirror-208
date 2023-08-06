// Tools for setting up the section_to_course admin fields.
"use strict";

{
  // The following section is copied and modified from upstream's admin/js/autocomplete.js.
  // Unfortunately we have to duplicate things a bit because we can't edit the existing code
  // and be sure we won't break things elsewhere in the admin for autocompleted fields.
  const $ = django.jQuery;
  const init = function($element, options) {
    const settings = $.extend({
      ajax: {
        url: function() {
          return $element.data('endpoint')
        },
        data: function(params) {
          return {
            term: params.term,
          };
        }
      }
    }, options);
    $element.select2(settings);
  };

  $.fn.courseSelect = function(options) {
    const settings = $.extend({}, options);
    $.each(this, function(i, element) {
      const $element = $(element);
      init($element, settings);
    });
    return this;
  };

  $(function() {
    // Initialize all autocomplete widgets except the one in the template
    // form used when a new formset is added.
    $('.course-section-autocomplete').not('[name*=__prefix__]').courseSelect();
  });

  $(document).on('formset:added', (function() {
    return function(event, $newFormset) {
      return $newFormset.find('.course-section-autocomplete').courseSelect();
    };
  })(this));

  $.fn.djangoAdminSelect2 = function(options) {
    const settings = $.extend({}, options);
    $.each(this, function(i, element) {
      const $element = $(element);
      init($element, settings);
    });
    return this;
  };

  // example matching string: course-v1:edX+DemoX+Demo_Course
  const courseRe = /[^:]+:[^+]+[+][^+]+[+][^+]+/

  // Find all the course section fields, and then augment them to find the course fields they belong to
  // so that we can dynamically enable/disable them and update their endpoint URLs.
  $(() => {
    $('.course-section-autocomplete').each((index, sectionSelect) => {

      let courseKey = '%3Ccourse_id%3E'
      const urlTemplate = sectionSelect.attributes['data-url-template'].value

      $(`#${sectionSelect.attributes['data-course-field'].value}`).on('change', (event) => {
        courseKey = event.target.value
        sectionSelect.value = ''
        if (courseRe.test(courseKey)) {
          sectionSelect.setAttribute('data-endpoint', urlTemplate.replace(/%3Ccourse_id%3E/, courseKey))
          sectionSelect.disabled = false
          return
        }
        sectionSelect.disabled = true
      })
    })
  })
}
