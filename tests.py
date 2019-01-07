from django.test import TestCase
from django.urls import reverse
import json
from .models import Question


# Create your tests here.
class QuestionModelTest(TestCase):
    def test_questions_return(self):
        response = self.client.post(reverse('JustSearch:get_questions', args=(0,)))
        print(json.loads(response.content.decode()).get('isOk'))
        pass
