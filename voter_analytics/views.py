from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from . models import Voter
from django.db.models import Case, When, IntegerField
import plotly
import plotly.graph_objs as go

# Create your views here.
class VoterListView(ListView):
    template_name = 'voter_analytics/voters.html'
    model = Voter
    context_object_name = 'voters'
    paginate_by = 100

    def get_queryset(self):
        results = super().get_queryset().order_by('first_name')

        if 'party_affil' in self.request.GET:
            party = self.request.GET['party_affil']
            if party:
                results = results.filter(party_affil=party)

        if 'min_dob' in self.request.GET:
            min_dob = self.request.GET['min_dob']
            if min_dob:
                results = results.filter(dob__year__gte=min_dob)

        if 'max_dob' in self.request.GET:
            max_dob = self.request.GET['max_dob']
            if max_dob:
                results = results.filter(dob__year__lte=max_dob)

        if 'voter_score' in self.request.GET:
            voter_score = self.request.GET['voter_score']
            if voter_score:
                results = results.filter(voter_score=voter_score)

        for election in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
            if election in self.request.GET:
                results = results.filter(**{election: 'TRUE'})

        return results
    
class VoterGraphView(ListView):
    '''View to display graphs of voter data'''

    template_name = 'voter_analytics/graphs.html'
    model = Voter
    context_object_name = 'voters'

    def get_queryset(self):
        results = super().get_queryset().annotate(
            voter_score=
                Case(When(v20state='TRUE', then=1), default=0, output_field=IntegerField()) +
                Case(When(v21town='TRUE', then=1), default=0, output_field=IntegerField()) +
                Case(When(v21primary='TRUE', then=1), default=0, output_field=IntegerField()) +
                Case(When(v22general='TRUE', then=1), default=0, output_field=IntegerField()) +
                Case(When(v23town='TRUE', then=1), default=0, output_field=IntegerField())
        )

        if 'party_affil' in self.request.GET:
            party = self.request.GET['party_affil']
            if party:
                results = results.filter(party_affil=party)

        if 'min_dob' in self.request.GET:
            min_dob = self.request.GET['min_dob']
            if min_dob:
                results = results.filter(dob__year__gte=min_dob)

        if 'max_dob' in self.request.GET:
            max_dob = self.request.GET['max_dob']
            if max_dob:
                results = results.filter(dob__year__lte=max_dob)

        if 'voter_score' in self.request.GET:
            voter_score = self.request.GET['voter_score']
            if voter_score:
                results = results.filter(voter_score=voter_score)

        for election in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
            if election in self.request.GET:
                results = results.filter(**{election: 'TRUE'})

        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voters = self.get_queryset()

        # Histogram for Birth Year

        birth_years = [v.dob.year for v in voters]
        fig = go.Bar(
            x=sorted(set(birth_years)),
            y=[birth_years.count(y) for y in sorted(set(birth_years))]
        )
        title_text = "Voter Distribution by Birth Year"
        context['graph_div_dob'] = plotly.offline.plot({"data": [fig], "layout_title_text": title_text},
                                                        auto_open=False, output_type="div")

        # Pi chart

        parties = [v.party_affil.strip() for v in voters]
        party_labels = sorted(set(parties))
        party_counts = [parties.count(p) for p in party_labels]
        color_map = {'D': 'blue', 'R': 'red', 'U': 'gray', 'Other': 'lightgray'}
        colors = [color_map.get(label, 'lightgray') for label in party_labels]

        fig = go.Pie(
            labels=party_labels, 
            values=party_counts,
            marker=dict(colors=colors)
        )
        title_text = "Voter Distribution by Party Affiliation"
        context['graph_div_party'] = plotly.offline.plot(
            {"data": [fig], 
            "layout": {"title": "Voter Distribution by Party Affiliation", "height": 600, "width": 1000}
            },
            auto_open=False, output_type="div"
        )

        # Histogram for participants in past elections

        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        election_labels = ['2020 State', '2021 Town', '2021 Primary', '2022 General', '2023 Town']
        election_counts = [voters.filter(**{e: 'TRUE'}).count() for e in elections]
        fig = go.Bar(x=election_labels, y=election_counts)
        title_text = "Voter Participation by Election"
        context['graph_div_elections'] = plotly.offline.plot({"data": [fig], "layout_title_text": title_text},
                                                              auto_open=False, output_type="div")

        return context
    
class VoterDetailView(DetailView):
    '''View to display a single voter record'''

    template_name = 'voter_analytics/voter.html'
    model = Voter
    context_object_name = 'voter'