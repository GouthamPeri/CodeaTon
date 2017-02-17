from django.shortcuts import render, render_to_response
from django.utils.safestring import mark_safe
import os
import datetime
import filecmp
from . import forms

# Create your views here.

def contest(request):
    user_code=''
    editor_form = forms.EditorForm()
    language=''
    if request.method == 'POST':
        user_filename = str(datetime.datetime.now().microsecond)
        user_code = request.POST['textarea']

        user_codefile = open(user_filename + '.c', 'w')
        user_codefile.write(user_code)
        user_codefile.close()

        #errors display
        os.system('gcc -w ' + user_filename + '.c -o ' + user_filename +'.o 2> errors_' + user_filename + '.txt')
        errors = open('errors_'+user_filename+'.txt').read()
        if len(errors) > 0:
            user_code = errors
            os.remove(user_filename + '.c')
            os.remove('errors_' + user_filename + '.txt')
        else:
            testcases_input_path = 'testcases/input/'
            testcases_output_path = 'testcases/output/'
            count = 0.0
            pass_percent = 0.0
            for filename in os.listdir(testcases_input_path):
                count += 1
                os.system(user_filename + '.o < ' + testcases_input_path + filename +' > ' + user_filename + '.txt')
                if filecmp.cmp(user_filename + '.txt', testcases_output_path + filename):
                    pass_percent += 1

            user_code = pass_percent/count
            os.remove(user_filename + '.txt')
            os.remove('errors_' + user_filename + '.txt')
            os.remove(user_filename + '.o')
            os.remove(user_filename + '.c')
        editor_form = forms.EditorForm(request.POST)
    return render_to_response('index.html', {'output' : user_code, 'editor_form' : editor_form,
                                             'language' : mark_safe('/static/codemirror2/mode/clike/clike.js')} );