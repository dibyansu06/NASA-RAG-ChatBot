from django import forms
from .models import UploadedDocument

class UploadedPDFForm(forms.ModelForm):
    class Meta:
        model = UploadedDocument
        fields = ['file']
        widgets = {
            'file' : forms.ClearableFileInput(attrs={"class" : "bg-gray-800 text-white rounded p-2"})
        }
