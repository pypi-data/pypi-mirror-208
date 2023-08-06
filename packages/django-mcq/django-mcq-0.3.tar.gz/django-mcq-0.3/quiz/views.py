from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView
from django.views import View

from .forms import StudentInterestsForm, TakeQuizForm
from .models import Quiz, Student, TakenQuiz, Question, Subject, Answer

User = get_user_model()

def get_or_create_student(user):
    try:
        return user.student
    except:
        return Student.objects.create(user=user)

@method_decorator([login_required], name='dispatch')
class StudentInterestsView(UpdateView):
    model = Student
    form_class = StudentInterestsForm
    template_name = 'quiz/interests_form.html'
    success_url = reverse_lazy('quiz:quiz_list')

    def get_object(self):
        return get_or_create_student(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)


@method_decorator([login_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'quiz/quiz_list.html'

    def get_queryset(self):
        student = get_or_create_student(self.request.user)
        # student_interests = student.interests.values_list('pk', flat=True)
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = get_or_create_student(self.request.user)
        context['student_subjects'] = student.interests.values_list('pk', flat=True)
        return context

@method_decorator([login_required], name='dispatch')
class QuizResultsView(View):
    template_name = 'quiz/quiz_result.html'

    def get(self, request, *args, **kwargs):        
        quiz = Quiz.objects.get(id = kwargs['pk'])
        taken_quiz = TakenQuiz.objects.filter(student = get_or_create_student(self.request.user), quiz = quiz)
        if not taken_quiz:
            """
            Don't show the result if the user didn't attempted the quiz
            """
            return render(request, '404.html')
        questions = Question.objects.filter(quiz =quiz)
        
        # questions = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'questions':questions, 
            'quiz':quiz, 'percentage': taken_quiz[0].percentage})

from django.http import JsonResponse

@method_decorator([login_required], name='dispatch')
class CreateQuizView(View):
    def create_quiz(self, quiz):
        subject, _ = Subject.objects.get_or_create(name=quiz['subject'])
        quiz_item= Quiz.objects.create(name=quiz['quiz'],subject=subject)
        for question in quiz['questions']:
            question_item = Question.objects.create(quiz=quiz_item,text=question['question'])
            for answer in question['answers']:
                is_correct = True if answer['is_correct'] == 'true' else False
                Answer.objects.create(question = question_item, text = answer['answer'],is_correct=is_correct)
    def post(self, request, *args, **kwargs): 
        import json
        try:
            quizzes = json.loads(request.POST['txt_quizzes_json'])
            with transaction.atomic():
                for quiz in quizzes:
                    self.create_quiz(quiz)
        except Exception as e:
            print(e)
            return JsonResponse({'resp':'error'})
        
        return JsonResponse({'resp':'success'})  

@method_decorator([login_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'quiz/taken_quiz_list.html'

    def get_queryset(self):
        student = get_or_create_student(self.request.user)
        queryset = student.taken_quizzes \
            .select_related('quiz', 'quiz__subject') \
            .order_by('quiz__name')
        return queryset


@login_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = get_or_create_student(request.user)

    if student.quizzes.filter(pk=pk).exists():
        return render(request, 'students/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = student.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()
                if student.get_unanswered_questions(quiz).exists():
                    return redirect('quiz:take_quiz', pk)
                else:
                    correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    percentage = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(student=student, quiz=quiz, score=correct_answers, percentage= percentage)
                    student.score = TakenQuiz.objects.filter(student=student).aggregate(Sum('score'))['score__sum']
                    student.save()
                    if percentage < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, percentage))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, percentage))
                    # return redirect('students:quiz_list')
                    return redirect('quiz:student_quiz_results', pk)
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'quiz/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress,
        'answered_questions': total_questions - total_unanswered_questions,
        'total_questions': total_questions
    })


@method_decorator([login_required], name='dispatch')
class StudentList(ListView):
    # model = get_user_model()
    paginate_by = 36
    template_name = 'quiz/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        query = self.request.GET.get('q','')
        User = get_user_model()

        queryset = Student.objects.order_by('-score')
        if query:
            # queryset = queryset.annotate(
            #     full_name = Concat('first_name','last_name')
            # ).filter(full_name__icontains = query)
            queryset = queryset.filter(user__username__icontains = query)
        return queryset

@method_decorator([login_required], name='dispatch')
class StudentDetail(View):
    """Show Details of a Student"""
    def get(self, request, **kwargs):
        student = Student.objects.get(user_id = kwargs['student'])
        subjects = student.taken_quizzes.all() \
            .values('quiz__subject__name','quiz__subject__color') \
            .annotate(score = Sum('score')) \
            .order_by('-score')
        
        return render(request,'quiz/student_detail.html', 
            {'student': student, 'subjects':subjects})