import json
import pandas
import random
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import CreateUserForm, PlayerForm, RoleForm
from .models import Player, Role, GameParameters, RoleAssignment, SavedGame


# Create your views here.
class Game:
    def __init__(self, roles, score, title):
        self.roles = roles
        self.score = score
        self.title = title


@login_required(login_url='/login')
def home(request):
    player_form = PlayerForm()
    player_list = Player.objects.filter(user=request.user)
    if not Role.objects.filter(user=request.user):
        df = pandas.read_csv('basicroles.csv')
        for index, row in df.iterrows():
            row = Role(
                score=row['role_score'],
                title=row['role_title'],
                description=row['role_description'],
                alignment=row['role_alignment'],
                type=row['role_type'],
                user=request.user
            )
            row.save()

        j = {key: True for key in
             Role.objects.filter(user=request.user).order_by().values_list('type', flat=True).distinct()}
        initial_prefs = {
            'typePref': j,
            'wolfCount': 2,
            'balanceGoal': 0,
            'playerCount': 7,
            'games_dict': {},
        }
        initial_prefs = json.dumps(initial_prefs)
        preferences = GameParameters(preferences=initial_prefs, user=request.user)
        preferences.save()

    game_params = GameParameters.objects.get(user=request.user)
    game_params_dict = json.loads(game_params.preferences)
    role_type_toggles = game_params_dict['typePref']
    wolf_count = game_params_dict['wolfCount']
    balance_goal = game_params_dict['balanceGoal']

    role_assignments = RoleAssignment.objects.filter(user=request.user)
    game_score = sum([i.role.score for i in role_assignments])
    player_list = Player.objects.filter(user=request.user)
    available_saved_games = SavedGame.objects.filter(user=request.user).filter(player_count=len(player_list))
    context = {
        'player_form': player_form,
        'player_list': player_list,
        'role_type_toggles': role_type_toggles,
        'wolf_count': wolf_count,
        'balance_goal': balance_goal,
        'role_assignments': role_assignments,
        'game_score': game_score,
        'available_saved_games': available_saved_games,
    }
    return render(request, 'wolfrollapp/home.html', context)


def speedRollerHome(request):
    game_params = GameParameters.objects.get(user=request.user)
    game_params_dict = json.loads(game_params.preferences)
    role_type_toggles = game_params_dict['typePref']
    wolf_count = game_params_dict['wolfCount']
    balance_goal = game_params_dict['balanceGoal']
    player_count = game_params_dict['playerCount']
    games_dict = game_params_dict['games_dict']

    games_list = []
    for key in games_dict:
        new_game = Game(roles=games_dict[key]['roles'], score=games_dict[key]['score'], title=key)
        games_list.append(new_game)

    all_saved_games = SavedGame.objects.filter(user=request.user)

    context = {
        'role_type_toggles': role_type_toggles,
        'wolf_count': wolf_count,
        'balance_goal': balance_goal,
        'player_count': player_count,
        'games_dict': games_dict,
        'games_list': games_list,
        'all_saved_games': all_saved_games,
    }
    return render(request, 'wolfrollapp/speedRoller.html', context)


def speedRoll(request):
    game_params = GameParameters.objects.get(user=request.user)
    game_params_dict = json.loads(game_params.preferences)
    role_type_toggles = game_params_dict['typePref']
    wolf_count = game_params_dict['wolfCount']
    balance_goal = game_params_dict['balanceGoal']
    player_count = game_params_dict['playerCount']
    games_dict = game_params_dict['games_dict']

    wolf_roles = Role.objects.filter(user=request.user, type="Wolf")
    available_types = [key for key in role_type_toggles if role_type_toggles[key]]
    available_roles = Role.objects.filter(user=request.user, type__in=available_types)
    new_games_dict = {}
    for i in range(5):
        roles_list = []
        for wolf in range(wolf_count):
            roles_list.append(random.choice(wolf_roles))
        while player_count > len(roles_list):
            if sum([i.score for i in roles_list]) > balance_goal:
                roles_list.append(random.choice([i for i in available_roles if i.score < 0 and i.alignment == 'Town']))
            elif sum([i.score for i in roles_list]) <= balance_goal:
                roles_list.append(random.choice([i for i in available_roles if i.score >= 0]))
        game_score = sum([i.score for i in roles_list])
        new_games_dict['Game ' + str(i+1)] = {'roles': [i.title for i in roles_list], 'score': game_score}
    new_prefs = {
        'typePref': role_type_toggles,
        'wolfCount': wolf_count,
        'balanceGoal': balance_goal,
        'playerCount': player_count,
        'games_dict': new_games_dict,
    }
    j = json.dumps(new_prefs)
    GameParameters.objects.filter(user=request.user).update(preferences=j)
    print(new_games_dict)
    return redirect('wolfrollapp:speedRollerHome')


