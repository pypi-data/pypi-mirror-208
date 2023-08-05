import django_filters as filters
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from base_system.models import Hospital, Office, Doctor, User, ExtraGroup, InspectionDictionaries, \
    ExaminationDictionaries, DrugDirectory, PharmacyDrug
from base_system.serializers import ExportHospitalSerializer, ExportOfficeSerializer, \
    ExportInspectionDictionariesSerializer, ExportExaminationDictionariesSerializer, ExportDrugDirectorySerializer, \
    ExportDoctorSerializer, ExportUserSerializer, ExportPharmacyDrugSerializer
from base_system.serializers import ExportGroupSerializer

column_header = {
    'height': 25,
    'style': {
        'fill': {
            'fill_type': 'solid',
            'start_color': 'FFCCFFCC',
        },
        'alignment': {
            'horizontal': 'center',
            'vertical': 'center',
            'wrapText': True,
            'shrink_to_fit': True,
        },
        'border_side': {
            'border_style': 'thin',
            'color': 'FF000000',
        },
        'font': {
            'name': 'Arial',
            'size': 14,
            'bold': True,
            'color': 'FF000000',
        },
    },
}

body = {
    'style': {
        'fill': {
            'fill_type': 'solid',
            'start_color': 'FFCCFFCC',
        },
        'alignment': {
            'horizontal': 'center',
            'vertical': 'center',
            'wrapText': True,
            'shrink_to_fit': True,
        },
        'border_side': {
            'border_style': 'thin',
            'color': 'FF000000',
        },
        'font': {
            'name': 'Arial',
            'size': 14,
            'bold': False,
            'color': 'FF000000',
        }
    },
    'height': 40,
}


class HospitalInfoFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    codenum = filters.CharFilter(field_name="codenum", lookup_expr='icontains')
    parent = filters.CharFilter(field_name="parent")

    class Meta:
        model = Hospital
        fields = "__all__"

        # fields = (
        #     "name",
        #     "codenum",
        #     "parent",
        # )


class HospitalInfoExportViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    pagination_class = None
    xlsx_use_labels = True
    xlsx_boolean_labels = {True: "是", False: "否"}
    queryset = Hospital.objects.all()
    serializer_class = ExportHospitalSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'hospital_export.xlsx'
    filterset_class = HospitalInfoFilter
    # filterset_fields = {"name": ["exact", "iexact", "contains", "icontains"], "is_active": ["exact", "in"]}

    header = {
        'tab_title': "医院信息",
        'header_title': "医院信息",
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }

    def get_body(self):
        return body

    def get_column_header(self):
        return column_header


class OfficeInfoFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    hospital = filters.CharFilter(field_name="hospital", lookup_expr='icontains')

    class Meta:
        model = Office
        fields = "__all__"

        # fields = (
        #     "name",
        #     "hospital",
        # )


class OfficeInfoExportViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    pagination_class = None
    xlsx_use_labels = True
    xlsx_boolean_labels = {True: "是", False: "否"}
    queryset = Office.objects.all()
    serializer_class = ExportOfficeSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'office_export.xlsx'
    filterset_class = OfficeInfoFilter

    header = {
        'tab_title': "科室信息",
        'header_title': "科室信息",
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }

    def get_body(self):
        return body

    def get_column_header(self):
        return column_header


class DoctorInfoFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    hospital = filters.CharFilter(field_name="hospital", lookup_expr='icontains')

    class Meta:
        model = Doctor
        fields = "__all__"
        # fields = (
        #     "name",
        #     "hospital",
        # )


class DoctorInfoExportViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    """医生信息导出接口"""
    pagination_class = None
    xlsx_use_labels = True
    xlsx_boolean_labels = {True: "是", False: "否"}
    queryset = Doctor.objects.all()
    serializer_class = ExportDoctorSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'doctor_export.xlsx'
    # filterset_fields = {"name": ["exact", "iexact", "contains", "icontains"], "is_active": ["exact", "in"]}
    filterset_class = DoctorInfoFilter

    header = {
        'tab_title': "医生信息",
        'header_title': "医生信息",
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }

    def get_body(self):
        return body

    def get_column_header(self):
        return column_header


