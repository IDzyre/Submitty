#!/usr/bin/env python3

import argparse
from collections import OrderedDict
import json
import os
import secrets
import shutil
import string
import tzlocal

from GENERATE_CONFIGS import generate_config

class StrToBoolAction(argparse.Action):
    """
    Custom action that parses strings to boolean values. All values that come
    from bash are strings, and so need to parse that into the appropriate
    bool value.
    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values != '0' and values.lower() != 'false')


##############################################################################
# this script must be run by root or sudo
if os.getuid() != 0:
    raise SystemExit('ERROR: This script must be run by root or sudo')

authentication_methods = [
    'PamAuthentication',
    'DatabaseAuthentication',
    'LdapAuthentication',
    'SamlAuthentication'
]

defaults = {
    'database_host': 'localhost',
    'database_port': 5432,
    'database_user': 'submitty_dbuser',
    'database_course_user': 'submitty_course_dbuser',
    'submission_url': '',
    'supervisor_user': 'submitty',
    'vcs_url': '',
    'authentication_method': 0,
    'institution_name' : '',
    'institution_homepage' : '',
    'user_create_account' : False,
    'timezone' : str(tzlocal.get_localzone()),
    'submitty_admin_username': '',
    'email_user': '',
    'email_password': '',
    'email_sender': 'submitty@myuniversity.edu',
    'email_reply_to': 'submitty_do_not_reply@myuniversity.edu',
    'email_server_hostname': 'mail.myuniversity.edu',
    'email_server_port': 25,
    'email_internal_domain': 'example.com',
    'course_code_requirements': "Please follow your school's convention for course code.",
    'sys_admin_email': '',
    'sys_admin_url': '',
    'ldap_options': {
        'url': '',
        'uid': '',
        'bind_dn': ''
    },
    'saml_options': {
        'name': '',
        'username_attribute': ''
    },
    'course_material_file_upload_limit_mb': 100,
    'user_id_requirements': {
        'any_user_id': True,
        'require_name': False,
        'min_length': 6,
        'max_length': 25,
        # Example for Alyssa Hacker : hackal -- Allows for shorter names. If they are shorter, then it will just take the entire name. 
        # Example for Joseph Wo : wojo
        'name_requirements': {
            'given_first': False,
            'given_name': 2,
            'family_name': 4
        },
        'require_email': False,
        # If the user_id must contain part of the email. If whole_email is true, it must match the email.
        # If whole_prefix is true, then the user_id must equal everything before the final @ sign.
        # Else, it must be a certain number of characters of the prefix. 
        # Examples for myemail@email.com:
        # Whole email: myemail@gmail.com
        # Whole prefix: myemail
        # Part of prefix: myemai
        'email_requirements': {
            'whole_email': False,
            'whole_prefix': False,
            'prefix_count': 6
        },
        'accepted_emails': [
            'gmail.com'
        ]
    }
}

parser = argparse.ArgumentParser(description='Submitty configuration script',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--debug', action='store_true', default=False, help='Configure Submitty to be in debug mode. '
                                                                        'This should not be used in production!')
parser.add_argument('--setup-for-sample-courses', action='store_true', default=False,
                    help="Sets up Submitty for use with the sample courses. This is a Vagrant convenience "
                         "flag and should not be used in production!")
parser.add_argument('--worker', action='store_true', default=False, help='Configure Submitty with autograding only')
parser.add_argument('--install-dir', default='/usr/local/submitty', help='Set the install directory for Submitty')
parser.add_argument('--data-dir', default='/var/local/submitty', help='Set the data directory for Submitty')
parser.add_argument('--websocket-port', default=8443, type=int, help='Port to use for websocket')

args = parser.parse_args()

# determine location of SUBMITTY GIT repository
# this script (CONFIGURES_SUBMITTY.py) is in the top level directory of the repository
# (this command works even if we run configure from a different directory)
SETUP_SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
SUBMITTY_REPOSITORY = os.path.dirname(SETUP_SCRIPT_DIRECTORY)

# recommended (default) directory locations
# FIXME: Check that directories exist and are readable/writeable?
SUBMITTY_INSTALL_DIR = args.install_dir
if not os.path.isdir(SUBMITTY_INSTALL_DIR) or not os.access(SUBMITTY_INSTALL_DIR, os.R_OK | os.W_OK):
    raise SystemExit('Install directory {} does not exist or is not accessible'.format(SUBMITTY_INSTALL_DIR))

SUBMITTY_DATA_DIR = args.data_dir
if not os.path.isdir(SUBMITTY_DATA_DIR) or not os.access(SUBMITTY_DATA_DIR, os.R_OK | os.W_OK):
    raise SystemExit('Data directory {} does not exist or is not accessible'.format(SUBMITTY_DATA_DIR))

TAGRADING_LOG_PATH = os.path.join(SUBMITTY_DATA_DIR, 'logs')
AUTOGRADING_LOG_PATH = os.path.join(SUBMITTY_DATA_DIR, 'logs', 'autograding')

WEBSOCKET_PORT = args.websocket_port

##############################################################################

# recommended names for special users & groups related to the SUBMITTY system
PHP_USER = 'submitty_php'
PHP_GROUP = 'submitty_php'
CGI_USER = 'submitty_cgi'
DAEMON_USER = 'submitty_daemon'
DAEMON_GROUP = 'submitty_daemon'
COURSE_BUILDERS_GROUP = 'submitty_course_builders'

##############################################################################

# adjust this number depending on the # of processors
# available on your hardware
NUM_GRADING_SCHEDULER_WORKERS = 5

##############################################################################

SETUP_INSTALL_DIR = os.path.join(SUBMITTY_INSTALL_DIR, '.setup')
SETUP_REPOSITORY_DIR = os.path.join(SUBMITTY_REPOSITORY, '.setup')

INSTALL_FILE = os.path.join(SETUP_INSTALL_DIR, 'INSTALL_SUBMITTY.sh')
CONFIGURATION_JSON = os.path.join(SETUP_INSTALL_DIR, 'submitty_conf.json')
SITE_CONFIG_DIR = os.path.join(SUBMITTY_INSTALL_DIR, "site", "config")
CONFIG_INSTALL_DIR = os.path.join(SUBMITTY_INSTALL_DIR, 'config')
SUBMITTY_USERS_JSON = os.path.join(CONFIG_INSTALL_DIR, 'submitty_users.json')
SUBMITTY_ADMIN_JSON = os.path.join(CONFIG_INSTALL_DIR, 'submitty_admin.json')
EMAIL_JSON = os.path.join(CONFIG_INSTALL_DIR, 'email.json')
AUTHENTICATION_JSON = os.path.join(CONFIG_INSTALL_DIR, 'authentication.json')

##############################################################################

if os.path.isdir(CONFIG_INSTALL_DIR):
    for file in os.scandir(CONFIG_INSTALL_DIR):
        if file.name not in IGNORED_FILES_AND_DIRS:
            if file.is_file():
                os.remove(os.path.join(CONFIG_INSTALL_DIR, file.name))
            else:
                os.rmdir(os.path.join(CONFIG_INSTALL_DIR, file.name))
elif os.path.exists(CONFIG_INSTALL_DIR):
    os.remove(CONFIG_INSTALL_DIR)
os.makedirs(CONFIG_INSTALL_DIR, exist_ok=True)
os.chmod(CONFIG_INSTALL_DIR, 0o755)

loaded_defaults = {}
if os.path.isfile(CONFIGURATION_JSON):
    with open(CONFIGURATION_JSON) as conf_file:
        loaded_defaults = json.load(conf_file)
if os.path.isfile(SUBMITTY_ADMIN_JSON):
    with open(SUBMITTY_ADMIN_JSON) as submitty_admin_file:
        loaded_defaults.update(json.load(submitty_admin_file))
if os.path.isfile(EMAIL_JSON):
    with open(EMAIL_JSON) as email_file:
        loaded_defaults.update(json.load(email_file))

if os.path.isfile(AUTHENTICATION_JSON):
    with open(AUTHENTICATION_JSON) as authentication_file:
        loaded_defaults.update(json.load(authentication_file))

# no need to authenticate on a worker machine (no website)
if not args.worker:
    if 'authentication_method' in loaded_defaults:
        loaded_defaults['authentication_method'] = authentication_methods.index(loaded_defaults['authentication_method']) + 1

# grab anything not loaded in (useful for backwards compatibility if a new default is added that
# is not in an existing config file.)
for key in defaults.keys():
    if key not in loaded_defaults:
        loaded_defaults[key] = defaults[key]
defaults = loaded_defaults

print("\nWelcome to the Submitty Homework Submission Server Configuration\n")
DEBUGGING_ENABLED = args.debug is True

if DEBUGGING_ENABLED:
    print('!! DEBUG MODE ENABLED !!')
    print()

if args.worker:
    print("CONFIGURING SUBMITTY AS A WORKER !!")

full_config = generate_config(defaults, args.worker, authentication_methods)

##############################################################################
# make the installation setup directory

if os.path.isdir(SETUP_INSTALL_DIR):
    shutil.rmtree(SETUP_INSTALL_DIR)
os.makedirs(SETUP_INSTALL_DIR, exist_ok=True)
os.chmod(SETUP_INSTALL_DIR, 0o751)

##############################################################################
# WRITE CONFIG FILES IN ${SUBMITTY_INSTALL_DIR}/.setup
config = full_config['general']

if args.worker: 
    config['supervisor_user'] = config['supervisor_user']
    with open(SUBMITTY_USERS_JSON, 'w') as json_file:
        json.dump(config, json_file, indent=2)

config['submitty_install_dir'] = SUBMITTY_INSTALL_DIR
config['submitty_repository'] = SUBMITTY_REPOSITORY
config['submitty_data_dir'] = SUBMITTY_DATA_DIR
config['course_builders_group'] = COURSE_BUILDERS_GROUP
config['num_grading_scheduler_workers'] = NUM_GRADING_SCHEDULER_WORKERS
config['daemon_user'] = DAEMON_USER

if not args.worker:
    config['php_user'] = PHP_USER
    config['cgi_user'] = CGI_USER
    
    config['websocket_port'] = WEBSOCKET_PORT
    config['debugging_enabled'] = DEBUGGING_ENABLED

# site_log_path is a holdover name. This could more accurately be called the "log_path"
config['site_log_path'] = TAGRADING_LOG_PATH
config['autograding_log_path'] = AUTOGRADING_LOG_PATH

if args.worker:
    config['worker'] = 1
else:
    config['worker'] = 0


with open(INSTALL_FILE, 'w') as open_file:
    def write(x=''):
        print(x, file=open_file)
    write('#!/bin/bash')
    write()
    write(f'bash {SETUP_REPOSITORY_DIR}/INSTALL_SUBMITTY_HELPER.sh  "$@"')

os.chmod(INSTALL_FILE, 0o700)

with open(CONFIGURATION_JSON, 'w') as json_file:
    json.dump(config, json_file, indent=2)

os.chmod(CONFIGURATION_JSON, 0o500)

##############################################################################
# Setup ${SUBMITTY_INSTALL_DIR}/config

DATABASE_JSON = os.path.join(CONFIG_INSTALL_DIR, 'database.json')
SUBMITTY_JSON = os.path.join(CONFIG_INSTALL_DIR, 'submitty.json')
SUBMITTY_USERS_JSON = os.path.join(CONFIG_INSTALL_DIR, 'submitty_users.json')
WORKERS_JSON = os.path.join(CONFIG_INSTALL_DIR, 'autograding_workers.json')
CONTAINERS_JSON = os.path.join(CONFIG_INSTALL_DIR, 'autograding_containers.json')
SECRETS_PHP_JSON = os.path.join(CONFIG_INSTALL_DIR, 'secrets_submitty_php.json')

# Rescue submitty config data
submitty_config = OrderedDict()
try:
    with open(SUBMITTY_JSON, 'r') as json_file:
        submitty_config = json.load(json_file, object_pairs_hook=OrderedDict)
except FileNotFoundError:
    pass

##############################################################################
# WRITE CONFIG FILES IN ${SUBMITTY_INSTALL_DIR}/config

if not args.worker:
    if not os.path.isfile(WORKERS_JSON):
        capabilities = ["default"]
        if args.setup_for_sample_courses:
            capabilities.extend(["cpp", "python", "et-cetera", "notebook", "unsupported"])

        worker_dict = {
            "primary": {
                "capabilities": capabilities,
                "address": "localhost",
                "username": "",
                "num_autograding_workers": NUM_GRADING_SCHEDULER_WORKERS,
                "enabled" : True
            }
        }

        with open(WORKERS_JSON, 'w') as workers_file:
            json.dump(worker_dict, workers_file, indent=4)

    if not os.path.isfile(CONTAINERS_JSON):
        container_dict = {
            "default":  [
                          "submitty/autograding-default:latest",
                          "submitty/python:latest",
                          "submitty/clang:latest",
                          "submitty/gcc:latest",
                          "submitty/rust:latest",
                          "submitty/java:latest",
                          "submitty/pdflatex:latest",
                          "submitty/jupyter:latest"
                        ],
            "python":   [
                          "submitty/autograding-default:latest",
                          "submitty/python:latest"
                        ],
            "cpp":      [
                          "submitty/autograding-default:latest",
                          "submitty/clang:latest",
                          "submitty/gcc:latest"
                        ],
            "notebook": [
                          "submitty/autograding-default:latest"
                        ]
        }

        with open(CONTAINERS_JSON, 'w') as container_file:
            json.dump(container_dict, container_file, indent=4)

    for file in [WORKERS_JSON, CONTAINERS_JSON]:
      os.chmod(file, 0o660)

##############################################################################
# Write database json

if not args.worker:
    database_config = full_config['database']
    database_config['debugging_enabled'] = DEBUGGING_ENABLED
    with open(DATABASE_JSON, 'w') as json_file:
        json.dump(database_config, json_file, indent=2)
    os.chmod(DATABASE_JSON, 0o440)

##############################################################################
# Write authentication json
if not args.worker:
    auth_config = full_config['authentication']
    with open(AUTHENTICATION_JSON, 'w') as json_file:
        json.dump(auth_config, json_file, indent=4)
    os.chmod(AUTHENTICATION_JSON, 0o440)

##############################################################################

config = submitty_config
generated_submitty_config = full_config['submitty']
config.update(generated_submitty_config)
config['submitty_install_dir'] = SUBMITTY_INSTALL_DIR
config['submitty_repository'] = SUBMITTY_REPOSITORY
config['submitty_data_dir'] = SUBMITTY_DATA_DIR
config['autograding_log_path'] = AUTOGRADING_LOG_PATH
# site_log_path is a holdover name. This could more accurately be called the "log_path"
config['site_log_path'] = TAGRADING_LOG_PATH

if not args.worker:
    config['websocket_port'] = WEBSOCKET_PORT
    config['duck_special_effects'] = False
    
config['worker'] = True if args.worker == 1 else False

with open(SUBMITTY_JSON, 'w') as json_file:
    json.dump(config, json_file, indent=2)
os.chmod(SUBMITTY_JSON, 0o444)

##############################################################################
# Write secrets_submitty_php json

if not args.worker:
    config = OrderedDict()
    characters = string.ascii_letters + string.digits
    config['session'] = ''.join(secrets.choice(characters) for _ in range(64))
    with open(SECRETS_PHP_JSON, 'w') as json_file:
        json.dump(config, json_file, indent=2)
    os.chmod(SECRETS_PHP_JSON, 0o440)

##############################################################################
# Write submitty_admin json

if not args.worker:
    config = OrderedDict()
    config['submitty_admin_username'] = full_config['admin_username']

    with open(SUBMITTY_ADMIN_JSON, 'w') as json_file:
        json.dump(config, json_file, indent=2)
    os.chmod(SUBMITTY_ADMIN_JSON, 0o440)

##############################################################################
# Write email json

if not args.worker:
    config = full_config['email']
    with open(EMAIL_JSON, 'w') as json_file:
        json.dump(config, json_file, indent=2)
    os.chmod(EMAIL_JSON, 0o440)

##############################################################################

print('Configuration completed. Now you may run the installation script')
print(f'    sudo {INSTALL_FILE}')
print('          or')
print(f'    sudo {INSTALL_FILE} clean')
print("\n")