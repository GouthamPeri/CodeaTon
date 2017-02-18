from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from .forms import *
from django.utils.safestring import mark_safe
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from codemirror2.widgets import CodeMirrorEditor
import os
import shutil
import datetime
import filecmp
from . import forms
import subprocess, shlex
from threading import Timer


lang_mode={'C':'text/x-csrc','C++':'text/x-c++src','JAVA':'text/x-java','PYTHON':'text/x-python'}


def run(cmd, input, output, errors, timeout_sec):
    proc = subprocess.Popen(cmd, stdin=open(input, 'r'), stdout=open(output, 'w'), stderr=open(errors, 'w'))
    kill_proc = lambda p: p.kill()
    timer = Timer(timeout_sec, kill_proc, [proc])
    try:
        timer.start()
        proc.communicate()
    finally:
        proc.terminate()
        error = open(errors).read()
        if error:
            timer.cancel()
            return error
        if not timer.is_alive():
            open(errors, 'w').write('Time limit Exceeded!\n')
        timer.cancel()
        return open(errors).read()


def compile(user_filename, user_code,language):
    errors=''
    if language=='C':
        user_codefile = open(user_filename + '.c', 'w')
        user_codefile.write(user_code)
        user_codefile.close()
        os.system('gcc -w ' + user_filename + '.c -o ' + user_filename + '.o 2> ' + user_filename + '_errors.txt')
        errors = open(user_filename + '_errors.txt').read()

    elif language=='C++':
        user_codefile = open(user_filename + '.cpp', 'w')
        user_codefile.write(user_code)
        user_codefile.close()
        os.system('g++ -w ' + user_filename + '.cpp -o ' + user_filename + '.o 2> ' + user_filename + '_errors.txt')
        errors = open(user_filename + '_errors.txt').read()

    elif language == 'JAVA':
        user_filename = user_filename.replace('\\','/')
        user_filename = user_filename[:user_filename.rfind('/')]
        user_codefile = open(user_filename + "/Main.java", 'w')
        user_codefile.write(user_code)
        user_codefile.close()
        os.system('javac -nowarn ' + user_filename + '/Main.java 2>' + user_filename + '/main_errors.txt')
        errors = open(user_filename + '/main_errors.txt').read()

    elif language=="PYTHON":
        errors="Python cannot be compiled"

    if len(errors) > 0:
         return errors.replace('\n', '<br>')
    return None


def validate(user_filename, testcases_input_path, testcases_output_path, language, sample=False):
    count = 0.0
    pass_percent = 0.0
    output=''
    if language == "C" or language == "C++":
        for filename in os.listdir(testcases_input_path):
            count += 1
            errors = run(user_filename + '.o', testcases_input_path + filename, user_filename + '.txt', user_filename + '_errors.txt', 2)
            if errors:
                return errors
            if filecmp.cmp(user_filename + '.txt', testcases_output_path + filename):
                pass_percent += 1
    elif language == "JAVA":
        user_filename = user_filename.replace('\\', '/')
        user_filename = user_filename[:user_filename.rfind('/')]
        for filename in os.listdir(testcases_input_path):
            count += 1
            open(user_filename + '.txt', 'w').close()
            #print(user_filename + '.o < ' + testcases_input_path + filename + ' > ' + user_filename + '.txt')
            os.system("start java -classpath " + user_filename + " Main < " + testcases_input_path + filename
                      + ' > ' + user_filename + '/' + user_filename[user_filename.find('/')+1:] + '.txt'
                      + ' 2> ' + user_filename + '/exceptions.txt')
            errors = timeout(user_filename, '', 1, '/')
            if errors:
                return errors
            errors = open(user_filename + '/exceptions.txt').read()
            if errors:
                return errors
            if filecmp.cmp(user_filename + '/' + user_filename[user_filename.find('/')+1:] + '.txt', testcases_output_path + filename):
                pass_percent += 1
            if sample:
                output += '<br>Expected:<br>' + open(testcases_output_path + filename).read() + '<br>Actual:<br>' \
                          + open(user_filename + '/' + user_filename[user_filename.find('/')+1:] + '.txt') .read()

    elif language == "PYTHON":
        for filename in os.listdir(testcases_input_path):
            count += 1
            #print(user_filename + '.o < ' + testcases_input_path + filename + ' > ' + user_filename + '.txt')
            os.system('python -W ignore '+ user_filename + '.py < ' + testcases_input_path + filename + ' > '
                      + user_filename + '.txt' + ' 2> ' + user_filename + '_errors.txt')
            errors = open(user_filename + '_errors.txt').read()
            if errors:
                return errors
            if filecmp.cmp(user_filename + '.txt', testcases_output_path + filename):
                pass_percent += 1
            if sample:
                output += '<br>Expected:<br>' + open(testcases_output_path + filename).read() + '<br>Actual:<br>' \
                          + open(user_filename + '.txt') .read()

    if pass_percent != count:
        return output + '<br>Testcase pass percentage:' + str(100*pass_percent/count)
    return 'All Testcases Passed!'