class GroupExportFilter(filters.FilterSet):
    role_name = filters.CharFilter(field_name="role_name", lookup_expr='icontains')
    hospital = filters.CharFilter(field_name="hospital", lookup_expr='icontains')

    class Meta:
        model = ExtraGroup
        fields = "__all__"


class GroupExportViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    pagination_class = None
    xlsx_use_labels = True
    xlsx_boolean_labels = {True: "是", False: "否"}
    queryset = ExtraGroup.objects.all()
    serializer_class = ExportGroupSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'group_export.xlsx'
    filterset_class = GroupExportFilter
    # filterset_fields = {"name": ["exact", "iexact", "contains", "icontains"], "is_active": ["exact", "in"]}

    header = {
        'tab_title': "角色信息",
        'header_title': "角色信息",
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }

    def get_body(self):
        return body

    def get_column_header(self):
        return column_header


class InspectionDictionariesInfoExportViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    """导出检查字典"""
    pagination_class = None
    xlsx_use_labels = True
    xlsx_boolean_labels = {True: "是", False: "否"}
    queryset = InspectionDictionaries.objects.all()
    serializer_class = ExportInspectionDictionariesSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'InspectionDictionaries_export.xlsx'
    # filterset_fields = {"project_name": ["exact", "iexact", "contains", "icontains"], "is_active": ["exact", "in"]}
    filterset_fields = "__all__"

    header = {
        'tab_title': "检查字典",
        'header_title': "检查字典",
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }

    def get_body(self):
        return body

    def get_column_header(self):
        return column_header


class ExaminationDictionariesInfoExportViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    """导出检验字典"""
    pagination_class = None
    xlsx_use_labels = True
    xlsx_boolean_labels = {True: "是", False: "否"}
    queryset = ExaminationDictionaries.objects.all()
    serializer_class = ExportExaminationDictionariesSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'ExaminationDictionaries_export.xlsx'
    # filterset_fields = {"project_name": ["exact", "iexact", "contains", "icontains"], "is_active": ["exact", "in"]}
    filterset_fields = "__all__"
    header = {
        'tab_title': "检验字典",
        'header_title': "检验字典",
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }

    def get_body(self):
        return body

    def get_column_header(self):
        return column_header


class DrugDirectoryExportViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    """导出药品目录"""
    pagination_class = None
    xlsx_use_labels = True
    xlsx_boolean_labels = {True: "是", False: "否"}
    queryset = DrugDirectory.objects.all()
    serializer_class = ExportDrugDirectorySerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'drug_directory.xlsx'
    # filterset_fields = {"drug_name": ["exact", "iexact", "contains", "icontains"], "is_active": ["exact", "in"]}
    filterset_fields = "__all__"
    header = {
        'tab_title': "药品目录",
        'header_title': "药品目录",
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }

    def get_body(self):
        return body

    def get_column_header(self):
        return column_header


class UserInfoExportViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    """用户信息导出接口"""
    pagination_class = None
    xlsx_use_labels = True
    xlsx_boolean_labels = {True: "是", False: "否"}
    queryset = User.objects.all()
    serializer_class = ExportUserSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'user_export.xlsx'
    # filterset_fields = {"name": ["exact", "iexact", "contains", "icontains"], "is_active": ["exact", "in"]}
    filterset_fields = "__all__"
    header = {
        'tab_title': "用户信息",
        'header_title': "用户信息",
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }

    def get_body(self):
        return body

    def get_column_header(self):
        return column_header


class PharmacyDrugExportViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    """导出药房药品目录"""
    pagination_class = None
    xlsx_use_labels = True
    xlsx_boolean_labels = {True: "是", False: "否"}
    queryset = PharmacyDrug.objects.all()
    serializer_class = ExportPharmacyDrugSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'pharmacy_drug.xlsx'
    # filterset_fields = {"drug_name": ["exact", "iexact", "contains", "icontains"], "is_active": ["exact", "in"]}
    filterset_fields = "__all__"
    header = {
        'tab_title': "药房-药品目录",
        'header_title': "药房-药品目录",
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }

    def get_body(self):
        return body

    def get_column_header(self):
        return column_header
