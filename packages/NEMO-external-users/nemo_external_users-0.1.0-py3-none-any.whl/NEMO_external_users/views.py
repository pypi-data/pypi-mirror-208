from django.shortcuts import render
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.shortcuts import HttpResponseRedirect, redirect
from django.urls import resolve, reverse
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from .backends import SettingsBackend, ExternalUsersBackend
from .forms import SignUpForm
from .models import ExternalUser
from .tokens import account_activation_token


def landing(request):
    return render(request, settings.LOGIN_REDIRECT_URL)


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        for backend in [SettingsBackend, ExternalUsersBackend]:
            user = backend().authenticate(request, username=username, password=password)
            if user is not None:
                break
        else:
            messages.error(request, 'Incorrect email address or password. Please try again, or create an account if you don\'t have one yet')
            return redirect("landing")

        if user is not None:
            # login(request, user, backend='backends.SettingsBackend')
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            try:
                next_page = request.GET[REDIRECT_FIELD_NAME]
                resolve(next_page)  # Make sure the next page is a legitimate URL for NEMO
            except:
                next_page = reverse("landing")
            return HttpResponseRedirect(next_page)
        else:
            return HttpResponseRedirect(settings.LOGIN_URL)
    else:
        return render(request, 'authenticate/login.html', {})


def create_account(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get('email'))
            return redirect('landing')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SignUpForm()
    ctx = {
        'form': form
    }
    return render(request, 'authenticate/create_account.html', ctx)


def account(request):
    return render(request, 'users/account.html')


def password_change(request):
    return redirect('landing')


def activate_email(request, user, to_email):
    mail_subject = 'Activate your user account'
    message = render_to_string('activate_account.html', {
        'user': user,
        'domain': request.get_host(),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(mail_subject, message, from_email=settings.EMAIL_HOST_USER, to=[to_email])

    if email.send():
        messages.success(request, f'Confirmation email sent to {to_email}. Please check your mailbox.')
    else:
        messages.error(request, f'Problem sending email to {to_email}. Check if you typed it in correctly.')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = ExternalUser.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation. Now you can log in.")
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('landing')
