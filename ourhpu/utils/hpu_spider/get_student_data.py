# from get_login_state import GetLoginMessage
from lxml import etree
import re
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

def data_correctness(data, a):
    """
    判断数据是否存在
    :param data:  列表
    :param a:  索引1
    :param b:  索引2
    :return: 数据
    """
    try:
        data = data[a]
    except Exception as e:
        data = None
    return data

def get_self_data(session):
    # 获取个人信息
    res_data = session.get("http://218.196.248.100/eams/stdDetail.action", headers=headers)
    # print(res_data.text)
    resp_lists = re.findall(r'<td colspan="2" style="text-align:center;color:red;">验证码错误</td>', res_data.text)

    print(resp_lists)
    if len(resp_lists) != 0:
        # 验证码错误
        student_data_dict = 0
        return student_data_dict
    else:
        # 书写xpath获取学生信息
        resp_xpath = etree.HTML(res_data.text)
        td_lists = resp_xpath.xpath('//div[@id="tabPage1"]/table//tr//td//text()')
        # 学号
        student_code = data_correctness(td_lists, 2)
        # 姓名
        name = data_correctness(td_lists, 4)
        # 性别
        sex = data_correctness(td_lists, 10)
        # 年级
        grade = data_correctness(td_lists, 12)
        # 学制
        educational_system = data_correctness(td_lists, 14)
        # school名称
        school = data_correctness(td_lists, 16)
        # 学历层次
        education_level = data_correctness(td_lists, 18)
        # 院系
        department = data_correctness(td_lists, 22)
        # 专业
        major = data_correctness(td_lists, 24)
        # 入学时间
        admission_time = data_correctness(td_lists, 27)
        # 预毕业时间
        pre_graduation_time = data_correctness(td_lists, 29)
        # 班级
        student_class = data_correctness(td_lists, 41)

        student_data_dict = {
            "student_code": student_code,
            "name": name,
            "sex": sex,
            "grade": grade,
            "educational_system": educational_system,
            "school": school,
            "education_level": education_level,
            "department": department,
            "major": major,
            "admission_time": admission_time,
            "pre_graduation_time": pre_graduation_time,
            "student_class": student_class
        }
        return student_data_dict


def get_grade_lists(session):
    params = {
        "tagId": "semesterBar13572391471Semester",
        "dataType": "semesterCalendar",
        "value": "39",
        "empty": "false"
    }

    params1 = {
        "project.id": "1",
        "semester.id": "39"
    }

    try:
        session.post("http://218.196.248.100/eams/teach/grade/course/person.action", headers=headers, params=params1)
        session.get("http://218.196.248.100/eams/static/scripts/semesterCalendar_zh.js?", headers=headers)
        req_grade_list = session.post("http://218.196.248.100/eams/dataQuery.action", headers=headers, params=params)
        req_grade_list = req_grade_list.content.decode()
        req_grade_list ="{y1:" + re.findall(r'y1:(.*?),yearIndex', req_grade_list)[0]
    except Exception as e:
        req_grade_list = None
    return req_grade_list

def get_all_achievement(session, semesterId):
    """
    获取成绩信息
    :param session:
    :return:
    """
    data_lists = []
    try:
        req_data = session.get("http://218.196.248.100/eams/teach/grade/course/person!search.action?semesterId={}&projectType=".format(semesterId), headers=headers).text
        req_data = etree.HTML(req_data)
        tr_lists = req_data.xpath("//div//tbody/tr")
        for tr in tr_lists:
            tr_text_lists = tr.xpath('.//text()')
            # 学年学期
            school_year = tr_text_lists[1]
            # 课程代码
            course_code = tr_text_lists[3]
            # 课程序号
            course_number = tr_text_lists[5]
            # 课程名称
            course_name = tr_text_lists[7].replace('\n', "").replace('\t', "").replace('\r', "")
            # 课程类别
            course_category = tr_text_lists[9]
            # 课程属性
            course_attribute = tr_text_lists[11]
            # 学分
            credit = tr_text_lists[13]
            # 总评成绩
            total_mark = tr_text_lists[15].replace('\n', "").replace('\t', "").replace('\r', "").replace(" ", "")
            # 最终成绩
            final_results = tr_text_lists[16].replace('\n', "").replace('\t', "").replace('\r', "").replace(" ", "")
            # 绩点
            GPA = tr_text_lists[17].replace('\n', "").replace('\t', "").replace('\r', "")

            data_dict = {
                "school_year": school_year,
                "course_code": course_code,
                "course_number": course_number,
                "course_name": course_name,
                "course_category": course_category,
                "course_attribute": course_attribute,
                "credit": credit,
                "total_mark": total_mark,
                "final_results": final_results,
                "GPA": GPA
            }

            data_lists.append(data_dict)

    except Exception as e:
        data_lists = None
    return data_lists

def get_class_schedule_card(session):
    """获取课程表信息"""
    schedule_lists = []
    params = {
        "ignoreHead": "1",
        "setting.kind": "std",
        "startWeek": "14",
        "project.id": "1",
        "semester.id": "62",
        "ids": "75470"
    }
    try:
        req_schedule_str = session.post("http://218.196.248.100/eams/courseTableForStd!courseTable.action", headers=headers, params=params).text
        req_schedule_lists = re.findall(r'var teachers =(.*)table0', req_schedule_str, re.S)[0].replace('\n', "").replace('\t', "").replace('\r', "").split("var teachers = ")
        for schedule in req_schedule_lists:
            teacher_name = re.findall(r',name:"(.*?)",lab:', schedule)[0]
            schedule_detail = re.findall(r'activity = new TaskActivity(.*?);', schedule)[0].split(",")
            schedule_name = schedule_detail[5][1: -1]
            schedule_location = schedule_detail[7][1:-1]
            schedule_time = re.findall(r'index =(.*?)\*unitCount\+(.*?);', schedule)

            schedule_dict = {
                "teacher_name": teacher_name,
                "schedule_name": schedule_name,
                "schedule_location": schedule_location,
                "schedule_time": schedule_time
            }
            schedule_lists.append(schedule_dict)

    except Exception as e:
        print(e)
        req_schedule_str = None

    return schedule_lists


#
# if __name__ == '__main__':
#     # get_grade_data()
#     get_self_data()