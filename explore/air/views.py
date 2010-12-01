from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from air.models import FBGraph
import pickle
from explore.air.divisi import airtoolkit

# Choose a Profile/Page or Categories
def explore(request, template_name="explore/explore.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "profiles": toolkit.getType('profile'),
        "pages": toolkit.getType('page'),
        }, context_instance=RequestContext(request))

# Given profile, choose action
def object(request, id, template_name="explore/object.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    fbobject = toolkit.getById(id)
    return render_to_response(template_name, {
        "object": fbobject,
        "topSim": toolkit.topSimilarity(id),
        "topPre": toolkit.topPredictions(id),
        }, context_instance=RequestContext(request))

# Choose what to compare it to
def compareTo(request, id, template_name="explore/compareto.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "object": toolkit.getById(id),
        "profiles": toolkit.getType('profile'),
        "pages": toolkit.getType('page'),
        }, context_instance=RequestContext(request))

# Calculate similarity
def compare(request, id1, id2, template_name="explore/compare.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "object1": toolkit.getById(id1),
        "object2": toolkit.getById(id2),
        "weight": toolkit.compare(id1,id2),
        }, context_instance=RequestContext(request))

# Choose items for category
def categories(request, template_name="explore/categories.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "profiles": toolkit.getType('profile'),
        "pages": toolkit.getType('pages'),
        }, context_instance=RequestContext(request))

# Show category features
def category(request, template_name="explore/category.html"):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('categories'))
    ids = request.POST.getlist('object')
    if len(ids) < 1:
        return HttpResponseRedirect(reverse('categories'))
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    category = toolkit.createCategory(ids)
    return render_to_response(template_name, {
        "objects": [toolkit.getById(id) for id in ids],
        "topFea": toolkit.categoryTopFeatures(category),
        "topSim": toolkit.categoryTopSimilarity(category),
        "topPre": toolkit.categoryTopPredictions(category),
        }, context_instance=RequestContext(request))

def projection(request, id1, id2, thresh=.01, template_name="explore/projection.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "profile1": toolkit.getById(id1),
        "profile2": toolkit.getById(id2),
        "projected_likes": toolkit.project_prediction(id1,id2,thresh=thresh),
        }, context_instance=RequestContext(request))

def add(request, template_name="explore/add.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    if request.method == 'POST':
        keylinks = [('gender',(request.POST.get('gender'),'hasProperty',1)),
                ('hometown',(request.POST.get('hometown'),'isFrom',1))]
        keylinks.extend([('like',(likeid,'likes',1)) for likeid in request.POST.getlist('likes')])
        profileName = request.POST.get('name')
        profile = toolkit.createProfile("FBGraphAltered",profileName,keylinks)
        graphpointer = FBGraph.objects.all()[0]
        graphpointer.filename = "FBGraphAltered.pickle"
        graphpointer.altered = True
        graphpointer.save()
        return HttpResponseRedirect(reverse('object',args=[profile.id]))
    return render_to_response(template_name, {
        "hometowns": [x for x in toolkit.getType('page') if x.getLink('category') == 'City'],
        "likes": [x for x in toolkit.getType('page') if x.getLink('category') != 'Gender'
                  and x.getLink('category') != 'Category'],
        }, context_instance=RequestContext(request))

def reset(request):
    graphpointer = FBGraph.objects.all()[0]
    graphpointer.filename = "FBGraph.pickle"
    graphpointer.altered = False
    graphpointer.save()
    return HttpResponseRedirect(reverse('explore'))
