from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput(), label="Подтвердите пароль")
    
    full_name = forms.CharField(max_length=255, required=False, label="Полное имя")
    phone = forms.CharField(max_length=20, required=False, label="Телефон")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Адрес")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': 'Логин',
            'email': 'Email',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким логином уже существует.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Пароли не совпадают.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            profile = user.profile
            profile.full_name = self.cleaned_data.get('full_name', '')
            profile.phone = self.cleaned_data.get('phone', '')
            profile.address = self.cleaned_data.get('address', '')
            profile.save()
        return user
