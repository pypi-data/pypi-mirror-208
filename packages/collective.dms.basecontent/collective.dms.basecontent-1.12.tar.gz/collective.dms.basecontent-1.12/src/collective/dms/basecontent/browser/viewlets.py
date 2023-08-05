from five import grok

from plone.app.layout.viewlets.interfaces import IHtmlHeadLinks

from collective.dms.basecontent.dmsdocument import IDmsDocument
from collective.dms.basecontent import _
from collective.dms.basecontent.browser.listing import (VersionsTable,
                                                        DmsAppendixTable)
from collective.dms.basecontent.browser.table import TableViewlet

from zope.interface import Interface



grok.templatedir('templates')
grok.context(IDmsDocument)


class DmsAboveContentViewletManager(grok.ViewletManager):
    grok.name('dms.abovecontent')


class DmsBelowContentViewletManager(grok.ViewletManager):
    grok.name('dms.belowcontent')


class BaseViewlet(TableViewlet):
    grok.baseclass()
    grok.viewletmanager(DmsBelowContentViewletManager)
    __table__ = VersionsTable

    def contentFilter(self):
        return {'portal_type': self.portal_type,
                }


class VersionsViewlet(BaseViewlet):
    grok.name('dms.files')
    grok.template('versionsviewlet')
    grok.viewletmanager(DmsAboveContentViewletManager)
    grok.order(10)
    portal_type = 'dmsmainfile'
    label = _(u"Versions")
    noresult_message = _(u"There is no version note for this document.")

    def contentFilter(self):
        return {'portal_type': self.portal_type,
                'sort_on': 'getObjPositionInParent',
                'sort_order': 'descending'}


class AppendixViewlet(BaseViewlet):
    grok.name('dms.appendix')
    grok.order(20)
    portal_type = 'dmsappendixfile'
    label = _(u"Appendix")
    noresult_message = _(u"There is no appendix for this document.")
    __table__ = DmsAppendixTable

    def contentFilter(self):
        return {'portal_type': self.portal_type,
                'sort_on': 'getObjPositionInParent',
                'sort_order': 'ascending'}


class ChangeTitleViewlet(grok.Viewlet):
    grok.name('dms.changetitle')
    grok.context(Interface)
    grok.viewletmanager(IHtmlHeadLinks)
    grok.require('zope2.View')

    def render(self):
        return u"""
<script type="text/javascript">
    (function ($) {
        $(document).ready(function () {
            $("body.template-dmsincomingmail label[for='form-widgets-IDublinCore-title']").text('Objet');
            $("body.template-dmsoutgoingmail label[for='form-widgets-IDublinCore-title']").text('Objet');
            $("body.template-edit.portaltype-dmsincomingmail label[for='form-widgets-IDublinCore-title']").text('Objet');
            $("body.template-edit.portaltype-dmsoutgoingmail label[for='form-widgets-IDublinCore-title']").text('Objet');
        });
    })(jQuery);
</script>"""
