from django.shortcuts import render, render_to_response
from django.utils.safestring import mark_safe
from codemirror2.widgets import CodeMirrorEditor
import os
import shutil
import datetime
import filecmp
from . import forms


def compile(user_filename, user_code):
    user_codefile = open(user_filename + '.c', 'w')
    user_codefile.write(user_code)
    user_codefile.close()

    # errors store
    os.system('gcc -w ' + user_filename + '.c -o ' + user_filename + '.o 2> ' + user_filename + '_errors.txt')
    errors = open(user_filename + '_errors.txt').read()

    if len(errors) > 0:
        return errors
    return None



def validate(user_filename, testcases_input_path, testcases_output_path):
    count = 0.0
    pass_percent = 0.0
    for filename in os.listdir(testcases_input_path):
        count += 1
        print(user_filename + '.o < ' + testcases_input_path + filename + ' > ' + user_filename + '.txt')
        os.system('" '+ user_filename + '.o < ' + '"' + testcases_input_path + filename + ' > ' + user_filename + '.txt')
        if filecmp.cmp(user_filename + '.txt', testcases_output_path + filename):
            pass_percent += 1

    return pass_percent/count


def contest(request):
    result=''
    language='C'
    EditorForm = forms.create_editor_form('text/x-csrc', initial='//Please select your language first')
    editor_form = EditorForm()
    language_file="/static/codemirror2/mode/clike/clike.js"
    if request.method == 'POST':
        print(request.POST.get('language'))
        if request.POST.get('language')=='C':
            language = request.POST.get('language')
            editor_form = forms.create_editor_form('text/x-csrc', open('initial/c.txt').read())()
            language_file = "/static/codemirror2/mode/clike/clike.js"
        elif request.POST.get('language')=='C++':
            language = request.POST.get('language')
            editor_form = forms.create_editor_form('text/x-c++src', open('initial/cpp.txt').read())()
            language_file = "/static/codemirror2/mode/clike/clike.js"
        elif request.POST.get('language')=='JAVA':
            language = request.POST.get('language')
            print(open('initial/java.txt').read())
            editor_form = forms.create_editor_form('text/x-java', open('initial/java.txt').read())()
            language_file="/static/codemirror2/mode/clike/clike.js"
        elif request.POST.get('language')=='PYTHON':
            language = request.POST.get('language')
            editor_form = forms.create_editor_form('text/x-python', open('initial/python.txt').read())()
            language_file="/static/codemirror2/mode/python/python.js"
        else:
            user_filename = str(datetime.datetime.now().microsecond)
            dirname = 'executions\\' + user_filename
            os.mkdir(dirname)
            if request.POST.get('compile'):
                result = compile(dirname + '\\' + user_filename, request.POST['textarea'], language)
                if result is None:
                    result = "Compiled Successfully!"
            elif request.POST.get('validate'):
                errors = compile(dirname + '\\' + user_filename, request.POST['textarea'], language)
                if errors is None:
                    result = 'Testcases pass percent: ' + str(100 *
                            validate(dirname + '\\' + user_filename, 'testcases/input/', 'testcases/output/', language))
                else:
                    result = errors

            shutil.rmtree(dirname)
            editor_form = EditorForm(request.POST)
    return render_to_response('index.html', {'output' : result, 'editor_form' : editor_form,
                                             'language' : mark_safe(language_file)} )