from django.http.response import JsonResponse
from django.views.generic.edit import UpdateView
from .models import Post, Category, Tag, Comment
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render, get_object_or_404
import requests
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm
from django.db.models import Q
# Create your views here.

class PostList(ListView):
    model = Post
    ordering = '-pk'
    paginate_by = 5
    
    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context
    
class PostDetail(DetailView):
    model = Post
    
    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context

def category_page(request,slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)
    
    return render(
        request,
        'blog/post_list.html',
        {
            'post_list' : post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category' : category,
        }
    )

def tag_page(request,slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()
    
    return render(
        request,
        'blog/post_list.html',
        {
            'post_list' : post_list,
            'tag' : tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )
    
class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = [ 'title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)
            
            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()
                
                tags_str = tags_str.replace(',',';')
                tags_list = tags_str.split(';')
            
                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response
            
        else:
            return redirect('/blog/')
        
class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']
    
    template_name = 'blog/post_update_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
           return super(PostUpdate,self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
        
    def get_context_data(self, **kwargs):
        context = super(PostUpdate,self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)
            
        return context
    
    def form_valid(self, form):
    
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()
        
        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',',';')
            tags_list = tags_str.split(';')
        
            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        return response
        
class PostSearch(PostList):
    paginate_by =None
    
    def get_queryset(self):
        q = self.kwargs['q']
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q)
        ).distinct()
        return post_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'
        return context

def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied
    
class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user==self.get_object().author:
            return super(CommentUpdate,self).dispatch(request,*args,**kwargs)
        else:
            raise PermissionDenied

def delete_comment(request,pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied


    
###### 카카오

def kakao_login(request):
    # client_id = os.environ.get("KAKAO_ID")
    client_id = '04a772c50eb4906739a6331fbe5e3dd9'
    REDIRECT_URI = "http://127.0.0.1:8000/blog/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={REDIRECT_URI}&response_type=code"
    )
def kakao_callback(request):
    try:
    	#(1)
        client_id = '04a772c50eb4906739a6331fbe5e3dd9'
        code = request.GET.get("code")
        REDIRECT_URI = "http://127.0.0.1:8000/blog/users/login/kakao/callback"
        #(2)
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={REDIRECT_URI}&code={code}"
        )
        #(3)
    #     token_json = token_request.json()
    #     error = token_json.get("error", None)
    #     if error is not None:
    #         raise KakaoException()
    #     #(4)
    #     access_token = token_json.get("access_token")
    #     #(5)
    #     profile_request = requests.get(
    #         "https://kapi.kakao.com/v2/user/me",
    #         headers={"Authorization": f"Bearer {access_token}"},
    #     )
    #     profile_json = profile_request.json()
    #     #(6)
    #     email = profile_json.get("kakao_account", None).get("email")
    #     if email is None:
    #         raise KakaoException()
    #     properties = profile_json.get("properties")
    #     nickname = properties.get("nickname")
    #     profile_image = properties.get("profile_image")
    #     #(7)
    #     try:
    #         user = models.User.objects.get(email=email)
    #         if user.login_method != models.User.LOGIN_KAKAO:
    #             raise KakaoException()
    #     except models.User.DoesNotExist:
    #         user = models.User.objects.create(
    #             email=email,
    #             username=email,
    #             first_name=nickname,
    #             login_method=models.User.LOGIN_KAKAO,
    #             email_verified=True,
    #         )
    #         user.set_unusable_password()
    #         user.save()
    #         #(8)
    #         if profile_image is not None:
    #             photo_request = requests.get(profile_image)
    #             user.avatar.save(
    #                 f"{nickname}-avatar", ContentFile(photo_request.content)
    #             )
    #     login(request, user)
    #     return redirect(reverse("core:home"))
    # except KakaoException:
    #     return redirect(reverse("users:login"))
    
    except:
        pass