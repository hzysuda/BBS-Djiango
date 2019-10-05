from django import forms
from bbs.models import User

class CheckForm(forms.Form):
    username = forms.CharField(max_length=21,min_length=3)
    password = forms.CharField(max_length=18,min_length=6)
    re_password = forms.CharField(max_length=18,min_length=6)
    telephone = forms.CharField(max_length=11,min_length=11)
    email = forms.EmailField()

    def clean_username(self):
        return self.cleaned_data.get('username')


#用户
def check_name(username,is_ajax=False):
    user = User.objects.filter(username=username)
    #判断是否是ajax
    if is_ajax:
        #如果用户存在
        if user:
            return 1
        else:
            return 0
    return 0
