def add_middleware_to_request(request, middleware_class):
    def dummy_get_response(request):  # pragma: no cover
        return None

    middleware = middleware_class(dummy_get_response)
    middleware.process_request(request)
