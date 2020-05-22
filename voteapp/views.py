import os
from string import ascii_letters, digits
from math import ceil

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect

from voteapp.forms import AddVotingForm, AuthForm, OptionTextForm, \
    ImageForm, SignUpForm, RecoverForm, CommentForm
from voteapp.models import Poll, Option, Avatar, Vote, Tag, Comment


def index(request):
    context = {}
    votings = Poll.objects.filter(is_deleted=False, is_active=True)
    context['polls'] = [(item.id, item.name, item.text,) for item in votings][::-1]
    return render(request, 'index.html', context)


@login_required
def add_voting(request):
    context = {'user': request.user}
    if request.POST:
        form = AddVotingForm(request.POST)
        if form.is_valid():
            checkbox = True if 'check' in form.data else False
            p = Poll(name=form.data['name'], text=form.data['text'], is_checkbox=checkbox, user=request.user)
            p.save()
            context['id'] = p.id
        else:
            context['errors'] = form.errors
        return render(request, 'add_result.html', context)
    else:
        form = AddVotingForm()
        context['add_form'] = form
        return render(request, 'add.html', context)


@login_required
def add_voting_option(request, poll_id):
    context = {}

    OptionTextFormSet = formset_factory(OptionTextForm)
    formset = OptionTextFormSet()
    context['formset'] = formset

    poll_options = []
    poll = Poll.objects.get(id=poll_id)
    context['options'] = Option.objects.filter(voting=poll)
    if poll.user != request.user:
        return HttpResponse('403 Forbidden')
    if poll.is_active:
        return redirect('/show/{}'.format(poll_id))
    else:
        if request.method == 'GET':
            return render(request, 'poll_edit.html', context)
        if request.method == 'POST':
            option_formset = OptionTextFormSet(request.POST)
            if option_formset.is_valid():
                for form in option_formset:
                    text = form.cleaned_data.get('text')
                    if text:
                        poll_options.append(
                            Option(
                                text=text,
                                voting=poll
                            )
                        )
                if poll_options:
                    Option.objects.bulk_create(poll_options)
        return redirect('/show/{}'.format(poll_id))


@login_required
def show_voting(request, id):
    context = {'id': id, }
    poll = Poll.objects.get(id=id)
    if poll:
        context['poll'] = poll
        is_voted = Vote.objects.filter(user=request.user, poll=poll).first() or poll.user == request.user
        context['options'] = Option.objects.filter(voting=poll)
        if is_voted:
            context['is_voted'] = True
            all = Vote.objects.filter(poll=poll).count()
            if all:
                percent = []
                for option in context['options']:
                    res = Vote.objects.filter(option=option).count() / float(all)
                    res *= 100
                    res = int(ceil(res)) if res / 1 >= 0.5 else int(res)
                    percent.append(res)
            else:
                percent = [0 for _ in context['options']]
            context['options'] = zip(context['options'], percent)
    else:
        context['error'] = True
    context['user'] = request.user
    context['total_options'] = Option.objects.filter(voting=poll).count()
    comments = Comment.objects.filter(poll=poll)
    context['comments'] = [
        (
            item.user,
            item.text,
            item.datetime
        ) for item in comments
    ]
    if request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            p = Comment(text=form.data['text'], user=request.user, poll=poll)
            p.save()
            return redirect('/show/{}'.format(id))
        else:
            context['errors'] = form.errors
            return redirect('/show/{}'.format(id))
    else:
        form = CommentForm()
        context['add_form'] = form
        return render(request, 'show_voting.html', context)


@login_required
def delete_poll(request, poll_id):
    poll = Poll.objects.filter(id=poll_id).first()
    if request.user == poll.user or request.user.is_superuser:
        poll.is_deleted = True
        poll.save()
    return redirect('/')


