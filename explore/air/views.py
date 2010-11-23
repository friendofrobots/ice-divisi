from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from air.models import FBGraph
import pickle
from explore.air.divisi import divisi_fb

# Choose a Profile/Page or Categories
def explore(request, template_name="explore/explore.html"):
    divisifb = divisi_fb.DivisiFB(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "profiles": divisifb.getProfiles(),
        "pages": divisifb.getPages(),
        }, context_instance=RequestContext(request))

# Given profile, choose action
def object(request, id, template_name="explore/object.html"):
    divisifb = divisi_fb.DivisiFB(FBGraph.objects.all()[0].filename)
    fbobject = divisifb.getById(id)
    return render_to_response(template_name, {
        "object": fbobject,
        "topSim": divisifb.topSimilarity(id),
        "topPre": divisifb.topPredictions(id),
        }, context_instance=RequestContext(request))

# Choose what to compare it to
def compareTo(request, id, template_name="explore/compareto.html"):
    divisifb = divisi_fb.DivisiFB(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "object": divisifb.getById(id),
        "profiles": divisifb.getProfiles(),
        "pages": divisifb.getPages(),
        }, context_instance=RequestContext(request))

# Calculate similarity
def compare(request, id1, id2, template_name="explore/compare.html"):
    divisifb = divisi_fb.DivisiFB(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "object1": divisifb.getById(id1),
        "object2": divisifb.getById(id2),
        "weight": divisifb.compare(id1,id2),
        }, context_instance=RequestContext(request))

# Choose items for category
def categories(request, template_name="explore/categories.html"):
    divisifb = divisi_fb.DivisiFB(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "profiles": divisifb.getProfiles(),
        "pages": divisifb.getPages(),
        }, context_instance=RequestContext(request))

# Show category features
def category(request, template_name="explore/category.html"):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('categories'))
    ids = request.POST.getlist('object')
    if len(ids) < 1:
        return HttpResponseRedirect(reverse('categories'))
    divisifb = divisi_fb.DivisiFB(FBGraph.objects.all()[0].filename)
    category = divisifb.createCategory(ids)
    return render_to_response(template_name, {
        "objects": [divisifb.getById(id) for id in ids],
        "topFea": divisifb.categoryTopFeatures(category),
        "topSim": divisifb.categoryTopSimilarity(category),
        "topPre": divisifb.categoryTopPredictions(category),
        }, context_instance=RequestContext(request))

def projection(request, id1, id2, thresh=.01, template_name="explore/projection.html"):
    divisifb = divisi_fb.DivisiFB(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "profile1": divisifb.getById(id1),
        "profile2": divisifb.getById(id2),
        "projected_likes": divisifb.project_prediction(id1,id2,thresh=thresh),
        }, context_instance=RequestContext(request))

def add(request, template_name="explore/projection.html"):
    divisifb = divisi_fb.DivisiFB(FBGraph.objects.all()[0].filename)
    if request.method == 'POST':
        data = {}
        data['name'] = request.POST.get('name')
        data['gender'] = request.POST.get('gender')
        data['hometown'] = request.POST.get('hometown')
        likeids = request.POST.getlist('likes')
        profile = divisifb.createProfile("FBGraphAltered",data,likeids)
        FBGraph.objects.all()[0].filename = "FBGraphAltered.pickle"
        FBGraph.objects.all()[0].altered = True
        return HttpResponseRedirect(reverse('object',args=[profile.id]))
    return render_to_response(template_name, {
        "hometowns": [x for x in divisifb.getPages() if x.category == 'City']
        "likes": [x for x in divisifb.getPages() if x.category != 'Gender']
        }, context_instance=RequestContext(request))
