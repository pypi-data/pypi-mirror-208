# coding=utf-8
from BTrees.Length import Length
from collective.dms.basecontent import _
from plone.app.contenttypes.interfaces import IFile
from plone.autoform import directives as form
from plone.dexterity.content import Item
from plone.dexterity.schema import DexteritySchemaPolicy
from plone.directives.form import default_value
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from Products.CMFPlone.utils import base_hasattr
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements


class IDmsFile(model.Schema, IFile):
    """Schema for DmsFile"""
    title = schema.TextLine(
        title=_(u'Version number'),
        required=False
    )
    form.mode(title='hidden')

    model.primary('file')
    file = NamedBlobFile(
        title=_(u"File"),
        required=True,
    )

    label = schema.TextLine(
        title=_(u'Label'),
        required=False,
    )


class DmsFile(Item):
    """DmsFile"""
    implements(IDmsFile)
    __ac_local_roles_block__ = True

    incomingmail = False

    def Title(self):
        if self.incomingmail:
            return _(u"Incoming mail")
        elif base_hasattr(self, 'signed') and self.signed:
            return _(u"Signed version")
        else:
            return self.title


class DmsFileSchemaPolicy(DexteritySchemaPolicy):
    """Schema Policy for DmsFile"""

    def bases(self, schemaName, tree):
        return (IDmsFile, )


class IDmsAppendixFile(model.Schema, IFile):
    """Schema for DmsAppendixFile"""
    model.primary('file')
    file = NamedBlobFile(
        title=_(u"File"),
        required=True,
    )


class DmsAppendixFile(Item):
    """DmsAppendixFile"""
    implements(IDmsAppendixFile)
    __ac_local_roles_block__ = True


class DmsAppendixFileSchemaPolicy(DexteritySchemaPolicy):
    """Schema Policy for DmsAppendixFile"""

    def bases(self, schemaName, tree):
        return (IDmsAppendixFile, )


@default_value(field=IDmsFile['title'])
def titleDefaultValue(data):
    container = data.context
    annotations = IAnnotations(container)
    if 'higher_version' not in annotations:
        version_number = 1
    else:
        version_number = annotations['higher_version'].value + 1
    return unicode(version_number)


def update_higher_version(context, event):
    """Stores the higher version number in a file parent annotation.

    data transfer: ✅"""
    container = context.getParentNode()
    annotations = IAnnotations(container)
    if 'higher_version' not in annotations:
        annotations['higher_version'] = Length()
    annotations['higher_version'].change(1)
