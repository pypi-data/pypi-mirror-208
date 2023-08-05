import base64
import datetime
import json

import requests
import xlrd2

import pyDes
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.db import transaction
from django.http import JsonResponse, HttpResponse
import django_filters as filters
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from base_system.models import Hospital, Office, Doctor, PositionTitle, User, ExtraGroup, InspectionDictionaries, \
    ExaminationDictionaries, DrugDirectory, PharmacyManagement, ExpenseStandard, ApiInfo, \
    DrugPreparationType, DrugType, DrugCategory, PharmacyDrug, InspectionType, ExaminationType
from base_system.serializers import UserSerializer, \
    PasswordSerializer, InspectionDictionariesSerializer, ExaminationDictionariesSerializer, \
    PharmacyManagementSerializer, DrugDirectorySerializer, \
    ApiInfoSerializer, InspectionTypeSerializer, ExaminationTypeSerializer
from base_system.serializers import PermissionSerializer
from django.conf import settings as django_settings


import xlrd as xlrd
from xlrd import xldate_as_tuple
import re
import pinyin


def register(request):
    """注册详情页"""
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        phone = data['phone']
        username = data['username']  # 工号
        user = User.objects.filter(username=username).first()

        if user and user.is_active is False:
            # 用户在所给的数据中验证通过，保存密码并激活
            user.is_active = True
            user.set_password('123456')
            user.phone = phone
            user.save()
            return JsonResponse({'data': True})
        else:
            return JsonResponse({'data': '该工号错误或者已被注册，请确认工号'})


def change_password(request):
    """修改用户信息"""
    data = json.loads(request.body.decode('utf-8'))
    print(data)
    user_id = data['user_id']
    password = data['password']
    user = User.objects.get(id=user_id)

    if password:
        user.set_password(password)
        user.error_times = 0
        user.last_change_time = datetime.datetime.now()
        user.is_change_pwd = True
        user.save()
        res = {'data': True}
        return JsonResponse(res)


class PermissionsView(ListAPIView):
    """
    获取当前用户前端权限
    """
    serializer_class = PermissionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        """
        得到角色权限
        """
        # defaultgroup = self.request.user.get_default_group
        groups = self.request.user.groups.all()
        if groups:
            permissions = Permission.objects.filter(group__in=groups).distinct()
        else:
            permissions = Permission.objects.none()
        return permissions


