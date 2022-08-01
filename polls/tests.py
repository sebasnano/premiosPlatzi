import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import Choice, Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text="¿que es un mono?", pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for questions whose pub_date is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(question_text="¿que es un mono?", pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns True for questions whose pub_date is within the last day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(question_text="¿que es un mono?", pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuetionIndexViewTests(TestCase):
    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="¿que es un mono?", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="¿que es un mono?", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        past_question = create_question(question_text="¿que es un mono?", days=-30)
        future_question = create_question(question_text="¿que es una rana?", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [past_question])


    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="¿que es un mono?", days=40)
        create_question(question_text="¿que es una rana?", days=50)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [])


    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        past_question_1 = create_question(question_text="¿que es un mono?", days=-30)
        past_question_2 = create_question(question_text="¿Que es una rana?", days=-40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [past_question_1, past_question_2])
    

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="¿que es un mono?", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="¿que es un mono?", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultsViewTests(TestCase):
    def test_question_not_exists(self):
        """ If question id not exists, get 404 """
        response= self.client.get(reverse("polls:results", kwargs={'pk':1}))
        self.assertEqual(response.status_code, 404)

    def test_future_question(self):
        """ If it is a question from future, get 404 """
        future_question= create_question("Future question", 30)
        response= self.client.get(reverse("polls:results", kwargs={'pk':future_question.pk}))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """ If it is a question from past, may display it """
        past_question= create_question("Past question", -10)
        response= self.client.get(reverse("polls:results", kwargs={'pk':past_question.pk}))
        self.assertContains(response, past_question.question_text)
    
    def test_display_question_choices_and_votes(self):
        """Page may display votes for every choice of a question"""
        question= create_question("Question", -1)
        choice1= Choice.objects.create(choice_text="Choice 1", question= question, votes=1)
        choice2= Choice.objects.create(choice_text="Choice 2", question= question)
        choice3= Choice.objects.create(choice_text="Choice 3", question= question)
        choice4= Choice.objects.create(choice_text="Choice 4", question= question)
        choice5= Choice.objects.create(choice_text="Choice 5", question= question)

        response = self.client.get(reverse("polls:results", kwargs={'pk': question.pk}))

        self.assertContains(response, question.question_text)
        self.assertContains(response, choice1.choice_text + ' -- ' + '1 vote' )
        self.assertContains(response, choice2.choice_text + ' -- ' + '0 votes' )
        self.assertContains(response, choice3.choice_text + ' -- ' + '0 votes' )
        self.assertContains(response, choice4.choice_text + ' -- ' + '0 votes' )
        self.assertContains(response, choice5.choice_text + ' -- ' + '0 votes' )