#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_zfiles.zmi.workflow module

This module defines ZFiles workflow management views.
"""

from pyams_form.ajax import ajax_form_config
from pyams_form.interfaces.form import IAJAXFormRenderer
from pyams_layer.interfaces import IPyAMSLayer
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.registry import get_utility
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url
from pyams_workflow.interfaces import IWorkflowState, IWorkflowVersion, IWorkflowVersions
from pyams_workflow.zmi.transition import WorkflowContentTransitionForm
from pyams_zfiles.interfaces import IDocument, IDocumentContainer, IDocumentFolder, IDocumentVersion, \
    MANAGE_DOCUMENT_PERMISSION, STATE
from pyams_zmi.interfaces import IAdminLayer


__docformat__ = 'restructuredtext'

from pyams_zfiles import _


class BaseWorkflowForm(WorkflowContentTransitionForm):
    """Base workflow form"""

    @property
    def title(self):
        """Title getter"""
        return super(WorkflowContentTransitionForm, self).title


@ajax_form_config(name='wf-publish.html',  # pylint: disable=abstract-method
                  context=IDocumentVersion, layer=IPyAMSLayer,
                  permission=MANAGE_DOCUMENT_PERMISSION)
class DocumentVersionPublishForm(BaseWorkflowForm):
    """Document version publish form"""


@ajax_form_config(name='wf-archive.html',  # pylint: disable=abstract-method
                  context=IDocumentVersion, layer=IPyAMSLayer,
                  permission=MANAGE_DOCUMENT_PERMISSION)
class DocumentVersionArchiveForm(BaseWorkflowForm):
    """Document version archive form"""


@ajax_form_config(name='wf-clone.html',  # pylint: disable=abstract-method
                  context=IDocumentVersion, layer=IPyAMSLayer,
                  permission=MANAGE_DOCUMENT_PERMISSION)
class DocumentVersionCloneForm(BaseWorkflowForm):
    """Document version clone form"""


@ajax_form_config(name='wf-delete.html',  # pylint: disable=abstract-method
                  context=IDocumentVersion, layer=IPyAMSLayer,
                  permission=MANAGE_DOCUMENT_PERMISSION)
class DocumentVersionDeleteForm(BaseWorkflowForm):
    """Document version delete form"""

    def update_actions(self):
        super().update_actions()
        action = self.actions.get('add')
        if action is not None:
            state = IWorkflowState(self.context)
            if state.version_id == 1:  # remove the first and only version => remove all
                action.add_class('btn-danger')
                action.title = _("Delete definitively")

    def create_and_add(self, data):
        data = data.get(self, data)
        state = IWorkflowState(self.context)
        if state.version_id == 1:  # remove the first and only version => remove all
            document = get_parent(self.context, IDocument)
            target = get_parent(document, IDocumentFolder)
            del target[document.__name__]
        else:
            versions = IWorkflowVersions(self.context)
            versions.remove_version(state.version_id,
                                    state=STATE.DELETED.value,
                                    comment=data.get('comment'))
            target = versions.get_last_versions(count=1)[0]
        return target

    @property
    def deleted_target(self):
        """Redirect target when current content is deleted"""
        return get_utility(IDocumentContainer)


@adapter_config(required=(IWorkflowVersion, IAdminLayer, DocumentVersionDeleteForm),
                provides=IAJAXFormRenderer)
class DocumentVersionDeleteFormRenderer(ContextRequestViewAdapter):
    """Document version delete form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if changes is None:
            return None
        return {
            'status': 'redirect',
            'location': absolute_url(self.view.deleted_target, self.request, 'admin')
        }
