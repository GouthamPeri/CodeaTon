from django import forms
from codemirror2.widgets import CodeMirrorEditor



class EditorForm(forms.Form):
    textarea=forms.CharField(widget=CodeMirrorEditor(options={'mode': 'text/x-csrc', 'lineNumbers': True, 'matchBrackets': True}))


