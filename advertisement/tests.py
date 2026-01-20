from django.contrib import admin
from django.test import SimpleTestCase

from advertisement.models import Advertisement, AdvertisementAdmin


class AdvertisementAdminImageTagTests(SimpleTestCase):
    def test_admin_image_tag_has_closing_bracket(self):
        admin_instance = AdvertisementAdmin(Advertisement, admin.site)
        class DummyImage:
            def __init__(self, url):
                self.url = url

        class DummyAdvertisement:
            def __init__(self, preview_image):
                self.preview_image = preview_image

        advertisement = DummyAdvertisement(DummyImage("https://example.com/image.jpg"))
        html = admin_instance.get_html_photo(advertisement)
        self.assertIn("<img", html)
        self.assertTrue(html.endswith(">"))
