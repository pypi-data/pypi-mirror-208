# -*- coding: utf-8 -*-
import logging

from plone import api

logger = logging.getLogger('collective.dms.basecontent: upgrade. ')


def v2(context):
    # install product
    setup = api.portal.get_tool('portal_setup')
    setup.runAllImportStepsFromProfile('profile-dexterity.localrolesfield:default')
    # remove old roles set
    config = {'treating_groups': 'Editor', 'recipient_groups': 'Reader'}
    catalog = api.portal.get_tool('portal_catalog')
    for brain in catalog(portal_type='dmsdocument'):
        obj = brain.getObject()
        for local_principal, local_roles in dict(obj.get_local_roles()).items():
            # a local_role is like (u'Contributor', u'Reviewer'))
            for attr, role in config.items():
                if local_principal in getattr(obj, attr) or []:
                    cleaned_local_roles = list(local_roles)
                    try:
                        cleaned_local_roles.remove(role)
                    except ValueError:
                        # if a role to remove was already removed (???) pass
                        logger.warn("Failed to remove role '%s' for principal '%s' on object '%s'"
                                    % (role, local_principal, '/'.join(obj.getPhysicalPath())))
                    # if there are still some local_roles, use manage_setLocalRoles
                    if cleaned_local_roles:
                        obj.manage_setLocalRoles(local_principal, cleaned_local_roles)
                    else:
                        # either use manage_delLocalRoles
                        obj.manage_delLocalRoles((local_principal, ))


def v3(context):
    # uninstall chosen products
    pqi = api.portal.get_tool("portal_quickinstaller")
    inst_prd = [dic['id'] for dic in pqi.listInstalledProducts() if dic['status'] == 'installed']
    for prd in ('collective.z3cform.chosen', 'collective.js.chosen'):
        if prd in inst_prd:
            pqi.uninstallProducts([prd])
    # install select2
    setup = api.portal.get_tool('portal_setup')
    setup.runAllImportStepsFromProfile('profile-collective.z3cform.select2:default',
                                       dependency_strategy='new')
