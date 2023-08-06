from typing import Optional

import jwt
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect


class TokenMissingError(Exception):
    def __init__(self, message):
        super().__init__(message)


class AuthenticatorKeyMissingError(Exception):
    def __init__(self, message):
        super().__init__(message)


class IssuerNotValid(Exception):
    def __init__(self, message):
        super().__init__(message)


def _encode_jwt(request) -> Optional[dict]:
    token = request.GET.get('token')
    if token is None:
        raise TokenMissingError()

    if settings.AUTHENTICATOR_KEY is None:
        return AuthenticatorKeyMissingError()

    data = jwt.decode(
        token,
        settings.AUTHENTICATOR_KEY,
        algorithms="HS256",
        options={
            "require": [
                "exp",
                "iss",
                "nbf"
            ]
        }
    )
    if data.get('iss') not in ['shopcloud-secrethub', 'shopcloud-tower']:
        raise IssuerNotValid()

    return data


def login_view(request):
    try:
        data = _encode_jwt(request)
    except TokenMissingError:
        return HttpResponse('Token missing', status=400)
    except AuthenticatorKeyMissingError:
        return HttpResponse('Authenticator key missing', status=500)
    except IssuerNotValid:
        return HttpResponse('Issuer not valid', status=400)
    except jwt.ExpiredSignatureError:
        return HttpResponse('Token Signature Error', status=400)
    except Exception:
        return HttpResponse('Invalid token', status=400)

    password = User.objects.make_random_password()
    user = User.objects.filter(username=data.get('username')).first()
    if user is None:
        user = User.objects.create(
            username=data.get('username'),
            password=password,
        )

    user.set_password(password)
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True if "admin" in data.get('scopes', []) else False
    user.save()

    login(request, user)

    url = '/'
    next = request.GET.get('next')
    if next is not None:
        if next.startswith('/'):
            next = next[1:]
        url = f"{url}{next}"

    return redirect(url, permanent=False)


def login_credential_rotation(request):
    try:
        data = _encode_jwt(request)
    except TokenMissingError:
        return HttpResponse('Token missing', status=400)
    except AuthenticatorKeyMissingError:
        return HttpResponse('Authenticator key missing', status=500)
    except IssuerNotValid:
        return HttpResponse('Issuer not valid', status=400)
    except jwt.ExpiredSignatureError:
        return HttpResponse('Token Signature Error', status=400)
    except Exception:
        return HttpResponse('Invalid token', status=400)

    user = User.objects.filter(username=data.get('username')).first()
    if user is None:
        return JsonResponse({
            'status': 'not-found',
        }, status=200)

    password = User.objects.make_random_password()
    user.set_password(password)
    user.save()

    return JsonResponse({
        'status': 'ok',
    }, status=201)


def session_rotation(request):
    try:
        data = _encode_jwt(request)
    except TokenMissingError:
        return HttpResponse('Token missing', status=400)
    except AuthenticatorKeyMissingError:
        return HttpResponse('Authenticator key missing', status=500)
    except IssuerNotValid:
        return HttpResponse('Issuer not valid', status=400)
    except jwt.ExpiredSignatureError:
        return HttpResponse('Token Signature Error', status=400)
    except Exception:
        return HttpResponse('Invalid token', status=400)

    if 'session-expire' not in data.get('scopes', []):
        return HttpResponse('missing scope session-expire', status=400)

    Session.objects.all().delete()

    return JsonResponse({
        'status': 'ok',
    }, status=201)


def users_list(request):
    try:
        data = _encode_jwt(request)
    except TokenMissingError:
        return HttpResponse('Token missing', status=400)
    except AuthenticatorKeyMissingError:
        return HttpResponse('Authenticator key missing', status=500)
    except IssuerNotValid:
        return HttpResponse('Issuer not valid', status=400)
    except jwt.ExpiredSignatureError:
        return HttpResponse('Token Signature Error', status=400)
    except Exception:
        return HttpResponse('Invalid token', status=400)

    if 'users-list' not in data.get('scopes', []):
        return HttpResponse('missing scope session-expire', status=400)

    users = [{
        'id': x.id,
        'username': x.username,
        'is_active': x.is_active,
        'is_staff': x.is_staff,
        'is_superuser': x.is_superuser,
        'last_login': x.last_login,
        'date_joined': x.date_joined,
        'email': x.email,
    } for x in User.objects.filter(is_active=True).all()]

    return JsonResponse({
        'count': len(users),
        'results': users,
    }, status=201)
