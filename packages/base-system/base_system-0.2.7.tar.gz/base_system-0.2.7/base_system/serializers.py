from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from base_system.models import Hospital, Office, Doctor, PositionTitle, User, ExtraGroup, InspectionDictionaries, \
    ExaminationDictionaries, DrugDirectory, DrugCategory, DrugPreparationType, PharmacyManagement, ApiInfo, \
    PharmacyDrug, ContentTypeCates, ContentTypeEx, ExpenseStandard, ExaminationType, InspectionType
from django.contrib.auth.models import Group
from functools import reduce


class ExtraGroupSerializer(serializers.ModelSerializer):
    """
    角色扩充序列化
    """

    class Meta:
        model = ExtraGroup
        fields = "__all__"
        extra_kwargs = {
            'role_code': {'validators': []}
        }


class ContentTypeSerializer(serializers.ModelSerializer):
    """
    功能序列化
    """

    class Meta:
        model = ContentType
        fields = "__all__"


class ContentTypeCateSerializer(serializers.ModelSerializer):
    """
    菜单／功能序列化
    """
    children = serializers.SerializerMethodField()

    class Meta:
        model = ContentTypeCates
        fields = "__all__"

    def get_children(self,obj):
        content_type_ex = obj.content_cates
        serializer = ContentTypeExSerializer(content_type_ex, many=True)
        serializer_data = serializer.data
        return serializer_data


class ContentTypeExSerializer(serializers.ModelSerializer):
    """
    功能菜单序列化扩展
    """
    id = serializers.SerializerMethodField()

    class Meta:
        model = ContentTypeEx
        fields = "__all__"

    def get_id(self,obj):
        new_id = 'nn' + str(obj.id)
        return new_id


class MenuSerializer(serializers.ModelSerializer):
    """
    菜单／功能序列化
    """
    id = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    # icon = serializers_folder.SerializerMethodField()

    class Meta:
        model = ContentTypeCates
        fields = "__all__"


    def get_id(self,obj):
        new_id = 'n' + str(obj.id)
        return new_id

    def get_path(self,obj):
        path=''
        if obj.content_cates.all():
            path=obj.content_cates.all().first().front_url
        return path

    def get_icon(self,obj):
        icon = obj.icon_class
        if obj.content_cates.all():
            icon = obj.content_cates.all().first().icon_class
        return icon


class GroupSerializer(serializers.ModelSerializer):
    """
    角色序列化
    """

    class Meta:
        model = Group
        fields = "__all__"


class GroupSerializerDetail(serializers.ModelSerializer):
    """
    角色序列化
    """
    permissions_serializer = serializers.SerializerMethodField()  # 当前角色所有权限
    # own_menu_tree = serializers_folder.SerializerMethodField()  # 当前角色权限树形结构
    # all_menu_tree = serializers_folder.SerializerMethodField()  # 所有权限树形结构

    class Meta:
        model = Group
        fields = "__all__"

    def get_content_types(self, obj, values=None):  # 获取content_type并去重
        if values:  # 所有权限
            content_type_ids = list(map(
                lambda perm: perm.content_type_id, Permission.objects.all()))
        else:  # 正常用户权限
            content_type_ids = list(map(
                lambda perm: perm.content_type_id, obj.permissions.all()))
        return ContentType.objects.filter(id__in=content_type_ids).distinct().all()

    def get_contentypecatrels(self, obj, values=None):
        # 获取所有的终极菜单
        content_types = self.get_content_types(obj, values)
        contentypeex = map(
            lambda ct: list(ct.extension.all()), content_types)
        try:
            content_type_cat_rels = reduce(lambda a, b: a + b, contentypeex)
            contentypecatrels = [a.content_type_cat for a in content_type_cat_rels]
        except Exception as e:
            contentypecatrels = []
        return contentypecatrels

    def get_parent(self, li, rels):
        if rels.parent:
            li.append(rels.parent)
            self.get_parent(li, rels.parent)
        return li

    def get_own_menu(self, obj, values=None):
        content_type_cat_rels = self.get_contentypecatrels(obj, values)
        rel_list = []
        for rel in content_type_cat_rels:
            self.get_parent(rel_list, rel)
        rel_list += content_type_cat_rels
        rel_list = list(set(rel_list))
        serializer_rels = ContentTypeCateSerializer(rel_list, many=True)
        return serializer_rels.data

    def get_menu_tree(self, obj, values=None):
        all_menu = self.get_own_menu(obj, values)
        menu_list = []
        for menu in all_menu:
            if not menu['parent']:
                menu_list.append(menu)
        for menu_1 in all_menu:
            children_list = []
            for children in all_menu:
                if children['parent'] == menu_1['id']:
                    children_list.append(children)
            menu_1['children'] = children_list
            if values:  # 获取所有菜单级权限,否则只获取菜单
                content_type_ex = ContentTypeEx.objects.filter(content_type_cat_id=menu_1['id']).first()
                if content_type_ex:
                    menu_1["permissions"]=map(lambda p: {"id": p.id, "name": p.name, "codename": p.codename},
                                               content_type_ex.content_type.permission_set.all())
        return menu_list

    def get_own_menu_tree(self, obj):
        menu_list = self.get_menu_tree(obj)
        return menu_list

    def get_all_menu_tree(self, obj):
        menu_list = self.get_menu_tree(obj, 1)
        return menu_list

    def get_permissions_serializer(self, obj):
        return PermissionSerializer(obj.permissions, many=True).data


