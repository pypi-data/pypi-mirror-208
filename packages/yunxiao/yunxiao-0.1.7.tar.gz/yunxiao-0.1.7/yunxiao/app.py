from .yunxiao import AppOAuth, UsedTime


class App(AppOAuth):
    def __init__(self, userphone: str, password: str, campus: list = None):
        """
        初始化，输入用户账号密码，以及要操作的校区。
        :param userphone: 账号
        :param password: 密码
        :param campus: 校区
        """
        super().__init__(userphone, password)
        if campus is None:
            self.campus = []
        else:
            self.campus = campus

        self.reportpath = "https://yunxiao.xiaogj.com/api/cs-report/report/"
        self.orderpath = "https://yunxiao.xiaogj.com/api/cs-edu/order"
        self.edupath = "https://yunxiao.xiaogj.com/api/cs-edu/"
        self.crmpath = "https://yunxiao.xiaogj.com/api/cs-crm/"

    def find_now_data_report(self):
        """
        [数据/当前数据]
        总剩余学费，总欠缴费用，总欠缴物品费用，在读学员。
        """
        return self.session.post(
            url=self.reportpath + "findNowDataReport",
            json={"campusIds": self.campus, "_t_": UsedTime.stamp}
        ).json()

    def find_course_money(self, date: str = UsedTime.yymm, datetype: int = 1):
        """
        课消数据。
        :param date: 月份，格式示例： 2023-02
        :param datetype:
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findCourseMoney",
            json={"campusIds": self.campus, "date": date, "dateType": datetype, "_t_": UsedTime.stamp}
        ).json()

    def find_tuition(self, date: str = UsedTime.yymm, datetype: int = 1):
        """
        学费收入数据。
        :param date: 月份，格式示例： 2023-02
        :param datetype:
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findTuition",
            json={"campusIds": self.campus, "date": date, "dateType": datetype, "_t_": UsedTime.stamp}
        ).json()

    def find_refund_money(self, date: str = UsedTime.yymm, datetype: int = 1):
        """
        学费退费数据
        :param date: 月份，格式示例： 2023-02
        :param datetype:
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findRefundMoney",
            json={"campusIds": self.campus, "date": date, "dateType": datetype, "_t_": UsedTime.stamp}
        ).json()

    # [数据][每日简报]
    def find_data_report(self, date: str = UsedTime.today):
        """
        每日简报。
        :param date: 日期，格式示例 2023-02-01
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findDataReport",
            json={"campusIds": self.campus, "date": date, "_t_": UsedTime.stamp}
        ).json()

    # [数据][报表][校区数据]
    def find_data_report_list(
            self,
            startdate: str = UsedTime.yymm01,
            enddate: str = UsedTime.today,
            orderbycampus: int = 1
    ):
        """
        某日到某日数据。
        :param startdate: 起始日期
        :param enddate: 截至日期
        :param orderbycampus:
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findDataReportList",
            json={
                "campusIds": self.campus,
                "startDate": startdate,
                "endDate": enddate,
                "orderByCampus": orderbycampus,
                "_t_": UsedTime.stamp
            }
        ).json()

    def find_student_course_fee(
            self,
            curriculumids: list = None,
            status: list = None,
            studentname: str = None
    ):
        """
        学生数据 - 费用报表。
        :param curriculumids: 课程ID列表
        :param status: 学生状态列表
        :param studentname: 按学生姓名检索
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findStudentCourseFee",
            json={
                "campusIds": self.campus,
                "curriculumIds": curriculumids,
                "status": status,
                "studentName": studentname,
                "_t_": UsedTime.stamp
            }
        ).json()

    def find_student_course_amount(
            self,
            curriculumids: list = None,
            status: list = None,
            studentname: str = None
    ):
        """
        学生数据 - 课时报表。
        :param curriculumids: 课程ID列表
        :param status: 学生状态列表
        :param studentname: 按学生姓名检索
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findStudentCourseAmount",
            json={
                "campusIds": self.campus,
                "curriculumIds": curriculumids,
                "status": status,
                "studentName": studentname,
                "_t_": UsedTime.stamp
            }
        ).json()

    def order(
            self,
            ordertype: int = 0,
            searchname: str = "",
            orderstatuslist: list = None,
            starttime: str = UsedTime.yymm01,
            endtime: str = UsedTime.today,
            pagesize: int = 1
    ):
        """
        [收银管理/订单管理]
        查看收费订单。
        :param ordertype:
        :param searchname:
        :param orderstatuslist:
        :param starttime:
        :param endtime:
        :param pagesize:
        :return:
        """
        data = {
            "_t_": UsedTime.stamp,
            "orderType": ordertype,
            "searchName": searchname,
            "campusIds": self.campus,
            "teacherList": [],
            "sourceTypeList": [],
            "productTypeList": [],
            "orderStatusList": orderstatuslist,
            "oweFeeList": [],
            "startTime": starttime,
            "endTime": endtime,
            "page": {
                "pageNum": 1,
                "pageSize": pagesize
            }
        }
        return self.session.post(url=self.orderpath + "Info/pageAdbOrder", json=data).json()

    def order_info(self, orderinfoid: int = 0):
        """
        [收银管理/订单管理/订单详情]
        查询订单详情。
        :param orderinfoid:
        :return:
        """
        params = {
            "_t_": UsedTime.stamp,
            "orderInfoId": orderinfoid,
        }
        return self.session.post(
            url=self.orderpath + "Info/get",
            params=params
        ).json()

    # [工作台][订单管理][退费]
    def refund_order(
            self,
            searchname: str = "",
            starttime: str = UsedTime.yymm01,
            endtime: str = UsedTime.today,
            pagesize: int = 1
    ):
        """
        [收银管理/订单管理/退费]
        查询退费订单。
        :param searchname:
        :param starttime:
        :param endtime:
        :param pagesize:
        :return:
        """
        data = {
            "_t_": UsedTime.stamp,
            "orderType": 2,
            "searchName": searchname,
            "campusIds": self.campus,
            "productTypeList": [],
            "startTime": starttime,
            "endTime": endtime,
            "page": {
                "pageNum": 1,
                "pageSize": pagesize
            }
        }
        return self.session.post(
            url=self.orderpath + "Refund/adbRefundOrderInfoPage",
            json=data
        ).json()

    def course_absent(
            self,
            starttime: str = UsedTime.yymm01,
            endtime: str = UsedTime.today,
            pagesize: int = 1
    ):
        """
        [教务管理/缺勤管理]
        :param starttime: 起始时间
        :param endtime: 结束时间
        :param pagesize: 单页项目数量
        :return:
        """
        data = {
            "_t_": UsedTime.stamp,
            "campusIds": self.campus,
            "remedyStatusList": [0],
            "courseRelations": [],
            "type": 1,
            "status": [1],
            "startTime": starttime,
            "endTime": endtime,
            "page": {
                "pageNum": 1,
                "pageSize": pagesize
            }
        }
        return self.session.post(
            url=self.edupath + "courseAbsent/list",
            json=data
        ).json()

    def company_course(
            self,
            date: str = UsedTime.today,
            teacherids: list = None,
            pagesize: int = 1
    ):
        """
        [教务管理/课表点名/全部课表]
        :param date:
        :param teacherids:
        :param pagesize:
        :return:
        """
        data = {
            "_t_": UsedTime.stamp,
            "date": date,
            "campusIds": self.campus,
            "teacherIds": teacherids,
            "classStatusList": [0],
            "page": {
                "pageNum": 1,
                "pageSize": pagesize
            }
        }
        return self.session.post(
            url=self.edupath + "arrange/getCompanyCourse",
            json=data
        ).json()

    # [工作台][学员][学员卡包]
    def student_card(
            self,
            studentid=None
    ):
        """
        查看学员的课程卡包
        :param studentid: 学生ID
        :return: json数据
        """
        data = {
            "_t_": UsedTime.stamp,
            "studentId": studentid,
            "page": {
                "pageNum": 1,
                "pageSize": 20
            }
        }
        return self.session.post(
            url=self.edupath + "cardInfo/findStudentCard",
            json=data
        ).json()

    # [工作台][学员][就读课程]
    def student_attend_course(
            self,
            studentid: str = None
    ):
        data = {
            "_t_": UsedTime.stamp,
            "studentId": studentid,
            "page": {
                "pageNum": 1,
                "pageSize": 20
            }
        }
        return self.session.post(
            url=self.edupath + "courseStudent/findStudentAttendCourse",
            json=data
        ).json()

    # [工作台][学员][就读课程][出入班记录]
    def operation_record_list(
            self,
            studentid: int = None,
            curriculum_id: int = None,
            campus_ids_index: int = None,
            campus_id: int = None
    ):
        """
        [工作台][学员][就读课程][出入班记录]
        :param campus_id:
        :param campus_ids_index: 实例中选择的校区列表索引，必须从中列表中选择一个。
        :param studentid:
        :param curriculum_id:
        :return:
        """
        if campus_ids_index:
            campus_id = self.campus[campus_ids_index]
        data = {
            "_t_": UsedTime.stamp,
            "campusId": campus_id,
            "studentId": str(studentid),
            "curriculumId": curriculum_id
        }
        return self.session.post(
            url=self.edupath + "student/findOperationRecordList",
            json=data
        ).json()

    # [工作台][班级]
    def class_info_page(
            self,
            classstatus=0,
            curriculumids: list = None,
            teacherids: list = None
    ):
        data = {
            "_t_": UsedTime.stamp,
            "orgTag": 1,
            "campusIds": self.campus,
            "classStatus": classstatus,
            "curriculumIds": curriculumids,
            "teacherIds": teacherids,
            "page": {"pageNum": 1, "pageSize": 500}
        }
        return self.session.post(
            url=self.edupath + "classInfo/page",
            json=data
        ).json()

    def class_info(self, classid: int = None):
        """
        查询指定班级信息
        :param classid: 班级id
        :return:
        """
        return self.session.get(
            url=self.edupath + "classInfo/getClassInfoVo",
            params={"_t_": UsedTime.stamp, "classId": classid}
        ).json()

    def class_student(self, classid: int = None, inout: int = 1):
        """
        查询指定班级的学员
        :param classid:     班级id
        :param inout:       [1]当前在班学员 [2]历史学员
        :return:
        """
        return self.session.get(
            url=self.edupath + "classStudent/findClassStudent",
            params={"_t_": UsedTime.stamp, "classId": classid, "inout": inout}
        ).json()

    def class_arrange(self, classid: int = None):
        """
        查询指定班级排课。
        :param classid: 班级id
        :return:
        """
        return self.session.post(
            url=self.edupath + "arrange/list",
            json={
                "_t_": UsedTime.stamp,
                "classId": classid,
                "isDesc": False,
                "status": None
            }
        ).json()

    def arrange(
            self,
            starttime: str = None,
            endtime: str = None
    ):
        """
        排课管理。
        :param starttime: 查询起始时间
        :param endtime: 查询截止时间
        :return:
        """
        data = {
            "_t_": UsedTime.stamp,
            "campusIds": self.campus,
            "startDate": starttime,
            "endDate": endtime,
            "courseStatusList": [0, 1],
            "displayCompletedClass": False,
            "page": {"pageNum": 1, "pageSize": 500}
        }
        return self.session.post(
            url=self.edupath + "arrange/page",
            json=data
        ).json()

    def curriculum(
            self,
            searchname: str = None,
            haltsalelist: list = None
    ):
        """
        查询所有在开的课程
        :param searchname: 查找关键字。
        :param haltsalelist: 是否在售。0>在售 1>停售
        :return:
        """
        return self.session.post(
            url=self.edupath + "curriculum/pageList",
            json={
                "_t_": UsedTime.stamp,
                "campusIds": self.campus,
                "curriculumName": searchname,
                "haltSaleList": haltsalelist,
                "page": {
                    "pageNum": 1,
                    "pageSize": 500
                }
            }
        ).json()

    def update_curriculum_price_item(
            self,
            searchname: str = None,
            haltsalelist: list = None
    ):
        """
        查询所有在开的课程
        :param searchname: 查找关键字。
        :param haltsalelist: 是否在售。0>在售 1>停售
        :return:
        """
        return self.session.post(
            url=self.edupath + "curriculum/updateCurriculumPriceItem",
            json={
                "_t_": UsedTime.stamp,
                "campusIds": self.campus,
                "curriculumName": searchname,
                "haltSaleList": haltsalelist,
                "page": {
                    "pageNum": 1,
                    "pageSize": 500
                }
            }
        ).json()

    def become_history(
            self,
            studentlist: list
    ):
        """
        设为曾就读学生。
        :param studentlist: 学生ID
        :return:
        """
        return self.session.post(
            url=self.edupath + "student/becomeHistory",
            json={
                "_t_": UsedTime.stamp, "studentIds": studentlist
            }
        ).json()

    def student_suspend_course(
            self,
            student_id: str,
            suspend_course_date: str = UsedTime.today,
            remove_class: int = True
    ):
        """
        设为停课状态。
        :param student_id: 学生ID
        :param suspend_course_date: 停课时间。0000-00-00
        :param remove_class: 是否从班级中移除
        :return:
        """
        return self.session.post(
            url=self.edupath + "student/studentSuspendCourse",
            json={
                "_t_": UsedTime.stamp,
                "recoveryCourseDate": "",
                "extendDays": "",
                "removeClass": remove_class,
                "studentId": student_id,
                "suspendCourseDate": suspend_course_date,
                "type": 0
            }
        ).json()

    def student_list(
            self,
            curriculumids: list = None,
            classids: list = None,
            name: str = "",
            status: list = None,
            class_student_status: int = 0
    ):
        """
        [教务管理/学员]
        列出学生
        :param curriculumids: 课程筛选
        :param classids: 班级筛选
        :param name: 姓名查询关键字
        :param status: 学员状态 0>未收费 1>在读 6>曾就读 7>停课 99>无效学员
        :param class_student_status: 0>不筛选 1>未入班 2>已入班
        :return:
        """
        if status is None:
            status = [1, 7]
        return self.session.post(
            url=self.crmpath + "student/list",
            json={
                "_t_": UsedTime.stamp,
                "name": name,
                "campusIds": self.campus,
                "status": status,
                "intentionStatus": 0,
                "curriculumIds": curriculumids,
                "classIds": classids,
                "classStudentStatus": class_student_status,
                "orgTag": 1,
                "page": {"pageNum": 1, "pageSize": 1000000}
            }
        ).json()

    def student_info(
            self,
            studentid: int = None
    ):
        """
        [教务管理/学员/学员详情]
        查询学员详细信息。
        :param studentid: 学生ID
        :return:
        """
        return self.session.get(
            url=self.crmpath + "student/getContainFace",
            params={"_t_": UsedTime.stamp, "id": studentid, "companyId": 658811}
        ).json()

    def get_teacher_list(
            self,
            querykey: str = None
    ):
        """
        查询老师
        :param querykey: 关键词检索
        :return:
        """
        return self.session.post(
            url=self.crmpath + "teacher/pageList",
            json={
                "_t_": UsedTime.stamp,
                "queryKey": querykey,
                "campusIds": self.campus,
                "statusList": [1],
                "page": {"pageNum": 1, "pageSize": 1000}
            }
        ).json()
