import datetime

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
import django_filters as filters
from base_system.models import Hospital, Office, Doctor


from django.contrib.auth.models import Group, Permission
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework import status

from base_system.models import ExtraGroup, ContentTypeCates, ContentTypeEx, User, Hospital
from base_system.serializers import GroupSerializer, ExtraGroupSerializer, ContentTypeCateSerializer, \
    ContentTypeExSerializer, MenuSerializer, HospitalSerializer, OfficeSerializer, DoctorSerializer
from django.db import transaction


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_fields = "__all__"
    # filterset_class = UserfFilter

    def get_parent(self, li, rels):
        if rels.parent:
            li.append(rels.parent)
            self.get_parent(li, rels.parent)
        return li

    @action(methods=["GET"], detail=True)
    def get_group_permission(self, request, pk):
        obj = self.get_object()
        # 获取当前组所拥有的权限
        permissions = Permission.objects.filter(group=obj.id).all().order_by('content_type_id')
        # serializer = PermissionSerializer(permissions, many=True)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)
        data = self.serializer_permission(permissions)
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False)
    def get_all_permission(self, request):
        # 获取所有的权限
        permissions = Permission.objects.all().order_by('content_type_id')
        # serializer = PermissionSerializer(permissions, many=True)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)
        data = self.serializer_permission(permissions)
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False)
    def get_ct_permission(self, request):
        # 获取当前组所拥有的权限
        ctrels = ContentTypeEx.objects.all().order_by('content_type_id')

        ret = map(
            lambda ctrel: {
                "id": ctrel.id,
                "name": ctrel.name,
                "permissions": map(
                    lambda p: {
                        "id": p.id,
                        "name": p.name,
                        "codename": p.codename
                    },
                    ctrel.content_type.permission_set.all()
                )
            },
            ctrels
        )

        # serializer = PermissionSerializer(permissions, many=True)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)

        # data = self.serializer_permission(permissions)
        return Response(data=ret, status=status.HTTP_200_OK)

    def serializer_permission(self, permissions):
        # 通过权限来得到权限的分类及权限的序列化信息
        permissions = set(permissions)
        content_types = map(lambda p: p.content_type, permissions)
        content_types = list(set(content_types))  # 得到去重的列表
        return map(
            lambda ct: {
                "id": ct.id,
                "name": ct.model,
                "permissions": map(
                    lambda p: {"id": p.id, "name": p.name, "codename": p.codename},
                    set(ct.permission_set.all()) & permissions
                )
            },
            content_types
        )

    # def retrieve(self, request, *args, **kwargs):
    #     # 获取单个角色的基本信息，该角色的权限，以及所有的权限
    #     obj = self.get_object()
    #     serializer = self.get_serializer(obj)
    #     # 基本的角色信息
    #     data = serializer.data
    #     # 该角色所拥有的权限
    #     permissions = Permission.objects.filter(group=obj.id).all().order_by('content_type_id')
    #     # serializer = PermissionSerializer(permissions, many=True)
    #     # data["permissions"] = serializer.data
    #     data["self_permissions"] = self.serializer_permission(permissions)
    #     # 所有的权限提供给修改使用
    #     total_permissions = Permission.objects.all().order_by('content_type_id')
    #     # serializer = PermissionSerializer(total_permissions, many=True)
    #     # data["total_permissions"] = serializer.data
    #     data["total_permissions"] = self.serializer_permission(total_permissions)
    #     return Response(data=data, status=status.HTTP_200_OK)
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        msec_str = datetime.datetime.now().strftime('%f')
        extra, group_data = self.check_data(request.data)
        # 创建角色及相关及权限
        new_group = Group.objects.filter(name=group_data["name"])
        if new_group:
            return Response(data={"msg": "角色已经存在"}, status=210)
        group = Group.objects.create(name=f'{msec_str}_'+group_data["name"])
        group.permissions.set(group_data["permission_ids"])
        group.save()
        # 创建用户附加信息
        # extra = ExtraGroup.objects.create(group_id=group.pk, **extra)
        extra['group']=group.pk

        serializer = ExtraGroupSerializer(data=extra)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=GroupSerializer(group).data, status=status.HTTP_201_CREATED)

    def check_data(self, data, flag=1):
        # 校验角色额外信息数据
        extra = dict()
        # data = dict(data)
        extra["note"] = data.get("note")
        extra["is_active"] = data.get("is_active", 1)
        extra["hospital"] = data.get("hospital_id")
        extra["order_by"] = data.get("order_by")
        extra["created_user"] = data.get("created_user")
        extra["role_code"] = data.get("role_code")
        extra["role_name"] = data.get("name")
        serializer = ExtraGroupSerializer(data=extra)
        serializer.is_valid(raise_exception=True)
        extra = serializer.data

        # 校验角色数据
        group_data = dict()
        permissions = data.get("permission_ids")
        # group_data["permission_ids"] = eval(permissions) if permissions else None
        group_data["permission_ids"] = permissions if permissions else []
        if flag == 1:  # 如果flag==1时验证group数据，否则不验证
            if data.get("name"):
                group_data["name"] = data.get("name")
                serializer = GroupSerializer(data=group_data)
                serializer.is_valid(raise_exception=True)
                # group_data = serializer.data

        return extra, group_data

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        group = self.get_object()
        extra_group = group.extra_group
        # if request.data.get("name") == group.name:
        #     del request.data["name"]
        extra, group_data = self.check_data(request.data, flag=2)
        extra_group.note = extra["note"]
        extra_group.is_active = extra["is_active"]
        extra_group.index = extra["order_by"]
        extra_group.hospital_id = extra["hospital"]
        extra_group.created_user = extra["created_user"]
        extra_group.role_code = extra["role_code"]
        extra_group.role_name = extra["role_name"]
        extra_group.save()
        # group.name = group_data.get('name', group.name)
        # if group_data.get("permission_ids"):
        group.permissions.set(group_data["permission_ids"])
        group.save()
        return Response(data=GroupSerializer(group).data, status=status.HTTP_205_RESET_CONTENT)

    # def destroy(self, request, *args, **kwargs):
    #     group = self.get_object()
    #     group.extra_group.is_active = 0
    #     group.extra_group.save()
    #     return Response(data={"message": "删除成功"}, status=status.HTTP_204_NO_CONTENT)


