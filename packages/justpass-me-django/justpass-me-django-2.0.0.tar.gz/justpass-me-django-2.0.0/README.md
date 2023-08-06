## Django Client for justpass.me


1. Install the justpassme app

    For django 2.2, use justpass-me-django==2.0.0
    For django 3.1+, use justpass-me-django==3.0.0
    
   ```sh
   pip install justpass-me-django
   ```

2. Add the following to your INSTALLED_APPS

    ```python
   INSTALLED_APPS = [ 
   '....'
   'mozilla_django_oidc',
    'justpassme',
   '....'
   ]

    ```

2. Add the following to `settings.py`

   ```python
   AUTHENTICATION_BACKENDS = (
    'justpassme.OIDC_CLIENT.OIDCUserFinder',
    'django.contrib.auth.backends.ModelBackend',
    )


   SITE_URL = YOUR_SITE_URL   #Your full site url
   OIDC_USERNAME_FIELD = "username"   # The field to use to create users on justpass.me
   LOGIN_URL = "/accounts/login/"     # Your login view as usual

   OIDC_RP_CLIENT_ID = "app.client_id"      # client_id from justpass.me
   OIDC_RP_CLIENT_SECRET="app.client_secret" # client_secret from justpass.me
   OIDC_OP_URL= "https://organization_domain.accounts.justpass.me/openid/" #Put your organization domain on justpass.me

   OIDC_RP_SCOPES= "openid"
   OIDC_RP_SIGN_ALGO = 'HS256'
   OIDC_STORE_ID_TOKEN = True
   OIDC_OP_JWKS_ENDPOINT=OIDC_OP_URL  +"jwks"
   OIDC_OP_AUTHORIZATION_ENDPOINT=OIDC_OP_URL + "authorize/"
   OIDC_OP_TOKEN_ENDPOINT = OIDC_OP_URL +"token/"
   OIDC_OP_USER_ENDPOINT = OIDC_OP_URL + "userinfo/"
   OIDC_CALLBACK_CLASS= "justpass.OIDC_CLIENT.OIDCAuthn"
   OIDC_AUTHENTICATE_CLASS = "justpass.OIDC_CLIENT.OIDC_AUTHENTICATE"
   LOGIN_REDIRECT_URL_FAILURE="/justpass/failure/"
   LOGIN_REDIRECT_URL = "/justpass/success/"

   # If your application uses SSL.
   USE_X_FORWARDED_HOST = True
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


   # Provide the following functions that will be called when event is triggered, check example functions below
   REGISTRATION_SUCCESS = "Shop.justpass.reg_success"
   REGISTRATION_FAILURE = "Shop.justpass.reg_failure"
   AUTHENTICATION_SUCCESS = "Shop.justpass.auth_success"
   AUTHENTICATION_FAILURE = "Shop.justpass.auth_failure"

   ```
3. Add `justpass` to your urls
   ```python 
   urls_patterns= [
   '...',
   path(r'justpass/', include('justpassme.urls')),
   path('oidc/',include('mozilla_django_oidc.urls')),
   '....',
    ]
    ```
## Note:  If you use justpass.me as 2nd factor

Break your login function, Usually your login function will check for username and password, log the user in if the username and password are correct and create the user session, to support justpass.me, this has to change
   
   * authenticate the user
   * if username and password are correct , check if the user has mfa or not
       * if user has mfa then redirect to justpass.me
       * if user doesn't have mfa then call your function to create the user session

3. To start registration, go `justpass:reg``

   ```python
   def start_reg(request):
       from justpassme.helpers import start_reg
       return start_reg(request)
   ```

4. Write a function to start login and add it to your `urls.py`

   **Note:** The function expects the user username to be in `request.session["base_username"]`

   ```python
   def start_login(request):
       from justpassme.helpers import start_oidc_sign
       return start_oidc_sign(request)
   ```

5. Write 4 functions that handle the success and failure of registration and login. 
You can use the four functions below as a reference.

   ```python
   def auth_success(request):
      return redirect('home')
         
   def auth_failure(request):
     return render(request, 'login.html', {"failed": True})
         
   def reg_success(request):
      request.user.mfa_enabled = True
      request.user.save()
      request.session["reg"] = True
      return redirect('home')
      
   def reg_failure(request):
      request.session["reg"] = False
      return redirect('home')
   ```