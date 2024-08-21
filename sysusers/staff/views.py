from django.views import View
from django.views.generic import FormView, ListView, TemplateView, DetailView
from syspriv import models
from django.shortcuts import render, redirect
import json

class PersonListView(View):
    def get(self, request):
        return render(request, 'staff/people_list.html', {'staff': models.AdPerson.objects.exclude(office='Centrum Obsługi Podatnika (COP)').exclude(office='b.d.').order_by('department','last_name','first_name')})

class DepartmentView(View):
    def get(self, request, dep):
        return render(request, 'staff/people_list.html',
                      {'staff': models.AdPerson.objects.exclude(office='Centrum Obsługi Podatnika (COP)').exclude(office='b.d.').filter(department=dep).order_by('department','last_name','first_name')})

class RoomView(View):
    def get(self, request, room):
        return render(request, 'staff/people_list.html',
                      {'staff': models.AdPerson.objects.exclude(office='Centrum Obsługi Podatnika (COP)').exclude(office='b.d.').filter(room_number=room).order_by('department','last_name','first_name')})


class TitleView(View):
    def get(self, request, title):
        return render(request, 'staff/people_list.html',
                      {'staff': models.AdPerson.objects.exclude(office='Centrum Obsługi Podatnika (COP)').exclude(office='b.d.').filter(title=title).order_by('department','last_name','first_name')})

'''class PersonDetailView(View):
    def get(self, request, id):
        try:
            person = models.AdPerson.objects.get(id=id)
            data = {'person': person}
            data['staff'] = models.AdPerson.objects.filter(manager=person.full_name)
            data['manager'] = models.AdPerson.objects.get(full_name=person.manager)
            # ważne, aby wyszukanie managera było na końcu, bo może być go brak w tabeli i daje to exception
        except:
            pass
        return render(request, 'staff/person_detail.html', {**data})
'''
class PersonDetailViewTable(View):
    def get(self, request, id):
        try:
            person = models.AdPerson.objects.get(id=id)
            data = {'person': person}
            data['staff'] = models.AdPerson.objects.filter(manager=person.full_name)
            data['manager'] = models.AdPerson.objects.get(full_name=person.manager)
            # ważne, aby wyszukanie managera było na końcu, bo może być go brak w tabeli i daje to exception
        except:
            pass
        return render(request, 'staff/person_detail_table.html', {**data})


'''
class TreeView(View):
    def get(self, request):
        people = models.AdPerson.objects.exclude(office='Centrum Obsługi Podatnika (COP)').exclude(office='b.d.')
        office_staff = [p.full_name for p in people]
        data = []
        for person in people:
            data.append({ "id" : person.full_name, "parent" : person.manager if person.manager in office_staff else "#", "text" : person.first_name + ' ' + person.last_name, "pk": person.id })
        return render(request, 'staff/tree.html',
                      {'data': data})
'''

class PersonTreeView(View):
    def get(self, request, id):
        people = models.AdPerson.objects.exclude(office='Centrum Obsługi Podatnika (COP)').exclude(office='b.d.')
        office_staff = [p.full_name for p in people]
        data = []
        for person in people:
            data.append({ "id" : person.full_name, "parent" : person.manager if person.manager in office_staff else "#", "text" : person.first_name + ' ' + person.last_name, "pk": person.id })
        return render(request, 'staff/tree.html',
                      {'data': data, 'selected': models.AdPerson.objects.filter(id=id)})
