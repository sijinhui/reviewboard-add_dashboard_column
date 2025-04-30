"""add_dashboard_column for Review Board."""
from typing import Any

from django.utils.translation import gettext_lazy as _
from reviewboard.extensions.base import Extension
from reviewboard.extensions.hooks import TemplateHook

from django.utils.html import escape
from django.forms.models import model_to_dict
from djblets.datagrid.grids import Column, StatefulColumn
# 仪表盘上的
from reviewboard.extensions.hooks import DashboardColumnsHook
# 所有申请列
from reviewboard.extensions.hooks import DataGridColumnsHook
from reviewboard.datagrids.grids import UsersDataGrid, ReviewRequestDataGrid
import json

from reviewboard.extensions.hooks import ReviewRequestApprovalHook
from reviewboard.reviews.models.review_request import ReviewRequest
from reviewboard.reviews.models.review import Review

import logging
logger = logging.getLogger(__name__)

class AlreadyUsedColumn(Column):
    def render_data(
            self,
            state: StatefulColumn,
            obj: Any,
    ) -> str:
        """Render the column data within the cell.

        Args:
            state (StatefulColumn):
                The state for the DataGrid instance.

            obj (object):
                The object being rendered for this row.

        Returns:
            str:
            The rendered data as HTML.
        """
        if 'already_used_in_post_commit_hook' in obj.extra_data:
            return (
                    '<span class="already_used_in_post_commit_hook">%s</span>'
                    % escape(obj.extra_data['already_used_in_post_commit_hook'])
            )

        return ''


class CustomApprovalStatusColumn(Column):
    def render_data(
            self,
            state: StatefulColumn,
            obj: Any,
    ) -> str:
        """Render the column data within the cell.

        Args:
            state (StatefulColumn):
                The state for the DataGrid instance.

            obj (object):
                The object being rendered for this row.

        Returns:
            str:
            The rendered data as HTML.
        """
        target_people = set()
        all_ship_reviews = set()
        try:
            if isinstance(obj, ReviewRequest):
                target_people = set([str(user) for user in obj.target_people.all()])
                all_ship_reviews = set(str(review.user) for review in
                                       Review.objects.filter(
                                           review_request=obj,
                                           public=True,
                                           ship_it=True
                                       ).select_related('user'))
        except Exception as e:
            logger.exception(
                '错误添加审批状态列: %s',
                e)
        ship_it_percent: str = f'{len(target_people & all_ship_reviews)}/{len(target_people)}'
        return '<span class="custom_approval_status">%s</span>' % escape(ship_it_percent)

class CustomReviewRequestApprovalHook(ReviewRequestApprovalHook):
    def is_approved(self, review_request, prev_approved, prev_failure):

        if not prev_approved:
            return prev_approved, prev_failure
        try:
            if isinstance(review_request, ReviewRequest):
                target_people = set([str(user) for user in review_request.target_people.all()])
                all_ship_reviews = set(str(review.user) for review in
                                       Review.objects.filter(
                                           review_request=review_request,
                                           public=True,
                                           ship_it=True
                                       ).select_related('user'))
                if not target_people <= all_ship_reviews:
                    return False, "还有目标审批人未审批 "
        except Exception as e:
            logger.exception(
                '错误计算审批状态: %s',
                e)
        return True

class AddDashboardColumnExtension(Extension):
    """Internal description for your extension here."""
    id = 'add_dashboard_column'
    metadata = {
        'Name': _('add_dashboard_column'),
        'Summary': _('添加一个自定义的扩展列'),
    }

    def initialize(self):
        """Initialize the extension."""
        # Set up any hooks your extension needs here. See
        # https://www.reviewboard.org/docs/manual/7.0/extending/extensions/#python-extension-hooks
        # TemplateHook(self,
        #              'before-login-form',
        #              'add_dashboard_column/before-login-form.html')
        DashboardColumnsHook(self, [
            AlreadyUsedColumn(id="already_used_in_post_commit_hook",
                              label="被使用"),
            CustomApprovalStatusColumn(id="custom_approval_status",
                                       label="审批状态")
        ]),
        DataGridColumnsHook(self, ReviewRequestDataGrid, [
            AlreadyUsedColumn(id="already_used_in_post_commit_hook",
                              label="被使用"),
            CustomApprovalStatusColumn(id="custom_approval_status",
                                       label="审批状态")
        ])
        # 重新计算审批数，所有人审批通过才算
        CustomReviewRequestApprovalHook(self)