class PermissionSerializer(serializers.ModelSerializer):
    """
    操作权限
    """

    class Meta:
        model = Permission
        fields = "__all__"


class PasswordSerializer(serializers.Serializer):
    origin_password = serializers.CharField(required=False)
    password = serializers.CharField(min_length=6, max_length=18)
    password2 = serializers.CharField(min_length=6, max_length=18)  # 确认密码

    class Meta:
        fields = ["password", 'password2']

    def validate_origin_password(self, value):
        user = self.context["request"].user
        if user.is_superuser:
            # 如果是超级管理员，可以更改其他人的密码
            return value
        if not user.check_password(value):
            raise serializers.ValidationError("原密码不正确")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:  # 防止为空
            raise serializers.ValidationError("两次密码不一致")
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    电子地图上标识的位置信息
    """

    # groups = GroupSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        # groups = validated_data.pop("groups")
        # parts = validated_data.pop("parts_up")
        user = super(UserSerializer, self).create(validated_data)
        # user.set_password(validated_data["password"])
        username = validated_data['username']
        pwd = f'{username}@1234'
        user.set_password(pwd)
        # # if parts:
        # #     # validated_data['default_part_id'] = list(parts)[0]
        # #     user.default_part_id = list(parts)[0]
        # if groups:
        #     user.default_group_id = list(groups)[0]
        user.save()
        # # user.parts.set(parts)
        # user.groups.set(groups)
        # user.save()
        return user


class ExportHospitalSerializer(serializers.ModelSerializer):
    '''
    导出医院序列化器
    '''
    parent = serializers.SerializerMethodField(label=('上级医院'))

    class Meta:
        model = Hospital
        # fields = "__all__"
        fields = (
            'codenum',
            'name',
            'parent',
            'address',
            'longitude',
            'latitude',
            'phone',
            'introduce',
            'created_time',
            'created_by',
        )

    def get_parent(self, obj):
        parent = obj.parent
        if parent:
            return parent.name


class HospitalSerializer(serializers.ModelSerializer):

    """
    医院信息序列化器
    """

    class Meta:
        model = Hospital
        fields = "__all__"


class OfficeSerializer(serializers.ModelSerializer):
    """
    科室信息序列化器
    """

    class Meta:
        model = Office
        fields = "__all__"


class DoctorSerializer(serializers.ModelSerializer):
    """
    医生信息序列化器
    """
    position_name = serializers.SerializerMethodField()
    office_code = serializers.SerializerMethodField()
    office_name = serializers.SerializerMethodField()
    hospital_code = serializers.SerializerMethodField()
    hospital_name = serializers.SerializerMethodField()
    doctor_fee = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = "__all__"

    def get_position_name(self, obj):
        return obj.doc_rank.name

    def get_office_code(self, obj):
        return obj.office.codenum

    def get_office_name(self, obj):
        return obj.office.name

    def get_hospital_code(self, obj):
        return obj.hospital.codenum

    def get_hospital_name(self, obj):
        return obj.hospital.name

    def get_doctor_fee(self, obj):
        drfees = obj.expensestandard_set.all()
        if 'fee_type' in self.context.keys():
            fee_type = self.context['fee_type']
            doctor_fee = drfees.filter(expense_type=fee_type).first()
            if doctor_fee:
                return doctor_fee.fees
        else:
            # dr_fee = ExpenseStandard.objects.filter(doctors=obj.id)
            serializer = ExpenseStandardSerializer(drfees, many=True)
            return serializer.data


class ExpenseStandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseStandard
        fields = "__all__"


class ExportOfficeSerializer(serializers.ModelSerializer):
    '''
    导出科室序列化器
    '''
    hospital = serializers.SerializerMethodField(label=('所属医院'))
    parent = serializers.SerializerMethodField(label=('上级科室'))

    class Meta:
        model = Office
        # fields = "__all__"
        fields = (
            'codenum',
            'name',
            'hospital',
            'parent',
            'address',
            'phone',
            'introduce',
            'created_time',
            'created_by',
        )

    def get_hospital(self, obj):
        return obj.hospital.name

    def get_parent(self, obj):
        parent = obj.parent
        if parent:
            return parent.name


class ExportDoctorSerializer(serializers.ModelSerializer):
    '''
    导出医生序列化器
    '''
    hospital = serializers.SerializerMethodField(label=('所属医院'))
    office = serializers.SerializerMethodField(label=('所属科室'))
    doc_rank = serializers.SerializerMethodField(label=('医生职称'))
    gender = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        # fields = "__all__"
        fields = (
            'hospital',
            'office',
            'job_number',
            'name',
            'gender',
            'phone',
            'idnum',
            'doc_rank',
            'describe',
            'is_online_consult',
        )

    def get_hospital(self, obj):
        hospital = obj.hospital
        if hospital:
            return hospital.name

    def get_office(self, obj):
        office = obj.office
        if office:
            return office.name

    def get_gender(self, obj):
        if obj.gender:
            if obj.gender == '1':
                return '男'
            elif obj.gender == '0':
                return '女'
            else:
                return '性别设置错误'

    def get_doc_rank(self, obj):
        doc_rank = obj.doc_rank
        if doc_rank:
            return doc_rank.name


class ExportPositionTitleSerializer(serializers.ModelSerializer):
    '''
    导出职称序列化器
    '''
    hospital = serializers.SerializerMethodField(label=('所属医院'))

    class Meta:
        model = PositionTitle
        # fields = "__all__"
        fields = (
            'codenum',
            'name',
            'hospital',
            'created_time',
            'created_by',
        )

    def get_hospital(self, obj):
        hospital = obj.hospital
        if hospital:
            return hospital.name


class ExportGroupSerializer(serializers.ModelSerializer):
    '''
    导出角色序列化器
    '''
    hospital = serializers.SerializerMethodField(label=('所属医院'))
    extra_group = serializers.SerializerMethodField(label=('角色名称'))

    class Meta:
        model = ExtraGroup
        # fields = "__all__"
        fields = (
            'role_code',
            'extra_group',
            'is_active',
            'hospital',
            'created_user',
            'created_at',
        )

    def get_hospital(self, obj):
        hospital = obj.hospital
        if hospital:
            return hospital.name

    def get_extra_group(self, obj):
        group = obj.group
        if group:
            return obj.group.name


class InspectionTypeSerializer(serializers.ModelSerializer):
    """检查字典类型序列化器"""

    children = serializers.SerializerMethodField()

    class Meta:
        model = InspectionType
        fields = "__all__"

    def get_children(self, obj):
        children = InspectionType.objects.filter(parent=obj)
        if children:
            serializer = InspectionTypeSerializer(children, many=True)
            return serializer.data


class InspectionDictionariesSerializer(serializers.ModelSerializer):
    """检查字典序列化器"""
    hospital_name = serializers.SerializerMethodField()
    office_name = serializers.SerializerMethodField()

    class Meta:
        model = InspectionDictionaries
        fields = "__all__"

    def get_hospital_name(self, obj):
        hospital = Hospital.objects.filter(codenum=obj.hospital_code).first()
        if hospital:
            return hospital.name

    def get_office_name(self, obj):
        office = Office.objects.filter(codenum=obj.office_code).first()
        if office:
            return office.name


class ExportInspectionDictionariesSerializer(serializers.ModelSerializer):
    """导出检查字典序列化器"""
    hospital_name = serializers.SerializerMethodField(label='所属医院')
    office_name = serializers.SerializerMethodField(label='所属科室')

    class Meta:
        model = InspectionDictionaries
        fields = (
            'project_code',
            'project_name',
            'hospital_name',
            'office_name',
            'project_fees',
            'code_srvtp',
            'name_srvtp',
            'remarks'
        )

    def get_hospital_name(self, obj):
        hospital = Hospital.objects.filter(codenum=obj.hospital_code).first()
        if hospital:
            return hospital.name

    def get_office_name(self, obj):
        office = Office.objects.filter(codenum=obj.office_code).first()
        if office:
            return office.name


class ExaminationTypeSerializer(serializers.ModelSerializer):
    """检验字典类型序列化器"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = ExaminationType
        fields = "__all__"

    def get_children(self, obj):
        children = ExaminationType.objects.filter(parent=obj)
        if children:
            serializer = ExaminationTypeSerializer(children, many=True)
            return serializer.data


