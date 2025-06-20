from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import *
import pandas as pd
from pandas import ExcelWriter
from django.http import HttpResponse
from datetime import timedelta, date
import calendar



def home(request):
    if not request.user.is_authenticated:
        return redirect("login")

    items = []
    exclude = [General_2, To_do]
    for model in all_models:
        if model not in exclude:
            size = len(model.objects.all())
            items.append((model.model_name, size))

    context = {'general': general, "items": items}
    return render(request, "home.html", context)

# -----------------------------
# --------AUTHENTICATION=------
# -----------------------------

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        firstname = request.POST['firstname']
        surname = request.POST['lastname']
        if form.is_valid():
            user = form.save()
            user.firstname = firstname
            user.surname = surname
            user.save()
            person = Person.objects.filter(firstname=firstname, surname=surname).first()
            if person and person.user is None:
                person.user = user
            else:
                person = Person(firstname=firstname, surname=surname, user=user)
            person.save()

            login(request, user)
            return redirect("answers")
    else:
        form = UserCreationForm()
    context = {'form': form, 'general': general}
    return render(request, 'registration/signup.html', context)

def switch(request):
    if request.user.username == "John":
        user = authenticate(request, username="Darren", password="admin")
    elif request.user.username == "Darren":
        user = authenticate(request, username="John", password="FoxyRoxy1")
    if user is not None:
        login(request, user)
    return redirect("answers")


def get_user(request):
    user = Person.objects.filter(user=request.user).first()
    if not user:
        user = Person(user=request.user, user_type="Admin")
        user.save()
    return user

def login_user(request):
    if request.user.is_authenticated: return redirect("home")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.success(request, ("Error logging in."))
            return redirect('login')
    else:
        context = {'general': general}
        return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    return redirect("login")


# ------------------------
# ---- Descriptions ------
# ------------------------

