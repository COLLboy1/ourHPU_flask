from ourhpu.utils.hpu_spider import get_login_state
from ourhpu.utils.hpu_spider.get_student_data import get_self_data, get_grade_lists, get_all_achievement, get_class_schedule_card

from . import api
from ourhpu import redis_store
from flask import request, jsonify, current_app
import pickle
import re
import datetime

@api.route("/encrypted", methods=["GET"])
def encrypted_data():
    """获取登陆状态"""
    username = request.args.get("username")
    password = request.args.get("password")

    if not all([username, password]):
        return jsonify(errno=0, errmsg="参数不完整")

    # 判断用户是否已经有了保存过的session
    try:
        session = redis_store.get(username)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if session is not None:
            return jsonify(errno=1, errmsg="用户状态已经保存")

    session = get_login_state.GetLoginMessage(username=username, password=password).get_message()

    # 用redis保存用户登陆状态
    try:
        redis_store.setex(username, 600, pickle.dumps(session))
    except Exception as e:
        return jsonify(errno=2, errmsg="保存登陆状态失败")

    return jsonify(errno=3, errmsg="OK")

@api.route("/schedule", methods=["GET"])
def get_schedule_card():
    """获取学生基本信息"""
    # 1、获取用户传递的参数，判断参数是否传递，没有传递返回错误信息
    username = request.args.get("username")

    if not all([username]):
        return jsonify(errno=0, errmsg="参数不完整")

    # 2、判断redis中是否保存着教务处密码的登陆状态。登陆了直接查询，没登陆返回给客户端，让客户端去访问网站去获取登陆状态
    try:
        session = pickle.loads(redis_store.get(username))
    except Exception as e:
        current_app.logger.error(e)
        session = None

    if session is None:
        return jsonify(errno=1, errmsg="登陆状态已经过期，请重新登陆")

    # 3、利用保存好的登陆状态获取学生信息
    student_data_dict = get_self_data(session)

    if student_data_dict == 0:
        return jsonify(errno=2, errmsg="用户登陆失败，请重新登陆")

    # 4、返回数据
    return jsonify(errno=2, errmsg="查询成功", data= student_data_dict)

@api.route('/grade/list', methods=['GET'])
def get_grade_list():
    """
    获取成绩列表信息
    返回数据：例如：{年份：2020， 季度：上季， url_index：1}
    """
    # 1、获取username参数，并判断参数是否完整
    username = request.args.get("username")
    grade = request.args.get("grade")
    educational_system = request.args.get("educational_system")

    if not all([username, grade, educational_system]):
        return jsonify(errno=0, errmsg="参数不完整")
    # 2、根据username获取登陆session
    try:
        session = pickle.loads(redis_store.get(username))
    except Exception as e:
        current_app.logger.error(e)
        session = None
    if session is None:
        # 代表用户session 登陆过期
        return jsonify(errno=1, errmsg="用户登陆过期")

    # 3、根据session 调用函数，获取成绩年份信息
    all_grade_lists = []
    grade_total_list = get_grade_lists(session)

    grade_id = str(int(grade) - 2000)

    # 获取当前年份，获取课程表列表信息
    now_year = int(datetime.datetime.now().year)

    if int(grade) + int(educational_system) > now_year:
        # 用户已经毕业，返回全部数据
        for i in range(int(educational_system)):
            grade_list = re.findall('y' + grade_id + ':(.*?)}]', grade_total_list)[0][1:] + "}"
            # 上班学期id号
            semesterId = re.findall(r'{id:(.*?),', grade_list)[0]
            schoolYear = re.findall(r'schoolYear:"(.*?)",', grade_list)[0]

            # 构造字典
            data_dict = {
                "semesterId-1": semesterId,
                "semesterId-2": int(semesterId) + 1,
                "schoolYear": schoolYear
            }
            all_grade_lists.append(data_dict)
            grade_id = str(int(grade_id) + 1)
    else:
        num = now_year - int(grade)
        for i in range(num):
            grade_list = re.findall('y' + grade_id + ':(.*?)}]', grade_total_list)[0][1:] + "}"
            # 上班学期id号
            semesterId = re.findall(r'{id:(.*?),', grade_list)[0]
            schoolYear = re.findall(r'schoolYear:"(.*?)",', grade_list)[0]

            # 构造字典
            data_dict = {
                "semesterId-1": semesterId,
                "semesterId-2": int(semesterId) + 1,
                "schoolYear": schoolYear
            }
            all_grade_lists.append(data_dict)
            grade_id = str(int(grade_id) + 1)

    # 4、返回数据
    return jsonify(errno=2, errmgs="OK", grade_list=all_grade_lists)

@api.route('/achievement', methods=["GET"])
def get_achievement():
    """
    获取成绩
    :return: 返回成绩列表
    """
    # 1、获取参数,判断是否接受到参数
    username = request.args.get("username")
    semesterId = request.args.get("semesterId")

    if not all([semesterId, username]):
        return jsonify(errno=0, errmsg="参数不完整")

    # 2、根据username获取登陆session
    try:
        session = pickle.loads(redis_store.get(username))
    except Exception as e:
        current_app.logger.error(e)
        session = None
    if session is None:
        # 代表用户session 登陆过期
        return jsonify(errno=1, errmsg="用户登陆过期")

    # 3、获取信息
    achievement_list = get_all_achievement(session, semesterId)

    return jsonify(errno=2, errmsg="OK", achievement_list=achievement_list)

@api.route('/schedule_card', methods=["GET"])
def get_schedule():
    """
    获取课程表
    :return:
    """
    # 1、获取参数,判断是否接受到参数
    username = request.args.get("username")

    if not all([username]):
        return jsonify(errno=0, errmsg="参数不完整")

    # 2、根据username获取登陆session
    try:
        session = pickle.loads(redis_store.get(username))
    except Exception as e:
        current_app.logger.error(e)
        session = None
    if session is None:
        # 代表用户session 登陆过期
        return jsonify(errno=1, errmsg="用户登陆过期")

    # 3、获取信息
    data = get_class_schedule_card(session)

    #4、返回数据
    return jsonify(errno=2, errmsg="OK", data=data)
