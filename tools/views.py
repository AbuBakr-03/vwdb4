from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import uuid


# In-memory storage for demo (in real app, use database models)
created_tools = []


@login_required
def tools_list(request):
    """Main tools view with dual sidebar structure."""
    # Handle search functionality
    search_query = request.GET.get('search', '').strip()
    filtered_tools = created_tools
    
    if search_query:
        # Filter tools based on name and type
        filtered_tools = [
            tool for tool in created_tools 
            if search_query.lower() in tool['name'].lower() or 
               search_query.lower() in tool['type'].lower()
        ]
    
    context = {
        'section_name': 'Tools',
        'message': 'Tools management interface with dual sidebar navigation.',
        'created_tools': filtered_tools,
        'all_tools': created_tools,  # Keep original list for sidebar count
        'selected_tool': None,
        'search_query': search_query,
    }
    return render(request, 'tools/tools_list.html', context)


@login_required
def create_tool(request, tool_type):
    """Automatically create a new tool of specified type."""
    # Generate tool ID and name
    tool_id = str(uuid.uuid4())[:8]
    tool_name = f'{tool_type}_tool'
    
    # Create tool object immediately
    new_tool = {
        'id': tool_id,
        'name': tool_name,
        'type': tool_type,
        'created': True,
    }
    
    created_tools.append(new_tool)
    
    # Add success message
    messages.success(request, 'Your tool has been created successfully!')
    
    # Redirect to tool detail/configuration page
    return redirect('tools:tool_detail', tool_id=tool_id)


@login_required
def tool_detail(request, tool_id):
    """Display tool configuration details."""
    # Find the tool
    selected_tool = None
    for tool in created_tools:
        if tool['id'] == tool_id:
            selected_tool = tool
            break
    
    if not selected_tool:
        messages.error(request, 'Tool not found.')
        return redirect('tools:tools_list')
    
    context = {
        'section_name': 'Tools',
        'created_tools': created_tools,
        'selected_tool': selected_tool,
        'show_success': request.GET.get('created') == 'true',
    }
    return render(request, 'tools/tools_list.html', context)


@login_required
def save_tool_config(request, tool_id):
    """Save tool configuration updates."""
    if request.method == 'POST':
        # Find the tool
        selected_tool = None
        for tool in created_tools:
            if tool['id'] == tool_id:
                selected_tool = tool
                break
        
        if not selected_tool:
            messages.error(request, 'Tool not found.')
            return redirect('tools:tools_list')
        
        # Update tool properties
        tool_name = request.POST.get('tool_name', selected_tool['name'])
        description = request.POST.get('description', '')
        
        # Update the tool object
        selected_tool['name'] = tool_name
        selected_tool['description'] = description
        
        # Add any tool-specific configurations
        if selected_tool['type'] == 'mcp':
            selected_tool['server_url'] = request.POST.get('server_url', '')
            selected_tool['secret_token'] = request.POST.get('secret_token', '')
            selected_tool['timeout'] = request.POST.get('timeout', '20')
        elif selected_tool['type'] == 'smtp':
            # SMTP Server Settings
            selected_tool['smtp_server'] = request.POST.get('smtp_server', '')
            selected_tool['smtp_port'] = request.POST.get('smtp_port', '587')
            selected_tool['smtp_username'] = request.POST.get('smtp_username', '')
            selected_tool['smtp_password'] = request.POST.get('smtp_password', '')
            # Email Configuration
            selected_tool['from_email'] = request.POST.get('from_email', '')
            selected_tool['from_name'] = request.POST.get('from_name', '')
            selected_tool['subject_template'] = request.POST.get('subject_template', '')
            selected_tool['body_template'] = request.POST.get('body_template', '')
        elif selected_tool['type'] == 'smpp':
            # SMPP Connection Settings
            selected_tool['smpp_host'] = request.POST.get('smpp_host', '')
            selected_tool['smpp_port'] = request.POST.get('smpp_port', '2775')
            selected_tool['system_id'] = request.POST.get('system_id', '')
            selected_tool['smpp_password'] = request.POST.get('smpp_password', '')
            # SMS Configuration
            selected_tool['source_address'] = request.POST.get('source_address', '')
            selected_tool['data_coding'] = request.POST.get('data_coding', '0')
            selected_tool['message_template'] = request.POST.get('message_template', '')
            selected_tool['request_delivery_receipt'] = 'request_delivery_receipt' in request.POST
            selected_tool['flash_message'] = 'flash_message' in request.POST
        
        messages.success(request, 'Tool configuration saved successfully!')
        return redirect('tools:tool_detail', tool_id=tool_id)
    
    return redirect('tools:tool_detail', tool_id=tool_id)


@login_required
def delete_tool(request, tool_id):
    """Delete a tool with confirmation."""
    # Find the tool
    selected_tool = None
    tool_index = None
    for i, tool in enumerate(created_tools):
        if tool['id'] == tool_id:
            selected_tool = tool
            tool_index = i
            break
    
    if not selected_tool:
        messages.error(request, 'Tool not found.')
        return redirect('tools:tools_list')
    
    if request.method == 'POST':
        # Confirm deletion
        confirm = request.POST.get('confirm_delete')
        if confirm == 'yes':
            # Remove tool from list
            created_tools.pop(tool_index)
            messages.success(request, f'Tool "{selected_tool["name"]}" has been deleted successfully!')
            return redirect('tools:tools_list')
        else:
            messages.info(request, 'Tool deletion cancelled.')
            return redirect('tools:tool_detail', tool_id=tool_id)
    
    # Show confirmation page (GET request)
    context = {
        'section_name': 'Tools',
        'created_tools': created_tools,
        'selected_tool': selected_tool,
        'confirming_delete': True,
    }
    return render(request, 'tools/tools_list.html', context)