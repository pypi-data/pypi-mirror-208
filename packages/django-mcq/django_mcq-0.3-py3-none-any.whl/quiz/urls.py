from django.urls import include, path

from . import views
app_name='quiz'

urlpatterns = [
    path('', views.StudentList.as_view(), name='student_list'),
    path('<int:student>/', views.StudentDetail.as_view(), name='student_detail'),
    path('interests/', views.StudentInterestsView.as_view(), name='student_interests'),
    path('taken/', views.TakenQuizListView.as_view(), name='taken_quiz_list'),
    path('create_quiz/', views.CreateQuizView.as_view(), name='create_quiz'),
    path('q/', views.QuizListView.as_view(), name='quiz_list'),
    path('q/<int:pk>/', views.take_quiz, name='take_quiz'),        
    path('q/<int:pk>/studentresults/', views.QuizResultsView.as_view(), name='student_quiz_results'),
    
]