class ExtraGroupViewSet(ModelViewSet):
    queryset = ExtraGroup.objects.all()
    serializer_class = ExtraGroupSerializer
    filter_fields = "__all__"


class ContentTypeCatesViewSet(ModelViewSet):
    queryset = ContentTypeCates.objects.all()
    serializer_class = ContentTypeCateSerializer
    pagination_class = None
    filter_fields = "__all__"


class ContentTypeExViewSet(ModelViewSet):
    queryset = ContentTypeEx.objects.all()
    serializer_class = ContentTypeExSerializer
    filter_fields = "__all__"


def get_own_permissions(request):
    user_id=request.GET.get('user_id')
    user=User.objects.get(id=request.GET.get('user_id'))
    # defaultgroup = user.get_default_group
    # print(defaultgroup)
    # permissions = Permission.objects.filter(group=defaultgroup)

    allgroups = user.get_allgroups
    permissions = Permission.objects.filter(group__in=allgroups).distinct()
    serializer = MenuSerializer
    menu_list = get_permissions(serializer,permissions, 0)
    return JsonResponse({"data": menu_list})


def all_permissions(request):
    permissions = Permission.objects.all()
    serializer = MenuSerializer
    menu_list=get_permissions(serializer,permissions,1)
    return JsonResponse({"data": menu_list})


class MenuViewSet(ModelViewSet):
    queryset = ContentTypeCates.objects.filter(is_active=True, parent=None)
    serializer_class = MenuSerializer
    pagination_class = None
    filter_fields = "__all__"