def saveGame(request, title):
    try:
        print("trying")
        SavedGame.objects.filter(user=request.user).get(name=request.POST.get('name'))
        print("got it")
        messages.warning(request, "You have already used that name! Choose a new name!")
    except SavedGame.DoesNotExist:
        game_params = GameParameters.objects.get(user=request.user)
        game_params_dict = json.loads(game_params.preferences)
        player_count = game_params_dict['playerCount']
        roles_list = json.dumps(game_params_dict['games_dict'][title])
        new_saved_game = SavedGame(name=request.POST.get('name'), roles=roles_list, user=request.user, player_count=player_count)
        new_saved_game.save()

    return redirect('wolfrollapp:speedRollerHome')


def rollGame(request):
    game_params = GameParameters.objects.get(user=request.user)
    game_params_dict = json.loads(game_params.preferences)
    role_type_toggles = game_params_dict['typePref']
    wolf_count = game_params_dict['wolfCount']
    balance_goal = game_params_dict['balanceGoal']


    player_list = Player.objects.filter(user=request.user)

    wolf_roles = Role.objects.filter(user=request.user, type="Wolf")
    available_types = [key for key in role_type_toggles if role_type_toggles[key]]
    available_roles = Role.objects.filter(user=request.user, type__in=available_types)

    # reset assignments
    RoleAssignment.objects.filter(user=request.user, locked=False).delete()
    locked_game = RoleAssignment.objects.filter(user=request.user)
    roles_list = []
    locked_roles = []
    for i in locked_game:
        roles_list.append(Role.objects.filter(user=request.user, title=i.role.title).get())
        locked_roles.append(Role.objects.filter(user=request.user, title=i.role.title).get())

    revised_wolf_count = wolf_count - len([i for i in roles_list if i.type == "Wolf"])

    RoleAssignment.objects.filter(user=request.user).delete()

    for i in range(revised_wolf_count):
        roles_list.append(random.choice(wolf_roles))

    while len(player_list) > len(roles_list):
        game_score = 0
        for i in roles_list:
            game_score += i.score
        if game_score > balance_goal:
            roles_list.append(random.choice([i for i in available_roles if i.score < 0 and i.alignment == 'Town']))
        elif game_score <= balance_goal:
            roles_list.append(random.choice([i for i in available_roles if i.score >= 0]))

    game_score = 0
    for i in roles_list:
        game_score += i.score
    random.shuffle(roles_list)
    random.shuffle(list(player_list))
    for i in range(len(roles_list)):
        assignment = RoleAssignment(
            player=player_list[i],
            role=roles_list[i],
            locked=True if roles_list[i] in locked_roles else False,
            user=request.user,
        )
        assignment.save()
    return redirect('wolfrollapp:home')


def rollFromSaved(request, pk):
    RoleAssignment.objects.filter(user=request.user).delete()
    player_list = Player.objects.filter(user=request.user)
    roles_list = json.loads(SavedGame.objects.get(id=pk).roles)['roles']

    random.shuffle(roles_list)
    random.shuffle(list(player_list))
    for i in range(len(roles_list)):
        print(roles_list[i])
        assignment = RoleAssignment(
            player=player_list[i],
            role=Role.objects.filter(user=request.user).get(title=roles_list[i]),
            locked=False,
            user=request.user,
        )
        assignment.save()
    return redirect('wolfrollapp:home')


def updateLock(request, pk):
    assignment = RoleAssignment.objects.get(id=pk)
    if assignment.locked:
        RoleAssignment.objects.filter(id=pk).update(locked=False)
    else:
        RoleAssignment.objects.filter(id=pk).update(locked=True)
    return redirect('wolfrollapp:home')


def updateRoleToggle(request, key):
    game_params = GameParameters.objects.get(user=request.user)
    game_params_dict = json.loads(game_params.preferences)
    role_type_toggles = game_params_dict['typePref']
    wolf_count = game_params_dict['wolfCount']
    balance_goal = game_params_dict['balanceGoal']
    player_count = game_params_dict['playerCount']
    games_dict = game_params_dict['games_dict']

    if role_type_toggles[key]:
        role_type_toggles[key] = False
    else:
        role_type_toggles[key] = True
    new_prefs = {
        'typePref': role_type_toggles,
        'wolfCount': wolf_count,
        'balanceGoal': balance_goal,
        'playerCount': player_count,
        'games_dict': games_dict
    }
    j = json.dumps(new_prefs)
    GameParameters.objects.filter(user=request.user).update(preferences=j)
    return redirect('wolfrollapp:home')


