"""
Tests for the milestones helpers library, which is the integration point for the edx_milestones API
"""

from django.test import TestCase
from mock import patch
from util import milestones_helpers
from xmodule.modulestore.tests.factories import CourseFactory


class MilestonesHelpersTestCase(TestCase):

    def setUp(self):
        """
        Test case scaffolding
        """
        self.course = CourseFactory.create(
            metadata={
                'entrance_exam_enabled': True,
            }
        )

        self.user = {'id': '123'}

        self.milestone = {
            'name': 'Test Milestone',
            'namespace': 'doesnt.matter',
            'description': 'Testing Milestones Helpers Library',
        }

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_add_milestone_returns_none_when_app_disabled(self):
        response = milestones_helpers.add_milestone(milestone=self.milestone)
        self.assertNone(response)

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_get_milestones_returns_none_when_app_disabled(self):
        response = milestones_helpers.get_milestones(namespace="whatever")
        self.assertNone(response)

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_get_milestone_relationship_types_returns_none_when_app_disabled(self):
        response = milestones_helpers.get_milestone_relationship_types()
        self.assertNone(response)

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_add_course_milestone_returns_none_when_app_disabled(self):
        response = milestones_helpers.add_course_milestone(unicode(self.course.id), 'requires', self.milestone)
        self.assertNone(response)

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_get_course_milestones_returns_none_when_app_disabled(self):
        response = milestones_helpers.get_course_milestones(unicode(self.course.id))
        self.assertNone(response)

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_add_course_content_milestone_returns_none_when_app_disabled(self):
        response = milestones_helpers.add_course_content_milestone(
            unicode(self.course.id),
            'i4x://any/content/id',
            'requires',
            self.milestone
        )
        self.assertNone(response)

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_get_course_content_milestones_returns_none_when_app_disabled(self):
        response = milestones_helpers.get_course_content_milestones(
            unicode(self.course.id),
            'i4x://doesnt/matter/for/this/test',
            'requires'
        )
        self.assertNone(response)

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_remove_content_references_returns_none_when_app_disabled(self):
        response = milestones_helpers.remove_content_references("i4x://any/content/id/will/do")
        self.assertNone(response)

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_get_namespace_choices_returns_values_when_app_disabled(self):
        response = milestones_helpers.get_namespace_choices()
        self.assertIn('ENTRANCE_EXAM', response)

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_get_course_milestones_fulfillment_paths_returns_none_when_app_disabled(self):
        response = milestones_helpers.get_course_milestones_fulfillment_paths(unicode(self.course.id), self.user)
        self.assertNone(response)

    @patch.dict('django.conf.settings.FEATURES', {'MILESTONES_APP': False})
    def test_add_user_milestone_returns_none_when_app_disabled(self):
        response = milestones_helpers.add_user_milestone(self.user, self.milestone)
        self.assertNone(response)
