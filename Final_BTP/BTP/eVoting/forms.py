from django import forms


class Roll_noForm(forms.Form):
    Roll_no = forms.CharField(label='Roll_no', max_length=100)


class OTPForm(forms.Form):
    OTP = forms.CharField(label='OTP', max_length=100)


class CandidateForm(forms.Form):
    CAD = forms.CharField(label='CAD', max_length=100)