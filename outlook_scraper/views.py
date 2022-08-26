import imp
from outlook_scraper.graph_helper import *
from dateutil import tz, parser
from outlook_scraper.auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, get_token
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, timedelta
from outlook_scraper.query_run import get_groups

def initialize_context(request):
  context = {}

  # Check for any errors in the session
  error = request.session.pop('flash_error', None)

  if error != None:
    context['errors'] = []
    context['errors'].append(error)

  # Check for user in the session
  context['user'] = request.session.get('user', {'is_authenticated': False})
  return context

def home(request):
  context = initialize_context(request)

  return render(request, 'outlook_scraper/home.html', context)

def sign_in(request):
  # Get the sign-in flow
  flow = get_sign_in_flow()
  # Save the expected flow so we can use it in the callback
  try:
    request.session['auth_flow'] = flow
  except Exception as e:
    print(e)
  # Redirect to the Azure sign-in page
  return HttpResponseRedirect(flow['auth_uri'])

def callback(request):
  # Make the token request
  result = get_token_from_code(request)

  #Get the user's profile
  user = get_user(result['access_token'])
  store_user(request, user)
  return HttpResponseRedirect(reverse('home'))

def sign_out(request):
  # Clear out the user and token
  remove_user_and_token(request)
  
  return HttpResponseRedirect(reverse('home'))

def calendar(request):
  context = initialize_context(request)
  user = context['user']

  # Load the user's time zone
  # Microsoft Graph can return the user's time zone as either
  # a Windows time zone name or an IANA time zone identifier
  # Python datetime requires IANA, so convert Windows to IANA
  time_zone = get_iana_from_windows(user['timeZone'])
  tz_info = tz.gettz(time_zone)

  # Get midnight today in user's time zone
  today = datetime.now(tz_info).replace(
    hour=0,
    minute=0,
    second=0,
    microsecond=0)

  # Based on today, get the start of the week (Sunday)
  if (today.weekday() != 6):
    start = today - timedelta(days=today.isoweekday())
  else:
    start = today

  end = start + timedelta(days=7)

  token = get_token(request)

  events = get_calendar_events(
    token,
    start.isoformat(timespec='seconds'),
    end.isoformat(timespec='seconds'),
    user['timeZone'])

  if events:
    # Convert the ISO 8601 date times to a datetime object
    # This allows the Django template to format the value nicely
    for event in events['value']:
      event['start']['dateTime'] = parser.parse(event['start']['dateTime'])
      event['end']['dateTime'] = parser.parse(event['end']['dateTime'])

    table_content = []
    slack_groups = get_groups()
    for group in slack_groups:
      for message in group:
        print(message)
        table_content.append({
          'application': 'Slack',
          'message_author': message['sender'],
          'message_content': message['text'],
          'timestamp': message['time_stamp']
        })
    for event in events['value']:
      table_content.append({
        'application': 'Outlook Calendar', 
        'message_author': event['organizer']['emailAddress']['name'],
        'message_content': event['subject']+' from '+event['start']['dateTime'].strftime('%-I:%M %p')+' to '+event['end']['dateTime'].strftime('%-I:%M %p')+' on '+event['end']['dateTime'].strftime('%A'),
        'timestamp': ''
      })
    

    # for item in table_content:
    #   print(item)
    context['notifications'] = table_content

  return render(request, 'outlook_scraper/calendar.html', context)
