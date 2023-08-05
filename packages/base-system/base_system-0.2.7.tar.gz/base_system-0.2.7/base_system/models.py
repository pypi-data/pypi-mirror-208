import json
import os

import requests
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings

GENDER_CHOICE = (
    ('1', '男'),
    ('0', '女'),
)


class MedicalBaseModel(models.Model):
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True)
    updated_time = models.DateTimeField(verbose_name='更新时间', auto_now=True, null=True)
    is_active = models.BooleanField(verbose_name="是否启用", default=True)

    class Meta:
        abstract = True


class Hospital(MedicalBaseModel):
    name = models.CharField(verbose_name="名称", max_length=255)
    phone = models.CharField(verbose_name='联系方式', max_length=100, null=True, blank=True)
    introduce = models.TextField(verbose_name="医院简介", null=True, blank=True)
    codenum = models.CharField(max_length=255, verbose_name="编码", unique=True)
    address = models.TextField(verbose_name="医院地址")
    longitude = models.FloatField(verbose_name="经度")
    latitude = models.FloatField(verbose_name="维度")
    parent = models.ForeignKey(
        'self',
        verbose_name="所属医院",
        on_delete=models.CASCADE,
        null=True
    )
    # hos_images = models.ImageField(verbose_name="医院图片", upload_to="images/hospital", null=True, blank=True)
    hos_images = models.CharField(verbose_name="医院图片", max_length=100, default='hospital_images', blank=True)
    # logo = models.ImageField(verbose_name="logo", upload_to="images/logo", null=True, blank=True)
    logo = models.CharField(verbose_name="logo", max_length=100, default='hospital_logo')
    created_by = models.CharField(verbose_name="创建人", max_length=100, null=True, blank=True)
    updated_by = models.CharField(verbose_name="更新人", max_length=100, null=True, blank=True)

    class Meta:
        db_table = "bs_hospital"
        verbose_name = "医院"
        verbose_name_plural = verbose_name

    # def __str__(self):
    #     return self.name


