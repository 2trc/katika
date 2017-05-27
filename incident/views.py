from django.shortcuts import render, HttpResponseRedirect
from .models import IncidentForm, IncidentProject
# from django.views import View

# Create your views here.


# class IncidentView(View):
#     name = 'incident'

def submit_incident(request, incide_project):
    form = IncidentForm(data=request.POST or None, label_suffix='')

    if request.method == 'POST' and form.is_valid():
        #blog_page = form.save(commit=False)
        blog_page = form.save()
        # blog_page.slug = slugify(blog_page.title)
        # blog = blog_index.add_child(instance=blog_page)

        # if blog:
        #     blog.unpublish()
        #     # Submit page for moderation. This requires first saving a revision.
        #     blog.save_revision(submitted_for_moderation=True)
        #     # Then send the notification to all Wagtail moderators.
        #     send_notification(blog.get_latest_revision().id, 'submitted', None)
        return HttpResponseRedirect(incide_project.url + incide_project.reverse_subpage('thanks'))
    #IncidentProject.reverse_subpage()
    context = {
        'form': form,
        'page': incide_project,
    }
    #return render(request, 'portal_pages/blog_page_add.html', context)
    return render(request, IncidentProject.url, context)
