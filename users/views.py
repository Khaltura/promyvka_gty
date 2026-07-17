from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm


def login_view(request):

    if request.user.is_authenticated:
        return redirect("balance_list")

    if request.method == "POST":

        form = LoginForm(
            request,
            data=request.POST,
        )

        if form.is_valid():

            login(
                request,
                form.get_user(),
            )

            return redirect("balance_list")

    else:
        form = LoginForm()

    return render(
        request,
        "users/login.html",
        {
            "form": form,
        },
    )


def logout_view(request):

    logout(request)

    return redirect("login")