from django.test import override_settings, RequestFactory
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.models import Page, Site
from wagtail.contrib.redirects.models import Redirect
from wagtail.test.utils import WagtailPageTests
from rest_framework.test import APIRequestFactory
from sandbox.models import FooPage
from .views import SPAExtendedPagesAPIEndpoint, RedirectViewSet, sitemap
from .utils import hash_draft_code


TEST_DRAFT_CODE = "abc"


class WagtailSPAIntegrationTests(WagtailPageTests):
    @override_settings(PREVIEW_DRAFT_CODE=TEST_DRAFT_CODE)
    def test_draft_api(self):
        home = Page.objects.last()
        old_title = home.title
        new_title = "edit it"
        home.title = new_title
        home.save_revision()

        request = APIRequestFactory().get("")
        request.site = Site.objects.first()
        request.wagtailapi_router = WagtailAPIRouter("wagtailapi")
        page_detail = SPAExtendedPagesAPIEndpoint.as_view({"get": "detail_view"})
        res = page_detail(request, pk=home.pk)
        self.assertContains(res, old_title)
        self.assertNotContains(res, new_title)

        params = {"draft": hash_draft_code(TEST_DRAFT_CODE, home.pk)}
        request = APIRequestFactory().get("", params)
        request.site = Site.objects.first()
        request.wagtailapi_router = WagtailAPIRouter("wagtailapi")
        res = page_detail(request, pk=home.pk)
        self.assertContains(res, new_title)

    @override_settings(PREVIEW_DRAFT_CODE=TEST_DRAFT_CODE)
    def test_draft_api_unpublished(self):
        home = Page.objects.last()
        new_title = "edit it"
        home.title = new_title
        home.save_revision()
        home.live = False
        home.save()

        params = {"draft": hash_draft_code(TEST_DRAFT_CODE, home.pk)}
        request = APIRequestFactory().get("", params)
        request.site = Site.objects.first()
        request.wagtailapi_router = WagtailAPIRouter("wagtailapi")
        page_detail = SPAExtendedPagesAPIEndpoint.as_view({"get": "detail_view"})
        res = page_detail(request, pk=home.pk)
        self.assertContains(res, new_title)

    @override_settings(PREVIEW_DRAFT_CODE=TEST_DRAFT_CODE)
    def test_draft_api_detail_by_path(self):
        home = Page.objects.last()
        foo = FooPage(title="foo")
        home.add_child(instance=foo)
        foo.live = False
        foo.save()

        url = "/api/v2/pages/detail_by_path/"
        params = {
            "html_path": foo.url,
            "draft": hash_draft_code(TEST_DRAFT_CODE, foo.pk),
        }
        res = self.client.get(url, params)
        self.assertContains(res, "foo")

    @override_settings(PREVIEW_DRAFT_CODE=TEST_DRAFT_CODE)
    def test_draft_api_detail_by_path_with_changed_slug(self):
        home = Page.objects.last()
        foo = FooPage(title="foo")
        home.add_child(instance=foo)
        foo.live = False
        foo.save()
        foo.slug = "foo-edit"
        foo.save_revision()

        url = "/api/v2/pages/detail_by_path/"
        params = {
            "html_path": "/foo-edit/",
            "draft": hash_draft_code(TEST_DRAFT_CODE, foo.pk),
        }
        res = self.client.get(url, params)
        self.assertContains(res, "foo")

    @override_settings(PREVIEW_DRAFT_CODE=TEST_DRAFT_CODE)
    def test_draft_api_detail_by_path_with_changed_slug_and_nested(self):
        """Ensure a deeply nested page works such as /sub/foo"""
        home = Page.objects.last()
        sub_page = FooPage(title="sub")
        home.add_child(instance=sub_page)
        foo = FooPage(title="foo")
        sub_page.add_child(instance=foo)
        foo.live = False
        foo.save()
        foo.slug = "foo-edit"
        foo.save_revision()

        url = "/api/v2/pages/detail_by_path/"
        params = {
            "html_path": "/foo-edit/",
            "draft": hash_draft_code(TEST_DRAFT_CODE, foo.pk),
        }
        res = self.client.get(url, params)
        self.assertContains(res, "foo")

    @override_settings(PREVIEW_DRAFT_CODE=TEST_DRAFT_CODE)
    def test_draft_api_detail_by_path_with_slug_404(self):
        """Pages detail_by_path 404s if no matching slug is found"""
        home = Page.objects.last()
        foo = FooPage(title="foo")
        home.add_child(instance=foo)
        foo.live = False
        foo.save()

        url = "/api/v2/pages/detail_by_path/"
        params = {
            "html_path": "/no/",
            "draft": hash_draft_code(TEST_DRAFT_CODE, foo.pk),
        }
        res = self.client.get(url, params)
        self.assertEquals(res.status_code, 404)

    @override_settings(PREVIEW_DRAFT_CODE=TEST_DRAFT_CODE)
    def test_draft_api_detail_by_path_with_too_many_slugs(self):
        home = Page.objects.last()
        foo = FooPage(title="foo")
        foo2 = FooPage(title="foo2")
        home.add_child(instance=foo)
        home.add_child(instance=foo2)
        foo.live = False
        foo2.live = False
        foo.save()
        foo2.save()
        foo.slug = "foo-edit"
        foo.save_revision()
        foo2.slug = "foo-edit"
        foo2.save_revision()

        url = "/api/v2/pages/detail_by_path/"
        params = {
            "html_path": "/foo-edit/",
            "draft": hash_draft_code(TEST_DRAFT_CODE, foo.pk),
        }
        res = self.client.get(url, params)

        self.assertEqual(res.status_code, 404)

    @override_settings(PREVIEW_DRAFT_CODE=TEST_DRAFT_CODE)
    def test_draft_api_detail_with_incorrect_draft_value(self):
        home = Page.objects.last()
        foo = FooPage(title="foo")
        home.add_child(instance=foo)
        foo.live = False
        foo.save()

        url = "/api/v2/pages/detail_by_path/"
        params = {
            "html_path": "/foo-edit/",
            "draft": "random_draft_code",  # some random draft code
        }
        res = self.client.get(url, params)

        self.assertEqual(res.status_code, 404)

    def test_sitemap_with_site(self):
        home = Page.objects.last()
        site_hostname = "http://example.com"
        site = Site.objects.create(root_page=home, hostname=site_hostname)
        params = {"site": site.hostname}
        request = RequestFactory().get("sitemap.xml", params)
        res = sitemap(request)
        res.render()
        self.assertContains(res, site_hostname)

    def test_redirect_viewset(self):
        home = Page.objects.last()
        site_hostname = "http://example.com"
        site = Site.objects.create(root_page=home, hostname=site_hostname)
        params = {"old_path": "/lol/"}
        request = APIRequestFactory().get("", params)
        redirect_list = RedirectViewSet.as_view({"get": "list"})
        Redirect.objects.create(
            old_path="/lol/", redirect_link="https://example.com", site=site
        )
        Redirect.objects.create(
            old_path="/test/", redirect_link="https://no.com", site=site
        )
        response = redirect_list(request)
        self.assertContains(response, "example.com")
        self.assertNotContains(response, "no.com")
        self.assertEqual(response.data[0]["site"], site_hostname)

    def test_redirect_viewset_by_site_filter(self):
        home = Page.objects.last()
        site_hostname = "http://example.com"
        site_hostname2 = "http://foo.com"
        site = Site.objects.create(root_page=home, hostname=site_hostname)
        site2 = Site.objects.create(root_page=home, hostname=site_hostname2)
        Redirect.objects.create(site=site)
        Redirect.objects.create(site=site2)

        params = {"site": site_hostname}
        request = APIRequestFactory().get("", params)
        redirect_list = RedirectViewSet.as_view({"get": "list"})
        response = redirect_list(request)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["site"], site_hostname)

    def test_exclude_type(self):
        home = Page.objects.last()
        foo = FooPage(title="foo")
        home.add_child(instance=foo)
        params = {"exclude_type": "sandbox.FooPage"}
        request = APIRequestFactory().get("", params)
        request.site = Site.objects.first()
        request.wagtailapi_router = WagtailAPIRouter("wagtailapi")
        page_list = SPAExtendedPagesAPIEndpoint.as_view({"get": "listing_view"})
        res = page_list(request)
        self.assertNotContains(res, foo.title)
        self.assertEqual(res.data["meta"]["total_count"], 1)

    def test_find_view(self):
        home = Page.objects.last()
        foo = FooPage(title="foo")
        home.add_child(instance=foo)

        url = "/api/v2/pages/find/"
        params = {"html_path": "/"}
        res = self.client.get(url, params)
        self.assertEqual(res.status_code, 302)

    def test_detail_by_path(self):
        home = Page.objects.last()

        url = "/api/v2/pages/detail_by_path/"
        params = {"html_path": "/"}
        res = self.client.get(url, params)
        self.assertContains(res, home.title)
