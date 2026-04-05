from collections import OrderedDict
import os

def get_input(question, default=""):
    add = "[{}] ".format(default) if default != "" else ""
    user = input("{}: {}".format(question, add)).strip()
    if user == "":
        user = default
    return user

def generate_config(defaults, worker, authentication_methods):
    print('Hit enter to use default in []')
    print()
        
    if worker:
        SUPERVISOR_USER = get_input('What is the id for your submitty user?', defaults['supervisor_user'])
        print('SUPERVISOR USER : {}'.format(SUPERVISOR_USER))
    else:
        DATABASE_HOST = get_input('What is the database host?', defaults['database_host'])
        print(DATABASE_HOST)

        if not os.path.isdir(DATABASE_HOST):
            DATABASE_PORT = int(get_input('What is the database port?', defaults['database_port']))
            print()
        else:
            DATABASE_PORT = defaults['database_port']

        DATABASE_USER = get_input('What is the global database user/role?', defaults['database_user'])
        print()

        default = ''
        if 'database_password' in defaults and DATABASE_USER == defaults['database_user']:
            default = '(Leave blank to use same password)'
        DATABASE_PASS = get_input('What is the password for the global database user/role {}? {}'.format(DATABASE_USER, default))
        if DATABASE_PASS == '' and DATABASE_USER == defaults['database_user'] and 'database_password' in defaults:
            DATABASE_PASS = defaults['database_password']
        print()

        DATABASE_COURSE_USER = get_input('What is the course database user/role?', defaults['database_course_user'])
        print()

        default = ''
        if 'database_course_password' in defaults and DATABASE_COURSE_USER == defaults['database_course_user']:
            default = '(Leave blank to use same password)'
        DATABASE_COURSE_PASSWORD = get_input('What is the password for the course database user/role {}? {}'.format(DATABASE_COURSE_USER, default))
        if DATABASE_COURSE_PASSWORD == '' and DATABASE_COURSE_USER == defaults['database_course_user'] and 'database_course_password' in defaults:
            DATABASE_COURSE_PASSWORD = defaults['database_course_password']
        print()

        TIMEZONE = get_input('What timezone should Submitty use? (for a full list of supported timezones see http://php.net/manual/en/timezones.php)', defaults['timezone'])
        print()

        DEFAULT_LOCALE = get_input('What default language should the Submitty site use?', 'en_US')
        print()

        COURSE_MATERIAL_UPLOAD_LIMIT_MB = get_input('What is the maximum file upload size for course materials (in MB)?', defaults['course_material_file_upload_limit_mb'])
        print()

        SUBMISSION_URL = get_input('What is the url for submission? (ex: http://192.168.56.101 or '
                                'https://submitty.cs.rpi.edu)', defaults['submission_url']).rstrip('/')
        print()

        VCS_URL = get_input('What is the url for VCS? (Leave blank to default to submission url + {$vcs_type}) (ex: http://192.168.56.101/{$vcs_type} or https://submitty-vcs.cs.rpi.edu/{$vcs_type}', defaults['vcs_url']).rstrip('/')
        print()

        INSTITUTION_NAME = get_input('What is the name of your institution? (Leave blank/type "none" if not desired)',
                                defaults['institution_name'])
        print()

        if INSTITUTION_NAME == '' or INSTITUTION_NAME.isspace():
            INSTITUTION_HOMEPAGE = ''
        else:
            INSTITUTION_HOMEPAGE = get_input("What is the url of your institution\'s homepage? "
                                        '(Leave blank/type "none" if not desired)', defaults['institution_homepage'])
            if INSTITUTION_HOMEPAGE.lower() == "none":
                INSTITUTION_HOMEPAGE = ''
            print()
        
        SYS_ADMIN_EMAIL = get_input("What is the email for system administration?", defaults['sys_admin_email'])
        SYS_ADMIN_URL = get_input("Where to report problems with Submitty (url for help link)?", defaults['sys_admin_url'])

        print('What authentication method to use:')
        for i in range(len(authentication_methods)):
            print(f"{i + 1}. {authentication_methods[i]}")

        while True:
            try:
                auth = int(get_input('Enter number?', defaults['authentication_method'])) - 1
            except ValueError:
                auth = -1
            if auth in range(len(authentication_methods)):
                break
            print(f'Number must in between 1 - {len(authentication_methods)} (inclusive)!')
        print()

        AUTHENTICATION_METHOD = authentication_methods[auth]

        default_auth_options = defaults.get('ldap_options', dict())
        LDAP_OPTIONS = {
            'url': default_auth_options.get('url', ''),
            'uid': default_auth_options.get('uid', ''),
            'bind_dn': default_auth_options.get('bind_dn', '')
        }
        USER_CREATE_ACCOUNT = False
        if AUTHENTICATION_METHOD == 'DatabaseAuthentication':
            user_create_account = get_input("Allow users to create their own accounts? [y/n]", 'n')
            USER_CREATE_ACCOUNT = user_create_account.lower() in ['yes', 'y']
            print()
        if AUTHENTICATION_METHOD == 'LdapAuthentication':
            LDAP_OPTIONS['url'] = get_input('Enter LDAP url?', LDAP_OPTIONS['url'])
            LDAP_OPTIONS['uid'] = get_input('Enter LDAP UID?', LDAP_OPTIONS['uid'])
            LDAP_OPTIONS['bind_dn'] = get_input('Enter LDAP bind_dn?', LDAP_OPTIONS['bind_dn'])

        default_auth_options = defaults.get('saml_options', dict())
        SAML_OPTIONS = {
            'name': default_auth_options.get('name', ''),
            'username_attribute': default_auth_options.get('username_attribute', '')
        }

        if AUTHENTICATION_METHOD == 'SamlAuthentication':
            SAML_OPTIONS['name'] = get_input('Enter name you would like shown to user for authentication?', SAML_OPTIONS['name'])
            SAML_OPTIONS['username_attribute'] = get_input('Enter SAML username attribute?', SAML_OPTIONS['username_attribute'])


        CGI_URL = SUBMISSION_URL + '/cgi-bin'

        SUBMITTY_ADMIN_USERNAME = get_input("What is the submitty admin username (optional)?", defaults['submitty_admin_username'])

        while True:
            is_email_enabled = get_input("Will Submitty use email notifications? [y/n]", 'y')
            if (is_email_enabled.lower() in ['yes', 'y']):
                EMAIL_ENABLED = True
                EMAIL_USER = get_input("What is the email user?", defaults['email_user'])
                EMAIL_PASSWORD = get_input("What is the email password",defaults['email_password'])
                EMAIL_SENDER = get_input("What is the email sender address (the address that will appear in the From: line)?",defaults['email_sender'])
                EMAIL_REPLY_TO = get_input("What is the email reply to address?", defaults['email_reply_to'])
                EMAIL_SERVER_HOSTNAME = get_input("What is the email server hostname?", defaults['email_server_hostname'])
                try:
                    EMAIL_SERVER_PORT = int(get_input("What is the email server port?", defaults['email_server_port']))
                except ValueError:
                    EMAIL_SERVER_PORT = defaults['email_server_port']
                EMAIL_INTERNAL_DOMAIN = get_input("What is the internal email address format?", defaults['email_internal_domain'])
                break

            elif (is_email_enabled.lower() in ['no', 'n']):
                EMAIL_ENABLED = False
                EMAIL_USER = defaults['email_user']
                EMAIL_PASSWORD = defaults['email_password']
                EMAIL_SENDER = defaults['email_sender']
                EMAIL_REPLY_TO = defaults['email_reply_to']
                EMAIL_SERVER_HOSTNAME = defaults['email_server_hostname']
                EMAIL_SERVER_PORT = defaults['email_server_port']
                EMAIL_INTERNAL_DOMAIN = defaults['email_internal_domain']
                break
        print()
        full_config = OrderedDict()
        general_config = OrderedDict()
        database_config = OrderedDict()
        authentication_config = OrderedDict()
        submitty_config = OrderedDict()
        email_config = OrderedDict()
        if worker:
            general_config['supervisor_user'] = SUPERVISOR_USER
            
        else: 

            general_config['database_host'] = DATABASE_HOST
            general_config['database_port'] = DATABASE_PORT
            general_config['database_user'] = DATABASE_USER
            general_config['database_password'] = DATABASE_PASS
            general_config['database_course_user'] = DATABASE_COURSE_USER
            general_config['database_course_password'] = DATABASE_COURSE_PASSWORD
            general_config['timezone'] = TIMEZONE
            general_config['default_locale'] = DEFAULT_LOCALE

            general_config['authentication_method'] = AUTHENTICATION_METHOD
            general_config['vcs_url'] = VCS_URL
            general_config['submission_url'] = SUBMISSION_URL
            general_config['cgi_url'] = CGI_URL
            
            general_config['institution_name'] = INSTITUTION_NAME
            general_config['institution_homepage'] = INSTITUTION_HOMEPAGE
            general_config['user_create_account'] = USER_CREATE_ACCOUNT
            
            database_config['authentication_method'] = AUTHENTICATION_METHOD
            database_config['database_host'] = DATABASE_HOST
            database_config['database_port'] = DATABASE_PORT
            database_config['database_user'] = DATABASE_USER
            database_config['database_password'] = DATABASE_PASS
            database_config['database_course_user'] = DATABASE_COURSE_USER
            database_config['database_course_password'] = DATABASE_COURSE_PASSWORD
            
            authentication_config['authentication_method'] = AUTHENTICATION_METHOD
            authentication_config['ldap_options'] = LDAP_OPTIONS
            authentication_config['saml_options'] = SAML_OPTIONS

            submitty_config['sys_admin_email'] = SYS_ADMIN_EMAIL
            submitty_config['sys_admin_url'] = SYS_ADMIN_URL
            submitty_config['submission_url'] = SUBMISSION_URL
            submitty_config['vcs_url'] = VCS_URL
            submitty_config['cgi_url'] = CGI_URL
            submitty_config['institution_name'] = INSTITUTION_NAME
            submitty_config['institution_homepage'] = INSTITUTION_HOMEPAGE
            submitty_config['timezone'] = TIMEZONE
            submitty_config['default_locale'] = DEFAULT_LOCALE

            submitty_config['course_material_file_upload_limit_mb'] = COURSE_MATERIAL_UPLOAD_LIMIT_MB
            submitty_config['user_create_account'] = USER_CREATE_ACCOUNT
            submitty_config['user_id_requirements'] = defaults['user_id_requirements']
                
            email_config['email_enabled'] = EMAIL_ENABLED
            email_config['email_user'] = EMAIL_USER
            email_config['email_password'] = EMAIL_PASSWORD
            email_config['email_sender'] = EMAIL_SENDER
            email_config['email_reply_to'] = EMAIL_REPLY_TO
            email_config['email_server_hostname'] = EMAIL_SERVER_HOSTNAME
            email_config['email_server_port'] = EMAIL_SERVER_PORT
            email_config['email_internal_domain'] = EMAIL_INTERNAL_DOMAIN

            full_config['database'] = database_config
            full_config['authentication'] = authentication_config
            full_config['submitty'] = submitty_config
            full_config['general'] = general_config
            full_config['email'] = email_config
            full_config['admin_username'] = SUBMITTY_ADMIN_USERNAME
    return full_config