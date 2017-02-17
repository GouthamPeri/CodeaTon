from django.shortcuts import render, render_to_response
import os
import datetime
# Create your views here.

def contest(request):
    string=''
    if request.method == 'POST':
        st = str(datetime.datetime.now().microsecond)
        string = request.POST['code']
        print(string)

        f=open(st + '.c', 'w')
        f.write(string)
        f.close()
        os.system('gcc ' + st + '.c -o ' + st +'.o')
        os.system(st + '.o > ' + st + '.txt')
        output = open(st + '.txt', 'r')
        string = output.read()
        output.close()
        os.remove(st + '.txt');
        os.remove(st + '.o');
        os.remove(st + '.c');

    return render_to_response('index.html', {'output' : string} );