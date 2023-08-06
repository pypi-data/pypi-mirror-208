from django.contrib import admin, messages
from django.contrib.redirects.admin import RedirectAdmin
from django.contrib.redirects.models import Redirect
from django.shortcuts import redirect, render
from django.urls import path, reverse

from .forms import RedirectImportForm

admin.site.unregister(Redirect)


@admin.register(Redirect)
class RedirectAdminExtension(RedirectAdmin):
    """
    Extension of the base RedirectAdmin in order to add
    a custom "import redirects" form
    """

    change_list_template = "redirects/admin/redirect_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import/csv/",
                self.admin_site.admin_view(self.import_csv),
                name="redirects_redirect_import_csv",
            ),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        form = RedirectImportForm(request.POST or None, request.FILES or None,)

        if form.is_valid():
            result = form.process()

            if result["error"]:
                messages.error(request, f'{result["message"]}')
            else:
                messages.success(request, f'{result["message"]}')

            return redirect(reverse("admin:redirects_redirect_changelist"))

        return render(request, "redirects/admin/csv_import.html", {"form": form})
