from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Client
from .form import AddClientForm, AddCommentForm, AddFileForm
from django.contrib import messages
from team.models import Team
from django.http import HttpResponse
import csv
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
@login_required

def clients_export(request):
    clients = Client.objects.filter(created_by=request.user)
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="clients.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow(["Client", "Description", "Create at", "Created by"])

    for client in clients:
        writer.writerow([client.name, client.description, client.created_at, client.created_by,])

    return response


@login_required
def clients_list(request):
    search_query = request.GET.get('q')
    clients_list = Client.objects.filter(created_by=request.user).order_by('-created_at')
    paginate_by = 15

    if search_query:
        clients_list = clients_list.filter(
            Q(name__icontains=search_query) |  # Thay 'name' bằng trường dữ liệu bạn muốn tìm kiếm
            Q(email__icontains=search_query) | # Thay 'email' bằng trường dữ liệu khác nếu cần
            Q(phone__icontains=search_query) | # Thay 'email' bằng trường dữ liệu khác nếu cần
            Q(product_line__name__icontains=search_query)  # Thay 'email' bằng trường dữ liệu khác nếu cần
            # Thêm các trường dữ liệu khác nếu muốn tìm kiếm ở nhiều trường
        )

    paginator = Paginator(clients_list, paginate_by)
  
    pageNumber = request.GET.get('page')
    try:
        clients = paginator.page(pageNumber)
    except PageNotAnInteger:
        clients = paginator.page(1)
    except EmptyPage:
        clients = paginator.page(paginator.num_pages)

    return render(request, 'client/clients_list.html',{
        'clients': clients,
        'search_query': search_query,# Trả về search_query để có thể hiển thị trên giao diện
    })


@login_required
def clients_add_file(request, pk):
    client = get_object_or_404(Client, created_by=request.user, pk=pk)

    if request.method == 'POST':
        form = AddFileForm(request.POST, request.FILES)

        if form.is_valid(): 
            file = form.save(commit=False)
            file.team = request.user.userprofile.active_team
            file.client_id = pk 
            file.created_by = request.user
            file.save()
            
        return redirect('clients:detail', pk=pk)



@login_required
def clients_detail(request, pk):
    client = get_object_or_404(Client, created_by=request.user, pk=pk)
    
    if request.method == 'POST':
        form = AddCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.team = request.user.userprofile.active_team
            comment.created_by = request.user
            comment.client = client
            comment.save()
            
            return redirect('clients:detail', pk=pk)
    else: 
        form = AddCommentForm()
        
    return render(request, 'client/clients_detail.html',{
            'client': client,
            'form': form,
            'fileform': AddFileForm(),
    })


@login_required
def clients_add(request):
    team = request.user.userprofile.active_team
    
    if request.method == 'POST':
        form = AddClientForm(request.POST)
        
        if form.is_valid():
            client = form.save(commit=False)
            client.created_by = request.user
            client.team = team
            client.save()

            messages.success(request, 'The client was created.')

            return redirect('clients:list')
    else: 
        form = AddClientForm()
    return render(request, 'client/clients_add.html',{
        'form': form,
        'team': team
    })

@login_required
def clients_delete(request, pk):
    client = get_object_or_404(Client, created_by=request.user, pk=pk)

    client.delete()
    messages.success(request, "The client was deleted.")

    return redirect('clients:list')

@login_required
def clients_edit(request,pk):
    client = get_object_or_404(Client, created_by=request.user, pk=pk)

    if request.method == 'POST':
        form = AddClientForm(request.POST, instance=client)

        if form.is_valid():
            form.save()
            messages.success(request, 'The changes was saved.')
            return redirect('clients:list')
    else:
        form = AddClientForm(instance=client)
    return render(request, 'client/clients_edit.html',{
        'form': form
        })

    