class Office(MedicalBaseModel):
    name = models.CharField(verbose_name="名称", max_length=255)
    address = models.CharField(verbose_name="科室位置", max_length=255, null=True, blank=True)
    phone = models.CharField(verbose_name='联系方式', max_length=255, null=True, blank=True)
    codenum = models.CharField(verbose_name="科室编码", max_length=255)
    office_type = models.CharField(verbose_name="类型", max_length=100, null=True, blank=True)
    introduce = models.TextField(verbose_name="科室简介", null=True, blank=True)
    hospital = models.ForeignKey(
        Hospital,
        verbose_name="所属医院",
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        'self',
        verbose_name="上级科室",
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        db_table = "bs_office"
        verbose_name = "科室"
        verbose_name_plural = verbose_name
        unique_together = (
            ('codenum', 'hospital',),  # 联合唯一
        )


class PositionTitle(MedicalBaseModel):
    name = models.CharField(verbose_name="名称", max_length=255)
    codenum = models.CharField(verbose_name="职称编码", max_length=255)
    hospital = models.ForeignKey(
        Hospital,
        verbose_name="所属医院",
        on_delete=models.CASCADE,
    )
    created_by = models.CharField(verbose_name="创建人", max_length=100, null=True, blank=True)
    updated_by = models.CharField(verbose_name="更新人", max_length=100, null=True, blank=True)

    class Meta:
        db_table = "bs_position_title"
        verbose_name = "职称"
        verbose_name_plural = verbose_name
        unique_together = (
            ('codenum', 'hospital',),  # 联合唯一
        )


class Doctor(MedicalBaseModel):
    name = models.CharField(verbose_name="名称", max_length=20)
    phone = models.CharField(verbose_name='联系方式', max_length=20, null=True, blank=True)
    email = models.CharField(verbose_name='邮箱', max_length=100, null=True, blank=True)
    address = models.CharField(verbose_name="地址", max_length=255, null=True, blank=True)
    codenum = models.CharField(verbose_name="工号", max_length=64)
    position = models.CharField(verbose_name="职位", max_length=20, null=True, blank=True)
    position_title = models.ForeignKey(
        PositionTitle,
        verbose_name="职称",
        on_delete=models.CASCADE,
    )
    gender = models.CharField(verbose_name='性别', max_length=2, choices=GENDER_CHOICE, null=True, blank=True)
    nation = models.CharField(verbose_name="民族", max_length=10, null=True, blank=True)
    idnum = models.CharField(verbose_name="身份证号", max_length=100, null=True, blank=True)
    office = models.ForeignKey(
        Office,
        verbose_name="所属科室",
        on_delete=models.CASCADE,
    )
    hospital = models.ForeignKey(
        Hospital,
        verbose_name="所属医院",
        on_delete=models.CASCADE,
    )
    birthday = models.DateField(verbose_name='出生日期', null=True, blank=True)
    # photo = models.ImageField(verbose_name="医生照片", upload_to="images/doctor", null=True, blank=True)
    photo = models.CharField(verbose_name="医生照片", max_length=50, default='doctor_photo')
    describe = models.TextField(verbose_name="医生描述", null=True, blank=True)
    created_by = models.CharField(verbose_name="创建人", max_length=20, null=True, blank=True)
    updated_by = models.CharField(verbose_name="更新人", max_length=20, null=True, blank=True)

    is_online_consult = models.BooleanField(verbose_name="是否互联网接诊", default=True)

    class Meta:
        db_table = "bs_doctor"
        verbose_name = "医生表"
        verbose_name_plural = verbose_name


class User(AbstractUser):
    name = models.CharField(verbose_name="名称", max_length=255, null=True, blank=True)
    phone = models.CharField(verbose_name='联系方式', max_length=100, null=True, blank=True)
    birthday = models.DateField(verbose_name='出生日期', null=True, blank=True)
    gender = models.CharField(verbose_name='性别', max_length=2, choices=GENDER_CHOICE, null=True, blank=True)
    idcardnum = models.CharField(verbose_name='身份证号', max_length=100, null=True, blank=True)
    order_by = models.IntegerField(verbose_name='排序', default=1, null=True, blank=True)
    office = models.ForeignKey(
        Office,
        verbose_name="所属科室",
        on_delete=models.CASCADE,
        null=True
    )
    hospital = models.ForeignKey(
        Hospital,
        verbose_name="所属医院",
        on_delete=models.CASCADE,
        null=True
    )
    doctor = models.ForeignKey(
        Doctor,
        verbose_name="绑定医生",
        on_delete=models.CASCADE,
        null=True
    )
    # avatar_url = models.ImageField(verbose_name="用户头像", upload_to="images/user", null=True, blank=True)
    avatar_url = models.CharField(verbose_name="用户头像", max_length=100, default='user_avatar')
    default_group_id = models.CharField(verbose_name='默认角色', max_length=255, null=True, blank=True)
    allow_office = models.CharField(verbose_name='可操作科室', max_length=255, null=True, blank=True)
    note = models.TextField(verbose_name="注释说明", null=True, blank=True)
    created_by = models.CharField(verbose_name="创建人", max_length=100, null=True, blank=True)
    updated_by = models.CharField(verbose_name="更新人", max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True)
    updated_time = models.DateTimeField(verbose_name='更新时间', auto_now=True, null=True)

    class Meta:
        # db_table = "bs_user"
        verbose_name = "用户信息"
        # verbose_name_plural = verbose_name

    # def __str__(self):
    #     return self.name

    @property
    def get_default_group(self):
        '''
        获取当前用户默认用户组,
        如果未设置，返回第一个用户组
        否则返回设置的用户组
        '''
        ret_group = self.default_group
        if not ret_group:
            ret_group = self.groups.first()
        return ret_group

    @property
    def get_allgroups(self):
        ret_group = self.groups.all()
        if not ret_group:
            ret_group = self.groups.none()
        return ret_group

    @property
    def get_default_organization(self):
        '''
        获取用户默认的组织机构
        '''
        ret_org = None
        ret_org = self.office
        if not ret_org:
            ret_org = self.hospital
        return ret_org


class ExtraGroup(models.Model):
    """
    角色扩充表
    """
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="extra_group", null=True, blank=True)
    role_code = models.CharField(max_length=50, verbose_name="角色代码")
    role_name = models.CharField(max_length=50, verbose_name="角色名称", blank=True)
    is_active = models.BooleanField(default=True, verbose_name='是否启用', null=True)
    note = models.CharField('描述', max_length=50, null=True, blank=True)
    hospital = models.ForeignKey(
        Hospital,
        verbose_name='所属医院',
        on_delete=models.CASCADE,
        related_name='groups',
        null=True
    )
    order_by = models.IntegerField(verbose_name='排序', default=1, null=True)
    created_user = models.CharField(max_length=50, verbose_name="创建人", null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name="最后更新时间", auto_now=True, null=True)

    class Meta:
        db_table = 'bs_extra_group'
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        unique_together = (
            ('role_code', 'hospital',),  # 联合唯一
        )


