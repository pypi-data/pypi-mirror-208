import pytest
from django.contrib.redirects.models import Redirect
from django.contrib.auth.models import User

from django.urls import reverse


@pytest.mark.django_db
class TestImportForm:
    @pytest.fixture
    def load_csv(self):
        with open("giant_redirect_import/tests/fixtures/test_data.csv") as f:
            self.data = f.read()

    def test_csv(self, load_csv):
        """
        Test the csv file is opened and contains the correct headers
        """
        assert "Original URL,Redirect To" in self.data

    def test_correct_format(self, client):
        """
        Test the form strips the url structure and 
        outputs the correct format for the Redirect object
        """
        my_admin = User.objects.create_superuser(
            username="myuser", email="myemail@test.com", password="password"
        )
        client.force_login(user=my_admin)

        with open("giant_redirect_import/tests/fixtures/test_data.csv") as f:
            client.post(reverse("admin:redirects_redirect_import_csv"), {"csv_file": f})
        
        expected_count = 1
        obj = Redirect.objects.first()
        assert Redirect.objects.all().count() == expected_count
        assert obj.old_path == "https://www.example.com/cookie-policy/"
        assert obj.new_path == "/cookies/"
