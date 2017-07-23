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
from .models import *
import shutil
import datetime
import filecmp
from . import forms
import shlex
import subprocess32 as subprocess
from threading import Timer
from django.contrib.auth.signals import user_logged_in
import json
import traceback
from django.template.defaulttags import register


lang_mode={'C':'text/x-csrc','C++':'text/x-c++src','JAVA':'text/x-java','PYTHON':'text/x-python'}

def calctime(status):
    time_object=status.time
    total_time=0.0
    time_object = json.loads(time_object)
    print type(time_object)
    for time in time_object.keys():
        total_time+=float(time_object[time])
    status.total_time = float(total_time)

def save(user, question_no, program_code,language, status=0.0):
    try:
        team_status = Status.objects.get(team_name=user)
        question = Questions.objects.get(question_code=question_no)
        pass_status = 0.0
        pass_statuses = json.loads(team_status.status)

        try:
            pass_status = pass_statuses[question_no]
        except:
            pass_statuses[question_no] = 0.0
            team_status.status=json.dumps(pass_statuses)
            team_status.save()

        if status > pass_statuses[question_no]:
            program_codes = json.loads(team_status.program_code)
            program_codes[question_no] = {}
            program_codes[question_no][language] = program_code
            team_status.program_code = json.dumps(program_codes)
            team_status.total_score -= int(pass_statuses[question_no] * question.question_marks)
            pass_statuses[question_no] = status
            team_status.status = json.dumps(pass_statuses)
            team_status.total_score += int(status * question.question_marks)
            calctime(team_status)
            try:
                times = json.loads(team_status.time)
            except:
                times = {}

            times[question_no] = str((datetime.datetime.now() - datetime.datetime.strptime(
                UserLoginTime.objects.get(user=user).login_time, "%b %d, %Y %H:%M:%S")).total_seconds()/60)
            team_status.time = json.dumps(times)
        team_status.save()


    except Exception as e:
        question = Questions.objects.get(question_code=question_no)
        pass_statuses = {}
        program_codes = {question_no: {}}
        times = {}
        pass_statuses[question_no] = status
        program_codes[question_no][language] = program_code
        times[question_no] = str((datetime.datetime.now() - datetime.datetime.strptime(
            UserLoginTime.objects.get(user=user).login_time, "%b %d, %Y %H:%M:%S")).total_seconds() / 60)
        Status.objects.create(team_name=user, status=json.dumps(pass_statuses),
                              program_code=json.dumps(program_codes), time=json.dumps(times) if times else None,total_score=int(status * question.question_marks),total_time=float(times[question_no]))


def run(cmd, input, output, errors, timeout_sec):
    one = open(input, 'r')
    two = open(output, 'w+')
    three = open(errors, 'w+')

    try:
        op = subprocess.check_output(cmd.split(), stdin=one, stderr=three, timeout=timeout_sec)
    except subprocess.CalledProcessError as e:
        return open(errors).read()
    except subprocess.TimeoutExpired as e:
        return "TIMEOUT"

    two.write(op)


