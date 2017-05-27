from django import forms
from django.db import models

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet

from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from django.template.response import TemplateResponse
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

from taggit.models import TaggedItemBase


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(BlogIndexPage, self).get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('BlogPage', related_name='tagged_items')


class BlogTagIndexPage(Page):
    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super(BlogTagIndexPage, self).get_context(request)
        context['blogpages'] = blogpages
        return context


class BlogPage(RoutablePageMixin,Page):
    #date = models.DateField("Post date")
    date = models.DateTimeField("Post time")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
    hits = models.PositiveIntegerField(default=0)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    def get_author(self):
        ''' Avoid showing 'admin' on site
        '''

        if str(self.owner) == 'admin':
            return 'katika'
        else:
            return self.owner

    @route(r'^$')
    def base(self, request):
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request)
        )

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(BlogPage, self).get_context(request)
        #blogpages = self.get_children().live().order_by('-first_published_at')
        #context['blogpages'] = blogpages

        # hit count
        # first get the related HitCount object for your model object
        hit_count = HitCount.objects.get_for_object(self)
        #hit_count = HitCount.objects.get(pk=1)

        # next, you can attempt to count a hit and get the response
        # you need to pass it the request object as well
        hit_count_response = HitCountMixin.hit_count(request, hit_count)
        if hit_count_response.hit_counted:
            print("hits response: {}".format(hit_count_response))
            print("hits hits: {}".format(hit_count.hits))
            print("hits pk: {}".format(hit_count.pk))
            self.hits = hit_count.pk
            self.save()
            context['hits'] = hit_count.pk
        return context

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
        InlinePanel('gallery_images', label="Gallery images"),
    ]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'


