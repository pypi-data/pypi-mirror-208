from csv import DictReader
from io import StringIO
from urllib.parse import urlparse

from django import forms
from django.conf import settings
from django.contrib.redirects.models import Redirect


class RedirectImportForm(forms.Form):

    """
    Form to handle csv file import from redirect admin.
    List the rows to be imported in the "rows" list
    """

    csv_file = forms.FileField()

    class Meta:
        fields = ["csv_file"]

    def process(self):
        """
        Do the actual import
        """
        import_file = self.cleaned_data["csv_file"]
        file = import_file.read().decode("utf-8-sig")
        csv_data = DictReader(StringIO(file), delimiter=",")
        site_id = 1
        schema = "https://www."

        if hasattr(settings, "REDIRECT_IMPORT_DEFAULT_SITE_ID"):
            site_id = settings.REDIRECT_IMPORT_DEFAULT_SITE_ID

        created, updated = 0, 0

        for row in csv_data:
            try:
                old_slug = row["Original URL"]
                new_slug = row["Redirect To"]
            except:
                return {
                    "message": "Import failed. Check the spelling of your column names.",
                    "error": True,
                }

            # Will catch urls with no schema, such as 'example.com/career/'
            if schema not in new_slug:
                new_slug = schema + new_slug

            # Ensuring paths end with a trailing slash
            if not new_slug.endswith("/"):
                new_slug += "/"

            if not old_slug.endswith("/"):
                old_slug += "/"

            _, status = Redirect.objects.update_or_create(
                site_id=site_id,
                old_path=old_slug,
                defaults={"new_path": urlparse(new_slug).path},
            )
            if status:
                created += 1
            else:
                updated += 1
        message = f"{created} new redirects were imported, {updated} redirects were updated."

        return {
            "message": message,
            "error": False,
        }
