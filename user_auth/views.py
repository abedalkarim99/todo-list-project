from django.shortcuts import render ,redirect , get_object_or_404
from django.contrib.auth import login , authenticate ,logout ,update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import *

# imports for generate_password function
import random





def login_user(request):
    if request.user.is_authenticated:
        messages.info(request, 'u are aready loged in')
        return redirect('home')
    else :
        if request.method == "GET":
            context = {
                'login_open': True,
            }
            return render(request, 'todo/index.html',context)

        elif request.method == "POST":
            user_username = request.POST['username']
            user_password = request.POST['password']
            user = authenticate(request, username=user_username, password=user_password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, "your username or password is incorrect , please try again")
                return redirect("home")

@login_required(login_url='login_user')
def logout_user(request) :
    if request.method == "POST" :
        logout(request)
        return redirect('home')

def sign_up_user(request) :
    if request.user.is_authenticated:
        messages.info(request,'u are aready Register')
        return redirect('home')
    else :
        if request.method == "GET" :
            context = {
                'title': 'Sign Up'
            }
            return render(request, 'todo/index.html',context)
        elif request.method == "POST" :
            user_first_name = request.POST['first_name']
            user_last_name = request.POST['last_name']
            user_username = request.POST['username']
            user_email = request.POST['email']
            user_password1 = request.POST['password1']
            user_password2 = request.POST['password2']

            if (user_first_name=="") or (user_last_name=="") or (user_username=="") or (user_email=="") or (user_password1=="") :
                messages.info(request, 'please full the blank inputs')
                return redirect('home')

            elif  User.objects.filter(username=user_username).exists():
                messages.info(request, 'username is taken, try another one')
                return redirect('home')


            elif User.objects.filter(email= user_email).exists() :
                messages.info(request, 'email is taken, try another one')
                return redirect('home')

            elif user_password1 != user_password2 :
                messages.info(request, 'password not matching')
                return redirect('home')


            else :
                user = User.objects.create_user(first_name = user_first_name,
                                                last_name = user_last_name,
                                                username = user_username,
                                                email = user_email,
                                                password = user_password1
                                                )
                user.save()
                UserProfile.objects.create(
                    user=user,
                )
                login(request,user)
                return redirect("home")


@login_required(login_url='login_user')
def delete_account(request) :
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == "POST":
        text_confirm = user.username + "-delete my account"
        if (request.POST['confirmation'] == text_confirm) and (
        user.check_password(request.POST['password_for_deleting_account'])):
            logout(request)
            user.delete()
            messages.info(request, "Your account was deleted sucssfully")
        else:
            messages.info(request, "the opreation was not sucssfully")
        return redirect('account_settings')


@login_required(login_url='login_user')
def change_password(request) :
    if request.method == "GET" :
        return render(request,'user_auth/change_password.html')
    if request.method == "POST" :
        user = get_object_or_404(User, pk=request.user.id)
        user_old_password = request.POST['old_password']
        user_new_password = request.POST['new_password']
        user_new_password2 = request.POST['new_password2']

        if not user.check_password(user_old_password):
            messages.info(request, 'the password(current) You entered is incorrect')
        elif user_new_password != user_new_password2 :
            messages.info(request, 'the new password did not matching')
        elif user_old_password == user_new_password :
            messages.info(request, 'the new password can not be the old password')
        else :
            user.set_password(user_new_password)
            user.save()
            # update_session_auth_hash(request, user)
            messages.info(request, "Your password was changed sucssfully , please login again")
        return redirect('account_settings')

def edit_information(request) :
    if request.method == "GET" :
        context = {

        }
        return render(request,"todo/index.html",context)
    elif request.method == "POST" :
        user = get_object_or_404(User, pk=request.user.id)
        userProfile = UserProfile.objects.get(user=user)

        user_first_name = request.POST['first_name']
        user_last_name = request.POST['last_name']
        user_username = request.POST['username']
        user_email = request.POST['email']
        user_gender = request.POST['gender']

        user.first_name = user_first_name
        user.last_name = user_last_name
        userProfile.gender = user_gender
        userProfile.save()

        uniqe_username = User.objects.filter(username=user_username)
        uniqe_email = User.objects.filter(email=user_email)
        same_username = user.username == user_username
        same_email = user.email == user_email



        if (uniqe_username.__len__() == 0) and (uniqe_email.__len__() == 0) :
            user.username = user_username
            user.email = user_email
            user.save()
            messages.info(request,"the changes done sucssfully")

        elif (uniqe_username.__len__() == 0) and (uniqe_email.__len__() != 0) :
            user.username = user_username
            user.save()
            if not same_email :
                messages.info(request,"the changes done , but the email is alrady taken , try another one !")
            else :
                messages.info(request, "the changes done sucssfully")

        elif (uniqe_username.__len__() != 0) and (uniqe_email.__len__() == 0) :
            user.email = user_email
            user.save()
            if not same_username :
                messages.info(request,"the changes done , but the username is alrady taken , try another one !")
            else :
                messages.info(request, "the changes done sucssfully")

        else :
            user.save()
            if (not same_username) and (not same_email) :
                messages.info(request,"the changes done , but the username and email is alrady taken , try another ones!")
            elif (same_username) and (not same_email) :
                messages.info(request,"the changes done , but the email is alrady taken , try another one !")
            elif (not same_username) and (same_email):
                messages.info(request,"the changes done , but the username is alrady taken , try another one !")
            else:
                messages.info(request, "the changes done sucssfully")
        return redirect("account_settings")






# generate_password function view
def generate_password(request) :
    if request.method == "GET" :
        context = {
            'title' : 'Password Generator' ,
            'range' : range(7,31) ,

        }
        return render(request,'user_auth/generate_password_function/generate_password.html', context)
    elif request.method == "POST" :
        characters = list('abcdefghijklmnopqrstuvwxyz')

        if request.POST.get('uppercase'):
            characters.extend(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        if request.POST.get('special_characters'):
            characters.extend(list('!@#$%^&*()<>?;.'))
        if request.POST.get('numbers'):
            characters.extend(list('0123456789'))
        if request.POST.get('arabic_letters'):
            characters.extend(list('ابتثجحخدذرزسشصضطظعغفقكلمنهوي'))

        length = int(request.POST.get('length', 12))

        password_generated = ''
        for i in range(length):
            password_generated += random.choice(characters)
        context =  {
            'title' : 'the result' ,
            'password': password_generated
        }

        return render(request,
                      'user_auth/generate_password_function/generate_password_result.html',
                      context)


#error views
def error_404(request,exception) :
    context = {

    }
    return render(request,'user_auth/errors/error_404.html',context)