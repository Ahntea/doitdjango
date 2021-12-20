from django.views.generic.edit import UpdateView
from .models import Post, Category, Tag
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
import requests
from django.core.exceptions import PermissionDenied
# Create your views here.

class PostList(ListView):
    model = Post
    ordering = '-pk'
    
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
            return super(PostCreate, self).form_valid(form)
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