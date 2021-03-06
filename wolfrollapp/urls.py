from django.urls import path

from . import views

app_name = "wolfrollapp"
urlpatterns = [
	path('login/', views.loginPage, name="loginPage"),
	path('logout/', views.logoutPage, name="logoutPage"),
	path('register/', views.registerPage, name="registerPage"),
	path('', views.home, name="home"),
	path('create/', views.createPlayer, name="createPlayer"),
	path('delete/<str:pk>', views.deletePlayer, name="deletePlayer"),
	path('roles/', views.viewRoles, name="viewRoles"),
	path('rolesedit/', views.editRoles, name="editRoles"),
	path('create_role/', views.createRole, name="createRole"),
	path('remove_role/<str:title>', views.deleteRole, name="deleteRole"),
	path('toggle_role_pref/<str:key>', views.updateRoleToggle, name="updateRoleToggle"),
	path('reset_params/', views.resetParams, name="resetParams"),
	path('increase_wolf_count/', views.increaseWolfCount, name="increaseWolfCount"),
	path('decrease_wolf_count/', views.decreaseWolfCount, name="decreaseWolfCount"),
	path('increase_balance_goal/', views.increaseBalanceGoal, name="increaseBalanceGoal"),
	path('decrease_balance_goal/', views.decreaseBalanceGoal, name="decreaseBalanceGoal"),
	path('roll_game/', views.rollGame, name="rollGame"),
	path('update_lock/<str:pk>', views.updateLock, name="updateLock"),
	path('increase_player_count/', views.increasePlayerCount, name="increasePlayerCount"),
	path('decrease_player_count/', views.decreasePlayerCount, name="decreasePlayerCount"),
	path('speed_roller/', views.speedRollerHome, name="speedRollerHome"),
	path('speed_roll/', views.speedRoll, name="speedRoll"),
	path('save_game/<str:title>', views.saveGame, name="saveGame"),
	path('roll_from_saved/<str:pk>', views.rollFromSaved, name="rollFromSaved"),
]
