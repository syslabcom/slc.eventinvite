import unittest2 as unittest

from plone.testing import z2
from plone.app.testing import SITE_OWNER_NAME

from slc.eventinvite import utils
from slc.eventinvite.testing import TestMixin
from slc.eventinvite.adapter import IAttendeesStorage
from slc.eventinvite.testing import \
    SLC_EVENTINVITE_INTEGRATION_TESTING

class TestContent(unittest.TestCase, TestMixin):
    layer = SLC_EVENTINVITE_INTEGRATION_TESTING

    def _create_event(self):
        portal = self.layer['portal']
        id = portal.invokeFactory(
                            'Event', 
                            'plone-conference',
                            title='Plone Conference')
        return  portal['plone-conference']

    def test_save_attendees(self):
        """ """
        portal = self.layer['portal']
        app = self.layer['app']
        z2.login(app['acl_users'], SITE_OWNER_NAME)
        self.register_users()
        event = self._create_event()
        storage = IAttendeesStorage(event)
        self.assertFalse(hasattr(storage, 'internal_attendees'))
        self.assertFalse(hasattr(storage, 'external_attendees'))
        self.assertFalse(hasattr(storage, 'groups'))

        data = {
            'internal_attendees': ['max-musterman', 'john-doe','Administrators'],
            'external_attendees': [{'name':'John Smith', 
                                    'email':'john@mail.com',}],
        }
        utils.save_attendees(event, data)

        self.assertTrue(hasattr(storage, 'internal_attendees'))
        self.assertTrue(hasattr(storage, 'external_attendees'))
        self.assertTrue(hasattr(storage, 'groups'))

        self.assertEqual(storage.internal_attendees, [
            {'id': 'max-musterman', 'name': 'Max Musterman', 'email': 'max@mail.com'}, 
            {'id': 'john-doe', 'name': 'John Doe', 'email': 'john@mail.com'}])

        self.assertEqual(storage.external_attendees, [
            {'name': 'John Smith', 'email': 'john@mail.com'}])

        self.assertEqual(storage.groups, [
            {'name': 'Administrators', 'confirmation':[]}])

    def test_get_new_attendees(self):
        """ """
        portal = self.layer['portal']
        app = self.layer['app']
        z2.login(app['acl_users'], SITE_OWNER_NAME)
        self.register_users()
        event = self._create_event()
        data = {
            'external_attendees': [
                    {'email': 'maxine@mail.com', 'name': 'Maxine Mustermann'},
                    {'email': 'jane@mail.com', 'name': 'Jane Doe'}
                ],
            'internal_attendees': [
                    'Administrators',
                    'Reviewers',
                    'Site Administrators',
                    'andreas-ebersbacher',
                    'jan-keller',
                    'werner-wechsler'
                ]
            }
        new_attendees = utils.get_new_attendees(event, data)
        control_new_attendees = {
            'internal_attendees': [
                { 'name': 'Andreas Ebersbacher', 'email': 'andreas@mail.com' }, 
                { 'name': 'Jan Keller', 'email': 'jan@mail.com' },
                { 'name': 'Werner Wechsler', 'email': 'werner@mail.com' }
            ], 
            'groups': [
                {'name': 'Administrators'}, 
                {'name': 'Reviewers'}, 
                {'name': 'Site Administrators'}
            ], 
            'external_attendees': [
                {'email': 'maxine@mail.com', 'name': 'Maxine Mustermann'}, 
                {'email': 'jane@mail.com', 'name': 'Jane Doe'}
            ]
        }
        self.assertEqual(new_attendees, control_new_attendees)
        utils.save_attendees(event, data)

        new_attendees = utils.get_new_attendees(event, data)
        self.assertEqual(new_attendees,
                { 'internal_attendees': [], 
                  'groups': [], 
                  'external_attendees': []})