class ContentTypeCates(models.Model):
    """
    菜单名称
    """
    name = models.CharField('名称', max_length=20)
    is_active = models.BooleanField('是否启用', default=True)
    order_by = models.IntegerField(verbose_name='排序', default=1, null=True)
    level = models.IntegerField(verbose_name="级别", default=1, null=True, blank=True)
    icon_class = models.CharField(verbose_name="图标", max_length=500, null=True, blank=True)
    parent = models.ForeignKey(
        'self',
        verbose_name='父级菜单',
        on_delete=models.CASCADE,
        related_name='children',
        null=True
    )

    class Meta:
        db_table = 'bs_content_type_cats'
        verbose_name = '菜单名称'
        verbose_name_plural = verbose_name
        ordering = ('order_by',)

    def __str__(self):
        return self.name


class ContentTypeEx(models.Model):
    """
    功能类别
    """
    name = models.CharField('名称', max_length=20, null=True)
    content_type = models.ForeignKey(
        ContentType,
        verbose_name="系统应用",
        on_delete=models.CASCADE,
        related_name='extension'
    )
    content_type_cat = models.ForeignKey(
        'ContentTypeCates',
        verbose_name='菜单',
        on_delete=models.CASCADE,
        related_name='content_cates'
    )
    icon_class = models.CharField(verbose_name="图标", max_length=500, null=True, blank=True)
    front_url = models.TextField(verbose_name='url', null=True, blank=True)
    front_component = models.TextField(verbose_name='组成', null=True, blank=True)
    front_params = models.CharField(verbose_name='参数', max_length=50, null=True)
    front_redirect_url = models.URLField(verbose_name='重定向', null=True)
    is_active = models.BooleanField('是否启用', default=True, null=True)
    order_by = models.IntegerField(verbose_name='排序', default=1, null=True)

    class Meta:
        db_table = 'bs_content_type_ex'
        verbose_name = '功能类别补充'
        verbose_name_plural = verbose_name
        ordering = ('order_by',)

    def __str__(self):
        return self.name


class ExpenseType(MedicalBaseModel):
    """
    费用类型
    """
    name = models.CharField(verbose_name="名称", max_length=64)
    code = models.CharField(verbose_name="编码", max_length=64)

    class Meta:
        db_table = "bs_expense_type"
        verbose_name = "费用类型"
        verbose_name_plural = verbose_name


class ExpenseStandard(MedicalBaseModel):
    # 挂号费用类型1:预约挂号, 2:电话问诊, 3:在线问诊, 4:在线复诊
    expense_type = models.CharField(verbose_name="费用类型", max_length=100, null=True)
    standard_name = models.CharField(verbose_name="标准名称", max_length=100)
    standard_code = models.CharField(verbose_name="标准编码", max_length=255)
    fees = models.FloatField(verbose_name="费用", null=True)
    hospital = models.ForeignKey(
        Hospital,
        verbose_name='所属医院',
        on_delete=models.CASCADE,
        null=True
    )
    created_by = models.CharField(verbose_name="创建人", max_length=100, null=True, blank=True)
    updated_by = models.CharField(verbose_name="更新人", max_length=100, null=True, blank=True)
    doctors = models.ManyToManyField(Doctor, verbose_name="医生费用标准", blank=True)

    class Meta:
        db_table = 'bs_expense_standard'
        verbose_name = '费用标准表'
        verbose_name_plural = verbose_name
        unique_together = (
            ('standard_code', 'hospital',),  # 联合唯一
        )


