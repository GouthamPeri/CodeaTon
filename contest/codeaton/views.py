from django.shortcuts import render, render_to_response
from django.utils.safestring import mark_safe
import os
import datetime
import filecmp
from . import forms

# Create your views here.

def contest(request):
    string=''
    txtarea = forms.EditorForm()
    language=''
    if request.method == 'POST':
        st = str(datetime.datetime.now().microsecond)
        string = request.POST['textarea']

        f=open(st + '.c', 'w')
        f.write(string)
        f.close()
        os.system('gcc -w ' + st + '.c -o ' + st +'.o 2> errors_' + st + '.txt')
        errors = open('errors_'+st+'.txt').read()
        if len(errors) > 0:
            string = errors
            os.remove(st + '.c')
            os.remove('errors_' + st + '.txt')
        else:
            input_path = 'testcases/input/'
            output_path = 'testcases/output/'
            c=0.0
            t=0.0
            for filename in os.listdir(input_path):
                c+=1
                os.system(st + '.o < ' + input_path + filename +' > ' + st + '.txt')
                print(repr(open(st+'.txt').read()))
                print(repr(open(output_path+filename).read()))
                if filecmp.cmp(st+".txt", output_path + filename):
                    t += 1
            print(t/c)
            string = str(t/c);
            os.remove(st + '.txt')
            os.remove('errors_' + st + '.txt')
            os.remove(st + '.o')
            os.remove(st + '.c')
        txtarea = forms.EditorForm(request.POST)
    return render_to_response('index.html', {'output' : string, 'txtarea' : txtarea,
                                             'language' : mark_safe('/static/codemirror2/mode/clike/clike.js')} );