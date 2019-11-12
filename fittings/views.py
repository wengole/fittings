from django.shortcuts import render
from .tasks import create_fit


# Create your views here.
def dashboard(request):
    msg = None
    if request.method == 'POST':
        eft_text = request.POST['eft']
        create_fit.delay(eft_text, "Test")

    ctx = {'msg': msg}
    return render(request, 'fittings/dashboard.html', context=ctx)
