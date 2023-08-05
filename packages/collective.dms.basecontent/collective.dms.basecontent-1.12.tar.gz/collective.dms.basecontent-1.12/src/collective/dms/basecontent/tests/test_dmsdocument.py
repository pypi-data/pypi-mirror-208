# -*- coding: utf8 -*-

from collective.dms.basecontent.source import RecipientGroupsVocabulary
from collective.dms.basecontent.source import TreatingGroupsVocabulary
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from ecreall.helpers.testing.base import BaseTest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest

from plone.dexterity.utils import createContentInContainer


class TestDmsdocument(unittest.TestCase, BaseTest):
    """Tests adapters"""

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestDmsdocument, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.doc = createContentInContainer(self.portal, 'dmsdocument', **{'title': 'Doc 1'})

    def test_RecipientGroupsVocabulary(self):
        voc_inst = RecipientGroupsVocabulary()
        voc_ids = [i.token for i in voc_inst(self.portal).__iter__()]
        self.assertEqual(set(voc_ids), set(['Administrators', 'Reviewers', 'Site Administrators']))
        voc_ids = [i.token for i in voc_inst(self.portal).search('user')]
        self.assertEqual(set(voc_ids), set(['test_user_1_', 'AuthenticatedUsers']))

    def test_TreatingGroupsVocabulary(self):
        voc_inst = TreatingGroupsVocabulary()
        voc_ids = [i.token for i in voc_inst(self.portal).__iter__()]
        self.assertEqual(set(voc_ids), set(['Administrators', 'Reviewers', 'Site Administrators']))
        voc_ids = [i.token for i in voc_inst(self.portal).search('user')]
        self.assertEqual(set(voc_ids), set(['test_user_1_', 'AuthenticatedUsers']))

    def test_getmainfiles(self):
        self.assertListEqual(self.doc.get_mainfiles(), [])
        file1 = createContentInContainer(self.doc, 'dmsmainfile', **{'title': 'MF 1'})
        createContentInContainer(self.doc, 'dmsappendixfile', **{'title': 'AF 1'})
        self.assertListEqual(self.doc.get_mainfiles(), [file1])
        file2 = createContentInContainer(self.doc, 'dmsmainfile', **{'title': 'MF 2'})
        self.assertListEqual(self.doc.get_mainfiles(), [file1, file2])
        self.doc.moveObjectsByDelta([file2.id], -2)
        self.assertListEqual(self.doc.get_mainfiles(), [file2, file1])
