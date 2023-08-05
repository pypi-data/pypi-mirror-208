import posixpath

from django.db.models import CharField, Q
from django.db.models.expressions import Exists, OuterRef
from django.db.models.functions import Length, Substr

from wagtail.models.sites import Site
from wagtail.search.queryset import SearchableQuerySetMixin
from wagtail.query import TreeQuerySet


class NavigationLinkQuerySet(SearchableQuerySetMixin, TreeQuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _clone(self):
        clone = super()._clone()
        return clone

    def link_q(self, other):
        return Q(id=other.id)

    def link(self, other):
        """
        This filters the QuerySet so it only contains the specified link.
        """
        return self.filter(self.link_q(other))

    def not_link(self, other):
        """
        This filters the QuerySet so it doesn't contain the specified link.
        """
        return self.exclude(self.link_q(other))

    def first_common_ancestor(self, include_self=False, strict=False):
        """
        Find the first ancestor that all links in this queryset have in common.
        For example, consider a link hierarchy like::

            - Home/
                - Foo Event Index/
                    - Foo Event Page 1/
                    - Foo Event Page 2/
                - Bar Event Index/
                    - Bar Event Page 1/
                    - Bar Event Page 2/

        The common ancestors for some queries would be:

        .. code-block:: python

            >>> Link.objects\\
            ...     .first_common_ancestor()
            <Link: Home>
            >>> Link.objects\\
            ...     .filter(title__contains='Foo')\\
            ...     .first_common_ancestor()
            <Link: Foo Event Index>

        This method tries to be efficient, but if you have millions of pages
        scattered across your page tree, it will be slow.

        If `include_self` is True, the ancestor can be one of the pages in the
        queryset:

        .. code-block:: python

            >>> Link.objects\\
            ...     .filter(title__contains='Foo')\\
            ...     .first_common_ancestor()
            <Link: Foo Event Index>
            >>> Link.objects\\
            ...     .filter(title__exact='Bar Event Index')\\
            ...     .first_common_ancestor()
            <Link: Bar Event Index>

        A few invalid cases exist: when the queryset is empty, when the root
        Page is in the queryset and ``include_self`` is False, and when there
        are multiple page trees with no common root (a case Wagtail does not
        support). If ``strict`` is False (the default), then the first root
        node is returned in these cases. If ``strict`` is True, then a
        ``ObjectDoesNotExist`` is raised.
        """
        # An empty queryset has no ancestors. This is a problem
        if not self.exists():
            if strict:
                raise self.model.DoesNotExist("Can not find ancestor of empty queryset")
            return self.model.get_first_root_node()

        if include_self:
            # Get all the paths of the matched pages.
            paths = self.order_by().values_list("path", flat=True)
        else:
            # Find all the distinct parent paths of all matched pages.
            # The empty `.order_by()` ensures that `Page.path` is not also
            # selected to order the results, which makes `.distinct()` works.
            paths = (
                self.order_by()
                .annotate(
                    parent_path=Substr(
                        "path",
                        1,
                        Length("path") - self.model.steplen,
                        output_field=CharField(max_length=255),
                    )
                )
                .values_list("parent_path", flat=True)
                .distinct()
            )

        # This method works on anything, not just file system paths.
        common_parent_path = posixpath.commonprefix(paths)

        # That may have returned a path like (0001, 0002, 000), which is
        # missing some chars off the end. Fix this by trimming the path to a
        # multiple of `Page.steplen`
        extra_chars = len(common_parent_path) % self.model.steplen
        if extra_chars != 0:
            common_parent_path = common_parent_path[:-extra_chars]

        if common_parent_path == "":
            # This should only happen when there are multiple trees,
            # a situation that Wagtail does not support;
            # or when the root node itself is part of the queryset.
            if strict:
                raise self.model.DoesNotExist("No common ancestor found!")

            # Assuming the situation is the latter, just return the root node.
            # The root node is not its own ancestor, so this is technically
            # incorrect. If you want very correct operation, use `strict=True`
            # and receive an error.
            return self.model.get_first_root_node()

        # Assuming the database is in a consistent state, this page should
        # *always* exist. If your database is not in a consistent state, you've
        # got bigger problems.
        return self.model.objects.get(path=common_parent_path)

    def translation_of_q(self, link, inclusive):
        q = Q(translation_key=link.translation_key)

        if not inclusive:
            q &= ~Q(pk=link.pk)

        return q

    def translation_of(self, link, inclusive=False):
        """
        This filters the QuerySet to only contain links that are translations of the specified link.

        If inclusive is True, the link itself is returned.
        """
        return self.filter(self.translation_of_q(link, inclusive))

    def not_translation_of(self, link, inclusive=False):
        """
        This filters the QuerySet to only contain links that are not translations of the specified link.

        Note, this will include the link itself as the link is technically not a translation of itself.
        If inclusive is True, we consider the link to be a translation of itself so this excludes the link
        from the results.
        """
        return self.exclude(self.translation_of_q(link, inclusive))

    def annotate_site_root_state(self):
        """
        Performance optimisation for listing pages.
        Annotates each object with whether it is a root page of any site.
        Used by `is_site_root` method on `wagtailcore.models.Page`.
        """
        return self.annotate(
            _is_site_root=Exists(
                Site.objects.filter(
                    root_link__translation_key=OuterRef("translation_key")
                )
            )
        )
