from django_filters import rest_framework as filters
from wagtail.contrib.redirects.models import Redirect


class RedirectFilter(filters.FilterSet):
    site = filters.CharFilter(field_name="site__hostname")

    class Meta:
        model = Redirect
        fields = ["old_path", "site"]
