from django.urls import reverse

from wagtail.admin.ui.side_panels import BasePreviewSidePanel, BaseSidePanels

__all__ = ['ArticleSidePanels']


class ArticlePreviewSidePanel(BasePreviewSidePanel):

    def get_context_data(self, parent_context):

        context = super().get_context_data(parent_context)

        if self.object.id:

            context["preview_url"] = reverse(
                "ruminate:preview_on_edit", args=[self.object.id]
            )

        """
        else:
            content_type = parent_context["content_type"]
            parent_page = parent_context["parent_page"]
            context["preview_url"] = reverse(
                "ruminate:preview_on_add",
                args=[content_type.app_label, content_type.model, parent_page.id],
            )
        """

        return context


class ArticleSidePanels(BaseSidePanels):
    def __init__(
        self,
        request,
        article
    ):
        super().__init__(request, article)

        self.side_panels += [
            ArticlePreviewSidePanel(article, self.request),
        ]

