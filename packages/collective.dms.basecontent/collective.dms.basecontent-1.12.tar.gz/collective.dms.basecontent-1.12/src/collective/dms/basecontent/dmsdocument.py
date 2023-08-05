from collective.dms.basecontent import _
from collective.dms.basecontent.relateddocs import RelatedDocs
from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget
from dexterity.localrolesfield.field import LocalRolesField
from imio.helpers.content import object_values
from plone.autoform import directives as form
from plone.dexterity.content import Container
from plone.dexterity.schema import DexteritySchemaPolicy
from plone.supermodel import model
from zope import schema
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty


class IDmsDocument(model.Schema):
    """Schema for DmsDocument"""

    notes = schema.Text(
        title=_(u"Notes"),
        required=False,
    )

    treating_groups = LocalRolesField(
        title=_(u"Treating groups"),
        required=False,
        value_type=schema.Choice(vocabulary=u'collective.dms.basecontent.treating_groups',)
    )
    # form.widget(treating_groups=MultiSelect2FieldWidget)

    recipient_groups = LocalRolesField(
        title=_(u"Recipient groups"),
        required=False,
        value_type=schema.Choice(vocabulary=u'collective.dms.basecontent.recipient_groups')
    )
    form.widget(recipient_groups=MultiSelect2FieldWidget)

    related_docs = RelatedDocs(
        title=_(u"Related documents"),
        required=False,
        display_backrefs=True,
    )


class DmsDocument(Container):
    """DmsDocument"""
    implements(IDmsDocument)
    # disable local roles inheritance
    __ac_local_roles_block__ = True

    def get_mainfiles(self):
        return object_values(self, ['DmsFile'])


class DmsDocumentSchemaPolicy(DexteritySchemaPolicy):
    """DmsDocument schema policy"""

    def bases(self, schemaName, tree):
        return (IDmsDocument, )
