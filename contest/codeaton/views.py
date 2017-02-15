from django.shortcuts import render, render_to_response
import os
# Create your views here.

def contest(request):
    str=''
    if request.method == 'POST':

        string = request.POST['code']
        print(string)
        f=open('file.c', 'w')
        f.write(string)
        print(string)
        f.close()
        os.system('gcc file.c')
        os.system('a.exe > output.txt')
        output = open('output.txt', 'r')
        str = output.read()
        output.close()


    return render_to_response('index.html', {'output' : str} );