#
from flask import Blueprint

# 创建蓝图对象
api = Blueprint("app_1_0", __name__)

from . import demo
from . import student_base_message