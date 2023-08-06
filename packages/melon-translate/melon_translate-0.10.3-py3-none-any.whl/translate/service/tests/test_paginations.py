from rest_framework import status


class TestTranslatePagination:
    def test_page_size(self):
        from translate.service.paginations import TranslateClientPagination

        pag = TranslateClientPagination()

        assert pag.page_size <= 500, "Page size should not be greater than 500"
        assert pag.max_page_size <= 800, "Max page size should not be greater than 800"

    def test_paginated_response(self, make_request, import_german_translations_fixture):
        from translate.service.views import TranslationsAPIView

        kwargs = {"language": "de"}
        data = {"page": 1, "page_size": 5}
        request = make_request(f"get::api_translations", kwargs=kwargs, data=data)
        response = TranslationsAPIView.as_view()(request, **kwargs)

        assert response.status_code == status.HTTP_200_OK
        assert response.data, "Response should return some data"
        assert {"links", "pages", "count", "results"} == set(response.data.keys())
        assert isinstance(response.data.get("results"), list)
        assert not len(response.data.get("results")) > 5, "Should not return more than page_size values"