class ExaminationDictionariesSerializer(serializers.ModelSerializer):
    """检验字典序列化器"""
    hospital_name = serializers.SerializerMethodField()
    office_name = serializers.SerializerMethodField()

    class Meta:
        model = ExaminationDictionaries
        fields = "__all__"

    def get_hospital_name(self, obj):
        hospital = Hospital.objects.filter(codenum=obj.hospital_code).first()
        if hospital:
            return hospital.name

    def get_office_name(self, obj):
        office = Office.objects.filter(codenum=obj.office_code).first()
        if office:
            return office.name


class ExportExaminationDictionariesSerializer(serializers.ModelSerializer):
    """导出检验字典序列化器"""
    hospital_name = serializers.SerializerMethodField(label='所属医院')
    office_name = serializers.SerializerMethodField(label='所属科室')

    class Meta:
        model = ExaminationDictionaries
        fields = (
            'project_code',
            'project_name',
            'hospital_name',
            'office_name',
            'project_fees',
            'code_srvtp',
            'name_srvtp',
            'remarks'
        )

    def get_hospital_name(self, obj):
        hospital = Hospital.objects.filter(codenum=obj.hospital_code).first()
        if hospital:
            return hospital.name

    def get_office_name(self, obj):
        office = Office.objects.filter(codenum=obj.office_code).first()
        if office:
            return office.name


