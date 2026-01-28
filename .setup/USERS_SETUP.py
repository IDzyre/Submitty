#!/usr/bin/env python3

import argparse
import grp
import json
import pwd
from collections import OrderedDict
import shutil
import tempfile
import os

def get_uid(user):
    return pwd.getpwnam(user).pw_uid


def get_gid(user):
    return pwd.getpwnam(user).pw_gid


def get_ids(user):
    try:
        return get_uid(user), get_gid(user)
    except KeyError:
        raise SystemExit("ERROR: Could not find user: " + user)

parser = argparse.ArgumentParser(description='Submitty configuration script',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--worker', action='store_true', default=False, help='Configure Submitty with autograding only')
parser.add_argument('--install-dir', default='/usr/local/submitty', help='Set the install directory for Submitty')
args = parser.parse_args()

##########################################################

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

SETUP_INSTALL_DIR = os.path.join(args.install_dir, '.setup')

INSTALL_FILE = os.path.join(SETUP_INSTALL_DIR, 'INSTALL_SUBMITTY.sh')
CONFIGURATION_JSON = os.path.join(SETUP_INSTALL_DIR, 'submitty_conf.json')
CONFIG_INSTALL_DIR = os.path.join(args.install_dir, 'config')

EMAIL_JSON = os.path.join(CONFIG_INSTALL_DIR, 'email.json')
AUTHENTICATION_JSON = os.path.join(CONFIG_INSTALL_DIR, 'authentication.json')
DATABASE_JSON = os.path.join(CONFIG_INSTALL_DIR, 'database.json')
SUBMITTY_JSON = os.path.join(CONFIG_INSTALL_DIR, 'submitty.json')
SUBMITTY_USERS_JSON = os.path.join(CONFIG_INSTALL_DIR, 'submitty_users.json')
WORKERS_JSON = os.path.join(CONFIG_INSTALL_DIR, 'autograding_workers.json')
SUBMITTY_ADMIN_JSON = os.path.join(CONFIG_INSTALL_DIR, 'submitty_admin.json')
CONTAINERS_JSON = os.path.join(CONFIG_INSTALL_DIR, 'autograding_containers.json')
SECRETS_PHP_JSON = os.path.join(CONFIG_INSTALL_DIR, 'secrets_submitty_php.json')

if not args.worker:
    PHP_UID, PHP_GID = get_ids(PHP_USER)
    CGI_UID, CGI_GID = get_ids(CGI_USER)
    # System Groups
    DAEMONPHP_GROUP = 'submitty_daemonphp'
    try:
        grp.getgrnam(DAEMONPHP_GROUP)
    except KeyError:
        raise SystemExit("ERROR: Could not find group: " + DAEMONPHP_GROUP)
    DAEMONCGI_GROUP = 'submitty_daemoncgi'
    try:
        grp.getgrnam(DAEMONCGI_GROUP)
    except KeyError:
        raise SystemExit("ERROR: Could not find group: " + DAEMONCGI_GROUP)
    DAEMONPHPCGI_GROUP = 'submitty_daemonphpcgi'
    try:
        grp.getgrnam(DAEMONPHPCGI_GROUP)
    except KeyError:
        raise SystemExit("ERROR: Could not find group: " + DAEMONPHPCGI_GROUP)

DAEMON_UID, DAEMON_GID = get_ids(DAEMON_USER)


try:
    grp.getgrnam(COURSE_BUILDERS_GROUP)
except KeyError:
    raise SystemExit("ERROR: Could not find group: " + COURSE_BUILDERS_GROUP)

##############################################################################

# This is the upper limit of the number of parallel grading threads on
# this machine
NUM_UNTRUSTED = 60

FIRST_UNTRUSTED_UID, FIRST_UNTRUSTED_GID = get_ids('untrusted00')

# confirm that the uid/gid of the untrusted users are sequential
for i in range(1, NUM_UNTRUSTED):
    untrusted_user = "untrusted{:0=2d}".format(i)
    uid, gid = get_ids(untrusted_user)
    if uid != FIRST_UNTRUSTED_UID + i:
        raise SystemExit('CONFIGURATION ERROR: untrusted UID not sequential: ' + untrusted_user)
    elif gid != FIRST_UNTRUSTED_GID + i:
        raise SystemExit('CONFIGURATION ERROR: untrusted GID not sequential: ' + untrusted_user)

with open(SUBMITTY_JSON, 'r') as json_file:
    config = json.load(json_file, object_pairs_hook=OrderedDict)
    config['num_untrusted'] = NUM_UNTRUSTED
    config['first_untrusted_uid'] = FIRST_UNTRUSTED_UID
    config['first_untrusted_gid'] = FIRST_UNTRUSTED_UID

    config['daemon_uid'] = DAEMON_UID
    config['daemon_gid'] = DAEMON_GID

    # not worker
    config['daemonphp_group'] = DAEMONPHP_GROUP
    config['daemoncgi_group'] = DAEMONCGI_GROUP
    config['daemonphpcgi_group'] = DAEMONPHPCGI_GROUP
    config['php_uid'] = PHP_UID
    config['php_gid'] = PHP_GID

#Rescue the autograding_workers and _containers files if they exist.
rescued = list()
tmp_folder = tempfile.mkdtemp()
if not args.worker:
    for full_file_name, file_name in [(WORKERS_JSON, 'autograding_workers.json'), (CONTAINERS_JSON, 'autograding_containers.json')]:
        if os.path.isfile(full_file_name):
            #make a tmp folder and copy autograding workers to it
            tmp_file = os.path.join(tmp_folder, file_name)
            shutil.move(full_file_name, tmp_file)
            rescued.append((full_file_name, tmp_file))

IGNORED_FILES_AND_DIRS = ['saml', 'login.md']

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
shutil.chown(CONFIG_INSTALL_DIR, 'root', COURSE_BUILDERS_GROUP)
os.chmod(CONFIG_INSTALL_DIR, 0o755)

# Finish rescuing files.
for full_file_name, tmp_file_name in rescued:
    #copy autograding workers back
    shutil.move(tmp_file_name, full_file_name)
    #make sure the permissions are correct.
    shutil.chown(full_file_name, 'root', DAEMON_GID)
    os.chmod(full_file_name, 0o660)

#remove the tmp folder
os.removedirs(tmp_folder)

##############################################################################
# Write users json

config = OrderedDict()
config['num_grading_scheduler_workers'] = NUM_GRADING_SCHEDULER_WORKERS
config['num_untrusted'] = NUM_UNTRUSTED
config['first_untrusted_uid'] = FIRST_UNTRUSTED_UID
config['first_untrusted_gid'] = FIRST_UNTRUSTED_UID
config['daemon_uid'] = DAEMON_UID
config['daemon_gid'] = DAEMON_GID
config['daemon_user'] = DAEMON_USER
config['course_builders_group'] = COURSE_BUILDERS_GROUP

if not args.worker:
    config['php_uid'] = PHP_UID
    config['php_gid'] = PHP_GID
    config['php_user'] = PHP_USER
    config['cgi_user'] = CGI_USER
    config['daemonphp_group'] = DAEMONPHP_GROUP
    config['daemoncgi_group'] = DAEMONCGI_GROUP
    config['daemonphpcgi_group'] = DAEMONPHPCGI_GROUP
if os.path.exists(SUBMITTY_USERS_JSON):
    with open(SUBMITTY_USERS_JSON, 'r') as json_file:
        config_file = json.load(json_file)
        config['supervisor_user'] = config_file['supervisor_user']
with open(SUBMITTY_USERS_JSON, 'w') as json_file:
    json.dump(config, json_file, indent=2)
shutil.chown(SUBMITTY_USERS_JSON, 'root', DAEMON_GROUP if args.worker else DAEMONPHP_GROUP)

os.chmod(SUBMITTY_USERS_JSON, 0o440)
shutil.chown(WORKERS_JSON, PHP_USER, DAEMON_GID)
shutil.chown(CONTAINERS_JSON, group=DAEMONPHP_GROUP)
shutil.chown(DATABASE_JSON, 'root', DAEMONPHP_GROUP)
shutil.chown(AUTHENTICATION_JSON, 'root', DAEMONPHP_GROUP)
shutil.chown(EMAIL_JSON, 'root', DAEMONPHP_GROUP)
shutil.chown(SECRETS_PHP_JSON, 'root', PHP_GROUP)
shutil.chown(SUBMITTY_ADMIN_JSON, 'root', DAEMON_GROUP)
shutil.chown(SETUP_INSTALL_DIR, 'root', COURSE_BUILDERS_GROUP)
shutil.chown(CONFIG_INSTALL_DIR, 'root', COURSE_BUILDERS_GROUP)