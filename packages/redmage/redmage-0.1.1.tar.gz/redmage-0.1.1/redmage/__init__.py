from starlette.convertors import register_url_convertor

from .components import Component
from .convertors import BoolConvertor, StringConverter
from .core import Redmage, app
from .targets import Target
from .triggers import Trigger

register_url_convertor("bool", BoolConvertor())
register_url_convertor("str", StringConverter())