class ExportDrugDirectorySerializer(serializers.ModelSerializer):
    """导出药品目录序列化器"""

    preparation_type_name = serializers.SerializerMethodField(label='制剂类型')
    category_name = serializers.SerializerMethodField(label='分类')
    drug_type_name = serializers.SerializerMethodField(label='药品类型')

    class Meta:
        model = DrugDirectory
        fields = (
            'drug_code',
            'drug_name',
            'standards',
            'units',
            'preparation_type_name',
            'drug_type_name',
            'category_name',
            'origin_place',
            'manufacturer',
            'unit_dose',
            'measure_unit',
            'stock_left',
            'stock_unit',
            'mic',
            'rcc_category',
            'is_essential',
            'hr_level',
            'gb_code',
            'gb_name',
        )

    def get_preparation_type_name(self, obj):
        preparation_type = obj.preparation_type
        if preparation_type:
            return preparation_type.type_name

    def get_category_name(self, obj):
        category = obj.category
        if category:
            return category.category_name

    def get_drug_type_name(self, obj):
        drug_type = obj.drug_type
        if drug_type:
            return drug_type.name


class PharmacyManagementSerializer(serializers.ModelSerializer):
    """药房管理序列化器"""
    belong_unit = serializers.SerializerMethodField()

    class Meta:
        model = PharmacyManagement
        fields = (
            'pharmacy_code',
            'pharmacy_name',
            'pharmacy_type',
            'address',
            'belong_unit',
            'is_active',
        )
        depth = 2

    def get_belong_unit(self, obj):
        if obj.pharmacy_type.id == 1:
            return obj.hospital.name
        elif obj.pharmacy_type.id == 2:
            return obj.enterprise.name


