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


def create_language_form(lang=None):
    class LanguageForm(forms.Form):
        language=forms.ChoiceField(choices=[("C","C"),("C++","C++"),("JAVA","JAVA"),("PYTHON","PYTHON")],
                                   widget=forms.Select(attrs={"onchange":"document.forms['editor'].submit()"},
                                    ),initial=lang)
    return LanguageForm