from django.contrib import admin
from polls.models import Choice, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

# Le permite editar las opciones para una pregunta en la misma página que la pregunta.
class QuestionAdmin(admin.ModelAdmin):
    fields = ['pub_date', 'question_text']
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']

admin.site.register(Question, QuestionAdmin)
