import json
from http import HTTPStatus

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.contrib.auth import login, get_user_model, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Permission
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from cloudspotlicense.api import CloudspotLicense_API
from cloudspotlicense.constants.errors import BadCredentials
from cloudspotlicense.constants.responses import ResponseStatus

from .models import GlobalPermission, CloudspotCompany
from .helpers import revoke_permissions, grant_permissions

class LoginView(View):
    """ Authenticates the user against the Cloudspot License Server """
    
    template_name = 'auth/login.html'
    
    def get(self, request, *args, **kwargs):
        redirect_url = settings.LOGIN_REDIRECT_URL if hasattr(settings, 'LOGIN_REDIRECT_URL') else '/'
        if request.user.is_authenticated: return redirect(redirect_url)
        
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        redirect_url = settings.LOGIN_REDIRECT_URL if hasattr(settings, 'LOGIN_REDIRECT_URL') else '/'
        login_url = settings.LOGIN_URL if hasattr(settings, 'LOGIN_URL') else '/'
        
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        if username: username = username.lower() # make case insensitive
        
        # We authenticate using the License Server
        api = CloudspotLicense_API(settings.CLOUDSPOT_LICENSE_APP)
        try:
            api.authenticate(username, password)
        except BadCredentials:
            messages.error(request, _('Email or password incorrect'))
            return redirect(login_url)
        
        # Gather the additional user info from the API
        api.get_user()
        
        # First we check all the returned companies, and create them if they're not already present on our system
        
        returned_companies = []
        for company_perm in api.permissions.items():
            company = CloudspotCompany.objects.filter(id=company_perm.company_id).first()
            if not company: company = CloudspotCompany.objects.create(id=company_perm.company_id, name=company_perm.company_name)
            elif company.name != company_perm.company_name:
                company.name = company_perm.company_name
                company.save()
            
            # Add the id to an array that we use later
            returned_companies.append(company_perm.company_id)
        
       # Then we check if we know the user in our system
        UserModel = get_user_model()
        try:
            
            # Update the user with the new information
            user = UserModel.objects.get(username=username)
            user.first_name = api.user.first_name
            user.last_name = api.user.last_name
            user.license_token = api.token
            user.is_active = True
            user.save()
            
        except ObjectDoesNotExist:
            
            # We don't know the user, so we create them
            # Push it to the database
            user = UserModel.objects.create_user(username=username, email=username, password=password, **{
                'first_name' : api.user.first_name,
                'last_name' : api.user.last_name,
                'license_token' : api.token,
            })
            
            user.save()
            
        # Now that we know the user, we clear all the previously linked companies and reassign them to the companies that are included in the response
        user.available_companies.clear()
        for company_id in returned_companies: user.available_companies.add(company_id)
        
        # The user and companies are created, if not already present. We check if the user already has a company linked to them, from a previous login.
        if user.company:
            
            # If there is a company present, we check if the current company has also been returned in the response.
            
            if str(user.company.id) in returned_companies:
                
                # The current company is included in the response, so we set the appropriate permissions and log the user in.
        
                # Remove all existing permissions
                revoke_permissions(user)
                
                # Assign all the returned permissions
                permissions = []
                for perm in api.permissions.items():
                    if perm.company_id == str(user.company.id):
                        for perm in perm.permissions:
                            permissions.append(perm)
                        break
                
                grant_permissions(user, permissions)
                
                # Finally, we log them in and redirect them
                login(request, user)
                
                return redirect(redirect_url)
            else:
                user.company = None
                user.save()
        
        # Else, if the user has no company OR the current company of the user is not included in the response, the users needs to select a new company.
        login(request, user)
        return redirect('select_company')
        
class SelectCompanyView(LoginRequiredMixin, View):
    """ Shows a list of all the available companies to a user to select from """
    
    template_name = 'auth/select_company.html'
    
    def get(self, request, *args, **kwargs):
        api = CloudspotLicense_API(settings.CLOUDSPOT_LICENSE_APP, token=request.user.license_token)
        api.get_permissions()
        context_data = { 'company_permissions' : api.permissions.items() }
        return render(request, self.template_name, context_data)

class SetCompanyView(LoginRequiredMixin, View):
    """ Sets the chosen company for a user and assigns the permissions """
    
    def get(self, request, *args, **kwargs):
        redirect_url = settings.LOGIN_REDIRECT_URL if hasattr(settings, 'LOGIN_REDIRECT_URL') else '/'
        
        user = request.user
        api = CloudspotLicense_API(settings.CLOUDSPOT_LICENSE_APP, token=user.license_token)
        
        # Set company
        user.company = self.company
        user.save()
        
        # Remove all existing permissions
        revoke_permissions(user)
        
        # Get permissions
        try:
            permissions = api.get_company_permissions(self.company.id)
        except Exception as e:
            messages.error(request, e)
            return redirect('select_company')
        
        # Assign all the returned permissions
        grant_permissions(user, permissions)
        
        return redirect(redirect_url)
    
    def dispatch(self, request, *args, **kwargs):
        self.company = CloudspotCompany.objects.filter(id=kwargs['company_id']).first()
        if not self.company: return HttpResponseBadRequest(_('The selected company does not exist'))
        return super().dispatch(request, *args, **kwargs)

class ImpersonationCheckView(View):
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({ 'status' : 'operational' })