def contest(request):
    result=''
    language='C'

    EditorForm = forms.create_editor_form(lang_mode['C'], initial='//Please select your language first')
    editor_form = EditorForm()
    language_form= forms.create_language_form("C")()
    language_file="/static/codemirror2/mode/clike/clike.js"
    if request.method == 'POST':
        #print(request.POST.get('language'))
        if request.POST.get('language')=='C':
            language = request.POST.get('language')
            language_form = forms.create_language_form(language)()
            editor_form = forms.create_editor_form(lang_mode['C'], open('initial/c.txt').read())()
            language_file = "/static/codemirror2/mode/clike/clike.js"
        elif request.POST.get('language')=='C++':
            language = request.POST.get('language')
            language_form = forms.create_language_form(language)()
            editor_form = forms.create_editor_form(lang_mode['C++'], open('initial/cpp.txt').read())()
            language_file = "/static/codemirror2/mode/clike/clike.js"
        elif request.POST.get('language')=='JAVA':
            language = request.POST.get('language')
            language_form = forms.create_language_form(language)()
            editor_form = forms.create_editor_form(lang_mode['JAVA'], open('initial/java.txt').read())()
            language_file="/static/codemirror2/mode/clike/clike.js"
        elif request.POST.get('language')=='PYTHON':
            language = request.POST.get('language')
            language_form = forms.create_language_form(language)()
            editor_form = forms.create_editor_form(lang_mode['PYTHON'], open('initial/python.txt').read())()
            language_file="/static/codemirror2/mode/python/python.js"
        if request.POST.get('compile') or request.POST.get('validate'):
            user_filename = str(datetime.datetime.now().microsecond)
            dirname = 'executions\\' + user_filename
            os.mkdir(dirname)
            if request.POST.get('compile'):
                result = compile(dirname + '\\' + user_filename, request.POST['textarea'], language)
                if result is None:
                    result = "Compiled Successfully!"
            elif request.POST.get('validate'):
                errors = compile(dirname + '\\' + user_filename, request.POST['textarea'], language)
                if language == "PYTHON":
                    user_codefile = open(dirname + '\\' + user_filename + '.py', 'w')
                    user_codefile.write(request.POST['textarea'])
                    user_codefile.close()
                    result = validate(dirname + '\\' + user_filename, 'testcases/input/', 'testcases/output/',
                                      language, sample=True)
                elif errors is None:
                    result = validate(dirname + '\\' + user_filename, 'testcases/input/', 'testcases/output/',
                                      language, sample=True)
                else:
                    result = errors
            shutil.rmtree(dirname)
            editor_form = forms.create_editor_form(lang_mode[language],initial=request.POST['textarea'])
    return render_to_response('index.html', {'output' : result, 'editor_form' : editor_form,
                                             'language' : mark_safe(language_file), 'language_form' : language_form} )

def login_view(request):
    print("he;;p")
    if request.POST:
        if 'crypt_password' in request.POST:
            form = LoginForm(request)
            username = request.POST['id_no']
            password = request.POST['crypt_password']
            user = authenticate(username=username, password=password)
            if not user is None:
                login(request, user)
                return HttpResponseRedirect('/contest/home')
            else:
                return HttpResponse("Invalid Authentication")
        else:
            return HttpResponse("<h1>Successfully Registered</h1>")
    else:
        form = LoginForm()
    return render_to_response("home.html", {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('login')