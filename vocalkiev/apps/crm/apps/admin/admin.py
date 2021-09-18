from django.contrib import admin
from vocalkiev.apps.crm.models import *
from import_export.admin import ImportExportActionModelAdmin
from import_export import resources
from import_export.results import RowResult
from django.utils.translation import gettext_lazy as _
from .forms import *

admin.site.site_header = _("vocalkiev.com")
admin.site.site_title = _("Dashboard")
admin.site.index_title = _("CRM Dashboard")


class ClientCommentInline(admin.StackedInline):
    model = ClientComment


class LessonCommentInline(admin.StackedInline):
    model = LessonComment


class LessonInline(admin.StackedInline):
    model = Lesson


class PaymentInline(admin.StackedInline):
    model = Payment
    form = PaymentInlineForm


class ClientResource(resources.ModelResource):
    def import_row(self, row, instance_loader, **kwargs):
        import_result = super(ClientResource, self).import_row(row, instance_loader, **kwargs)

        if import_result.import_type == RowResult.IMPORT_TYPE_ERROR:
            import_result.diff = [row[val] for val in row]
            import_result.diff.append('Errors: {}'.format([err.error for err in import_result.errors]))
            import_result.errors = []
            import_result.import_type = RowResult.IMPORT_TYPE_SKIP

        return import_result

    class Meta:
        model = Client
        skip_unchanged = True
        report_skipped = True
        raise_errors = False
        import_id_fields = ['id']
        fields = ('id', 'firstname', 'lastname', 'email', 'phone', ' created_at', 'updated_at')


class SubscriptionResource(resources.ModelResource):
    def import_row(self, row, instance_loader, **kwargs):
        import_result = super(SubscriptionResource, self).import_row(row, instance_loader, **kwargs)

        if import_result.import_type == RowResult.IMPORT_TYPE_ERROR:
            import_result.diff = [row[val] for val in row]
            import_result.diff.append('Errors: {}'.format([err.error for err in import_result.errors]))
            import_result.errors = []
            import_result.import_type = RowResult.IMPORT_TYPE_SKIP

        return import_result

    class Meta:
        model = Subscription
        skip_unchanged = True
        report_skipped = True
        raise_errors = False
        import_id_fields = ['id']
        fields = ('id', 'name', 'price', 'percentage', 'lessons_qty', 'percentage_if_absent', 'created_at', 'updated_at')


class ClientAdmin(ImportExportActionModelAdmin):
    resource_class = ClientResource
    list_display = ('firstname', 'lastname', 'email', 'phone', 'comment', 'updated_at')
    search_fields = ('firstname', 'lastname')
    inlines = [
        ClientCommentInline,
    ]


class LessonCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'comment')
    search_fields = ('lesson',)
    form = LessonCommentAdminForm

    def get_changeform_initial_data(self, request):
        return {'user': request.user.pk}

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return False


class ClientCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'client', 'comment')
    search_fields = ('client',)
    form = ClientCommentAdminForm

    def get_changeform_initial_data(self, request):
        return {'user': request.user.pk}

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return False


class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('place', 'name')
    search_fields = ('place', 'name')


class ClientSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'client', 'teacher', 'status', 'comment', 'payment_type', 'created_at', 'updated_at')
    search_fields = ('subscription', 'client', 'teacher', 'status',)
    inlines = [
        LessonInline,
        PaymentInline,
    ]

    def get_queryset(self, request):
        qs = super(ClientSubscriptionAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return qs
        return qs.filter(teacher=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_field_queryset(self, db, db_field, request):
        qs = super().get_field_queryset(db, db_field, request)
        if db_field.name == 'teacher':
            qs = UserFullName.objects.filter(groups__name='Teacher')
        return qs


class SubscriptionAdmin(ImportExportActionModelAdmin,  admin.ModelAdmin):
    resource_class = SubscriptionResource
    list_display = ('name', 'subject', 'status', 'price', 'percentage', 'lessons_qty', 'percentage_if_absent', 'created_at', 'updated_at')
    search_fields = ('name', 'subject')


class LessonAdmin(admin.ModelAdmin):
    list_display = ('client_subscription', 'teacher', 'classroom', 'datetime', 'status')
    search_fields = ('client_subscription', 'teacher')
    form = LessonAdminForm
    form_teacher = LessonTeacherAdminForm
    inlines = [
        LessonCommentInline,
    ]


    def get_queryset(self, request):
        qs = super(LessonAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return qs
        return qs.filter(teacher=request.user)

    def get_field_queryset(self, db, db_field, request):
        qs = super().get_field_queryset(db, db_field, request)
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return qs
        elif db_field.name == 'client_subscription':
            qs = ClientSubscription.objects.filter(teacher=request.user)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if request.user.groups.filter(name='Teacher').exists():
            defaults['form'] = self.form_teacher
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('client_subscription', 'admin', 'payment_type', 'amount', 'comment')
    search_fields = ('client_subscription', 'admin')
    form = PaymentAdminForm

    def get_changeform_initial_data(self, request):
        return {'admin': request.user.pk}

    def save_model(self, request, obj, form, change):
        if not change:
            obj.admin = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Place)
admin.site.register(Subject)
admin.site.register(LessonComment, LessonCommentAdmin)
admin.site.register(ClientComment, ClientCommentAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(ClientSubscription, ClientSubscriptionAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Payment, PaymentAdmin)