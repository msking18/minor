from django.shortcuts import render, redirect, get_object_or_404
from .models import Question, Answer, Reply
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from . import forms
from .models import Question, Answer
from django.urls import reverse


class QuestionListView(ListView):
    model = Question
    template_name = 'quesans/listall.html'
    context_object_name = 'questions'
    ordering = ['created_on']


class YourQuestionListView(LoginRequiredMixin, ListView):
    model = Question
    template_name = 'quesans/listall.html'
    context_object_name = 'questions'
    ordering = ['created_on']

    def get_queryset(self):
        questions = Question.objects.all().filter(author=self.request.user)
        return questions


class SearchView(ListView):
    model = Question
    template_name = 'quesans/search-ques.html'
    context_object_name = 'search_results'

    def get_queryset(self):
        result = super(SearchView, self).get_queryset()
        query = self.request.GET.get('search')
        if query:
            postresult = Question.objects.filter(title__contains=query)
            result = postresult
        else:
            result = None
        return result


class PostQuestionView(LoginRequiredMixin, CreateView):
    model = Question
    fields = ['title', 'desc']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Question posted successfully!")
        return super().form_valid(form)


class QuestionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Question
    fields = ['title', 'desc', 'image', 'answered']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Question updated successfully!")
        return super().form_valid(form)

    def test_func(self):
        question = self.get_object()
        if self.request.user == question.author:
            return True
        else:
            messages.error(self.request, "Error editing question!")
            return False

    def get_login_url(self):
        if self.request.user.is_authenticated:
            return '/quesans/list/'
        return super().get_login_url()

    def get_absolute_url(self):
        return reverse('quesans:qlist')


class QuestionAnswerView(DetailView):
    model = Question
    context_object_name = 'question'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        return Question.objects.get(slug=self.kwargs.get("slug"))

    # get all answers corresponding to the question object
    def get_context_data(self, **kwargs):
        object = self.get_object()
        context = super().get_context_data(**kwargs)
        try:
            lst = []
            context['answers'] = Answer.objects.all().filter(question=object)
            for answer in Answer.objects.all().filter(question=object):
                if answer.upvote.filter(id=self.request.user.id).exists():
                    lst.append(answer)
            context['lst'] = lst
            return context
        except:
            return None


def AnswerDetail(request, pk):
    answer = get_object_or_404(Answer, id=pk)
    # List of active comments for this post
    replies = answer.replies.filter(active=True)
    new_reply = None
    if request.method == 'POST':
        # A comment was posted
        reply_form = forms.PostReply(data=request.POST)
        if reply_form.is_valid():
            # Create Comment object but don't save to database yet
            new_reply = reply_form.save(commit=False)
            # Assign the current answer and user to the comment
            new_reply.answer = answer
            new_reply.user = request.user
            # Save the comment to the database
            new_reply.save()
            # redirect to same page and focus on that comment
            return HttpResponseRedirect(reverse('quesans:ans-detail', args=[str(pk)])+'#'+str(new_reply.id))
            # answer.get_absolute_url()+'#'+str(new_reply.id)
    else:
        reply_form = forms.PostReply()
    return render(request, 'quesans/answer_detail.html', {'answer': answer, 'replies': replies, 'reply_form': reply_form})


def reply_page(request):
    if request.method == "POST":
        form = forms.PostReply(request.POST)
        if form.is_valid():
            answer_id = request.POST.get('answer_id')  # from hidden input
            parent_id = request.POST.get('parent')  # from hidden input
            answer_url = request.POST.get('answer_url')  # from hidden input
            reply = form.save(commit=False)
            reply.answer = Answer(id=answer_id)
            reply.parent = Reply(id=parent_id)
            reply.user = request.user
            reply.save()
            return redirect(answer_url+'#'+str(reply.id))
    return redirect("/")


class AnswerPostView(LoginRequiredMixin, CreateView):
    model = Answer
    fields = ['answer_text', 'image']

    def get_context_data(self, **kwargs):
        kwargs['question'] = Question.objects.get(pk=self.kwargs.get('pk'))
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.question = Question.objects.get(pk=self.kwargs.get('pk'))
        messages.success(self.request, "Answer posted successfully!")
        return super().form_valid(form)


class AnswerDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Answer
    success_url = '/quesans'

    def test_func(self):
        answer = self.get_object()
        if self.request.user == answer.user:
            return True
        else:
            messages.error(self.request, "Cannot delete answer!")
            return False


def UpvoteView(request, slug):
    answer = get_object_or_404(Answer, id=request.POST.get('answer_id'))
    if answer.upvote.filter(id=request.user.id).exists():
        answer.upvote.remove(request.user)
    else:
        answer.upvote.add(request.user)
    messages.success(request, "Answer upvoted")
    return HttpResponseRedirect(reverse('quesans:qthread', args=[str(slug)]))


def DownvoteView(request, slug):
    answer = get_object_or_404(Answer, id=request.POST.get('answer_id'))
    # check if user has already upvoted or not
    upvotes = answer.upvote.all()
    # if so then remove upvote and notify user to downvote
    if request.user in upvotes:
        answer.upvote.remove(request.user)
        messages.success(
            request, "Upvote removed! Select downvote button to downvote")
    else:
        answer.downvote.add(request.user)
        messages.success(request, "Answer downvoted")
    return HttpResponseRedirect(reverse('quesans:qthread', args=[str(slug)]))


def QuestionAnswered(request, slug):
    question = get_object_or_404(Question, id=request.POST.get('question_id'))
    question.answered = True
    question.save()
    return HttpResponseRedirect(reverse('quesans:qthread', args=[str(slug)]))
