# Campaigns Module

## Overview
The Campaigns module provides a comprehensive interface for creating and managing AI agent campaigns across multiple communication channels.

## Campaign Creation Form

### Features
- **Beautiful UI**: Built with daisyUI 5 and Tailwind CSS 4
- **Comprehensive Fields**: Covers all aspects of campaign configuration
- **Auto-save**: Automatically saves drafts every 30 seconds
- **Responsive Design**: Works on all device sizes
- **Form Validation**: Client-side and server-side validation

### Form Sections

#### 1. Basic Information
- Campaign Name (required)
- Use Case (HR Screening, Collections, Sales, etc.)
- Description

#### 2. Channel & Voice Configuration
- Communication Channel (Voice, SMS, WhatsApp, Email)
- Voice ID (for voice campaigns)
- Language Selection

#### 3. Script & Content
- Script Template with variable support ({{variable_name}})
- Campaign Variables (JSON format)

#### 4. Scheduling & Timing
- Start/End Date & Time
- Daily Time Windows
- Days of Week Selection

#### 5. Campaign Limits & Settings
- Priority Level
- Maximum Calls
- Maximum Concurrent Calls

#### 6. Retry Policy
- Maximum Retry Attempts
- Retry Conditions (No Answer, Busy, Failed, Voicemail)
- Backoff Delays

### Usage

#### Access the Form
Navigate to `/campaigns/create/` to access the campaign creation form.

#### Creating a Campaign
1. Fill in the required fields (marked with *)
2. Configure optional settings as needed
3. Click "Create Campaign" to submit
4. Form automatically saves drafts every 30 seconds

#### Form Features
- **Auto-save**: Your progress is automatically saved to localStorage
- **Draft Recovery**: If you refresh the page, your draft will be restored
- **Smart Fields**: Voice ID field only shows for voice campaigns
- **Validation**: Required fields are enforced both client and server-side

### Technical Details

#### Form Fields Mapping
The form fields are mapped to the Campaign model as follows:

- `name` → `Campaign.name`
- `description` → `Campaign.description`
- `script_template` → `Campaign.prompt_template`
- `voice_id` → `Campaign.voice_id`
- `max_calls` → `Campaign.max_calls`
- `max_concurrent` → `Campaign.max_concurrent`

Additional fields are stored in `Campaign.agent_config` JSON field:
- `use_case`, `channel`, `language`, `priority`
- `campaign_variables`, `start_date`, `end_date`
- `start_local_time`, `end_local_time`, `days_of_week`
- `max_attempts`, `retry_on`, `backoff_seconds`

#### JavaScript Features
- Auto-save functionality
- Draft recovery
- Dynamic field visibility (voice fields for voice campaigns)
- Form validation

### Styling Guidelines
- Uses daisyUI 5 components (cards, forms, buttons)
- Follows Tailwind CSS 4 utility classes
- Responsive grid layouts
- Semantic color usage (primary, secondary, accent, etc.)
- Consistent spacing and typography

### Future Enhancements
- File upload for script templates
- Campaign templates/presets
- Advanced scheduling (timezone support)
- Integration with contact lists
- Campaign preview/testing
- Multi-language script support