def login_view(request):
    context = {}
    if request.POST:
        form = AuthForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.data['username'], password=form.data['password'])
            if user is not None:
                login(request, user)
                return redirect(index)
            else:
                return redirect('/signin')
        else:
            return redirect('/signin')
    else:
        form = AuthForm()
        context['auth_form'] = form
        return render(request, 'auth.html', context)


def logout_view(request):
    logout(request)
    return redirect(index)


def add_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(index)
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


@login_required
def change_password(request):
    context = {}
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('/')
        else:
            return redirect('profile/new_pass/')
    else:
        form = PasswordChangeForm(request.user)
        context['new_pass_form'] = form
    return render(request, 'new_pass.html', context)


def reset_password(request):
    context = {}
    if request.method == 'POST':
        form = RecoverForm(request.POST)
        if form.is_valid():
            name = form.data['username']
            u = User.objects.filter(username=name).first()
            if u is not None:
                new_password = User.objects.make_random_password(length=10, allowed_chars=ascii_letters + digits)
                u.set_password(new_password)
                u.save()
                message = 'Hi! Your new password is: ' + new_password
                mail = u.email
                send_mail('New Password', message, 'from@example.com', [mail])
                return redirect(index)
            else:
                return redirect('/')
        else:
            return redirect('signin/')
    else:
        form = RecoverForm()
        context['name_form'] = form
    return render(request, 'rec_pass.html', context)


@login_required
def user_profile(request):
    context = {}
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = Avatar.objects.filter(user=request.user).first()
            if img is not None:
                if str(img.img) != 'voteapp/static/avatars/default.png':
                    os.remove(str(img.img))
            else:
                img = Avatar(user=request.user, )
            img.img = form.cleaned_data['img']
            img.save()
            return redirect("/profile")
        else:
            return redirect('/profile')
    else:
        img = Avatar.objects.filter(user=request.user).first()
        img = str(img.img) if img is not None else 'voteapp/static/avatars/default.png'
        context['avatar'] = img[15:]
        voting = (Poll.objects.filter(user=request.user, is_deleted=False))
        context['username'] = request.user.username
        context['user_created_polls'] = [
            (
                item.id,
                item.name
            ) for item in voting
        ]
        return render(request, 'user_profile.html', context)


def all_are_in(tags, poll):
    for tag in tags:
        suitable_to_cur = Poll.objects.filter(tag=tag)
        print("---", suitable_to_cur, "---", end='\n')
        if poll not in suitable_to_cur or not tags:
            return False
    return True


def show_answer(request):
    context = {}
    votings = Poll.objects.filter(is_active=True, is_deleted=False)
    s = request.GET['quest']
    a = s.split('#')
    text = a[1:]
    if len(a) > 1:
        a[0] = a[0][:a[0].find(' ')]
    written_tags = Tag.objects.filter(text__in=text)
    context['search'] = s
    context['suitable_pools'] = []
    for item in votings:
        if (a[0] in item.user.username or a[0] in item.name or a[0] in item.text) \
                and (all_are_in(written_tags, item)) and a[0]:
            context['suitable_pools'].append((item.id, item.name))
    return render(request, 'search_answer.html', context)


@login_required
def vote(request, poll_id):
    if request.method == 'POST':
        if 'option' not in request.POST:
            return redirect('/show/{}'.format(poll_id))
        poll = Poll.objects.get(id=poll_id)
        for opt in dict(request.POST)['option']:
            option = Option.objects.get(id=opt)
            vote = Vote(user=request.user, option=option, poll=poll)
            vote.save()
        return redirect('/show/{}'.format(poll_id))
    else:
        return redirect('/')


@login_required()
def activate_poll(request, poll_id):
    poll = Poll.objects.get(id=poll_id)
    if request.method == 'POST':
        if poll.user == request.user and Option.objects.filter(voting=poll).count() > 0:
            poll.is_active = True
            poll.save()
            return redirect(show_voting, poll_id)
    return HttpResponse("403 Prohibited")