class InspectionType(MedicalBaseModel):
    code_srvtp = models.CharField(verbose_name="检查类型编码", max_length=50)
    name_srvtp = models.CharField(verbose_name="检查类型名称", max_length=50)
    parent = models.ForeignKey(
        'self',
        verbose_name='父级',
        on_delete=models.CASCADE,
        related_name='children',
        null=True
    )

    class Meta:
        db_table = 'bs_inspection_type'
        verbose_name = '检查字典类型'
        verbose_name_plural = verbose_name


class InspectionDictionaries(MedicalBaseModel):
    project_code = models.CharField(max_length=255, verbose_name="项目编码", unique=True)
    project_name = models.CharField(max_length=64, verbose_name="项目名称")
    hospital_code = models.CharField(max_length=128, verbose_name="医院编码")
    office_code = models.CharField(max_length=128, verbose_name="科室编码")
    project_fees = models.FloatField(verbose_name="项目费用", null=True)
    remarks = models.CharField(max_length=128, verbose_name="备注", null=True, blank=True)
    distinguish = models.CharField(max_length=128, verbose_name="区分字段", null=True, blank=True)
    code_srvtp = models.CharField(verbose_name="检查类型编码", max_length=50, null=True)
    name_srvtp = models.CharField(verbose_name="检查类型名称", max_length=50, null=True)

    class Meta:
        db_table = 'bs_inspection_dictionaries'
        verbose_name = '检查字典'
        verbose_name_plural = verbose_name


class ExaminationType(MedicalBaseModel):
    code_srvtp = models.CharField(verbose_name="检查类型编码", max_length=50)
    name_srvtp = models.CharField(verbose_name="检查类型名称", max_length=50)
    parent = models.ForeignKey(
        'self',
        verbose_name='父级',
        on_delete=models.CASCADE,
        related_name='children',
        null=True
    )

    class Meta:
        db_table = 'bs_examination_type'
        verbose_name = '检验字典类型'
        verbose_name_plural = verbose_name


class ExaminationDictionaries(MedicalBaseModel):
    project_code = models.CharField(max_length=255, verbose_name="项目编码", unique=True)
    project_name = models.CharField(max_length=64, verbose_name="项目名称")
    hospital_code = models.CharField(max_length=128, verbose_name="医院编码")
    office_code = models.CharField(max_length=128, verbose_name="科室编码")
    project_fees = models.FloatField(verbose_name="项目费用", null=True)
    remarks = models.CharField(max_length=128, verbose_name="备注", null=True, blank=True)
    distinguish = models.CharField(max_length=128, verbose_name="区分字段", null=True, blank=True)
    code_srvtp = models.CharField(verbose_name="检验类型编码", max_length=50, null=True)
    name_srvtp = models.CharField(verbose_name="检验类型名称", max_length=50, null=True)

    class Meta:
        db_table = 'bs_examination_dictionaries'
        verbose_name = '检验字典'
        verbose_name_plural = verbose_name


class DrugPreparationType(MedicalBaseModel):
    codenum = models.CharField(max_length=255, verbose_name="编码", unique=True)
    type_name = models.CharField(max_length=64, verbose_name="类型名称", null=True, blank=True)

    class Meta:
        db_table = 'bs_drug_preparation_type'
        verbose_name = '药品制剂类型'
        verbose_name_plural = verbose_name


class DrugType(MedicalBaseModel):
    code = models.CharField(verbose_name="编码", max_length=255, unique=True)
    name = models.CharField(verbose_name="名称", max_length=64, null=True, blank=True)

    class Meta:
        db_table = 'bs_drug_type'
        verbose_name = '药品类型'
        verbose_name_plural = verbose_name


