from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect
from MainApp.models import Snippet, Comment, LANGS
from MainApp.forms import SnippetForm, CommentForm
from MainApp.forms import UserRegistrationForm
from django.contrib import auth
from django.db.models import Q
from django.contrib import messages


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


@login_required
def add_snippet_page(request):
    if request.method == "GET":
        form = SnippetForm()
        context = {
            'pagename': 'Добавление нового сниппета',
            'form': form
        }
        return render(request, 'pages/add_snippet.html', context)
    if request.method == "POST":
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            if request.user.is_authenticated:
                snippet.user = request.user
                snippet.save()
            return redirect("snippets_list")
        return render(request, 'pages/add_snippet.html', {'form': form})


def snippets_page(request):
    user = request.user
    pagename = 'Просмотр сниппетов'
    my = request.GET.get('my')
    lang = request.GET.get('filter_by_lang')
    sort = request.GET.get('sort')
    if isinstance(user, AnonymousUser):
        if not lang:
            snippets = Snippet.objects.filter(private=False)
        else:
            snippets = Snippet.objects.filter(private=False, lang=lang)
    else:
        if not request.GET.get('my'):
            if not lang:
                snippets = Snippet.objects.filter(Q(private=False) | Q(private=True, user=user))
            else:
                snippets = Snippet.objects.filter(Q(private=False) | Q(private=True, user=user)).filter(lang=lang)
        else:
            pagename = 'Мои сниппеты'
            my = True
            if not lang:
                snippets = Snippet.objects.filter(user=user)
            else:
                snippets = Snippet.objects.filter(user=user, lang=lang)
    if sort:
        snippets = snippets.order_by(sort)
    context = {'pagename': pagename,
               'snippets': snippets,
               'langs': [{'val': item[0], 'name': item[1]} for item in LANGS],
               'selected_lang': lang,
               'my': my,
               'count': snippets.count()}
    return render(request, 'pages/view_snippets.html', context)


def snippet_detail(request, snippet_id, edit=False):
    try:
        snippet = Snippet.objects.get(id=snippet_id)
    except ObjectDoesNotExist:
        raise Http404
    if edit:
        context = {'pagename': 'Редактирование сниппета',
                   'edit': True,
                   'snippet': snippet}
        return render(request, 'pages/snippet_detail.html', context)
    comment_form = CommentForm
    context = {'pagename': 'Просмотр сниппета',
               'snippet': snippet, 'comment_form': comment_form, 'comments': snippet.comments.all(),
               'lang_name': dict(LANGS).get(snippet.lang)}
    return render(request, 'pages/snippet_detail.html', context)


def snippet_search(request):
    try:
        snippet = Snippet.objects.get(id=request.POST.get('id'))
        context = {'pagename': 'Просмотр сниппета',
                   'snippet': snippet}
        return render(request, 'pages/snippet_detail.html', context)
    except ObjectDoesNotExist:
        raise Http404


@login_required()
def snippet_save(request, snippet_id):
    snippet = Snippet.objects.get(id=snippet_id)
    if request.user.id == snippet.user.id or request.user.is_superuser:
        snippet.name = request.POST.get('name')
        snippet.code = request.POST.get('code')
        if request.POST.get('private'):
            snippet.private = True
        else:
            snippet.private = False
        snippet.save()
        return redirect("snippets_list")
    return HttpResponseForbidden('403 Forbidden')


@login_required()
def snippet_delete(request, snippet_id):
    snippet = Snippet.objects.get(id=snippet_id)
    snippet.delete()
    return redirect("snippets_list")


@login_required()
def logout(request):
    auth.logout(request)
    return redirect('home')


def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
        else:
            context = {'pagename': 'PythonBin',
                       'errors': ['wrong username or password']}
            return render(request, 'pages/index.html', context)
    return redirect('home')


@login_required()
def comment_add(request, snippet_id):
    if request.method == "POST":
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.snippet = Snippet.objects.get(pk=snippet_id)
            comment.save()
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    raise Http404


@login_required()
def comment_edit(request, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    snippet = comment.snippet
    if request.user.id == comment.author_id:
        context = {'pagename': 'Редактирование комментария',
                   'comment_edit': True,
                   'snippet': snippet,
                   'comment': comment}
        return render(request, 'pages/snippet_detail.html', context)
    return HttpResponseForbidden('403 Forbidden')


@login_required()
def comment_save(request, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    if request.user.id == comment.author_id:
        new_text = request.POST.get('comment_text')
        comment.text = new_text
        comment.save()
        messages.success(request, 'Комментарий отредактирован')
        return redirect(f'/snippet/{comment.snippet.id}')
    return HttpResponseForbidden('403 Forbidden')


@login_required()
def comment_delete(request, comment_id):
    if request.user.is_superuser:
        comment = Comment.objects.get(pk=comment_id)
        snippet_id = comment.snippet.id
        comment.delete()
        return redirect(f'/snippet/{snippet_id}')
    return HttpResponseForbidden('403 Forbidden')


def create_user(request):
    form = UserRegistrationForm
    if request.method == 'GET':
        context = {'pagename': 'Регистрация', 'form': form}
        return render(request, 'pages/register.html', context)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
        return render(request, 'pages/register.html', {'Pagename': 'Регистрация', 'form': form})
