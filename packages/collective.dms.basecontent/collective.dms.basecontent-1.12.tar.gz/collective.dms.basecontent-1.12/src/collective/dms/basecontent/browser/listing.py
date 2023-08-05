# -*- coding: utf-8 -*-
from five import grok

from zope.interface import Interface
from zope.cachedescriptors.property import CachedProperty
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory

from Products.CMFCore.utils import getToolByName

from collective.dms.basecontent import _
from collective.dms.basecontent.browser import column
from collective.dms.basecontent.browser.table import Table


grok.templatedir('templates')

PMF = MessageFactory('plone')


class BaseTable(Table):

    @CachedProperty
    def values(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        query = {'path': {'query': folder_path},
                 'sort_on': 'getObjPositionInParent',
                 'sort_order': 'ascending'}
        query.update(self.viewlet.contentFilter())
        results = portal_catalog.searchResults(query)
        return results


class VersionsTable(BaseTable):

    cssClasses = {'table': 'listing nosort dv'}


class DmsAppendixTable(VersionsTable):

    def setUpColumns(self):
        columns = super(DmsAppendixTable, self).setUpColumns()
        return [column for column in columns if column.__name__ != 'dms.state']


class BaseTitleColumn(column.TitleColumn):
    grok.name('dms.title')
    grok.adapts(Interface, Interface, BaseTable)


class VersionsTitleColumn(BaseTitleColumn):
    grok.adapts(Interface, Interface, VersionsTable)
    domain = 'collective.dms.basecontent'
    linkCSS = 'version-link'

    def getLinkContent(self, item):
        content = super(VersionsTitleColumn, self).getLinkContent(item)
        return translate(content, domain=self.domain, context=self.request)


class DownloadColumn(column.DownloadColumn):
    grok.name('dms.download')
    grok.adapts(Interface, Interface, VersionsTable)


class EditColumn(column.EditColumn):
    grok.name('dms.edit')
    grok.adapts(Interface, Interface, VersionsTable)


class ExternalEditColumn(column.ExternalEditColumn):
    grok.name('dms.extedit')
    grok.adapts(Interface, Interface, VersionsTable)


class DeleteColumn(column.DeleteColumn):
    grok.name('dms.delete')
    grok.adapts(Interface, Interface, VersionsTable)


class AuthorColumn(column.PrincipalColumn):
    grok.name('dms.author')
    grok.adapts(Interface, Interface, VersionsTable)
    header = _(u"Author")
    weight = 30
    attribute = 'Creator'
    cssClasses = {'th': 'th_header_author', 'td': 'td_cell_author'}


class UpdateColumn(column.DateColumn):
    grok.name('dms.update')
    grok.adapts(Interface, Interface, VersionsTable)
    header = PMF(u"listingheader_modified")
    attribute = 'modified'
    weight = 40
    cssClasses = {'th': 'th_header_modified', 'td': 'td_cell_modified'}


class StateColumn(column.StateColumn):
    grok.name('dms.state')
    grok.adapts(Interface, Interface, BaseTable)
    weight = 50


class VersionLabelColumn(column.LabelColumn):
    grok.name('dms.label')
    grok.adapts(Interface, Interface, VersionsTable)
    attribute = 'label'
    header = _(u"Label")
    weight = 15
