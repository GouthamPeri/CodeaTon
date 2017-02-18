from django import forms
from codemirror2.widgets import CodeMirrorEditor


def create_editor_form(language_mode, initial):
    class EditorForm(forms.Form):
        textarea = forms.CharField(label='', widget=CodeMirrorEditor(options={
            'mode': language_mode,
            'lineNumbers': True,
            'matchBrackets': True
        }), initial=initial)
    return EditorForm

