from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from explore.divisi import divisi_fb

# Choose a Profile/Page or Categories
def explore(request, template_name="explore/explore.html", extra_context=None):
    divisifb = divisi_fb.DivisiFB("divisi/FBGraph.pickle")
    return render_to_response(template_name, dict({
        "profiles": divisifb.getProfiles(),
        "pages": divisifb.getPages(),
    }, **extra_context), context_instance=RequestContext(request))

# Given profile, choose action
def object(request, id, template_name="explore/object.html", extra_context=None):
    divisifb = divisi_fb.DivisiFB("air/divisi/FBGraph.pickle")
    return render_to_response(template_name, dict({
        "object": divisifb.getById(id),
        "topSim": divisifb.topSimilarity(id),
        "topPre": divisifb.topPredictions(id),
    }, **extra_context), context_instance=RequestContext(request))

# Choose what to compare it to
def compareTo(request, id, template_name="explore/compareto.html", extra_context=None):
    divisifb = divisi_fb.DivisiFB("air/divisi/FBGraph.pickle")
    return render_to_response(template_name, dict({
        "object": divisifb.getById(id),
        "profiles": divisifb.getProfiles(),
        "pages": divisifb.getPages(),
    }, **extra_context), context_instance=RequestContext(request))

# Calculate similarity
def compare(request, id1, id2, template_name="explore/compare.html", extra_context=None):
    divisifb = divisi_fb.DivisiFB("air/divisi/FBGraph.pickle")
    return render_to_response(template_name, dict({
        "object1": divisifb.getById(id1),
        "object2": divisifb.getById(id2),
        "weight": divisifb.compare(id1,id2),
    }, **extra_context), context_instance=RequestContext(request))

# Choose items for category
def categories(request, template_name="explore/categories.html", extra_context=None):
    divisifb = divisi_fb.DivisiFB("air/divisi/FBGraph.pickle")
    return render_to_response(template_name, dict({
        "profiles": divisifb.getProfiles(),
        "pages": divisifb.getPages(),
    }, **extra_context), context_instance=RequestContext(request))

# Show category features
def category(request, template_name="explore/category.html", extra_context=None):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('categories'))
    ids = request.POST.getlist('object')
    if len(ids) < 1:
        return HttpResponseRedirect(reverse('categories'))
    divisifb = divisi_fb.DivisiFB("air/divisi/FBGraph.pickle")
    category = divisifb.createCategory(ids)
    return render_to_response(template_name, dict({
        "objects": [divisifb.getById(id) for id in ids],
        "topFea": divisifb.categoryTopFeatures(category),
        "topSim": divisifb.categoryTopSimilarity(category),
        "topPre": divisifb.categoryTopPredictions(category),
    }, **extra_context), context_instance=RequestContext(request))

def projection(request, id1, id2, thresh=.03, template_name="explore/projection.html", extra_context=None):
    divisifb = divisi_fb.DivisiFB("air/divisi/FBGraph.pickle")
    return render_to_response(template_name, dict({
        "profile1": divisifb.getById(id1),
        "profile2": divisifb.getById(id2),
        "projected_likes": project_prediction(id1,id2),
    }, **extra_context), context_instance=RequestContext(request))
