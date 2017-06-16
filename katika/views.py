from django.shortcuts import render


def busted(request):

    print("formalities")

    #return render(request, 'home.html', {'incidents': incidents})
    return render(request, 'busted.html')


def home(request):

    #return render(request, 'home.html', {'incidents': incidents})
    return render(request, 'home.html')


def about(request):

    return render(request, 'about.html')