def compile(user_filename, user_code,language):
    errors=''
    if language == 'C':
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
                return [errors]
            cmpop = filecmp.cmp(user_filename + '.txt', testcases_output_path + filename)
            if cmpop:
                pass_percent += 1
            if sample:
                output += '<h3><b>Sample Test ' + str(int(count))  + '</b></h3><br><b>Expected:</b><br>' + open(testcases_output_path + filename).read() \
                          + '<br><b>Actual:</b><br>' + open(user_filename + '.txt').read() + '<hr>'

    elif language == "JAVA":
        user_filename = user_filename.replace('/', '/')
        user_filename = user_filename[:user_filename.rfind('/')]
        for filename in os.listdir(testcases_input_path):
            count += 1
            errors = run("java -classpath " + user_filename + " Main ", testcases_input_path + filename,
                        user_filename + '/' + user_filename[user_filename.find('/')+1:] + '.txt',
                        user_filename + '/exceptions.txt',2)
            if errors:
                return [errors]
            if filecmp.cmp(user_filename + '/' + user_filename[user_filename.find('/')+1:] + '.txt', testcases_output_path + filename):
                pass_percent += 1
            if sample:
                output += '<h3><b>Sample Test ' + str(int(count))  + '</b></h3><br><b>Expected:</b><br>' + open(testcases_output_path + filename).read() \
                          + '<br><b>Actual:</b><br>' + open(user_filename + '/' + user_filename[user_filename.find('/')+1:] + '.txt').read() + '<hr>'

    elif language == "PYTHON":
        for filename in os.listdir(testcases_input_path):
            count += 1
            errors = run('python -W ignore '+ user_filename + '.py ', testcases_input_path + filename,
                        user_filename + '.txt',user_filename + '_errors.txt',3)
            if errors:
                return [errors]
            if filecmp.cmp(user_filename + '.txt', testcases_output_path + filename):
                pass_percent += 1
            if sample:
                output += '<h3><b>Sample Test ' + str(int(count))  + '</b></h3><br><b>Expected:</b><br>' + open(testcases_output_path + filename).read() \
                          + '<br><b>Actual:</b><br>' + open(user_filename + '.txt').read() + '<hr>'

    if pass_percent != count:
        return (output + '<h2 class="w3-label">' + ('Sample ' if sample else '') + 'Testcases pass percentage: ' + str(100*pass_percent/count) + '%</h2>', pass_percent/count)
    return ('<h2 class="w3-label">' + ('All Sample Testcases passed! ' if sample else 'Solution Accepted, Congratulations!') + '</h2>',1)

def get_saved_code(user,question_code,language):
    try:
        status_object = Status.objects.get(team_name=user)
        return json.loads(status_object.program_code)[question_code][language]
    except Exception as e:
        return None

@login_required
def contest(request):
    result=''
    language='C'
    time = datetime.datetime.strptime(UserLoginTime.objects.get(user=request.user).login_time, "%b %d, %Y %H:%M:%S") + datetime.timedelta(seconds=2000)
    if time < datetime.datetime.now():
        return HttpResponseRedirect('/contest/home')

    time = time.strftime("%b %d, %Y %H:%M:%S")

    saved_code=get_saved_code(request.user, request.GET['qid'], language)
    if not saved_code:
        editor_form = forms.create_editor_form(lang_mode['C'], open('initial/c.txt').read())()
    else:
        editor_form = forms.create_editor_form(lang_mode['C'], saved_code)()
    language_form= forms.create_language_form("C")()
    language_file="/static/codemirror2/mode/clike/clike.js"

    if request.method == 'POST':
        if request.POST.get('language')=='C':
            language = request.POST.get('language')
            language_form = forms.create_language_form(language)()
            saved_code = get_saved_code(request.user, request.GET['qid'], language)
            if not saved_code:
                editor_form = forms.create_editor_form(lang_mode['C'], open('initial/c.txt').read())()
            else:
                editor_form = forms.create_editor_form(lang_mode['C'], saved_code)()
            language_file = "/static/codemirror2/mode/clike/clike.js"
        elif request.POST.get('language')=='C++':
            language = request.POST.get('language')
            language_form = forms.create_language_form(language)()
            saved_code = get_saved_code(request.user, request.GET['qid'], language)
            if not saved_code:
                editor_form = forms.create_editor_form(lang_mode['C++'], open('initial/cpp.txt').read())()
            else:
                editor_form = forms.create_editor_form(lang_mode['C++'], saved_code)()
            language_file = "/static/codemirror2/mode/clike/clike.js"
        elif request.POST.get('language')=='JAVA':
            language = request.POST.get('language')
            language_form = forms.create_language_form(language)()
            saved_code = get_saved_code(request.user, request.GET['qid'], language)
            if not saved_code:
                editor_form = forms.create_editor_form(lang_mode['JAVA'], open('initial/java.txt').read())()
            else:
                editor_form = forms.create_editor_form(lang_mode['JAVA'], saved_code)()
            language_file="/static/codemirror2/mode/clike/clike.js"
        elif request.POST.get('language')=='PYTHON':
            language = request.POST.get('language')
            language_form = forms.create_language_form(language)()
            saved_code = get_saved_code(request.user, request.GET['qid'], language)
            if not saved_code:
                editor_form = forms.create_editor_form(lang_mode['PYTHON'], open('initial/python.txt').read())()
            else:
                editor_form = forms.create_editor_form(lang_mode['PYTHON'], saved_code)()
            language_file="/static/codemirror2/mode/python/python.js"
        if request.POST.get('compile') or request.POST.get('validate') or request.POST.get('submit_answer'):
            user_filename = str(datetime.datetime.now().microsecond)
            dirname = 'executions/' + request.user.username + "_" + user_filename
            os.makedirs(dirname)
            #if request.POST.get('save'):
            test_case_folder_name = "testcases/"+request.GET['qid']
            if request.POST.get('compile'):
                result = compile(dirname + '/' + user_filename, request.POST['textarea'], language)
                if result is None:
                    result = "Compiled Successfully!"
            elif request.POST.get('validate'):
                errors = compile(dirname + '/' + user_filename, request.POST['textarea'], language)
                test_case_folder_name += "_sample/"
                if language == "PYTHON":
                    user_codefile = open(dirname + '/' + user_filename + '.py', 'w')
                    user_codefile.write(request.POST['textarea'])
                    user_codefile.close()
                    result = validate(dirname + '/' + user_filename, test_case_folder_name+'input/', test_case_folder_name+'output/',
                                      language, sample=True)[0].replace('\n', '<br>')
                elif errors is None:
                    result = validate(dirname + '/' + user_filename, test_case_folder_name+'input/', test_case_folder_name+'output/',
                                      language, sample=True)[0].replace('\n', '<br>')
                else:
                    result = errors
            elif request.POST.get('submit_answer'):
                errors = compile(dirname + '/' + user_filename, request.POST['textarea'], language)
                test_case_folder_name += "_real/"
                if language == "PYTHON":
                    user_codefile = open(dirname + '/' + user_filename + '.py', 'w')
                    user_codefile.write(request.POST['textarea'])
                    user_codefile.close()
                    result = validate(dirname + '/' + user_filename, test_case_folder_name+'input/', test_case_folder_name+'output/',
                                      language)
                    save(request.user, request.GET['qid'], request.POST['textarea'],language, result[1])
                    result = result[0]
                elif errors is None:
                    result = validate(dirname + '/' + user_filename, test_case_folder_name+'input/', test_case_folder_name+'output/',
                                      language)
                    save(request.user, request.GET['qid'], request.POST['textarea'],language, result[1])
                    result = result[0]
                else:
                    result = errors

            shutil.rmtree(dirname)
            editor_form = forms.create_editor_form(lang_mode[language],initial=request.POST['textarea'])

    if 'qid' not in request.GET:
        return render_to_response('404.html')
    question = Questions.objects.get(question_code=request.GET['qid'])
    if not question:
        return render_to_response('404.html')
    username = request.user.username

    return render_to_response('index.html', {'output' : result, 'editor_form' : editor_form, 'question': question,
                                             'language' : mark_safe(language_file), 'language_form' : language_form, 'time':time ,'username':username} )

