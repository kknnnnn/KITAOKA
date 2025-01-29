# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}さんが登録されました！')
            return redirect('login')
        else:
            # バリデーションエラーを表示
            messages.error(request, '登録に失敗しました。')
            # エラーをテンプレートに渡す
            return render(request, 'registration/register.html', {'form': form})
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('search_view')  # ホームページへのリダイレクト
        else:
            messages.error(request, 'ユーザー名またはパスワードが正しくありません。')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('search_view')  # ログインページへのリダイレクト
