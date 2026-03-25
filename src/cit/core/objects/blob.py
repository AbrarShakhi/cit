
from cit.core.objects.object import Object


class Blob(Object):
    def __init__(self, content: bytes):
        super().__init__("blob", content)