from types import SimpleNamespace

from django.contrib import admin
from django.test import SimpleTestCase

from advertisement.models import Advertisement, AdvertisementAdmin


class AdvertisementAdminImageTagTests(SimpleTestCase):
    def test_admin_image_tag_has_closing_bracket(self):
        admin_instance = AdvertisementAdmin(Advertisement, admin.site)
        advertisement = SimpleNamespace(preview_image=SimpleNamespace(url="https://example.com/image.jpg"))
        html = admin_instance.get_html_photo(advertisement)
        self.assertIn("<img", html)
        self.assertTrue(html.endswith(">"))
