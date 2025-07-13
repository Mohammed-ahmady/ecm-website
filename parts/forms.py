# C:\Users\Mohammed\Documents\ECM\parts\forms.py
from django import forms
from .models import Inquiry

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['customer_name', 'customer_email', 'part_number', 'message']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-ecm-accent', 'placeholder': 'Your Full Name'}),
            'customer_email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-ecm-accent', 'placeholder': 'Your Email Address'}),
            'part_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-ecm-accent', 'placeholder': 'Specific Part Number (if known, e.g., 123456)'}),
            'message': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-ecm-accent h-32', 'placeholder': 'Tell us about the parts you need, quantities, truck models, or any specific details.'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add required attribute to fields (Django forms handle required naturally, but this adds HTML5 validation visual cues)
        for field_name in ['customer_name', 'customer_email', 'message']:
            self.fields[field_name].widget.attrs['required'] = 'true'