class DrugCategory(MedicalBaseModel):
    codenum = models.CharField(max_length=255, verbose_name="编码", unique=True)
    category_name = models.CharField(max_length=64, verbose_name="类别名称", null=True, blank=True)

    class Meta:
        db_table = 'bs_drug_category'
        verbose_name = '药品类别'
        verbose_name_plural = verbose_name


class DrugDirectory(MedicalBaseModel):
    drug_code = models.CharField(verbose_name="药品编码", max_length=255, unique=True)
    drug_name = models.CharField(max_length=64, verbose_name="药品名称", null=True, blank=True)
    standards = models.CharField(max_length=64, verbose_name="规格", null=True, blank=True)
    total_unit = models.CharField(max_length=64, verbose_name="基本单位", null=True, blank=True)  # 盒，袋，瓶
    total_unit_code = models.CharField(verbose_name="总量单位编码", max_length=20, null=True, blank=True)
    preparation_type = models.ForeignKey(
        DrugPreparationType,
        verbose_name='制剂类型',
        on_delete=models.DO_NOTHING,
    )
    category = models.ForeignKey(
        DrugCategory,
        verbose_name='类别',
        on_delete=models.DO_NOTHING,
    )
    drug_type = models.ForeignKey(
        DrugType,
        verbose_name='药品类型',
        on_delete=models.DO_NOTHING,
    )
    unit_dose = models.CharField(verbose_name="单位剂量", max_length=20, null=True, blank=True)
    measure_unit = models.CharField(verbose_name="计量/零售单位", max_length=20, null=True, blank=True)
    measure_unit_code = models.CharField(verbose_name="计量单位编码", max_length=20, null=True, blank=True)
    stock_left = models.CharField(verbose_name="库存数量", max_length=20, null=True, blank=True)
    stock_unit = models.CharField(verbose_name="库存单位", max_length=20, null=True, blank=True)
    mic = models.CharField(verbose_name="医保类别", max_length=20, null=True, blank=True)
    rcc_category = models.CharField(verbose_name="农合类别", max_length=20, null=True, blank=True)
    is_essential = models.BooleanField(verbose_name="是否是基药", default=True)
    hr_level = models.CharField(verbose_name="高危等级", max_length=64, null=True, blank=True)
    gb_code = models.CharField(verbose_name="国家贯标编码", max_length=64, null=True, blank=True)
    gb_name = models.CharField(verbose_name="国家贯标名称", max_length=64, null=True, blank=True)
    origin_place = models.CharField(max_length=64, verbose_name="产地", null=True, blank=True)
    manufacturer = models.CharField(max_length=64, verbose_name="生产厂家", null=True, blank=True)
    code_medu_cur = models.CharField(verbose_name="单次用量单位编码", max_length=64, null=True)

    class Meta:
        db_table = 'bs_drug_directory'
        verbose_name = '药品目录'
        verbose_name_plural = verbose_name


class PharmacyType(MedicalBaseModel):
    code = models.CharField(verbose_name="编码", max_length=255, unique=True)
    name = models.CharField(verbose_name="名称", max_length=64, null=True, blank=True)

    class Meta:
        db_table = 'bs_pharmacy_type'
        verbose_name = '药房类型'
        verbose_name_plural = verbose_name


class PharmacyEnterprise(MedicalBaseModel):
    code = models.CharField(verbose_name="编码", max_length=255, unique=True)
    name = models.CharField(verbose_name="名称", max_length=64, null=True, blank=True)

    class Meta:
        db_table = 'bs_pharmacy_enterprise'
        verbose_name = '药企管理'
        verbose_name_plural = verbose_name


