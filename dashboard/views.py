from django.shortcuts import render


def home(request):
    return render(request, "dashboard/home.html")


def enrollment(request):
    return render(request, "dashboard/enrollment.html")


def members(request):
    return render(request, "dashboard/members.html")


def contributions(request):
    return render(request, "dashboard/contributions.html")


def interest(request):
    return render(request, "dashboard/interest.html")


def withdrawals(request):
    return render(request, "dashboard/withdrawals.html")


def claims(request):
    return render(request, "dashboard/claims.html")


def trust_fund(request):
    return render(request, "dashboard/trust_fund.html")


def income_drawdown(request):
    return render(request, "dashboard/income_drawdown.html")


def pensioners_payroll(request):
    return render(request, "dashboard/pensioners_payroll.html")