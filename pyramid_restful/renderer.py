# need to import this module to register the proper serializers
import projex.rest
from pyramid.renderers import JSON


class JSON2(JSON):
    def __init__(self, serializer=projex.rest.jsonify, adapters=(), **kw):
        serializer = projex.rest.jsonify
        super(JSON2, self).__init__(serializer=serializer, adapters=adapters, **kw)

json2_renderer_factory = JSON2()