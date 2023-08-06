from .yunxiao import WebOAuth, UsedTime


class Web(WebOAuth):
    def __init__(self, userphone: str, password: str, campus: list = None):
        super().__init__(userphone, password)
        if campus is None:
            self.campus = []
        else:
            self.campus = campus
        self.reportpath = "https://yunxiao.xiaogj.com/api/cs-pc-report/cs-report/reports/"
        self.edupath = "https://yunxiao.xiaogj.com/api/cs-pc-edu/"

    def find_course_sign_charge(
            self,
            starttime: str = None,
            endtime: str = None,
            sort_field: str = "operationTime"
    ):
        """
        查询课消记录
        :param sort_field: 时间筛选模式。 <operationTime> - 操作时间
        :param starttime:
        :param endtime:
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findCourseSignCharge",
            json={
                "_t_": UsedTime.stamp,
                "page": {"pageNum": 1, "pageSize": 10000},
                "campusIds": self.campus,
                "courseStartTime": starttime,
                "courseEndTime": endtime,
                "sort": 1,
                "sortField": sort_field
            }
        ).json()

    def find_order_item_all(
            self,
            starttime: str = UsedTime.yymm01,
            endtime: str = UsedTime.today,
            orderstatus: list = None
    ):
        """
        查询订单明细。
        :param starttime: 起始时间
        :param endtime: 结束时间
        :param orderstatus: 订单状态。
        :return:
        """
        if orderstatus is None:
            orderstatus = [1, 4, 6]
        return self.session.post(
            url=self.reportpath + "findOrderItemAll/page",
            json={
                "_t_": UsedTime.stamp,
                "page": {"pageNum": 1, "pageSize": 10000},
                "campusIds": self.campus,
                "startTime": starttime,
                "endTime": endtime,
                "orderStatusAllList": orderstatus
            }
        ).json()

    def student_course_card(self, page_num: int = 1, page_size: int = 10000):
        """
        取得所有学员的课程卡片。
        :param page_num: 页数。
        :param page_size: 每页记录数。
        :return:
        """
        return self.session.post(
            url=self.reportpath + "studentCourseCard/report",
            json={
                "_t_": UsedTime.stamp,
                "page": {"pageNum": page_num, "pageSize": page_size},
                "campusIds": self.campus,
                "displayHistory": False,
                "remainAmountMin": "1",
                "remainAmountMax": ""
            }
        ).json()

    def find_student_course_amount(self, page_num: int = 1, page_size: int = 10000):
        """
        取得所有学员的课时统计数据。
        :param page_num: 页数。
        :param page_size: 每页记录数。
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findStudentCourseAmount",
            json={
                "_t_": UsedTime.stamp,
                "page": {"pageNum": page_num, "pageSize": page_size},
                "campusIds": self.campus,
                "displayHistory": False,
                "status": [1]
            }
        ).json()

    def find_student_course_fee(
            self,
            display_history: int = False,
            status: list = None,
            student_name: str = None,
            page_num: int = 1,
            page_size: int = 10000
    ):
        """
        取得所有学员的课时统计数据。
        :param student_name: 学员姓名。
        :param status: 学员状态。[0:"未收费"][1:"在读"][7:"停课"]
        :param display_history: 是否显示曾就读。<True:显示><False:不显示>
        :param page_num: 页数。
        :param page_size: 每页记录数。
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findStudentCourseFee",
            json={
                "_t_": UsedTime.stamp,
                "page": {"pageNum": page_num, "pageSize": page_size},
                "campusIds": self.campus,
                "displayHistory": display_history,
                "status": status,
                "studentName": student_name
            }
        ).json()

    def teacher_arrange(
            self,
            teacher_id: int,
            start_date: str = UsedTime.weekstrat,
            end_date: str = UsedTime.weekend,
            page_num: int = 1,
            page_size: int = 9999
    ):
        """
        取得指定老师的课表。
        :param teacher_id: 查询的老师ID
        :param start_date: 起始日期，默认为本周一
        :param end_date: 结束日期，默认为本周日
        :param page_num: 页数。
        :param page_size: 每页记录数。
        :return:
        """
        return self.session.post(
            url=self.edupath + "arrange/page",
            json={
                "_t_": UsedTime.stamp,
                "campusIds": self.campus,
                "startDate": start_date,
                "endDate": end_date,
                "teacherIds": [teacher_id],
                "assistantTeacherIds": [],
                "classRoomIds": [],
                "studentIds": [],
                "reserve": 0,
                "displayCompletedClass": False,
                "courseStatusList": [],
                "page": {"pageNum": page_num, "pageSize": page_size}
            }
        ).json()

    def find_payment_list(
            self,
            pay_start_date: str = UsedTime.weekstrat,
            pay_end_date: str = UsedTime.weekend,
            order_status: int = "",
            group_no: str = "",
            page_num: int = 1,
            page_size: int = 9999
    ):
        """
        收入明细报表。
        :param group_no: 收据编号
        :param pay_start_date: 支付起始时间
        :param pay_end_date: 支付结束时间
        :param order_status: 订单状态 1>已付款 4>已作废
        :param page_num: 页数
        :param page_size: 每页项目数
        :return:
        """
        return self.session.post(
            url=self.reportpath + "findPaymentList",
            json={
                "_t_": UsedTime.stamp,
                "campusIds": self.campus,
                "payType": "",
                "payStartTime": pay_start_date,
                "payEndTime": pay_end_date,
                "orderStatus": order_status,
                "groupNo": group_no,
                "orderStartTime": "",
                "orderEndTime": "",
                "btransactionId": "",
                "aymentAccountCustomIds": [],
                "confirmStatusList": [],
                "revenueType": "",
                "page": {"pageNum": page_num, "pageSize": page_size}
            }
        ).json()

    def find_receipt(
            self,
            order_id: int,
            payment_group_id: int
    ):
        """
        收据。
        :param order_id: 订单 ID
        :param payment_group_id: 支付 ID
        :return:
        """
        return self.session.get(
            url="https://yunxiao.xiaogj.com/api/cs-pc-edu/public/receipt/findReceipt",
            params={
                "orderInfoId": order_id,
                "paymentGroupId": payment_group_id,
                "_t_": UsedTime.stamp
            }
        ).json()

    def snap_info_by_payment_group_id(
            self,
            order_id: int,
            payment_group_id: int
    ):
        """
        收据。
        :param order_id: 订单 ID
        :param payment_group_id: 支付 ID
        :return:
        """
        return self.session.get(
            url="https://yunxiao.xiaogj.com/api/cs-pc-edu/public/receipt/snapInfoByPaymentGroupId",
            params={
                "orderId": order_id,
                "paymentGroupId": payment_group_id,
                "_t_": UsedTime.stamp
            }
        ).json()

    def receipt(
            self,
            order_id: int,
            payment_group_id: int
    ):
        """
        收据。
        :param order_id: 订单 ID
        :param payment_group_id: 支付 ID
        :return: Respose 数据
        """
        return self.session.get(
            url="https://yunxiao.xiaogj.com/web/teacher/#/receipt",
            params={
                "orderId": order_id,
                "paymentGroupId": payment_group_id
            }
        )


if __name__ == "__main__":
    pass
