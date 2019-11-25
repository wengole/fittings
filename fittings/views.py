from django.shortcuts import render, redirect
from .tasks import create_fit
from django.contrib.auth.decorators import login_required
from django.db.models import Subquery, OuterRef, Case, When, Value, CharField, F, Exists
from .models import Doctrine, Fitting, Type, FittingItem, DogmaEffect


# Create your views here.
def _build_slots(type_id):
    ship = Type.objects.get(type_id=type_id)
    attributes = (12, 13, 14, 1137, 1367, 2056)

    attributes = ship.dogma_attributes.filter(attribute_id__in=attributes)

    slots = {}
    for attribute in attributes:
        if attribute.attribute_id == 1367:
            slots['sub'] = 4
        elif attribute.attribute_id == 12:
            slots['low'] = int(attribute.value)
        elif attribute.attribute_id == 13:
            slots['med'] = int(attribute.value)
        elif attribute.attribute_id == 14:
            slots['high'] = int(attribute.value)
        elif attribute.attribute_id == 1137:
            slots['rig'] = int(attribute.value)

    return slots


@login_required()
def dashboard(request):
    msg = None

    doc_dict = {}
    docs = Doctrine.objects.all()
    for doc in docs:
        doc_dict[doc.pk] = doc.fittings.all()
    ctx = {'msg': msg, 'docs': docs, 'doc_dict': doc_dict}
    return render(request, 'fittings/dashboard.html', context=ctx)


@login_required()
def add_fit(request):
    msg = None
    if request.method == 'POST':
        etf_text = request.POST['eft']
        description = request.POST['description']

        create_fit.delay(etf_text, description)
        # Add success message, with note that it may take some time to see the fit on the dashboard.
        return redirect('fittings:dashboard')

    ctx = {'msg': msg}
    return render(request, 'fittings/add_fit.html', context=ctx)


@login_required()
def view_fit(request, fit_id):
    ctx = {}
    try:
        fit = Fitting.objects.get(pk=fit_id)
    except Fitting.DoesNotExist:
        msg = ('warning', 'Fit not found!')

        return redirect('fittings:dashboard')

    types = Type.objects.filter(type_id=OuterRef('type_id'))
    items = FittingItem.objects.filter(fit=fit).annotate(item_name=Subquery(types.values('name')))

    fittings = {'Cargo': []}
    for item in items:
        if item.flag == "Cargo":
            fittings['Cargo'].append(item)
        else:
            fittings[item.flag] = item

    ctx['slots'] = _build_slots(fit.ship_type_type_id)
    ctx['fit'] = fit
    ctx['fitting'] = fittings
    return render(request, 'fittings/view_fit.html', context=ctx)


@login_required()
def add_doctrine(request):
    pass


@login_required()
def view_doctrine(request, doctrine_id):
    pass