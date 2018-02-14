from django.shortcuts import render
from mezzanine.blog.models import BlogPost
# Create your views here.


def blog_home(request):

    blogs = BlogPost.objects.all()

    return render(request, 'blog_index.html', {'blogs': blogs})


def blog_page(request, page_slug):

    blog = BlogPost.objects.get(slug=page_slug)

    return render(request, 'blog_detail.html', {'blog_post': blog})