def is_admin(user):
    return user.groups.filter(name="admin").exists();

@user_passes_test(is_admin)
def contest_admin(request):
    if request.method == "POST":
        return HttpResponseRedirect('/contest/configure_question/')
    questions = Questions.objects.all()
    return render_to_response("contest_admin.html", {'questions': questions})

@user_passes_test(is_admin)
def configure_question(request):
    if request.method == "POST":
        Questions.objects.create(question_code = request.POST['question_code'], question_text = request.POST['problem_statement'],
                                 question_marks = request.POST['marks'], input_format = request.POST['input_format'],
                                 output_format  = request.POST['output_format'], sample_input = request.POST['sample_input'],
                                 sample_output = request.POST['sample_output'], constraints = request.POST['constraints'],
                                 explanation = request.POST['explanation'])
        return HttpResponseRedirect('/contest/contest_admin/')

    questions = Questions.objects.values_list('question_code',flat=True)
    return render_to_response("configure_question.html", {'question_codes':questions})

@login_required
def questions(request):
    question_objects = Questions.objects.all()

    time = datetime.datetime.strptime(UserLoginTime.objects.get(user=request.user).login_time, "%b %d, %Y %H:%M:%S") + datetime.timedelta(seconds=2000)
    print time
    print datetime.now()
    if time < datetime.datetime.now():
	    return HttpResponseRedirect('/contest/home')

    time = time.strftime("%b %d, %Y %H:%M:%S")



    print time
    try:
        status_dict = Status.objects.get(team_name=request.user).status
        json_acceptable_string = status_dict.replace("'", "\"")
        status_dict = json.loads(json_acceptable_string)
        for question in question_objects:
            if question.question_code in status_dict:
                status_dict[question.question_code] *= 100
            else:
                status_dict[question.question_code] = 0
    except:
        status_dict = {}
        for question in question_objects:
            status_dict[question.question_code] = 0
    for i in range(len(question_objects)):
        question_objects[i].question_text = question_objects[i].question_text[:150] + "...."
    username = request.user.username
    return render_to_response('questions.html', {'questions': question_objects, 'status': status_dict,'username':username, 'time':time},)

