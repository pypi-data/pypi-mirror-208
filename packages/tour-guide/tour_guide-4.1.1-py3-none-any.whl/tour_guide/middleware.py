
class AnchorMiddleware(object):

    """

    AnchorMiddleware no longer needs to be installed as middleware, but instead is used by the AnchorRegistry
    page mixin inside its serve() method.


    """

    def __init__(self, get_response):
        self.current_anchor_registry_and_inventory = None
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        # Deactivated because it introduces whitespace which might mess up the appearance of the output
        # if settings.DEBUG and response.get('Content-Type', ";").split(';', 1)[0] == 'text/html':
        #    response.content = BeautifulSoup(response.content, "html5lib").prettify()

        return response

    def process_template_response(self, request, response):

        if self.current_anchor_registry_and_inventory is None:
            from .anchors import current_anchor_registry_and_inventory
            self.current_anchor_registry_and_inventory = current_anchor_registry_and_inventory

        if response.get('Content-Type', ";").split(';', 1)[0] != 'text/html':
            return response

        if response.context_data is None:
            return response

        registry, inventory = self.current_anchor_registry_and_inventory()

        if not registry:
            return response

        registry.reset()

        content = str(response.rendered_content)

        tokens = self.parse_tokens(registry, content)
        self.order_tokens(registry, inventory, tokens)
        processed_content = self.apply_tokens(registry, inventory, tokens, content)
        response.content = processed_content.encode(encoding=response.charset)

        return response

    # noinspection PyMethodMayBeStatic
    def order_tokens(self, registry, template_context, tokens):

        for token in tokens:
            if token.directive != 'define':
                continue

            registry.order_anchor(template_context, token.category, token.identifier, token.level)

    # noinspection PyMethodMayBeStatic
    def apply_tokens(self, registry, template_context, tokens, text):

        result = ''
        pos = 0

        for token in tokens:

            if pos < token.start_offset:
                result += text[pos:token.start_offset]

            token_result = registry.resolve_token(template_context,
                                                  token.directive, token.category, token.identifier)

            result += token_result
            pos = token.end_offset

        if pos < len(text):
            result += text[pos:]

        return result

    # noinspection PyMethodMayBeStatic
    def parse_tokens(self, registry, text):

        tokens = []
        pos = 0

        while pos < len(text):

            token = registry.match_next_token(text, pos)

            if token is None:
                break

            tokens.append(token)
            pos = token.end_offset

        return tokens
