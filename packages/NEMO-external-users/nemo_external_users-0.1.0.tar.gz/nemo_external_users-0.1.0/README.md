# NEMO External Users
NEMO plugin allowing users to create and manage their own accounts.

## Installation

1. Install the package using pip

   ```bash
   pip install NEMO-external-users
   ```

2. Edit **settings.py** 

   - Add the plugin to your INSTALLED_APPS:
   
      ```python
      INSTALLED_APPS = [
          "django.contrib.sites",
          ...,
          "NEMO_external_users",
          "NEMO",
          ...,
      ]
      ```
     
      It's important that "NEMO_external_users" is added before "NEMO" (it overrides some of the templates).
   
   - Extend authentication backends:
      ```python
      AUTHENTICATION_BACKENDS = [
          ...,
          'NEMO_external_users.backends.SettingsBackend',
          'NEMO_external_users.backends.ExternalUsersBackend',
      ]
      ```
   
   - Add to context_processors:
      ```python
      'NEMO.context_processors.show_logout_button',
      ```

3. Run migrations

   ```bash
   python manage.py migrate
   ```

## Settings
   ```python
   # Default projects to which new users will be assigned
   NEMO_EXTERNAL_USERS_NEW_USER_PROJECTS = [...]
   
   # Default tool qualification groups to which new users will be assigned
   NEMO_EXTERNAL_USERS_NEW_USER_TOOL_QUALIFICATION_GROUPS = [...]
   
   # Default tools to which new users will be assigned
   NEMO_EXTERNAL_USERS_NEW_USER_TOOLS = [...]
   
   # Permissions for the new users (boolean)
   NEMO_EXTERNAL_USERS_NEW_USER_IS_STAFF = False
   NEMO_EXTERNAL_USERS_NEW_USER_IS_USER_OFFICE = False
   NEMO_EXTERNAL_USERS_NEW_USER_IS_ACCOUNTING_OFFICER = False
   NEMO_EXTERNAL_USERS_NEW_USER_IS_FACILITY_MANAGER = False
   NEMO_EXTERNAL_USERS_NEW_USER_IS_ADMINISTRATOR = False
   NEMO_EXTERNAL_USERS_NEW_USER_IS_TECHNICIAN = False
   NEMO_EXTERNAL_USERS_NEW_USER_IS_SERVICE_PERSONNEL = False
   
   # Indicator if training is required for the new users
   NEMO_EXTERNAL_USERS_NEW_USER_TRAINING_REQUIRED = True
   ```