def login_view(request):
    error = ''
    if request.method == 'POST':
        if 'crypt_password' in request.POST:
            username = request.POST['id_no']
            password = request.POST['crypt_password']
            user = authenticate(username=username, password=password)
            if not user is None:
                login(request, user)
                return HttpResponseRedirect('/contest/questions')
            else:
                error="Invalid Authentication"
        elif 'password1' in request.POST:
            username = request.POST['id_no']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            new_user = User.objects.create()
            new_user.username = username
            new_user.set_password(password1)
            new_user.save()
            return HttpResponseRedirect('/contest/home')
    return render_to_response("home.html", {'form': LoginForm(),'reg_form' : RegistrationForm(),'error':error})

def not_found(request):
    return render_to_response("404.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('home')


def user_logged_in_handler(sender, request, user, **kwargs):
    try:
        UserLoginTime.objects.get(user=user)
    except:
        UserLoginTime.objects.create(user = user, login_time = datetime.datetime.now().strftime("%b %d, %Y %H:%M:%S"))

@login_required
def leader_board(request):
    username = request.user.username
    time = (datetime.datetime.strptime(UserLoginTime.objects.get(user=request.user).login_time, "%b %d, %Y %H:%M:%S") \
            + datetime.timedelta(seconds=2000)).strftime("%b %d, %Y %H:%M:%S")
    status_objects=Status.objects.order_by('-total_score','total_time')
    return render_to_response('status_leaderboard.html',{'leaderboard': status_objects,'username':username,'time':time})

def dummy_leader_board(request):
    status_objects = Status.objects.order_by('-total_score', 'total_time')
    return render_to_response('leaderboard.html',
                              {'leaderboard': status_objects})

@login_required
def change_password(request):
    error = ''
    time = (datetime.datetime.strptime(UserLoginTime.objects.get(user=request.user).login_time, "%b %d, %Y %H:%M:%S") \
            + datetime.timedelta(seconds=2000)).strftime("%b %d, %Y %H:%M:%S")
    password_form = ChangePasswordForm()
    if request.method == 'POST':
        if not authenticate(username=request.user.username, password=request.POST['password']) is None:
            try:
                user = User.objects.get(username=request.user.username)
                if request.POST['password1'] == request.POST['password2']:
                    user.set_password(request.POST['password1'])
                    user.save()
                    logout(request)
                    return HttpResponseRedirect("home")
                else:
                    error="Passwords mismatch!"
            except:
                error = "Error changing password"
        else:
            error = "Wrong password!"
    else:
        password_form = ChangePasswordForm()

    return render_to_response('change_password.html', {'password_form':password_form, 'error': error,
                                                       'username':request.user.username,'time':time})
def rules(request):
    return render(request, 'rules.html')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

user_logged_in.connect(user_logged_in_handler)

def register(request):
    error=""
    if request.method == "POST":
        num = request.POST['member_2_phone_no']
        if not num:
            num=None
        try:
            Registration.objects.create(team_name=request.POST['team_name'],
                                        member_1_name = request.POST['member_1_name'],
                                        member_1_phone_no = request.POST['member_1_phone_no'],
                                        member_1_email = request.POST['member_1_email'],
                                        member_2_name = request.POST['member_2_name'],
                                        member_2_phone_no = num,
                                        member_2_email = request.POST['member_2_email'],
                                        )
            new_user = User.objects.create()
            new_user.username = request.POST['team_name']
            new_user.set_password(request.POST['team_name'])
            new_user.save()
        except:
            error = "Sorry the team name is already taken, please try giving a new team name"
            return render_to_response('registration.html', {'error':error})
        return render_to_response('register_thankyou.html',{'error':error})
    return render_to_response('registration.html')

