from typing import Dict




class BastionIntegrationError(Exception):
    error_type: str = "C"
    default_class: int = 999
    default_subclass: int = 999
    context: Dict[str, str | int] = None

    def __init__(self, ex=None, message=None, context=None):
        if ex:
            self.message = str(ex)
        else:
            self.message = message
        if context:
            self.context = context
        elif not self.context:
            self.set_default_context()

        super().__init__(self.message)

    def set_default_context(self):
        self.context = {
            "type": self.error_type,
            "code": f"{self.error_type}-{self.default_class}-{self.default_subclass}",
            "class": self.default_class,
            "subclass": self.default_subclass,
            "comment": self.message
        }


async def _handle_response(response, dto):
    model_list = []
    for info in response:
        model_list.append(dto(**info))
    return model_list