from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from velait.main.api.responses import APIResponse


class VelaitAPIRenderer(CamelCaseJSONRenderer):
    def render(self, data, *args, **kwargs):
        if isinstance(data, dict):
            if data.get('pagination') is None:
                data = APIResponse.format_data(data)

        return super(VelaitAPIRenderer, self).render(data, *args, **kwargs)


__all__ = ['VelaitAPIRenderer']
