from django.shortcuts import render, render_to_response
from django.utils.safestring import mark_safe
import os
import datetime
import filecmp
from . import forms


def compile(user_filename, user_code):
    user_codefile = open(user_filename + '.c', 'w')
    user_codefile.write(user_code)
    user_codefile.close()

    # errors store
    os.system('gcc -w ' + user_filename + '.c -o ' + user_filename + '.o 2> errors_' + user_filename + '.txt')
    errors = open('errors_' + user_filename + '.txt').read()
    os.remove(user_filename + '.c')
    os.remove('errors_' + user_filename + '.txt')

    if len(errors) > 0:
        return errors
    return None


def validate(user_filename, testcases_input_path, testcases_output_path):
    count = 0.0
    pass_percent = 0.0
    for filename in os.listdir(testcases_input_path):
        count += 1
        os.system(user_filename + '.o < ' + testcases_input_path + filename + ' > ' + user_filename + '.txt')
        if filecmp.cmp(user_filename + '.txt', testcases_output_path + filename):
            pass_percent += 1

    os.remove(user_filename + '.txt')
    os.remove(user_filename + '.o')
    return pass_percent/count


def contest(request):
    result=''
    editor_form = forms.EditorForm()
    language=''
    print(request.POST)
    if request.method == 'POST':
        user_filename = str(datetime.datetime.now().microsecond)
        if request.POST.get('compile'):
            result = compile(user_filename, request.POST['textarea'])
            if result is None:
                os.remove(user_filename + '.o')
                result = "Compiled Successfully!"
        elif request.POST.get('validate'):
            errors = compile(user_filename, request.POST['textarea'])
            if errors is None:
                result = 'Testcases pass percent: ' + str(100 * validate(user_filename, 'testcases/input/', 'testcases/output/'))
            else:
                result = errors
        editor_form = forms.EditorForm(request.POST)
    return render_to_response('index.html', {'output' : result, 'editor_form' : editor_form,
                                             'language' : mark_safe('/static/codemirror2/mode/clike/clike.js')} )