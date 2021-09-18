from django import forms
from vocalkiev.apps.crm.models import *


class LessonTeacherAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].widget = forms.HiddenInput()
        self.fields['teacher'].required = False

    def clean(self):
        data = self.cleaned_data
        if not data.get('teacher'):
            data['teacher'] = data['client_subscription'].teacher
        return data


class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = '__all__'


class PaymentAdminForm(forms.ModelForm):
    class Meta:
        model = Payment
        exclude = 'admin',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LessonCommentAdminForm(forms.ModelForm):
    class Meta:
        model = LessonComment
        exclude = 'user',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClientCommentAdminForm(forms.ModelForm):
    class Meta:
        model = ClientComment
        exclude = 'user',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PaymentInlineForm(forms.ModelForm):
    class Meta:
        model = Payment
        exclude = 'admin',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

