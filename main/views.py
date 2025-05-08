from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from main.utils import can_access, get_all_subordinates
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Level4Text, Profile  # Import the model
from django.http import HttpResponse
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from django.http import HttpResponseRedirect,HttpResponseBadRequest
from django.urls import reverse
# Check if the user is Level 4
def is_level_4(user):
    return user.profile.level == 4


@login_required
def main_page(request):
    user_profile = request.user.profile  # Get the user's profile
    user_level = user_profile.level      # Get the user's level
    user_div = user_profile.div          # Get the user's division
    user_sub_div = user_profile.sub_div  # Get the user's subdivision

    if user_level == 4:
        # Level 4 users see their own highlights and lowlights
        return render(request, 'main.html', {
            'user_level': user_level,
            'user_div': user_div,
            'user_sub_div': user_sub_div,
        })

    elif user_level == 3:
        # Level 3 users see subdivisions directly under them
        subordinates = Profile.objects.filter(manager=user_profile)
        sub_divisions = subordinates.values_list('sub_div', flat=True).distinct()
        return render(request, 'main.html', {
            'user_level': user_level,
            'user_div': user_div,
            'sub_divisions': sub_divisions,
        })

    elif user_level == 2:
        # Level 2 users see aggregated data for all subdivisions under their division
        subordinates = Profile.objects.filter(manager=user_profile)
        sub_divisions = subordinates.values_list('sub_div', flat=True).distinct()
        return render(request, 'main.html', {
            'user_level': user_level,
            'user_div': user_div,
            'sub_divisions': sub_divisions,
        })

    elif user_level == 1:
        # Level 1 users see the admin dashboard
        return render(request, 'main.html', {
            'user_level': user_level,
        })

    else:
        # Redirect to login if the user level is invalid
        return HttpResponseRedirect(reverse('login'))

@login_required
def level_4_page(request):
    user_profile = request.user.profile  # Get the user's profile
    user_div = user_profile.div          # Get the user's division
    user_sub_div = user_profile.sub_div  # Get the user's subdivision

    if request.method == 'POST':
        # Handle the submitted highlights and lowlights
        highlight_text = request.POST.get('highlight_text', '').strip()
        lowlight_text = request.POST.get('lowlight_text', '').strip()

        if highlight_text:  # Save highlights if not empty
            Level4Text.objects.create(
                user=request.user,
                sub_div=user_sub_div,
                category='highlight',
                text=highlight_text
            )

        if lowlight_text:  # Save lowlights if not empty
            Level4Text.objects.create(
                user=request.user,
                sub_div=user_sub_div,
                category='lowlight',
                text=lowlight_text
            )

        # Redirect to the same page to prevent form resubmission
        return HttpResponseRedirect(reverse('HL_LL'))

    # Retrieve only the texts written by the current user for their division and subdivision
    all_highlights = Level4Text.objects.filter(
        user=request.user,
        sub_div=user_sub_div,
        category='highlight'
    ).order_by('-created_at')

    all_lowlights = Level4Text.objects.filter(
        user=request.user,
        sub_div=user_sub_div,
        category='lowlight'
    ).order_by('-created_at')

    return render(request, 'level_4_page.html', {
        'all_highlights': all_highlights,
        'all_lowlights': all_lowlights,
        'user_div': user_div,
        'user_sub_div': user_sub_div,
    })

@login_required
def level_1_page(request):
    if request.user.profile.level != 1:
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Retrieve all highlights and lowlights grouped by division and subdivision
    divisions = Profile.objects.values_list('div', flat=True).distinct()
    grouped_data = {}

    for div in divisions:
        subdivisions = Profile.objects.filter(div=div).values_list('sub_div', flat=True).distinct()
        grouped_data[div] = {}
        for sub_div in subdivisions:
            highlights = Level4Text.objects.filter(sub_div=sub_div, category='highlight').order_by('-created_at')
            lowlights = Level4Text.objects.filter(sub_div=sub_div, category='lowlight').order_by('-created_at')
            grouped_data[div][sub_div] = {
                'highlights': highlights,
                'lowlights': lowlights,
            }

    return render(request, 'level_1_page.html', {
        'grouped_data': grouped_data,
    })

@login_required
def level_3_page(request):
    if request.user.profile.level != 3:
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Get the subdivisions directly under the Level 3 user
    subordinates = Profile.objects.filter(manager=request.user.profile)
    subdivisions = subordinates.values_list('sub_div', flat=True).distinct()

    # Get the selected subdivision from the query parameters
    selected_sub_div = request.GET.get('sub_div', None)

    if selected_sub_div:
        # Filter highlights and lowlights for the selected subdivision
        subordinate_user_ids = subordinates.filter(sub_div=selected_sub_div).values_list('user', flat=True)
        all_highlights = Level4Text.objects.filter(user__in=subordinate_user_ids, category='highlight').order_by('-created_at')
        all_lowlights = Level4Text.objects.filter(user__in=subordinate_user_ids, category='lowlight').order_by('-created_at')
    else:
        # Default to showing no highlights or lowlights if no subdivision is selected
        all_highlights = []
        all_lowlights = []

    return render(request, 'level_3_page.html', {
        'subdivisions': subdivisions,
        'selected_sub_div': selected_sub_div,
        'all_highlights': all_highlights,
        'all_lowlights': all_lowlights,
    })


