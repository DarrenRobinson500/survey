from django.db.models import *
from django.contrib.auth.models import User
# from .utilities import *
# import pandas as pd

def create_choices(choices):
    result = []
    for choice in choices:
        result.append((choice, choice))
    return result


user_type_choices = create_choices(['Admin', 'Respondent'])
statuses = ['Answered', 'Unanswered']
answer_status = create_choices(statuses)

question_choices = create_choices(['RAG', 'YN'])
frequency_choices = create_choices(['Weekly', 'Monthly', 'Quarterly'])
file_choices = create_choices(['Company' 'Person', "Question"])

# class Description(Model):
#     model_name = "descriptions"
#     name = CharField(max_length=255, null=True, blank=True)
#     company = TextField(null=True, blank=True)
#     period = TextField(null=True, blank=True)
#     person = TextField(null=True, blank=True)
#     answer_type = TextField(null=True, blank=True)
#     question = TextField(null=True, blank=True)
#     answer = TextField(null=True, blank=True)

class General_2(Model):
    model_name = "general"
    name = CharField(max_length=255, null=True, blank=True)
    colour = CharField(max_length=10, null=True, blank=True, default="#A6C9EC")
    colour_text = CharField(max_length=10, null=True, blank=True, default="#000000")

    company = TextField(null=True, blank=True, default="Company description")
    period = TextField(null=True, blank=True, default="Period description")
    person = TextField(null=True, blank=True, default="Person description")
    answer_type = TextField(null=True, blank=True, default="Answer type description")
    question = TextField(null=True, blank=True, default="Question description")
    answer = TextField(null=True, blank=True, default="Answer description")
    # descriptions = ForeignKey(Descriptions, null=True, blank=True, on_delete=SET_NULL)
    def __str__(self): return self.name

# class General(Model):
#     model_name = "general"
#     name = CharField(max_length=255, null=True, blank=True)
#     colour = CharField(max_length=10, null=True, blank=True, default="#A6C9EC")
#     colour_text = CharField(max_length=10, null=True, blank=True, default="#000000")
#     # descriptions = ForeignKey(Descriptions, null=True, blank=True, on_delete=SET_NULL)
#     def __str__(self): return self.name

class Company(Model):
    model_name = "company"
    name = TextField(null=True, blank=True)
    def __str__(self):
        return self.name
    def monthly_data(self):
        data = []
        months = Period.objects.filter(frequency="Monthly").order_by('end_date')
        row = [""]
        for month in months:
            row.append(month.name)
        data.append(row)
        questions = Question.objects.filter(company=self, frequency="Monthly")
        for question in questions:
            row = [question.question]
            answers = Answer.objects.filter(question=question, company=self).order_by('date')
            for answer in answers:
                result = answer.answer
                if not result: result = "Not answered"
                row.append(result)
            data.append(row)
        return data


        return data


class Period(Model):
    model_name = "period"
    name = CharField(max_length=255, null=True, blank=True)
    frequency = CharField(max_length=10, choices=frequency_choices, default='Quarterly')
    start_date = DateField(null=True, blank=True)
    end_date = DateField(null=True, blank=True)
    def __str__(self): return f"{self.name}"
    def unanswered(self):
        answers = Answer.objects.filter(period=self, answer__isnull=True)
        return len(answers)

class Person(Model):
    model_name = "person"
    user = ForeignKey(User, null=True, blank=True, on_delete=SET_NULL)
    user_type = CharField(max_length=10, choices=user_type_choices, default='Respondent')
    firstname = TextField(null=True, blank=True)
    surname = TextField(null=True, blank=True)
    email = EmailField(null=True, blank=True)
    selected_person = ForeignKey('self', null=True, blank=True, on_delete=SET_NULL)
    selected_company = ForeignKey(Company, null=True, blank=True, on_delete=SET_NULL)
    selected_period = ForeignKey(Period, null=True, blank=True, on_delete=SET_NULL)
    selected_status = TextField(null=True, blank=True, choices=answer_status, default=None)
    area = TextField(null=True, blank=True)
    def __str__(self):
        if self.firstname:
            return f"{self.firstname} {self.surname}"
        else:
            return "No name"
    def unanswered(self):
        answers = Answer.objects.filter(person=self, answer__isnull=True)
        return len(answers)

class AnswerType(Model):
    model_name = "answer_type"
    name = TextField(null=True, blank=True)
    answer_list = TextField(null=True, blank=True)
    def __str__(self): return self.name
    def answers(self):
        return [item.strip() for item in self.answer_list.split(",")]

class Question(Model):
    model_name = "question"
    question = TextField(null=True, blank=True)
    answer_type = ForeignKey(AnswerType, null=True, on_delete=SET_NULL)
    frequency = CharField(max_length=10, choices=frequency_choices, default='Quarterly')
    company = ForeignKey(Company, null=True, on_delete=SET_NULL)
    person = ForeignKey(Person, null=True, on_delete=SET_NULL)
    def __str__(self): return self.question
    def answer_choices(self):
        return self.answer_type.answers()

class Answer(Model):
    model_name = "answer"
    question = ForeignKey(Question, null=True, on_delete=SET_NULL)
    period = ForeignKey(Period, null=True, on_delete=SET_NULL)
    answer = TextField(null=True, blank=True)
    company = ForeignKey(Company, null=True, on_delete=SET_NULL)
    date = DateField(null=True, blank=True)
    person = ForeignKey(Person, null=True, on_delete=SET_NULL)
    answered_by = ForeignKey(Person, null=True, related_name="answered_by", on_delete=SET_NULL)
    notes = TextField(null=True, blank=True)
    def __str__(self): return f"{self.question}: {self.answer}"

    def needs_notes(self):
        if not self.answer: return False
        print("Needs notes:", self.answer[-1])
        return self.answer[-1] == "+"

    def set_period_date(self):
        self.date = self.period.end_date
        self.save()

class To_do(Model):
    model_name = "to_do"
    name = CharField(max_length=512)
    owner = CharField(max_length=512, blank=True, null=True, default="Darren")
    priority = IntegerField(default=1)
    open = BooleanField(default=True)
    def __str__(self): return f"{self.name}"

# class File(Model):
#     model_name = "file"
#     name = CharField(max_length=512)
#     time_stamp = DateTimeField(auto_now_add=True, null=True,blank=True)
#     last_update = DateTimeField(null=True,blank=True)
#     document = FileField(upload_to="files/", blank=True, null=True)
#     url = URLField(blank=True, null=True)
#     type = CharField(max_length=100, blank=True, null=True, choices=file_choices)
#     company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
#
#     def __str__(self):
#         return f"{self.name}"
#
#     def sheets(self):
#         return pd.ExcelFile(self.document).sheet_names
#
#     def html_people(self): return self.html("People")
#     def html_questions(self): return self.html("Questions")
#     def html_pings(self): return self.html("Pings")
#     def html_logic(self): return self.html("Logic")
#
#     def html(self, file_type):
#         if not file_type in self.type: return ""
#         try:
#             df = pd.read_excel(self.document, sheet_name=file_type)
#         except:
#             return ""
#         df_html = df.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
#         df_html = f"<b>{file_type}</b><br>" + df_html
#         return df_html
#
#     def delete(self, *args, **kwargs):
#         self.document.delete()
#         super().delete(*args, **kwargs)


# all_models = [General, Company, Person, Question, Answer]
all_models = [General_2, Company, Period, Person, AnswerType, Question, Answer, To_do, ]