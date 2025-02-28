from django import forms


class scedshiftform(forms.Form):
    client_id = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dep_code = forms.CharField(required=True)
    rec_shift = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'onchange': 'myFunction()'}))
    shift_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    scheduled_start = forms.TimeField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'time'}))
    scheduled_end = forms.TimeField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'time'}))
    staff_id = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    shift_super = forms.BooleanField(required=False)
    shift_notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))