@login_required
def level_2_page(request):
    if request.user.profile.level != 2:
        return HttpResponseForbidden("You do not have permission to access this page.")


    # Fetch all subordinates recursively
    all_subordinates = get_all_subordinates(request.user.profile)
    subordinate_user_ids = [subordinate.user.id for subordinate in all_subordinates]
    selected_sub_div = request.GET.get('sub_div', None)
    # Retrieve highlights and lowlights for all subordinates
    all_highlights = Level4Text.objects.filter(user__in=subordinate_user_ids, category='highlight').order_by('-sub_div', '-created_at')
    all_lowlights = Level4Text.objects.filter(user__in=subordinate_user_ids, category='lowlight').order_by('-sub_div', '-created_at')

    # Get all subdivisions under the Level 2 user
    subdivisions = Profile.objects.filter(manager=request.user.profile).values_list('sub_div', flat=True).distinct()

    return render(request, 'level_2_page.html', {
        'subdivisions': subdivisions,
        'selected_sub_div': selected_sub_div,
        'all_highlights': all_highlights,
        'all_lowlights': all_lowlights,
    })

@login_required
def delete_text(request, text_id):
    text = get_object_or_404(Level4Text, id=text_id)
    text.delete()
    if(request.user.profile.level == 4):
        return redirect('HL_LL')
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def edit_text(request, text_id):
    text = get_object_or_404(Level4Text, id=text_id)

    if request.method == 'POST':
        new_text = request.POST.get('typed_text', '')
        text.text = new_text
        text.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return render(request, 'edit_text.html', {'text': text})

@login_required
def add_text(request):
    if request.method == 'POST':
        sub_div = request.POST.get('sub_div')
        highlight_text = request.POST.get('highlight_text', '').strip()
        lowlight_text = request.POST.get('lowlight_text', '').strip()

        if not sub_div:
            return HttpResponseBadRequest("Subdivision is required.")

        # Add highlight if provided
        if highlight_text:
            Level4Text.objects.create(
                user=request.user,
                sub_div=sub_div,
                category='highlight',
                text=highlight_text
            )

        # Add lowlight if provided
        if lowlight_text:
            Level4Text.objects.create(
                user=request.user,
                sub_div=sub_div,
                category='lowlight',
                text=lowlight_text
            )

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def generate_ppt(request):
    if request.user.profile.level == 4:
        all_highlights = Level4Text.objects.filter(user=request.user, category='highlight').order_by('-created_at')
        all_lowlights = Level4Text.objects.filter(user=request.user, category='lowlight').order_by('-created_at')
        subdivisions = [request.user.profile.sub_div]  # Only the user's subdivision

    elif request.user.profile.level == 1:
        # Retrieve all highlights and lowlights for all subdivisions
        all_highlights = Level4Text.objects.filter(category='highlight').order_by('-created_at')
        all_lowlights = Level4Text.objects.filter(category='lowlight').order_by('-created_at')
        subdivisions = Profile.objects.values_list('sub_div', flat=True).distinct()
        
    else:
        # Fetch all subordinates recursively
        all_subordinates = get_all_subordinates(request.user.profile)
        subordinate_user_ids = [subordinate.user.id for subordinate in all_subordinates]

        # Retrieve highlights and lowlights for all subordinates
        all_highlights = Level4Text.objects.filter(user__in=subordinate_user_ids, category='highlight').order_by('-created_at')
        all_lowlights = Level4Text.objects.filter(user__in=subordinate_user_ids, category='lowlight').order_by('-created_at')

        # Get all subdivisions under the Level 2 user
        subdivisions = Profile.objects.filter(manager=request.user.profile).values_list('sub_div', flat=True).distinct()
    # Create a new PowerPoint presentation
    presentation = Presentation()

    for sub_div in subdivisions:
        subdiv_highlights = all_highlights.filter(sub_div=sub_div)
        subdiv_lowlights = all_lowlights.filter(sub_div=sub_div)
        # Clean the text to remove carriage return characters
        highlights = [text.text.replace('\r', '').replace('\n', ' ') for text in subdiv_highlights]
        lowlights = [text.text.replace('\r', '').replace('\n', ' ') for text in subdiv_lowlights]

        # Add a slide for the current subdivision
        slide_layout = presentation.slide_layouts[5]  # Title and Content layout
        slide = presentation.slides.add_slide(slide_layout)

        # Add title
        title = slide.shapes.title
        title.text = f"Highlights and Lowlights - {sub_div}"

        # Add a table for Highlights and Lowlights
        row_count = max(len(highlights), len(lowlights)) + 1  # +1 for the header row
        col_count = 2

        # Table position and dimensions
        left = Inches(1)
        top = Inches(2)
        width = Inches(8)
        height = Inches(0.6 * row_count)

        table = slide.shapes.add_table(row_count, col_count, left, top, width, height).table

        # Set column headers
        table.cell(0, 0).text = "Highlights"
        table.cell(0, 1).text = "Lowlights"

        # Style the header row
        for i in range(2):
            cell = table.cell(0, i)
            cell.text_frame.paragraphs[0].font.bold = True
            cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            cell.text_frame.paragraphs[0].font.size = Pt(14)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(10, 130, 118)
            cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

        # Populate the table with highlights and lowlights
        for i in range(1, row_count):
            # Highlights
            if i - 1 < len(highlights):
                table.cell(i, 0).text = highlights[i - 1]
            else:
                table.cell(i, 0).text = ""

            # Lowlights
            if i - 1 < len(lowlights):
                table.cell(i, 1).text = lowlights[i - 1]
            else:
                table.cell(i, 1).text = ""

            # Style table content
            for j in range(2):
                cell = table.cell(i, j)
                cell.text_frame.paragraphs[0].font.size = Pt(12)
                cell.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT

    # Save the presentation to a BytesIO stream
    from io import BytesIO
    ppt_stream = BytesIO()
    presentation.save(ppt_stream)
    ppt_stream.seek(0)

    # Return the PowerPoint file as a response
    response = HttpResponse(ppt_stream, content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
    response['Content-Disposition'] = 'attachment; filename="Highlights_Lowlights.pptx"'
    return response