def resetParams(request):
    j = {key: True for key in
         Role.objects.filter(user=request.user).order_by().values_list('type', flat=True).distinct()}
    initial_prefs = {
        'typePref': j,
        'wolfCount': 2,
        'balanceGoal': 0,
        'playerCount': 7,
        'games_dict': {}
    }
    initial_prefs = json.dumps(initial_prefs)
    GameParameters.objects.filter(user=request.user).update(preferences=initial_prefs)
    return redirect('wolfrollapp:home')


def increaseWolfCount(request):
    params = GameParameters.objects.get(user=request.user)
    params_dict = json.loads(params.preferences)
    params_dict['wolfCount'] += 1
    updated_params = json.dumps(params_dict)
    GameParameters.objects.filter(user=request.user).update(preferences=updated_params)
    print(request.path_info)
    return redirect('wolfrollapp:home')


def decreaseWolfCount(request):
    params = GameParameters.objects.get(user=request.user)
    params_dict = json.loads(params.preferences)
    params_dict['wolfCount'] -= 1
    updated_params = json.dumps(params_dict)
    GameParameters.objects.filter(user=request.user).update(preferences=updated_params)
    return redirect('wolfrollapp:home')


def increaseBalanceGoal(request):
    params = GameParameters.objects.get(user=request.user)
    params_dict = json.loads(params.preferences)
    params_dict['balanceGoal'] += 1
    updated_params = json.dumps(params_dict)
    GameParameters.objects.filter(user=request.user).update(preferences=updated_params)
    return redirect('wolfrollapp:home')


def decreaseBalanceGoal(request):
    params = GameParameters.objects.get(user=request.user)
    params_dict = json.loads(params.preferences)
    params_dict['balanceGoal'] -= 1
    updated_params = json.dumps(params_dict)
    GameParameters.objects.filter(user=request.user).update(preferences=updated_params)
    return redirect('wolfrollapp:home')


def increasePlayerCount(request):
    params = GameParameters.objects.get(user=request.user)
    params_dict = json.loads(params.preferences)
    params_dict['playerCount'] += 1
    updated_params = json.dumps(params_dict)
    GameParameters.objects.filter(user=request.user).update(preferences=updated_params)
    return redirect('wolfrollapp:speedRollerHome')


def decreasePlayerCount(request):
    params = GameParameters.objects.get(user=request.user)
    params_dict = json.loads(params.preferences)
    params_dict['playerCount'] -= 1
    updated_params = json.dumps(params_dict)
    GameParameters.objects.filter(user=request.user).update(preferences=updated_params)
    return redirect('wolfrollapp:speedRollerHome')


@login_required(login_url='/login')
def viewRoles(request):
    roles_list = Role.objects.filter(user=request.user)
    context = {
        'roles_list': roles_list,
    }
    return render(request, 'wolfrollapp/roles.html', context)


@login_required(login_url='/login')
def editRoles(request):
    roles_list = Role.objects.filter(user=request.user)
    form = RoleForm()
    context = {
        'roles_list': roles_list,
        'form': form,
    }
    return render(request, 'wolfrollapp/rolesEdit.html', context)


def createRole(request):
    title = request.POST.get('title')
    score = request.POST.get('score')
    description = request.POST.get('description')
    alignment = request.POST.get('alignment')
    role_type = request.POST.get('type')
    user = request.user
    role = Role(title=title, score=score, description=description, alignment=alignment, type=role_type, user=user)
    role.save()
    return redirect('wolfrollapp:editRoles')


def deleteRole(request, title):
    role = Role.objects.filter(user=request.user).get(title=title)
    role.delete()
    return redirect('wolfrollapp:editRoles')


def createPlayer(request):
    if request.method == "POST":
        name = request.POST.get('name')
        user = request.user
        new_player = Player(id=None, name=name, user=user)
        new_player.save()
    return redirect('wolfrollapp:home')


def deletePlayer(request, pk):
    player = Player.objects.get(id=pk)
    player.delete()
    return redirect('wolfrollapp:home')


def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')

        else:
            messages.info(request, "Username or Password is incorrect")

    context = {}
    return render(request, 'wolfrollapp/loginPage.html', context)


def logoutPage(request):
    logout(request)
    return redirect('/')


def registerPage(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, "Account Created: " + user)
            return redirect('wolfrollapp:home')

    context = {'form': form}
    return render(request, 'wolfrollapp/registerPage.html', context)
