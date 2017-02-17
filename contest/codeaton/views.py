from django.shortcuts import render, render_to_response
from django.utils.safestring import mark_safe
import os
import datetime
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
            os.system(st + '.o > ' + st + '.txt')
            output = open(st + '.txt', 'r')
            string = output.read()
            output.close()
            os.remove(st + '.txt')
            os.remove('errors_' + st + '.txt')
            os.remove(st + '.o')
            os.remove(st + '.c')

    return render_to_response('index.html', {'output' : string, 'txtarea' : txtarea,
                                             'language' : mark_safe('/static/codemirror2/mode/clike/clike.js')} );