class OverrideUserAuthentication(ModelBackend):
    """
    重写用户验证
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, request, username=None, password=None, appss=None, **kwargs):
        try:
            key = 'K3bDD6Zytur5RLCJ'
            pdes2 = PyDES3(key)
            decrypt_username = pdes2.decrypt(username)
            decrypt_password = pdes2.decrypt(password)
            user = User.objects.get(username=decrypt_username)
        except Exception as e:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            return None
        else:
            if user.check_password(decrypt_password):
                return user


'''
# 随机生成密钥
def __createkey(request):
    N = 16
    newkey = ''.join(secrets.choice(string.ascii_letters+string.digits) for _ in range(N))
    base64.b64decode(newkey.encode())
    return JsonResponse({'newkey': newkey})
'''


class PyDES3():
    def __init__(self, key):
        """
        三重DES加密、对称加密。py2下不可用
        :param key: 密钥
        """
        self.cryptor = pyDes.triple_des(key, padmode=pyDes.PAD_PKCS5)

    def encrypt(self, text):
        """
        加密
        :param text:
        :return:
        """
        x = self.cryptor.encrypt(text.encode())
        return base64.standard_b64encode(x).decode()

    def decrypt(self, text):
        """
        解密
        :param text:
        :return:
        """
        x = base64.standard_b64decode(text.encode())
        x = self.cryptor.decrypt(x)
        return x.decode()


@transaction.atomic
def import_position_title(request):
    """导入excel表数据"""
    created_user = request.POST.get('created_user')
    excel_file = request.FILES.get('excel_file', '')  # 获取前端上传的文件
    file_type = excel_file.name.split('.')[1].split('"')[0]  # 拿到文件后缀
    # file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
    data_list = []
    # PositionTitle
    if file_type in ['xlsx', 'xls']:  # 支持这两种文件格式
        # 打开工作文件
        try:
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read(), ragged_rows=True)
            sheets = data.sheets()
            for sheet in sheets:
                rows = sheet.nrows  # 总行数
                for row in range(2, rows):  # 从1开始是为了去掉表头
                    row_values = sheet.row_values(row)  # 每一行的数据
                    if row_values:
                        # codenum = row_values[0]  # 匹配编码
                        ctype = sheet.cell(row, 0).ctype  # 表格的数据类型
                        codenum = sheet.cell_value(row, 0)
                        if ctype == 2 and codenum % 1 == 0:  # 如果是整形
                            codenum = int(codenum)
                        name = row_values[1]
                        hospital_name = row_values[2]
                        hospital = Hospital.objects.get(name=hospital_name).id
                        created_time = row_values[3]
                        created_by = row_values[4]
                        positiontitle = PositionTitle.objects.filter(codenum=codenum)
                        if positiontitle:
                            positiontitle.update(**{"codenum": codenum,
                                                    "name": name,
                                                    "hospital": hospital,
                                                    "created_time": created_time,
                                                    "created_by": created_by,
                                                    })
                        else:
                            positiontitle.create(**{"codenum": codenum,
                                                    "name": name,
                                                    "hospital": hospital,
                                                    "created_time": created_time,
                                                    "created_by": created_by,
                                                    })
                        excel_data = {
                            "codenum": codenum,
                            "name": name,
                            "hospital": hospital,
                            "created_time": created_time,
                            "created_by": created_by,
                        }
                        data_list.append(excel_data)
        except Exception as e:
            raise e

    if data_list:
        res = {"data": data_list}
    else:
        res = {"data": "文件内容格式有误，请检查内容格式是否正确！"}
    return JsonResponse(res)


class UserFilter(filters.FilterSet):
    # company_id = filters.NumberFilter(field_name="company_id")
    # department_id = filters.NumberFilter(field_name="department_id")
    # job_id = filters.NumberFilter(field_name="job_id")
    gender = filters.NumberFilter(field_name="gender")
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    avatar_url = filters.CharFilter(field_name="avatar_url")

    class Meta:
        model = User
        fields = "__all__"


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    filterset_class = UserFilter
    filter_fields = "__all__"

    @action(methods=["PUT"], detail=True)
    def change_password(self, request, pk):
        # 更改密码
        serializer = PasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        password = serializer.data.get("password")
        user = self.get_object()
        user.set_password(password)
        user.last_change_time = datetime.datetime.now()
        user.error_times = 0
        user.is_change_pwd = False
        user.save()

        return Response(data={"message": "修改成功"}, status=status.HTTP_205_RESET_CONTENT)


class InspectionTypeViewSet(ModelViewSet):
    """检查字典"""
    queryset = InspectionType.objects.filter(parent=None)
    serializer_class = InspectionTypeSerializer
    pagination_class = None


class InspectionDictFilter(filters.FilterSet):
    project_code = filters.CharFilter(field_name="project_code", lookup_expr="icontains")
    project_name = filters.CharFilter(field_name="project_name", lookup_expr="icontains")
    hospital_code = filters.CharFilter(field_name="hospital_code", lookup_expr="icontains")
    office_code = filters.CharFilter(field_name="office_code", lookup_expr="icontains")
    distinguish = filters.CharFilter(field_name="distinguish", lookup_expr="icontains")

    class Meta:
        model = InspectionDictionaries
        fields = "__all__"


class InspectionDictionariesViewSet(ModelViewSet):
    """检查字典"""
    queryset = InspectionDictionaries.objects.all().order_by('-id')
    serializer_class = InspectionDictionariesSerializer
    # filter_fields = "__all__"
    filterset_class = InspectionDictFilter

    # 导入json文件数据
    # def create(self, request, *args, **kwargs):
    #     with open('spdic.json', encoding='utf-8') as a:
    #         # 读取文件
    #         result = json.load(a)
    #         data = result['content']['data']['itemsrvinfos']['itemsrvinfo']
    #         for res in data:
    #             print(res)
    #             InspectionDictionaries.objects.create(
    #                 project_code=res['code_srv'],
    #                 project_name=res['name_srv'],
    #                 hospital_code=res['code_org'],
    #                 project_fees=res['price'],
    #                 code_srvtp=res['code_srvtp'],
    #                 name_srvtp=res['name_srvtp'],
    #             )
    #     return Response({"data": data})


class ExaminationTypeViewSet(ModelViewSet):
    """检查字典"""
    queryset = ExaminationType.objects.filter(parent=None)
    serializer_class = ExaminationTypeSerializer
    pagination_class = None


class ExaminationDictFilter(filters.FilterSet):
    project_code = filters.CharFilter(field_name="project_code", lookup_expr="icontains")
    project_name = filters.CharFilter(field_name="project_name", lookup_expr="icontains")
    hospital_code = filters.CharFilter(field_name="hospital_code", lookup_expr="icontains")
    office_code = filters.CharFilter(field_name="office_code", lookup_expr="icontains")
    distinguish = filters.CharFilter(field_name="distinguish", lookup_expr="icontains")

    class Meta:
        model = ExaminationDictionaries
        fields = "__all__"


class ExaminationDictionariesViewSet(ModelViewSet):
    """检验字典"""
    queryset = ExaminationDictionaries.objects.all().order_by('-id')
    serializer_class = ExaminationDictionariesSerializer
    # filter_fields = "__all__"
    filterset_class = ExaminationDictFilter

    # 导入json文件数据
    # def create(self, request, *args, **kwargs):
    #     with open('response.json', encoding='utf-8') as a:
    #         # 读取文件
    #         result = json.load(a)
    #         data = result['content']['data']['itemsrvinfos']['itemsrvinfo']
    #         for res in data:
    #             print(res)
    #             sp_dic = InspectionDictionaries.objects.filter(project_code=res['code_srv'])
    #             if not sp_dic:
    #                 ExaminationDictionaries.objects.create(
    #                     project_code=res['code_srv'],
    #                     project_name=res['name_srv'],
    #                     hospital_code=res['code_org'],
    #                     project_fees=res.get('price'),
    #                     code_srvtp=res['code_srvtp'],
    #                     name_srvtp=res['name_srvtp'],
    #                 )
    #     return Response({"data": data})


class PharmacyManagementViewSet(ModelViewSet):
    """药房管理"""
    queryset = PharmacyManagement.objects.all().order_by('-id')
    serializer_class = PharmacyManagementSerializer
    filter_fields = "__all__"


@transaction.atomic
def import_office(request):
    """导入excel表科室数据"""
    created_user = request.POST.get('created_user')
    excel_file = request.FILES.get('excel_file', '')  # 获取前端上传的文件
    file_type = excel_file.name.split('.')[1].split('"')[0]  # 拿到文件后缀
    # file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
    data_list = []
    # PositionTitle
    if file_type in ['xlsx', 'xls']:  # 支持这两种文件格式
        # 打开工作文件
        try:
            data = xlrd2.open_workbook(filename=None, file_contents=excel_file.read(), ragged_rows=True)
            sheets = data.sheets()
            for sheet in sheets:
                rows = sheet.nrows  # 总行数
                for row in range(2, rows):  # 从1开始是为了去掉表头
                    row_values = sheet.row_values(row)  # 每一行的数据
                    if row_values:
                        # codenum = row_values[0]  # 匹配编码
                        ctype = sheet.cell(row, 0).ctype  # 表格的数据类型
                        codenum = sheet.cell_value(row, 0)
                        if ctype == 2 and codenum % 1 == 0:  # 如果是整形
                            codenum = int(codenum)
                        name = row_values[1]
                        hospital_name = row_values[2]
                        hospital = Hospital.objects.get(name=hospital_name).id
                        parent_name = row_values[3]
                        if parent_name:
                            parent = Office.objects.get(name=parent_name).id
                        else:
                            parent = None
                        address = row_values[4]
                        phone = row_values[5]
                        introduce = row_values[6]
                        # created_time = row_values[7]
                        # # created_by = row_values[8]
                        office = Office.objects.filter(codenum=codenum)
                        if office:
                            office.update(**{"codenum": codenum,
                                             "name": name,
                                             "hospital_id": hospital,
                                             "parent_id": parent,
                                             "address": address,
                                             "phone": phone,
                                             "introduce": introduce,
                                             "created_time": datetime.datetime.now(),
                                             "created_by": created_user,
                                             })
                        else:
                            office.create(**{"codenum": codenum,
                                             "name": name,
                                             "hospital_id": hospital,
                                             "parent_id": parent,
                                             "address": address,
                                             "phone": phone,
                                             "introduce": introduce,
                                             "created_time": datetime.datetime.now(),
                                             "created_by": created_user,
                                             })
                        excel_data = {
                            "codenum": codenum,
                            "name": name,
                            "hospital": hospital,
                            "parent": parent,
                            "address": address,
                            "phone": phone,
                            "introduce": introduce,
                            "created_time": datetime.datetime.now(),
                            "created_by": created_user,
                        }
                        data_list.append(excel_data)
        except Exception as e:
            raise e

    if data_list:
        res = {"data": data_list}
    else:
        res = {"data": "文件内容格式有误，请检查内容格式是否正确！"}
    return JsonResponse(res)


@transaction.atomic
def import_doctor(request):
    """导入excel表医生数据"""
    created_user = request.POST.get('created_user')
    excel_file = request.FILES.get('excel_file', '')  # 获取前端上传的文件
    file_type = excel_file.name.split('.')[1].split('"')[0]  # 拿到文件后缀
    # file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
    data_list = []
    # PositionTitle
    if file_type in ['xlsx', 'xls']:  # 支持这两种文件格式
        # 打开工作文件
        try:
            data = xlrd2.open_workbook(filename=None, file_contents=excel_file.read(), ragged_rows=True)
            sheets = data.sheets()
            for sheet in sheets:
                rows = sheet.nrows  # 总行数
                for row in range(2, rows):  # 从1开始是为了去掉表头
                    row_values = sheet.row_values(row)  # 每一行的数据
                    if row_values:
                        # codenum = row_values[0]  # 匹配编码
                        ctype = sheet.cell(row, 2).ctype  # 表格的数据类型
                        job_number = sheet.cell_value(row, 2)
                        if ctype == 2 and job_number % 1 == 0:  # 如果是整形
                            job_number = int(job_number)
                        name = row_values[3]
                        hospital_name = row_values[0]
                        hospital = Hospital.objects.filter(name=hospital_name).first()
                        if hospital:
                            hospital_id = hospital.id
                        else:
                            excel_data = {
                                "job_number": job_number,
                                "name": name,
                                "hospital": hospital_name,
                                "office_name": None,
                                "doc_rank_name": None,
                                "describe": None,
                                "is_online_consult": None,
                                "created_time": None,
                                "created_by": created_user,
                                "msg": "医院查询有误，请检查！！！",
                            }
                            data_list.append(excel_data)
                            continue

                        office_name = row_values[1]
                        if office_name:
                            office = Office.objects.filter(name=office_name, hospital_id=hospital_id).first()
                            if office:
                                office_id = office.id
                            else:
                                excel_data = {
                                    "job_number": job_number,
                                    "name": name,
                                    "hospital": hospital_name,
                                    "office_name": office_name,
                                    "doc_rank_name": None,
                                    "is_online_consult": None,
                                    "created_time": None,
                                    "created_by": created_user,
                                    "msg": "该条记录医院下的科室查询有误，请检查！！！已自动跳过该条记录的导入",
                                }
                                data_list.append(excel_data)
                                continue
                        gender = row_values[4]
                        if gender:
                            if gender == '男':
                                gender_vlue = '1'
                            elif gender == '女':
                                gender_vlue = '0'
                            else:
                                gender_vlue = None
                        phone = row_values[5]
                        if phone:
                            phone_int = int(phone)
                        idnum = row_values[6]
                        if idnum:
                            idnum_int = int(idnum)
                        doc_rank_name = row_values[7]
                        if doc_rank_name:
                            doc_rank = PositionTitle.objects.filter(name=doc_rank_name, hospital_id=hospital_id).first()
                            if doc_rank:
                                doc_rank_id = doc_rank.id
                            else:
                                excel_data = {
                                    "job_number": job_number,
                                    "name": name,
                                    "hospital": hospital_name,
                                    "office_name": office_name,
                                    "doc_rank_name": doc_rank_name,
                                    "is_online_consult": None,
                                    "created_time": None,
                                    "created_by": created_user,
                                    "msg": "该条记录医院下的职称查询有误，请检查！！！已自动跳过该条记录的导入",
                                }
                                data_list.append(excel_data)
                                continue
                        describe = row_values[8]
                        is_online_consult = row_values[9]
                        if is_online_consult == '是':
                            is_true = True
                        else:
                            is_true = False
                        doctor = Doctor.objects.filter(job_number=job_number)
                        if doctor:
                            doctor.update(**{"job_number": job_number,
                                             "name": name,
                                             "hospital_id": hospital_id,
                                             "office_id": office_id,
                                             "doc_rank_id": doc_rank_id,
                                             "position": doc_rank.name,
                                             "describe": describe,
                                             "gender": gender_vlue,
                                             "phone": phone_int,
                                             "idnum": idnum_int,
                                             "is_online_consult": is_true,
                                             "updated_time": datetime.datetime.now(),
                                             "created_by": created_user,
                                             })
                        else:
                            doctor1 = doctor.create(**{"job_number": job_number,
                                                       "name": name,
                                                       "hospital_id": hospital_id,
                                                       "office_id": office_id,
                                                       "doc_rank_id": doc_rank_id,
                                                       "position": doc_rank.name,
                                                       "describe": describe,
                                                       "gender": gender_vlue,
                                                       "phone": phone_int,
                                                       "idnum": idnum_int,
                                                       "is_online_consult": is_true,
                                                       "created_time": datetime.datetime.now(),
                                                       "created_by": created_user,
                                                       })
                            # 为其创建账号，增加其费用标准
                            User.objects.create(**{
                                "name": name,
                                "username": job_number,
                                "email": '111@qq.com',
                                'password': make_password('123456'),  # 初始密码为123456
                                "doctor_id": doctor1.id,
                                "hospital_id": hospital_id,
                                "office_id": office_id,
                                "user_rank_id": doc_rank_id,
                                "gender": gender_vlue,
                                "phone": phone_int,
                                "idcardnum": idnum_int,
                                # "created_time": datetime.datetime.now(),
                                # "updated_time": datetime.datetime.now(),
                                "created_by": created_user,
                            })
                            if is_true:  # 仅在允许互联网接诊时调用以下逻辑
                                Initial_hospital = get_pinyin_initials(hospital_name)  # 医院首字母
                                Initial_doc_rank = get_pinyin_initials(doc_rank_name)  # 职称首字母
                                combination_hd1 = f'1_{Initial_hospital}_{Initial_doc_rank}'  # '1_WYRMYY_FZRYS'
                                es_1 = ExpenseStandard.objects.filter(standard_code=combination_hd1,
                                                                      hospital_id=hospital_id).first()
                                combination_hd2 = f'2_{Initial_hospital}_{Initial_doc_rank}'
                                es_2 = ExpenseStandard.objects.filter(standard_code=combination_hd2,
                                                                      hospital_id=hospital_id).first()
                                combination_hd3 = f'3_{Initial_hospital}_{Initial_doc_rank}'
                                es_3 = ExpenseStandard.objects.filter(standard_code=combination_hd3,
                                                                      hospital_id=hospital_id).first()
                                combination_hd4 = f'4_{Initial_hospital}_{Initial_doc_rank}'
                                es_4 = ExpenseStandard.objects.filter(standard_code=combination_hd4,
                                                                      hospital_id=hospital_id).first()
                                if es_1 or es_2 or es_3 or es_4:  # 四个标准中至少存在一条存在，否则跳过为其增加费用标准
                                    es_list = []
                                    es_list.append(es_1)
                                    es_list.append(es_2)
                                    es_list.append(es_3)
                                    es_list.append(es_4)
                                    for es in es_list:
                                        es.doctors.add(doctor1)
                                else:
                                    excel_data = {
                                        "job_number": job_number,
                                        "name": name,
                                        "hospital": hospital_name,
                                        "office_name": office_name,
                                        "doc_rank_name": doc_rank_name,
                                        "is_online_consult": is_online_consult,
                                        "created_time": datetime.datetime.now(),
                                        "created_by": created_user,
                                        "msg": "成功！但是费用标准查询出错！！！请手动为该医生添加费用标准！！！",
                                    }
                                    data_list.append(excel_data)
                                    continue
                        excel_data = {
                            "job_number": job_number,
                            "name": name,
                            "hospital": hospital_name,
                            "office_name": office_name,
                            "doc_rank_name": doc_rank_name,
                            "is_online_consult": is_online_consult,
                            "created_time": datetime.datetime.now(),
                            "created_by": created_user,
                            "msg": "成功！！！",
                        }
                        data_list.append(excel_data)
        except Exception as e:
            raise e

    if data_list:
        res = {"data": data_list}
    else:
        res = {"data": "文件内容格式有误，请检查内容格式是否正确！"}
    return JsonResponse(res)


# 获取中文姓名的拼音首字母
def get_pinyin_initials(name):
    samplename = pinyin.get_initial(name, delimiter="").upper()
    return samplename


#
# # 示例
# name = "张三"
# initials = get_pinyin_initials(name)
# print(initials)  # "ZS"


class DrugDirectoryFilter(filters.FilterSet):
    drug_code = filters.CharFilter(field_name="drug_code", lookup_expr="icontains")
    drug_name = filters.CharFilter(field_name="drug_name", lookup_expr="icontains")
    specification = filters.CharFilter(field_name="standards", lookup_expr="icontains")
    measure_unit = filters.CharFilter(field_name="measure_unit", lookup_expr="icontains")
    preparation_type = filters.CharFilter(field_name="preparation_type__name", lookup_expr="icontains")
    category = filters.CharFilter(field_name="category__name", lookup_expr="icontains")
    drug_type = filters.CharFilter(field_name="drug_type__name", lookup_expr="icontains")
    unit_dose = filters.CharFilter(field_name="unit_dose", lookup_expr="icontains")
    stock_left = filters.CharFilter(field_name="stock_left", lookup_expr="icontains")
    stock_unit = filters.CharFilter(field_name="stock_unit", lookup_expr="icontains")
    mic = filters.CharFilter(field_name="mic", lookup_expr="icontains")
    rcc_category = filters.CharFilter(field_name="rcc_category", lookup_expr="icontains")
    is_essential = filters.BooleanFilter(field_name="is_essential")
    hr_level = filters.CharFilter(field_name="hr_level", lookup_expr="icontains")
    gb_code = filters.CharFilter(field_name="gb_code", lookup_expr="icontains")
    gb_name = filters.CharFilter(field_name="gb_name", lookup_expr="icontains")
    origin_place = filters.CharFilter(field_name="origin_place", lookup_expr="icontains")
    manufacturer = filters.CharFilter(field_name="manufacturer", lookup_expr="icontains")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = DrugDirectory
        fields = "__all__"


def if_contain_symbol(keyword):
    symbols = "~!@#$%^&*()+-*/<>,.[]\/|'`、"
    for symbol in symbols:
        if symbol in keyword:
            return True
    else:
        return False


class DrugDirectoryViewSet(ModelViewSet):
    queryset = DrugDirectory.objects.all().order_by('-id')
    serializer_class = DrugDirectorySerializer
    filterset_class = DrugDirectoryFilter

    def list(self, request, *args, **kwargs):
        hospital_code = self.request.query_params.get('hospital_code')
        drug_name = self.request.query_params.get('drug_name')
        page = self.request.query_params.get('page')
        page_size = self.request.query_params.get('page_size')
        symbol = if_contain_symbol(drug_name)
        if symbol:
            return Response(data='参数错误！', status=400)
        flag = 1
        if flag:
            in_data = {
                "hospital_code": hospital_code,
                "Code_field": "Name",
                "Code_oper": "03",
                "Value_field": drug_name,
                "Pageindex": page,
                "Pagesize": page_size
            }
            api_info = ApiInfo()
            rest = api_info.writeback(in_data, 'YPDACX')
            if rest['code'] == 200:
                print("药品查询成功")
                rest_data = rest['content']['data']
                page_info = rest['content']['pageinfo']
                rest_dict = {"count": page_info['recordscount'], "results": rest_data}
                return Response(rest_dict)
            else:
                print("药品查询失败")
                return Response(rest)
        else:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)


class ApiInfoViewSet(ModelViewSet):
    queryset = ApiInfo.objects.all().order_by('-id')
    serializer_class = ApiInfoSerializer


@transaction.atomic
def import_inspection_dictionaries(request):
    """导入检查字典excel表数据"""
    created_user = request.POST.get('created_user')
    excel_file = request.FILES.get('excel_file', '')  # 获取前端上传的文件
    file_type = excel_file.name.split('.')[1].split('"')[0]  # 拿到文件后缀
    # file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
    data_list = []
    # PositionTitle
    if file_type in ['xlsx', 'xls']:  # 支持这两种文件格式
        # 打开工作文件
        try:
            data = xlrd2.open_workbook(filename=None, file_contents=excel_file.read(), ragged_rows=True)
            sheets = data.sheets()
            for sheet in sheets:
                rows = sheet.nrows  # 总行数
                for row in range(2, rows):  # 从1开始是为了去掉表头
                    row_values = sheet.row_values(row)  # 每一行的数据
                    if row_values:
                        # codenum = row_values[0]  # 匹配编码
                        ctype = sheet.cell(row, 0).ctype  # 表格的数据类型
                        project_code = int(sheet.cell_value(row, 0))
                        project_name = row_values[1]
                        hospital_name = row_values[2]
                        hospital = Hospital.objects.filter(name=hospital_name).first()
                        hospital_code = hospital.codenum

                        office_name = row_values[3]
                        office = Office.objects.filter(hospital_id=hospital.id, name=office_name).first()
                        office_code = office.codenum
                        project_fees = row_values[4]
                        code_srvtp = int(row_values[5])
                        name_srvtp = row_values[6]
                        remarks = row_values[7]
                        ins_dictionaries = InspectionDictionaries.objects.filter(project_code=project_code).first()
                        if ins_dictionaries:
                            ins_dictionaries.update(**{"project_code": project_code,
                                                       "project_name": project_name,
                                                       "hospital_code": hospital_code,
                                                       "office_code": office_code,
                                                       "project_fees": project_fees,
                                                       "code_srvtp": code_srvtp,
                                                       "name_srvtp": name_srvtp,
                                                       "remarks": remarks,
                                                       })
                        else:
                            InspectionDictionaries.objects.create(**{"project_code": project_code,
                                                                     "project_name": project_name,
                                                                     "hospital_code": hospital_code,
                                                                     "office_code": office_code,
                                                                     "project_fees": project_fees,
                                                                     "code_srvtp": code_srvtp,
                                                                     "name_srvtp": name_srvtp,
                                                                     "remarks": remarks,
                                                                     })
                        excel_data = {
                            "project_code": project_code,
                            "project_name": project_name,
                            "hospital_name": hospital_name,
                            "office_name": office_name,
                            "project_fees": project_fees,
                            "code_srvtp": code_srvtp,
                            "name_srvtp": name_srvtp,
                            "remarks": remarks,
                        }
                        data_list.append(excel_data)
        except Exception as e:
            raise e

    if data_list:
        res = {"data": data_list}
    else:
        res = {"data": "文件内容格式有误，请检查内容格式是否正确！"}
    return JsonResponse(res)


@transaction.atomic
def import_examination_dictionaries(request):
    """导入检验字典excel表数据"""
    created_user = request.POST.get('created_user')
    excel_file = request.FILES.get('excel_file', '')  # 获取前端上传的文件
    file_type = excel_file.name.split('.')[1].split('"')[0]  # 拿到文件后缀
    # file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
    data_list = []
    # PositionTitle
    if file_type in ['xlsx', 'xls']:  # 支持这两种文件格式
        # 打开工作文件
        try:
            data = xlrd2.open_workbook(filename=None, file_contents=excel_file.read(), ragged_rows=True)
            sheets = data.sheets()
            for sheet in sheets:
                rows = sheet.nrows  # 总行数
                for row in range(2, rows):  # 从1开始是为了去掉表头
                    row_values = sheet.row_values(row)  # 每一行的数据
                    if row_values:
                        # codenum = row_values[0]  # 匹配编码
                        ctype = sheet.cell(row, 0).ctype  # 表格的数据类型
                        project_code = int(sheet.cell_value(row, 0))
                        project_name = row_values[1]
                        hospital_name = row_values[2]
                        hospital = Hospital.objects.filter(name=hospital_name).first()
                        hospital_code = hospital.codenum

                        office_name = row_values[3]
                        office = Office.objects.filter(hospital_id=hospital.id, name=office_name).first()
                        office_code = office.codenum
                        project_fees = row_values[4]
                        code_srvtp = int(row_values[5])
                        name_srvtp = row_values[6]
                        remarks = row_values[7]
                        exa_dictionaries = ExaminationDictionaries.objects.filter(project_code=project_code).first()
                        if exa_dictionaries:
                            exa_dictionaries.update(**{"project_code": project_code,
                                                       "project_name": project_name,
                                                       "hospital_code": hospital_code,
                                                       "office_code": office_code,
                                                       "project_fees": project_fees,
                                                       "code_srvtp": code_srvtp,
                                                       "name_srvtp": name_srvtp,
                                                       "remarks": remarks,
                                                       })
                        else:
                            ExaminationDictionaries.objects.create(**{"project_code": project_code,
                                                                      "project_name": project_name,
                                                                      "hospital_code": hospital_code,
                                                                      "office_code": office_code,
                                                                      "project_fees": project_fees,
                                                                      "code_srvtp": code_srvtp,
                                                                      "name_srvtp": name_srvtp,
                                                                      "remarks": remarks,
                                                                      })
                        excel_data = {
                            "project_code": project_code,
                            "project_name": project_name,
                            "hospital_name": hospital_name,
                            "office_name": office_name,
                            "project_fees": project_fees,
                            "code_srvtp": code_srvtp,
                            "name_srvtp": name_srvtp,
                            "remarks": remarks,
                        }
                        data_list.append(excel_data)
        except Exception as e:
            raise e

    if data_list:
        res = {"data": data_list}
    else:
        res = {"data": "文件内容格式有误，请检查内容格式是否正确！"}
    return JsonResponse(res)


@transaction.atomic
def import_drug_directory(request):
    """导入药品目录excel表数据"""
    created_user = request.POST.get('created_user')
    excel_file = request.FILES.get('excel_file', '')  # 获取前端上传的文件
    file_type = excel_file.name.split('.')[1].split('"')[0]  # 拿到文件后缀
    # file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
    data_list = []
    # PositionTitle
    if file_type in ['xlsx', 'xls']:  # 支持这两种文件格式
        # 打开工作文件
        try:
            data = xlrd2.open_workbook(filename=None, file_contents=excel_file.read(), ragged_rows=True)
            sheets = data.sheets()
            for sheet in sheets:
                rows = sheet.nrows  # 总行数
                for row in range(2, rows):  # 从1开始是为了去掉表头
                    row_values = sheet.row_values(row)  # 每一行的数据
                    if row_values:
                        # codenum = row_values[0]  # 匹配编码
                        ctype = sheet.cell(row, 0).ctype  # 表格的数据类型
                        drug_code = int(sheet.cell_value(row, 0))
                        drug_name = row_values[1]
                        standards = row_values[2]
                        units = row_values[3]
                        preparation_type_name = row_values[4]
                        preparation_type = DrugPreparationType.objects.filter(type_name=preparation_type_name).first()
                        drug_type_name = row_values[5]
                        drug_type = DrugType.objects.filter(name=drug_type_name).first()
                        category_name = row_values[6]
                        category = DrugCategory.objects.filter(category_name=category_name).first()
                        origin_place = row_values[7]
                        manufacturer = row_values[8]
                        unit_dose = row_values[9]
                        measure_unit = row_values[10]
                        stock_left = row_values[11]
                        stock_unit = row_values[12]
                        mic = row_values[13]
                        rcc_category = row_values[14]
                        is_essential_str = row_values[15]
                        if is_essential_str == '是':
                            is_essential = True
                        else:
                            is_essential = False
                        hr_level = row_values[16]
                        gb_code = row_values[17]
                        gb_name = row_values[18]
                        drug_directory = DrugDirectory.objects.filter(drug_code=drug_code)
                        if drug_directory:
                            drug_directory.update(**{"drug_code": drug_code,
                                                     'drug_name': drug_name,
                                                     'standards': standards,
                                                     'units': units,
                                                     'preparation_type': preparation_type.id,
                                                     'drug_type': drug_type.id,
                                                     'category': category.id,
                                                     'origin_place': origin_place,
                                                     'manufacturer': manufacturer,
                                                     'unit_dose': unit_dose,
                                                     'measure_unit': measure_unit,
                                                     'stock_left': stock_left,
                                                     'stock_unit': stock_unit,
                                                     'mic': mic,
                                                     'rcc_category': rcc_category,
                                                     'is_essential': is_essential,
                                                     'hr_level': hr_level,
                                                     'gb_code': gb_code,
                                                     'gb_name': gb_name,
                                                     })
                        else:
                            DrugDirectory.objects.create(**{"drug_code": drug_code,
                                                            'drug_name': drug_name,
                                                            'standards': standards,
                                                            'units': units,
                                                            'preparation_type': preparation_type,
                                                            'drug_type': drug_type,
                                                            'category': category,
                                                            'origin_place': origin_place,
                                                            'manufacturer': manufacturer,
                                                            'unit_dose': unit_dose,
                                                            'measure_unit': measure_unit,
                                                            'stock_left': stock_left,
                                                            'stock_unit': stock_unit,
                                                            'mic': mic,
                                                            'rcc_category': rcc_category,
                                                            'is_essential': is_essential,
                                                            'hr_level': hr_level,
                                                            'gb_code': gb_code,
                                                            'gb_name': gb_name,
                                                            })
                        excel_data = {
                            "drug_code": drug_code,
                            'drug_name': drug_name,
                            'standards': standards,
                            'units': units,
                            'preparation_type_name': preparation_type_name,
                            'drug_type_name': drug_type_name,
                            'category_name': category_name,
                            'origin_place': origin_place,
                            'manufacturer': manufacturer,
                            'unit_dose': unit_dose,
                            'measure_unit': measure_unit,
                            'stock_left': stock_left,
                            'stock_unit': stock_unit,
                            'mic': mic,
                            'rcc_category': rcc_category,
                            'is_essential': is_essential_str,
                            'hr_level': hr_level,
                            'gb_code': gb_code,
                            'gb_name': gb_name,
                        }
                        data_list.append(excel_data)
        except Exception as e:
            raise e

    if data_list:
        res = {"data": data_list}
    else:
        res = {"data": "文件内容格式有误，请检查内容格式是否正确！"}
    return JsonResponse(res)


@transaction.atomic
def import_pharmacy_drug(request):
    """导入药房药品excel表数据"""
    created_user = request.POST.get('created_user')
    excel_file = request.FILES.get('excel_file', '')  # 获取前端上传的文件
    file_type = excel_file.name.split('.')[1].split('"')[0]  # 拿到文件后缀
    # file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
    data_list = []
    # PositionTitle
    if file_type in ['xlsx', 'xls']:  # 支持这两种文件格式
        # 打开工作文件
        try:
            data = xlrd2.open_workbook(filename=None, file_contents=excel_file.read(), ragged_rows=True)
            sheets = data.sheets()
            for sheet in sheets:
                rows = sheet.nrows  # 总行数
                for row in range(2, rows):  # 从1开始是为了去掉表头
                    row_values = sheet.row_values(row)  # 每一行的数据
                    if row_values:
                        # codenum = row_values[0]  # 匹配编码
                        ctype = sheet.cell(row, 0).ctype  # 表格的数据类型
                        pharmacy_name = sheet.cell_value(row, 0)
                        pharmacy_management = PharmacyManagement.objects.filter(pharmacy_name=pharmacy_name).first()
                        drug_code = row_values[1]
                        drug_name = row_values[2]
                        standards = row_values[3]
                        preparation_type_name = row_values[4]
                        preparation_type = DrugPreparationType.objects.filter(type_name=preparation_type_name).first()
                        drug_type_name = row_values[5]
                        drug_type = DrugType.objects.filter(name=drug_type_name).first()
                        category_name = row_values[6]
                        category = DrugCategory.objects.filter(category_name=category_name).first()
                        origin_place = row_values[7]
                        manufacturer = row_values[8]
                        valid_date_str = row_values[9]
                        valid_date = datetime.datetime.strptime(valid_date_str, '%Y-%m-%d')
                        inventory_quantity = row_values[10]
                        measurement_unit = row_values[11]
                        cost_unit_price = row_values[12]
                        cost_amount = row_values[13]
                        retail_unit_price = row_values[14]
                        is_active_str = row_values[16]
                        if is_active_str == '是':
                            is_active = True
                        else:
                            is_active = False
                        retail_amount = row_values[15]
                        pharmacy_drug = PharmacyDrug.objects.filter(drug_code=drug_code)
                        if pharmacy_drug:
                            pharmacy_drug.update(**{"drug_code": drug_code,
                                                    'pharmacy': pharmacy_management.id,
                                                    'drug_name': drug_name,
                                                    'standards': standards,
                                                    'preparation_type': preparation_type.id,
                                                    'drug_type': drug_type.id,
                                                    'category': category.id,
                                                    'origin_place': origin_place,
                                                    'manufacturer': manufacturer,
                                                    'valid_date': valid_date,
                                                    'inventory_quantity': inventory_quantity,
                                                    'measurement_unit': measurement_unit,
                                                    'cost_unit_price': float(cost_unit_price),
                                                    'cost_amount': float(cost_amount),
                                                    'retail_unit_price': float(retail_unit_price),
                                                    'is_active': is_active,
                                                    'retail_amount': float(retail_amount),
                                                    })
                        else:
                            PharmacyDrug.objects.create(**{"drug_code": drug_code,
                                                           'pharmacy': pharmacy_management,
                                                           'drug_name': drug_name,
                                                           'standards': standards,
                                                           'preparation_type': preparation_type,
                                                           'drug_type': drug_type,
                                                           'category': category,
                                                           'origin_place': origin_place,
                                                           'manufacturer': manufacturer,
                                                           'valid_date': valid_date,
                                                           'inventory_quantity': inventory_quantity,
                                                           'measurement_unit': measurement_unit,
                                                           'cost_unit_price': float(cost_unit_price),
                                                           'cost_amount': float(cost_amount),
                                                           'retail_unit_price': float(retail_unit_price),
                                                           'is_active': is_active,
                                                           'retail_amount': float(retail_amount),
                                                           })
                        excel_data = {
                            "pharmacy_name": pharmacy_name,
                            "drug_code": drug_code,
                            'drug_name': drug_name,
                            'standards': standards,
                            'preparation_type_name': preparation_type_name,
                            'drug_type_name': drug_type_name,
                            'category_name': category_name,
                            'origin_place': origin_place,
                            'manufacturer': manufacturer,
                            'valid_date': valid_date,
                            'inventory_quantity': inventory_quantity,
                            'measurement_unit': measurement_unit,
                            'cost_unit_price': cost_unit_price,
                            'cost_amount': cost_amount,
                            'retail_unit_price': retail_unit_price,
                            'is_active': is_active,
                            'retail_amount': retail_amount,
                        }
                        data_list.append(excel_data)
        except Exception as e:
            raise e

    if data_list:
        res = {"data": data_list}
    else:
        res = {"data": "文件内容格式有误，请检查内容格式是否正确！"}
    return JsonResponse(res)