class ImpersonationView(View):
    """ Handles the verification and authentication for an impersonation request """
    
    def get(self, request, *args, **kwargs):
        redirect_url = settings.LOGIN_REDIRECT_URL if hasattr(settings, 'LOGIN_REDIRECT_URL') else '/'
        
        impersonation_token = kwargs.get('token', None)
        api = CloudspotLicense_API(settings.CLOUDSPOT_LICENSE_APP)
        
        validate = api.auth.validate_impersonation(impersonation_token)
        if validate.has_error:
            return HttpResponseBadRequest('Token could not be validated. Error: {0}'.format(validate.error.message))

        # user and company checking
        username = validate.user
        company_id = validate.company
        auth_token = validate.auth_token
        
        user = get_user_model().objects.filter(username=username).first()
        if not user: return HttpResponseBadRequest('User with username {0} could not be found.'.format(username))
        company = CloudspotCompany.objects.filter(pk=company_id).first()
        if not company: return HttpResponseBadRequest('Company with ID {0} could not be found.'.format(company_id))
        if company not in user.available_companies.all(): return HttpResponseBadRequest('User is not in requested company.')
        
        # User is a valid user and has a valid company
        # Use the returned auth token to get all the permissions for the specified company
        api = CloudspotLicense_API(settings.CLOUDSPOT_LICENSE_APP, token=auth_token)
        
        # Set the company for impersonation
        # TODO: Change the company only for the impersonation, so that the user can still use their own chosen company while being impersonated
        user.company = company
        
        # Update the license token so we don't get a mismatch between the license server and the application
        user.license_token = auth_token
        
        user.save()
        
        try:
            permissions = api.get_company_permissions(company_id)
        except Exception as e:
            return HttpResponseBadRequest('Could not retrieve permissions for user. Error: {0}'.format(e))
        
        # Assign all the returned permissions
        grant_permissions(user, permissions)
        
        # Login
        messages.success(request, f"You're now impersonating <b>{user.get_full_name()}.")
        login(request, user)
        return redirect(redirect_url)

@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    """ Handles all the webhook events that the Cloudspot License Server server sends """
    
    def post(self, request, *args, **kwargs):
        
        req = json.loads(request.body)
        event = req['event']
        data = req['data']
        UserModel = get_user_model()
        
        if event == 'permissions.updated':
            token = data['token']
            
            try:
                user = UserModel.objects.get(license_token=token)
            except UserModel.DoesNotExist:
                return JsonResponse({ 'status' : ResponseStatus.NOT_FOUND, 'error' : { 'message' : 'No user matched the token.' }}, status=HTTPStatus.NOT_FOUND)
            
            permissions = data['permissions']
            company_id = data['company_id']
            available_companies = data['available_companies']
            
            # update the companies that the user is in
            user.available_companies.clear()
            for company_perm in available_companies:
                company = CloudspotCompany.objects.filter(id=company_perm['company_id']).first()
                if not company: company = CloudspotCompany.objects.create(id=company_perm['company_id'], name=company_perm['company_name'])
                elif company.name != company_perm['company_name']:
                    company.name = company_perm['company_name']
                    company.save()
                
                user.available_companies.add(company.id)
            
            try:
                company = CloudspotCompany.objects.get(pk=company_id)
            except CloudspotCompany.DoesNotExist:
                return JsonResponse({ 'status' : ResponseStatus.NOT_FOUND, 'error' : { 'message' : 'No company matched the id.' }}, status=HTTPStatus.NOT_FOUND)

            # Only update the user permissions if the current company is the company in the request
            # Otherwise, these permissions do not apply to this user at this moment
            # When the user switches companies, the new permissions get retrieved from the License Server anyway
            if user.company == company:
                if 'use_app' not in permissions:
                    # if the 'use_app' permission is revoked, the user is not allowed to use the app for this company anymore.
                    # we set the company to none. This will force the user to choose a new company on next page load or get logged out.
                    user.company = None
                    user.save()
                else:
                    revoke_permissions(user)
                    grant_permissions(user, permissions)

            return JsonResponse({ 'status' : ResponseStatus.OBJECT_UPDATED })
        elif event == 'user.email.updated':
            current_email = data['current_email']
            change_to_email = data['change_to_email']
            
            try:
                user = UserModel.objects.get(username=current_email)
            except UserModel.DoesNotExist:
                return JsonResponse({ 'status' : ResponseStatus.NOT_FOUND, 'error' : { 'message' : 'No user matched the current_email.' }}, status=HTTPStatus.NOT_FOUND)
            
            user.username = change_to_email
            user.email = change_to_email
            user.save()
            
            return JsonResponse({ 'status' : ResponseStatus.OBJECT_UPDATED })
        elif event == 'user.pin.updated':
            user_username = data['user_username']
            pin = data['pin']
            if pin == '': pin = None
            
            try:
                user = UserModel.objects.get(username=user_username)
            except UserModel.DoesNotExist:
                return JsonResponse({ 'status' : ResponseStatus.NOT_FOUND, 'error' : { 'message' : 'No user matched the user_username.' }}, status=HTTPStatus.NOT_FOUND)
            
            user.pin = pin
            user.save()
            
            return JsonResponse({ 'status' : ResponseStatus.OBJECT_UPDATED })