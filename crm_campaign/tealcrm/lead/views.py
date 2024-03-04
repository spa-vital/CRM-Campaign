
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView, View
from .models import Lead
from client.models import Client, Comment as ClientComment
from team.models import Team
from .form import AddCommentForm, AddFileForm, AddLeadForm

from django.core.mail import send_mail

from django.core.mail import send_mass_mail

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Q
from django.shortcuts import render


class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    paginate_by = 20  # Số lượng mục trên mỗi trang
    template_name = 'lead/lead_list.html'  # Thay 'your_template.html' bằng tên thực của template bạn muốn sử dụng

    def get_queryset(self):
        # Lọc queryset dựa trên người dùng đăng nhập và trạng thái chưa chuyển đổi
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user, converted_to_client=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Lấy queryset đã lọc
        queryset = self.get_queryset().order_by('-created_at')

        # Phân trang cho queryset đã lọc
        paginator = Paginator(queryset, self.paginate_by)

        # Lấy số trang hiện tại từ tham số GET trong request
        page_number = self.request.GET.get('page')

        try:
            # Lấy các đối tượng trên trang được chỉ định
            leads = paginator.page(page_number)
        except PageNotAnInteger:
            # Nếu page_number không phải là số nguyên, trả về trang đầu tiên
            leads = paginator.page(1)
        except EmptyPage:
            # Nếu trang không tồn tại (vd: page = 9999), trả về trang cuối cùng
            leads = paginator.page(paginator.num_pages)

        # Đưa queryset phân trang vào context
        context['object_list'] = leads
        return context
    def get_queryset(self):
        # Lọc queryset dựa trên người dùng đăng nhập và trạng thái chưa chuyển đổi
        queryset = super().get_queryset()
        queryset = queryset.filter(created_by=self.request.user, converted_to_client=False)

        # Tìm kiếm nếu có từ khóa
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(status__icontains=search_query)
                # Thêm các trường bạn muốn tìm kiếm ở đây
            )

        return queryset



class LeadDetailView(LoginRequiredMixin,DetailView):
    model = Lead
    
    def get_context_data(self, **kwarg):
        context = super().get_context_data(**kwarg)
        context['form'] = AddCommentForm()
        context['fileform'] = AddFileForm()

        return context
    
    def get_queryset(self):
        queryset = super(LeadDetailView, self).get_queryset()
        return queryset.filter(created_by=self.request.user, pk = self.kwargs.get('pk'))
    

class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    success_url = reverse_lazy('leads:list')

    
    def get_queryset(self):
        queryset = super(LeadDeleteView, self).get_queryset()
        return queryset.filter(created_by=self.request.user, pk = self.kwargs.get('pk'))
    

    
class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    # fields = ('name', 'email', 'description','phone', 'priority', 'status', 'product_line', 'company','job')
    form_class = AddLeadForm
    success_url = reverse_lazy('leads:list')

    
    def get_context_data(self, **kwarg):
        context = super().get_context_data(**kwarg)
        context['title'] = 'Edit lead'
        return context

    
    def get_queryset(self):
        queryset = super(LeadUpdateView, self).get_queryset()
        return queryset.filter(created_by=self.request.user, pk = self.kwargs.get('pk'))
    
    


class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    #fields = ('name', 'email', 'description', 'phone', 'priority', 'status', 'product_line', 'company','job')
    form_class = AddLeadForm
    success_url = reverse_lazy('leads:list')

    # send_mail("It works!", "This will get sent through Sendinblue",
    #        "Bảo Lâm <baolam.main@gmail.com>", ["nguyenngocbaolamcva2020@gmail.com"])


    def get_context_data(self, **kwarg):
        context = super().get_context_data(**kwarg)
        team = self.request.user.userprofile.active_team
        context['team'] = team
        context['title'] = 'Add lead'

        return context
    
    def get_queryset(self):
        queryset = super(LeadCreateView, self).get_queryset()
        return queryset.filter(created_by=self.request.user)
    
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        team = self.request.user.userprofile.active_team
        self.object.created_by = self.request.user
        self.object.team = team
        self.object.save()

        return redirect(self.get_success_url())
    

class AddFileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        
        form = AddFileForm(request.POST, request.FILES)

        if form.is_valid():
            team = self.request.user.userprofile.active_team
            file = form.save(commit=False)
            file.team = team
            file.lead_id = pk 
            file.created_by = request.user
            file.save()
            
        return redirect('leads:detail', pk=pk)
            
    

class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        
        form = AddCommentForm(request.POST)

        if  form.is_valid():
            team = self.request.user.userprofile.active_team
            comment = form.save(commit=False)
            comment.team = team 
            comment.created_by = request.user
            comment.lead_id = pk
            comment.save()

        return redirect('leads:detail', pk=pk)




class ConvertToClientView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        lead = get_object_or_404(Lead, created_by=request.user, pk=pk)
        team = self.request.user.userprofile.active_team

        client = Client.objects.create(
        name = lead.name,
        email = lead.email,
        description = lead.description,
        created_by= request.user,
        team=team,
        phone=lead.phone,
        company=lead.company,
        job=lead.job,
        product_line=lead.product_line,

        )
        lead.converted_to_client = True
        lead.save()
        
        #convert lead comment to client  comment
        comments = lead.comments.all()
        for comment in comments:
            ClientComment.objects.create(
                client = client,
                content = comment.content,
                created_by  =  comment.created_by,
                team = team,
            )
        
        messages.success(request, 'The lead was converted to a client.')

        return redirect('leads:list')




# Xử lý API dữ liệu

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


from lead.serializers import LeadSerializer
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

class ListCreateLeadView(ListCreateAPIView):
    model = Lead
    serializer_class = LeadSerializer

    def get_queryset(self):
        return Lead.objects.all()

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        # Kiểm tra định dạng email
        validator = EmailValidator()
        try:
            validator(email)
        except ValidationError as e:
            return JsonResponse({
                'message': 'Invalid email format!'
            }, status=status.HTTP_400_BAD_REQUEST)

        existing_lead = Lead.objects.filter(email=email).first()

        if existing_lead:
            serializer = LeadSerializer(existing_lead, data=request.data, partial=True)
        else:
            serializer = LeadSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return JsonResponse({
                'message': 'Create a new Lead successful!'
            }, status=status.HTTP_201_CREATED)

        return JsonResponse({
            'message': 'Create a new Lead unsuccessful!'
        }, status=status.HTTP_400_BAD_REQUEST)
    

class UpdateDeleteLeadView(RetrieveUpdateDestroyAPIView):
    model = Lead
    serializer_class = LeadSerializer

    def put(self, request, *args, **kwargs):
        lead_instance = get_object_or_404(Lead, id=kwargs.get('pk'))
        serializer = LeadSerializer(lead_instance, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return JsonResponse({
                'message': 'Update Car successful!'
            }, status=status.HTTP_200_OK)

        return JsonResponse({
            'message': 'Update Car unsuccessful!'
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        lead_instance = get_object_or_404(Lead, id=kwargs.get('pk'))
        lead_instance.delete()

        return JsonResponse({
            'message': 'Delete Car successful!'
        }, status=status.HTTP_200_OK)

        