def edit_descriptions(request):
    print("Edit descriptions")
    if not request.user.is_authenticated: return redirect("login")
    form = DescriptionForm
    item = general
    if request.method == 'POST':
        print("Edit descriptions - post")
        form = form(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('home')
    print("Edit description Form")
    print(form)
    form = form(instance=item)
    context = {'general': general, 'form':form, 'item':item, }
    return render(request, 'edit.html', context)

# ---------------------
# ---- Periods ------
# ---------------------
def make_period():
    name, start_date, end_date = get_quarter_dates(date.today())
    existing = Period.objects.filter(name=name)
    if not existing:
        Period(name=name, start_date=start_date, end_date=end_date).save()
    name, start_date, end_date = get_month_dates(date.today())
    existing = Period.objects.filter(name=name)
    if not existing:
        Period(name=name, start_date=start_date, end_date=end_date, frequency="Monthly").save()

def add_previous(request, id):
    add_previous_function(id)
    return redirect("list_view", "period")

def add_previous_function(id):
    period = Period.objects.get(id=id)
    date_to_use = period.start_date + timedelta(days=-1)
    if period.frequency == "Quarterly":
        name, start_date, end_date = get_quarter_dates(date_to_use)
    if period.frequency == "Monthly":
        name, start_date, end_date = get_month_dates(date_to_use)
    existing = Period.objects.filter(name=name)
    if not existing:
        Period(name=name, start_date=start_date, end_date=end_date, frequency=period.frequency).save()

def add_next(request, id):
    period = Period.objects.get(id=id)
    date_to_use = period.end_date + timedelta(days=1)
    if period.frequency == "Quarterly":
        name, start_date, end_date = get_quarter_dates(date_to_use)
    if period.frequency == "Monthly":
        name, start_date, end_date = get_month_dates(date_to_use)
    existing = Period.objects.filter(name=name)
    if not existing:
        Period(name=name, start_date=start_date, end_date=end_date).save()
    return redirect("list_view", "period")

# ---------------------
# ---- Answers ------
# ---------------------

def make_all_answers():
    questions = Question.objects.all()
    periods = Period.objects.all()
    for question in questions:
        for period in periods:
            if question.frequency == period.frequency:
                existing = Answer.objects.filter(question=question, period=period).first()
                if not existing:
                    new = Answer(question=question, period=period)
                    new.person = question.person
                    new.company = question.company
                    new.save()
                    new.set_period_date()

def select(request, model_str, id):
    user = get_user(request)
    model, form = get_model(model_str)
    if model:
        selected = model.objects.get(id=id)
    else:
        selected = id
    if model == Person:
        if user.selected_person == selected:
            user.selected_person = None
        else:
            user.selected_person = selected
    if model == Company:
        if user.selected_company == selected:
            user.selected_company = None
        else:
            user.selected_company = selected
    if model == Period:
        if user.selected_period == selected:
            user.selected_period = None
        else:
            user.selected_period = selected
    if model_str == "status":
        if user.selected_status == selected:
            user.selected_status = None
        else:
            user.selected_status = selected

    user.save()
    return redirect('answers')

def answers(request):
    model_str = "answer"
    make_all_answers()
    items = Answer.objects.all()
    people = Person.objects.all()
    companies = Company.objects.all()
    periods = Period.objects.all().order_by('frequency', 'start_date')
    description = get_description(model_str)

    user = get_user(request)
    if user.user_type == "Respondent":
        user.selected_person = user
        # people = [user]

    if user.selected_person: items = items.filter(person=user.selected_person)
    if user.selected_company: items = items.filter(company=user.selected_company)
    if user.selected_period: items = items.filter(period=user.selected_period)
    if user.selected_status == "Answered": items = items.filter(answer__isnull=False)
    if user.selected_status == "Unanswered": items = items.filter(answer__isnull=True)

    context = {'general': general, 'companies': companies, 'people': people, 'periods': periods, 'statuses': statuses, 'items': items,
               'selected_company': user.selected_company, 'selected_person': user.selected_person, 'selected_period': user.selected_period, 'selected_status': user.selected_status,
               'model_str': model_str, 'description':description}
    return render(request, 'answers.html', context)

def add_answer(request, answer_id, answer_str):
    answer = Answer.objects.get(id=answer_id)
    answered_by = Person.objects.filter(user=request.user).first()

    if answer_str == 'clear':
        answer_str = None
        answered_by = None
        answer.notes = None
    answer.answer = answer_str
    answer.answered_by = answered_by
    answer.save()
    if answer.needs_notes():
        return redirect('add_notes', answer_id)
    return redirect(answers)

def add_notes(request, answer_id):
    if not request.user.is_authenticated: return redirect("login")
    item = Answer.objects.get(id=answer_id)
    form = AnswerNoteForm
    if request.method == 'POST':
        form = form(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('answers')
    form = form(instance=item)
    context = {'general': general, 'form':form, 'item':item}
    return render(request, 'answer.html', context)


# ---------------------
# ---- Utilities ------
# ---------------------

def get_company(row):
    try: return Company.objects.get(id=row['company_id']).name
    except: return ""

def get_person(row):
    try:
        person = Person.objects.get(id=row['person_id'])
        return str(person)
    except:
        return ""

def get_question(row):
    try: return str(Question.objects.get(id=row['question_id']))
    except: return ""

def get_period(row):
    try: return str(Period.objects.get(id=row['period_id']))
    except: return ""

def download(request):
    if not request.user.is_authenticated: return redirect("login")

    writer = ExcelWriter('Responses.xlsx', engine='xlsxwriter')
    model = Answer
    data = model.objects.filter()
    df = pd.DataFrame(list(data.values()))

    company = df.apply(get_company, axis=1)
    person = df.apply(get_person, axis=1)
    question = df.apply(get_question, axis=1)
    period = df.apply(get_period, axis=1)
    # df.columns = ['Company', 'Ping', 'Email', 'Area']
    df = pd.concat([company, person, question, period, df['answer']], axis=1)
    df.rename(columns={0: 'Company', 1: 'Person', 2: 'Question', 3: 'Period', 4: 'Answer'}, inplace=True)

    today = date.today().strftime("%d %B %Y")
    df.to_excel(writer, sheet_name=f'{today}', index=False)
    writer.close()

    # Create an HttpResponse object with the Excel file
    response = HttpResponse(open('Responses.xlsx', 'rb').read(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Responses.xlsx"'

    return response

# ---------------------------
# ---- File Management ------
# ---------------------------

# def files(request):
#     if not request.user.is_authenticated: return redirect("login")
#     # user = get_user(request)
#
#     context = {'general': general, }
#     return render(request, "files.html", context)
#
# def file_upload(request):
#     if not request.user.is_authenticated: return redirect("login")
#     # user = get_user(request)
#     if request.method == "POST":
#         form = FileForm(request.POST, request.FILES)
#         if form.is_valid():
#             new_file = form.save()
#             new_file.company = company
#             new_file.save()
#             print("Saved File:", new_file, company, new_file.company)
#             return redirect("files")
#     else:
#         form = FileForm()
#     return render(request, "file_upload.html", {"form": form, 'company': company})
#
# def file_to_db(request, id):
#     if not request.user.is_authenticated: return redirect("login")
#     user = get_user(request)
#     file_object = File.objects.filter(id=id).first()
#     file = file_object.document
#     data_set = []
#     if "People" in file_object.type:
#         df_people = pd.read_excel(file, sheet_name="People")
#         # df_people_html = df_people.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
#         df_to_db_people(df_people, company)
#         db_people = Person.objects.filter(company=company)
#         db_people = pd.DataFrame.from_records(db_people.values())
#         db_people['company_id'] = db_people['company_id'].map(company_names)
#         db_people_html = db_people.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
#         data_set.append(("People", file_object.html_people, db_people_html))
#
#     if "Questions" in file_object.type:
#         df_questions = pd.read_excel(file, sheet_name="Questions")
#         df_to_db_questions(df_questions, company)
#         db = Question.objects.filter(company=company)
#         db = pd.DataFrame.from_records(db.values())
#         db = db.sort_values(by=['ref'])
#         db = convert_id_to_string(db)
#         db_questions_html = db.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
#         data_set.append(("Questions", file_object.html_questions, db_questions_html))
#
#     context = {"company": company, 'data_set': data_set, 'file': file}
#     return render(request, "file_to_db.html", context)
#
# def convert_id_to_string(df):
#     foreign_keys = [
#         ('company_id', company_names),
#         ('person_id', people_names),
#         ('ping_id', ping_names),
#         ('question_id', question_names),
#         ('last_question_id', question_names),
#         ('next_question_id', question_names), ]
#     for name_string, map_name in foreign_keys:
#         if name_string in df.columns:
#             df[name_string] = df[name_string].map(map_name)
#     return df
#
# def change_sheet_name(request, id, current_sheet):
#     file = File.objects.get(id=id)
#     file.rename_sheet(current_sheet)
#     return redirect("files")

# -----------------------
# ---- Development ------
# -----------------------

def development(request):
    if not request.user.is_authenticated: return redirect("login")
    items = To_do.objects.all()
    model_str = "to_do"
    context = {'general': general, 'items': items, 'model_str': model_str}
    return render(request, "to_do.html", context)

def toggle_value(request, id, parameter):
    to_do = To_do.objects.get(id=id)
    if parameter == "open": to_do.open = not to_do.open
    if parameter == "priority_down": to_do.priority = max(to_do.priority - 1, 1)
    if parameter == "priority_up": to_do.priority = to_do.priority + 1
    if parameter == "owner":
        if to_do.owner == "Darren": to_do.owner = None
        else: to_do.owner = "Darren"
    to_do.save()
    return redirect('list_view', 'to_do')


# ------------------------------
# ---- Generic Functions  ------
# ------------------------------
def list_view(request, model_str):
    if not request.user.is_authenticated: return redirect("login")
    model, form = get_model(model_str)
    description = get_description(model_str)
    if model == Answer:
        return redirect('answers')
    if model == Period: make_period()
    items = model.objects.all()
    if model_str == "to_do": items = items.order_by('priority', 'name')
    if model_str == "period": items = items.order_by('frequency', 'start_date')
    context = {'general': general, 'description': description, 'items': items, 'model_str': model_str, }
    return render(request, model_str + "s.html", context)

def item(request, model_str, id):
    if not request.user.is_authenticated: return redirect("login")
    model, form = get_model(model_str)
    item = model.objects.get(id=id)
    context = {'general': general, 'item': item, 'model_str': model_str, }
    return render(request, model_str + ".html", context)

def new(request, model_str):
    if not request.user.is_authenticated: return redirect("login")
    model, form = get_model(model_str)
    if request.method == 'POST':
        form = form(request.POST)
        if form.is_valid():
            form.save()
        return redirect('list_view', model_str)
    form = form()
    context = {'general': general, 'form':form, 'model_str': model_str, 'mode': 'New'}
    return render(request, 'new.html', context)

def edit(request, model_str, id):
    if not request.user.is_authenticated: return redirect("login")
    model, form = get_model(model_str)
    item = model.objects.get(id=id)
    if request.method == 'POST':
        form = form(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('list_view', model_str)
    form = form(instance=item)
    context = {'general': general, 'form':form, 'model_str': model_str, 'mode': 'Edit'}
    return render(request, 'edit.html', context)

def delete(request, model_str, id):
    model, form = get_model(model_str)
    item = model.objects.get(id=id)
    if item: item.delete()
    return redirect("list_view", model_str)

def delete_all(request, model_str):
    model, form = get_model(model_str)
    user = get_user(request)
    items = model.objects.all()
    items.delete()
    if model_str == "logic":
        return redirect("logic")
    return redirect("home")

def make_data(request, model_str):
    model, form = get_model(model_str)
    if model == Company:
        Company(name="NULIS").save()
        Company(name="OPC").save()
    if model == Period:
        make_period()
        periods = Period.objects.all()
        for period in periods:
            add_previous_function(period.id)
    if model == Person:
        darren_user = User.objects.filter(username="Darren").first()
        john_user = User.objects.filter(username="John").first()
        Person(firstname="Darren", surname="Robinson", user=darren_user, user_type="Admin").save()
        Person(firstname="John", surname="Robinson", user=john_user).save()
        Person(firstname="Max", surname="Robinson").save()
    if model == AnswerType:
        AnswerType(name="RAG", answer_list="Green, Amber+, Red+").save()
        AnswerType(name="Y/N", answer_list="Yes, No+").save()
    if model == Question:
        nulis = Company.objects.filter(name="NULIS").first()
        opc = Company.objects.filter(name="OPC").first()
        rag = AnswerType.objects.filter(name="RAG").first()
        yn = AnswerType.objects.filter(name="Y/N").first()
        darren = Person.objects.filter(firstname="Darren").first()
        john = Person.objects.filter(firstname="John").first()
        max = Person.objects.filter(firstname="Max").first()
        Question(question="Question A", frequency="Monthly", person=john, company=nulis, answer_type=rag).save()
        Question(question="Question B", frequency="Quarterly", person=max, company=opc, answer_type=rag).save()
        Question(question="Question C", frequency="Monthly", person=john, company=nulis, answer_type=yn).save()
        Question(question="Question D", frequency="Quarterly", person=max, company=opc, answer_type=yn).save()
    return redirect('home')

# ----------------------
# ---- Utilities  ------
# ----------------------

def get_month_dates(input_date):
    start_date = date(input_date.year, input_date.month, 1)
    end_date = date(input_date.year, input_date.month, calendar.monthrange(input_date.year, input_date.month)[1])
    month_label = f"{input_date.strftime('%B %Y')}"
    return month_label, start_date, end_date

def get_quarter_dates(input_date):
    quarters = [
        (date(input_date.year, 1, 1), date(input_date.year, 3, 31)),
        (date(input_date.year, 4, 1), date(input_date.year, 6, 30)),
        (date(input_date.year, 7, 1), date(input_date.year, 9, 30)),
        (date(input_date.year, 10, 1), date(input_date.year, 12, 31)),
    ]
    for start_date, end_date in quarters:
        if start_date <= input_date <= end_date:
            label = f"{end_date.strftime('%B %Y')} Quarter"
            return label, start_date, end_date