class ExportUserSerializer(serializers.ModelSerializer):
    '''
    导出用户序列化器
    '''
    hospital = serializers.SerializerMethodField(label=('所属医院'))
    office = serializers.SerializerMethodField(label=('所属科室'))
    user_rank = serializers.SerializerMethodField(label=('职级'))
    doctor = serializers.SerializerMethodField(label=('绑定医生'))
    is_online_consult = serializers.SerializerMethodField(label=('是否互联网接诊'))
    groups = serializers.SerializerMethodField(label=('用户角色'))

    class Meta:
        model = User
        # fields = "__all__"
        fields = (
            'hospital',
            'office',
            'doctor',
            'user_rank',
            'username',
            'password',
            'is_online_consult',
            'groups',
        )

    def get_groups(self, obj):
        groups = obj.groups.all()
        role_list = [group.name for group in groups if groups]
        role_str = ",".join(role_list)
        return role_str

    def get_hospital(self, obj):
        hospital = obj.hospital
        if hospital:
            return hospital.name

    def get_office(self, obj):
        office = obj.office
        if office:
            return office.name

    def get_user_rank(self, obj):
        user_rank = obj.user_rank
        if user_rank:
            return user_rank.name

    def get_doctor(self, obj):
        doctor = obj.doctor
        if doctor:
            return doctor.name

    def get_is_online_consult(self, obj):
        doctor = obj.doctor
        if doctor:
            return doctor.is_online_consult


class DrugDirectorySerializer(serializers.ModelSerializer):
    preparation_type = serializers.SerializerMethodField()
    drug_type = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = DrugDirectory
        fields = "__all__"

    def get_preparation_type(self, obj):
        preparation_type = obj.preparation_type
        if preparation_type:
            return preparation_type.type_name

    def get_drug_type(self, obj):
        drug_type = obj.drug_type
        if drug_type:
            return drug_type.name

    def get_category_name(self, obj):
        category = obj.category
        if category:
            return category.category_name


class ApiInfoSerializer(serializers.ModelSerializer):
    """
    回写参数序列化器
    """

    class Meta:
        model = ApiInfo
        fields = "__all__"


class ExportPharmacyDrugSerializer(serializers.ModelSerializer):
    """导出药品目录序列化器"""
    preparation_type_name = serializers.SerializerMethodField(label='制剂类型')
    pharmacy_name = serializers.SerializerMethodField(label='药房名称')
    category_name = serializers.SerializerMethodField(label='分类')
    drug_type_name = serializers.SerializerMethodField(label='药品类型')

    class Meta:
        model = PharmacyDrug
        fields = (
            'pharmacy_name',
            'drug_code',
            'drug_name',
            'standards',
            'preparation_type_name',
            'drug_type_name',
            'category_name',
            'origin_place',
            'manufacturer',
            'valid_date',
            'inventory_quantity',
            'measurement_unit',
            'cost_unit_price',
            'cost_amount',
            'retail_unit_price',
            'retail_amount',
            'is_active',
        )

    def get_preparation_type_name(self, obj):
        preparation_type = obj.preparation_type
        if preparation_type:
            return preparation_type.type_name

    def get_pharmacy_name(self, obj):
        if obj.pharmacy:
            return obj.pharmacy.pharmacy_name

    def get_category_name(self, obj):
        category = obj.category
        if category:
            return category.category_name

    def get_drug_type_name(self, obj):
        drug_type = obj.drug_type
        if drug_type:
            return drug_type.name
