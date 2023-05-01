from django.shortcuts import render, get_object_or_404, redirect
from .models import BlogPost
from .forms import BlogPostForm

def blog_post_create_view(request):
    form = BlogPostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('blog_app:blog_post_list_view')

    context = {
        'form': form
    }
    return render(request, 'blog/post_form.html', context)

# def blog_post_list_view(request):
#     posts = BlogPost.objects.filter(is_draft=False)
#     categories = Category.objects.all()

#     context = {
#         'posts': posts,
#         'categories': categories
#     }
#     return render(request, 'blog/post_list.html', context)

def blog_post_list_view(request):
    blog_posts = BlogPost.objects.filter(is_draft=False)
    context = {
        'blog_posts': blog_posts,
    }
    return render(request, 'blog/blog_post_list.html', context)

def blog_post_detail_view(request, id):
    post = get_object_or_404(BlogPost, id=id)

    context = {
        'post': post
    }
    return render(request, 'blog/post_detail.html', context)