def get_permissions(serializer,permissions,value):
    content_type_ids = list(map(lambda perm: perm.content_type_id, permissions))
    content_type_ex = ContentTypeEx.objects.filter(is_active=True,content_type_id__in=content_type_ids)
    content_type_cat_ids = list(map(lambda cat: cat.content_type_cat_id, content_type_ex))
    content_type_cats = ContentTypeCates.objects.filter(id__in=content_type_cat_ids).order_by('order_by')
    rel_list = []
    for rel in content_type_cats:
        get_parent(rel_list, rel)
    rel_list += content_type_cats
    rel_list = list(set(rel_list))
    serializer_rels = serializer(rel_list, many=True)
    all_menu = serializer_rels.data

    menu_list = [menu for menu in all_menu if not menu['parent']]
    for menu_1 in all_menu:
        children_list = [children for children in all_menu if children['parent'] == int(menu_1['id'].replace('n',''))]
        children_list = sorted(children_list, key=lambda x: x['order_by'])
        menu_1['children'] = children_list
        content_type_ex = ContentTypeEx.objects.filter(content_type_cat_id=int(menu_1['id'].replace('n',''))).first()
        if value:
            if content_type_ex and children_list ==[]:
                menu_1["children"] = list(map(lambda p: {"id": p.id, "name": p.name, "codename": p.codename},
                                                 content_type_ex.content_type.permission_set.all()))
    menu_list = sorted(menu_list, key=lambda x: x['order_by'])
    return menu_list


def menu_permissions(request):
    permissions = Permission.objects.all()
    serializer = MenuSerializer
    menu_list = get_permissions(serializer, permissions, 1)
    return JsonResponse({"data": menu_list})


def get_parent(li, rels):
    if rels.parent:
        if rels.parent not in li:
            li.append(rels.parent)
            get_parent(li, rels.parent)
    return li


class HospitalFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    codenum = filters.CharFilter(field_name="codenum", lookup_expr='icontains')
    parent = filters.CharFilter(field_name="parent")

    class Meta:
        model = Hospital
        fields = (
            "name",
            "codenum",
            "parent",
        )


class HospitalViewSet(ModelViewSet):
    queryset = Hospital.objects.filter(is_active=True).order_by('id')
    serializer_class = HospitalSerializer
    filterset_class = HospitalFilter
    # filter_fields = "__all__"


class OfficeFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    codenum = filters.CharFilter(field_name="codenum", lookup_expr='icontains')
    office_type = filters.CharFilter(field_name="office_type", lookup_expr='icontains')
    hospital = filters.CharFilter(field_name="hospital")
    parent = filters.CharFilter(field_name="parent")

    class Meta:
        model = Office
        fields = "__all__"
        search_fields = ('name', 'codenum', 'office_type')  # 允许模糊查询的字段


class OfficeViewSet(ModelViewSet):
    queryset = Office.objects.filter(is_active=True)
    serializer_class = OfficeSerializer
    # filter_fields = "__all__"
    filterset_class = OfficeFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # page = None
        if 'page' in self.request.query_params.keys():
            page = self.paginate_queryset(queryset)
            # if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})


class DoctorFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    job_number = filters.CharFilter(field_name="job_number", lookup_expr='icontains')
    phone = filters.CharFilter(field_name="phone", lookup_expr='icontains')

    class Meta:
        model = Doctor
        fields = "__all__"
        search_fields = ('name', 'job_number', 'phone')  # 允许模糊查询的字段


class DoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.filter(is_active=True)
    serializer_class = DoctorSerializer
    filterset_class = DoctorFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = None
        if 'page' in self.request.query_params.keys():
            page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        if 'fee_type' in self.request.query_params.keys():
            fee_type = self.request.query_params.get('fee_type')
            serializer = self.get_serializer(queryset, many=True, context={'fee_type': fee_type})
            return Response({'results': serializer.data})

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'fee_type' in self.request.query_params.keys():
            fee_type = self.request.query_params.get('fee_type')
            serializer = self.get_serializer(instance, context={'fee_type': fee_type})
            return Response(serializer.data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
