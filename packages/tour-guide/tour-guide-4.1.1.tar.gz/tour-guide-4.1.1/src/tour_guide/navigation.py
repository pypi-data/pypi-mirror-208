from django.utils.deconstruct import deconstructible

from .links import RichLink

__all__ = ['NavigationNode']


@deconstructible
class NavigationNode(RichLink):

    def __init__(self, *, is_active=False, depth=0, order=0, path=None, **kwargs):
        super().__init__(**kwargs)

        self.is_active = is_active
        self.depth = depth
        self.order = order
        self.path = path if path is not None else list()
        self.children = []

    def traverse(self, callback):
        stack = [(self, 0)]

        while stack:
            node, index = stack[-1]  # noqa

            if index == 0:
                # node open
                callback(node, stack[:], True)

            if index >= len(node.children):
                # node close
                callback(node, stack[:], False)
                stack.pop()  # noqa
                continue

            stack[-1] = node, index + 1
            node = node.children[index]
            stack.append((node, 0))