class PharmacyManagement(MedicalBaseModel):
    pharmacy_code = models.CharField(verbose_name="药房编码", max_length=255, unique=True)
    pharmacy_name = models.CharField(verbose_name="药房名称", max_length=64, null=True, blank=True)
    pharmacy_type = models.ForeignKey(
        PharmacyType,
        verbose_name='药房类型',
        on_delete=models.DO_NOTHING,
    )
    address = models.TextField(verbose_name="药房地址", null=True, blank=True)
    hospital = models.ForeignKey(Hospital, verbose_name="所属医院", on_delete=models.CASCADE,null=True)
    enterprise = models.ForeignKey(PharmacyEnterprise, verbose_name="所属药企", on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'bs_pharmacy_management'
        verbose_name = '药房管理'
        verbose_name_plural = verbose_name


class PharmacyDrug(MedicalBaseModel):
    pharmacy = models.ForeignKey(PharmacyManagement, verbose_name="所属药房", on_delete=models.CASCADE, null=True)
    drug_code = models.CharField(verbose_name="药品编码", max_length=255, null=True, blank=True)
    drug_name = models.CharField(max_length=64, verbose_name="药品名称", null=True, blank=True)
    standards = models.CharField(max_length=64, verbose_name="规格", null=True, blank=True)
    units = models.CharField(max_length=64, verbose_name="单位", null=True, blank=True)
    preparation_type = models.ForeignKey(
        DrugPreparationType,
        verbose_name='制剂类型',
        on_delete=models.DO_NOTHING,
    )
    drug_type = models.ForeignKey(
        DrugType,
        verbose_name='药品类型',
        on_delete=models.DO_NOTHING,
    )
    category = models.ForeignKey(
        DrugCategory,
        verbose_name='类别',
        on_delete=models.DO_NOTHING,
    )
    origin_place = models.CharField(max_length=500, verbose_name="产地", null=True, blank=True)
    manufacturer = models.CharField(max_length=200, verbose_name="生产厂家", null=True, blank=True)
    hospital = models.ForeignKey(Hospital, verbose_name="所属医院", on_delete=models.CASCADE, null=True)
    valid_date = models.DateField(verbose_name='有效日期', auto_now=True, null=True)
    inventory_quantity = models.IntegerField(verbose_name='库存数量', default=0, null=True)
    measurement_unit = models.CharField(max_length=64, verbose_name="计量单位", null=True, blank=True)
    cost_unit_price = models.FloatField(verbose_name="成本单价", null=True)
    cost_amount = models.FloatField(verbose_name="成本金额", null=True)
    retail_unit_price = models.FloatField(verbose_name="零售单价", null=True)
    retail_amount = models.FloatField(verbose_name="零售金额", null=True)

    class Meta:
        db_table = 'bs_pharmacy_drug'
        verbose_name = '药房-药品'
        verbose_name_plural = verbose_name


class ApiInfo(models.Model):
    org_code = models.CharField(max_length=50, verbose_name="医院编码")
    req_code = models.CharField(max_length=50, verbose_name="请求编码")
    req_name = models.CharField(max_length=50, verbose_name="请求名称", null=True, blank=True)
    req_method = models.CharField(max_length=50, verbose_name="请求方式")
    content_type = models.CharField(max_length=50, verbose_name="请求数据类型")
    ip_domain = models.CharField(max_length=200, verbose_name="ip地址或域名")
    front_url = models.CharField(max_length=200, verbose_name="请求路由")
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True)
    updated_time = models.DateTimeField(verbose_name='更新时间', auto_now=True, null=True)
    is_active = models.BooleanField(verbose_name="是否启用", default=True)

    class Meta:
        db_table = "bs_api_info"
        verbose_name = "接口信息"
        verbose_name_plural = verbose_name
        unique_together = (
            ('org_code', 'req_code',),  # 联合唯一
        )

    def writeback(self, in_data, req_code):
        api_info_obj = ApiInfo.objects.filter(org_code=in_data['hospital_code'], req_code=req_code).first()
        if api_info_obj:
            cms_url = api_info_obj.ip_domain + api_info_obj.front_url
            if api_info_obj.req_method == "POST":
                res = requests.post(url=cms_url, json=in_data)
            elif api_info_obj.req_method == "GET":
                res = requests.get(url=cms_url, params=in_data)
            elif api_info_obj.req_method == "PUT":
                res = requests.put(url=cms_url, data=in_data)
            elif api_info_obj.req_method == "DELETE":
                res = requests.delete(url=cms_url)
            else:
                res = requests.patch(url=cms_url)
            res_json = json.loads(res.text)
        else:
            res_json = {"success": False, "code": 2001, "message": "不存在对接医院信息！", "data": {}}
        return res_json
