from django.forms import *
from .models import *

# general = General_2.objects.filter(name="Insignia").first()
# if not general:
#     General_2(name="Insignia").save()

general = None

class DescriptionForm(ModelForm):
    class Meta:
        model = General_2
        fields = ("company", "period", "person", "answer_type", "question", "answer", )
        widgets = {
            "company": TextInput(attrs={"class": "form-control", "placeholder": "Company description"}),
            "period": TextInput(attrs={"class": "form-control", "placeholder": "Period description"}),
            "person": TextInput(attrs={"class": "form-control", "placeholder": "Person description"}),
            "answer_type": TextInput(attrs={"class": "form-control", "placeholder": "Answer type description"}),
            "question": TextInput(attrs={"class": "form-control", "placeholder": "Question description"}),
            "answer": TextInput(attrs={"class": "form-control", "placeholder": "Answer description"}),
        }

class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ("name", )
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": ""}),
        }

class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ("firstname", "surname", "email", "user_type")
        widgets = {
            "firstname": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "surname": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "email": EmailInput(attrs={"class": "form-control", "placeholder": ""}),
            "user_type": Select(attrs={"class": "form-control", "placeholder": ""}),
        }

class QuestionForm(ModelForm):
    class Meta:
        model = Question
        # fields = ("question", "frequency", "company", "person")
        fields = ("question", "answer_type", "frequency", "company", "person")
        widgets = {
            "question": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "answer_type": Select(attrs={"class": "form-control", "placeholder": ""}),
            "frequency": Select(attrs={"class": "form-control", "placeholder": ""}),
            "company": Select(attrs={"class": "form-control", "placeholder": ""}),
            "person": Select(attrs={"class": "form-control", "placeholder": ""}),
        }

class PeriodForm(ModelForm):
    class Meta:
        model = Period
        fields = ("name", "start_date", "end_date", "frequency")
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "frequency": Select(attrs={"class": "form-control", "placeholder": ""}),
            "start_date": DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            "end_date": DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class AnswerForm(ModelForm):
    class Meta:
        model = Answer
        fields = ("answer", )
        widgets = {
            "answer": TextInput(attrs={"class": "form-control", "placeholder": ""}),
        }

class AnswerNoteForm(ModelForm):
    class Meta:
        model = Answer
        fields = ("notes", )
        widgets = {
            "answer": Textarea(attrs={"class": "form-control", "placeholder": "", 'rows':4}),
        }

class AnswerTypeForm(ModelForm):
    class Meta:
        model = AnswerType
        fields = ("name", "answer_list")
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "answer_list": TextInput(attrs={"class": "form-control", "placeholder": ""}),
        }


# class FileForm(ModelForm):
#     class Meta:
#         model = File
#         fields = ("name", "type", "document")
#         widgets = {
#             "type": Select(attrs={"class": "form-control"}),
#             "name": TextInput(attrs={"class": "form-control", "placeholder": ""}),
#             "document": FileInput(attrs={"class": "form-control", "placeholder": ""}
#             ),
#         }


class To_DoForm(ModelForm):
    class Meta:
        model = To_do
        fields = ("name", "priority", )
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "priority": TextInput(attrs={"class": "form-control", "placeholder": ""}),
        }


form_library = {
    Company: CompanyForm,
    Person: PersonForm,
    AnswerType: AnswerTypeForm,
    Question: QuestionForm,
    Period: PeriodForm,
    Answer: AnswerForm,
    To_do: To_DoForm
}

def get_form(model):
    try:    return form_library[model]
    except:
        print("Couldn't find form for:", model)
        return

def get_model(model_str):
    for model in all_models:
        # print(model.model_name, model_str, model.model_name == model_str)
        if model.model_name == model_str:
            # print("Get model", model, get_form(model))
            return model, get_form(model)
    return None, None

def get_description(model_str):
    if model_str == "company": return general.company
    if model_str == "period": return general.period
    if model_str == "person": return general.person
    if model_str == "answer_type": return general.answer_type
    if model_str == "question": return general.question
    if model_str == "answer": return general.answer
