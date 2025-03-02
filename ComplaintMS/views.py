from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from .models import Profile, Complaint
from .forms import UserRegisterForm, ProfileUpdateForm, UserProfileform, ComplaintForm, UserProfileUpdateform, StatusUpdateForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Page loading
def index(request):
    return render(request, "ComplaintMS/home.html")

def aboutus(request):
    return render(request, "ComplaintMS/aboutus.html")

def login(request):
    return render(request, "ComplaintMS/login.html")

def signin(request):
    return render(request, "ComplaintMS/signin.html")

# Get the count of all the submitted complaints (total, unsolved, solved)
def counter(request):
    total = Complaint.objects.all().count()
    unsolved = Complaint.objects.all().exclude(status='1').count()
    solved = Complaint.objects.all().exclude(Q(status='3') | Q(status='2')).count()
    dataset = Complaint.objects.values('Type_of_complaint').annotate(
        total=Count('status'),
        solved=Count('status', filter=Q(status='1')),
        notsolved=Count('status', filter=Q(status='3')),
        inprogress=Count('status', filter=Q(status='2'))
    ).order_by('Type_of_complaint')
    args = {'total': total, 'unsolved': unsolved, 'solved': solved, 'dataset': dataset}
    return render(request, "ComplaintMS/counter.html", args)

# Change password for grievance member
def change_password_g(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password_g')
        else:
            messages.warning(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'ComplaintMS/change_password_g.html', {'form': form})

# Registration page
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = UserProfileform(request.POST)
        if form.is_valid() and profile_form.is_valid():
            new_user = form.save()
            profile = profile_form.save(commit=False)
            if profile.user_id is None:
                profile.user_id = new_user.id
            profile.save()
            messages.success(request, 'Registered Successfully')
            return redirect('/login/')
    else:
        form = UserRegisterForm()
        profile_form = UserProfileform()

    context = {'form': form, 'profile_form': profile_form}
    return render(request, 'ComplaintMS/register.html', context)

# Login redirect based on user type
def login_redirect(request):
    if request.user.profile.type_user == 'student':
        return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponseRedirect('/counter/')

@login_required
def dashboard(request):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, instance=request.user)
        profile_update_form = UserProfileUpdateform(request.POST, instance=request.user.profile)
        if p_form.is_valid() and profile_update_form.is_valid():
            user = p_form.save()
            profile = profile_update_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Updated Successfully')
            return render(request, 'ComplaintMS/dashboard.html')
    else:
        p_form = ProfileUpdateForm(instance=request.user)
        profile_update_form = UserProfileUpdateform(instance=request.user.profile)

    context = {'p_form': p_form, 'profile_update_form': profile_update_form}
    return render(request, 'ComplaintMS/dashboard.html', context)

# Change password for user
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.warning(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'ComplaintMS/change_password.html', {'form': form})

# Complaint handling and submission section
@login_required
def complaints(request):
    if request.method == 'POST':
        complaint_form = ComplaintForm(request.POST)
        if complaint_form.is_valid():
            instance = complaint_form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.success(request, 'Your complaint has been registered!')
            return render(request, 'ComplaintMS/comptotal.html')
    else:
        complaint_form = ComplaintForm(request.POST)

    context = {'complaint_form': complaint_form}
    return render(request, 'ComplaintMS/comptotal.html', context)

@login_required
def list(request):
    c = Complaint.objects.filter(user=request.user).exclude(status='1')
    result = Complaint.objects.filter(user=request.user).exclude(Q(status='3') | Q(status='2'))
    args = {'c': c, 'result': result}
    return render(request, 'ComplaintMS/Complaints.html', args)

@login_required
def slist(request):
    result = Complaint.objects.filter(user=request.user).exclude(Q(status='3') | Q(status='2'))
    args = {'result': result}
    return render(request, 'ComplaintMS/solvedcomplaint.html', args)

@login_required
def allcomplaints(request):
    complaints = Complaint.objects.all().exclude(status='1')  # Exclude "solved" complaints initially
    comp_search = request.GET.get("search")
    drop_filter = request.GET.get("drop")

    # Apply filters dynamically
    if drop_filter:
        complaints = complaints.filter(Q(Type_of_complaint__icontains=drop_filter))
    if comp_search:
        complaints = complaints.filter(Q(Type_of_complaint__icontains=comp_search) | 
                                       Q(Description__icontains=comp_search) | 
                                       Q(Subject__icontains=comp_search))

    # Handle the form submission
    if request.method == 'POST':
        cid = request.POST.get('cid2')
        if cid:
            complaint = Complaint.objects.get(id=cid)
            form = StatusUpdateForm(request.POST, instance=complaint)
            if form.is_valid():
                form.save()
                # Send email or other actions if needed
                messages.success(request, 'The complaint has been updated!')
                return redirect('allcomplaints')
    else:
        form = StatusUpdateForm()

    return render(request, 'ComplaintMS/allcomplaints.html', {'complaints': complaints, 'form': form, 'comp_search': comp_search})

# PDF viewer for complaint
def pdf_viewer(request):
    cid = request.POST.get('cid')
    if not cid:
        return HttpResponse("Error: Complaint ID not provided", status=400)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=Complaint_id.pdf'
    p = canvas.Canvas(response, pagesize=A4)

    # Fetch complaint details
    complaint = get_object_or_404(Complaint, id=cid)
    detail_string = complaint.Description
    detailname = f"User: {complaint.user.username}"
    detailsubject = f"Subject: {complaint.Subject}"
    detailtype = f"Type of Complaint: {complaint.get_type_of_complaint_display()}"
    detailtime = f"Time of Issue: {complaint.Time}"

    p.drawString(25, 770, "Report:")
    p.drawString(30, 750, detailname)
    p.drawString(30, 710, detailtype)
    p.drawString(30, 690, detailtime)
    p.drawString(30, 670, detailsubject)
    p.drawString(30, 650, "Description:")
    p.drawString(30, 630, detail_string)

    p.showPage()
    p.save()
    return response

# PDF view for user's complaint
@login_required
def pdf_view(request):
    cid = request.POST.get('cid')
    if not cid:
        return HttpResponse("Error: Complaint ID not provided", status=400)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=complaint_id.pdf'
    p = canvas.Canvas(response, pagesize=A4)

    # Fetch complaint details
    complaint = get_object_or_404(Complaint, id=cid)
    detail_string = complaint.Description
    detailname = f"User: {complaint.user.username}"
    detailsubject = f"Subject: {complaint.Subject}"
    detailtype = f"Type of Complaint: {complaint.get_type_of_complaint_display()}"
    detailtime = f"Time of Issue: {complaint.Time}"

    p.drawString(25, 770, "Report:")
    p.drawString(30, 750, detailname)
    p.drawString(30, 710, detailtype)
    p.drawString(30, 690, detailtime)
    p.drawString(30, 670, detailsubject)
    p.drawString(30, 650, "Description:")
    p.drawString(30, 630, detail_string)

    p.showPage()
    p.save()
    return response

@login_required
def solved(request):
    solved_complaints = Complaint.objects.filter(status='1')
    return render(request, 'ComplaintMS/solved.html', {'solved_complaints': solved_complaints})