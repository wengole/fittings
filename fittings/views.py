from django.shortcuts import render, redirect
from .tasks import create_fit
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required()
def dashboard(request):
    msg = None

    ctx = {'msg': msg}
    return render(request, 'fittings/dashboard.html', context=ctx)


@login_required()
def add_fit(request):
    msg = None
    if request.METHOD == 'POST':
        etf_text = request.POST['eft']
        description = request.POST['description']

        create_fit.delay(etf_text, description)
        # Add success message, with note that it may take some time to see the fit on the dashboard.
        return redirect('fittings:dashboard')

    ctx = {'msg': msg}
    return render(request, 'fittings/add_fit.html', context=ctx)
