import os
import ConfigParser

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# Read config
cfg = ConfigParser.ConfigParser()
cfg.read(os.path.join(SITE_ROOT, "config.properties"))
dbEngine = cfg.get("webconfig", "engine")
dbName = cfg.get("webconfig", "name")
dbUser = cfg.get("webconfig", "user")
dbPass = cfg.get("webconfig", "password")
dbHost = cfg.get("webconfig", "host")
dbPort = cfg.get("webconfig", "port")
cfgDebug = cfg.get("webconfig", "debug")
cfgDevserver = cfg.getboolean("webconfig", "django-devserver")
cfgSubsPeriod = cfg.getboolean("webconfig", "subs_period")
cfgAdminName = cfg.get("webconfig", "admin_name")
cfgAdminEmail = cfg.get("webconfig", "admin_email")
cfgTablePrefix = cfg.get("webconfig", "tableprefix")
cfgSuGids = [int(cgid) for cgid in cfg.get("webconfig", "superuser_groupids").split(",")]
cfgStaffGids = [int(cgid) for cgid in cfg.get("webconfig", "staff_groupids").split(",")]
cfgStandardGids = [int(cgid) for cgid in cfg.get("webconfig", "standard_groupids").split(",")]
cfgPaidGid = cfg.getint("webconfig", "paid_groupid")
cfgNotPaidGid = cfg.getint("webconfig", "not_paid_groupid")
cfgSubsZeroGid = cfg.getint("webconfig", "subscription_0")
cfgBannedGid = cfg.getint("webconfig", "banned_groupid")
cfgEBPaymasterId = cfg.getint("webconfig", "ebanking_paymaster_id")

DEBUG = cfgDebug.lower() == "true"
TEMPLATE_DEBUG = DEBUG

ADMINS = (
  (cfgAdminName, cfgAdminEmail),
)

MANAGERS = ADMINS

DATABASES = {
  'default': {
    'ENGINE': dbEngine, # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    'NAME': dbName,                      # Or path to database file if using sqlite3.
    'USER': dbUser,                      # Not used with sqlite3.
    'PASSWORD': dbPass,                  # Not used with sqlite3.
    'HOST': dbHost,                      # Set to empty string for localhost. Not used with sqlite3.
    'PORT': dbPort,                      # Set to empty string for default. Not used with sqlite3.
  }
}

LOGIN_URL = "login"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zagreb'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'hr-HR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#  'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'v)n4nsav))a!g+t^z)gmoin11*lc6yt8)(l%pp*n4*7sh1u8vy'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
#   'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
)

AUTHENTICATION_BACKENDS = ('subsf2net.subscriptions.auth.backends.VBulletinBackend', )

AUTH_PROFILE_MODULE = 'subscriptions.UserProfile'

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
  os.path.join(SITE_ROOT, 'templates' )
)

INSTALLED_APPS = (
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'django.contrib.admin',
  'subsf2net.subscriptions',
)

if cfgDevserver:
  INSTALLED_APPS += ('devserver',)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'verbose': {
      'format': '%(levelname)s %(asctime)s %(module)s - %(message)s'
      },
    'simple': {
      'format': '%(levelname)s %(message)s'
      },
  },
  'handlers': {
    'mail_admins': {
      'level': 'ERROR',
      'class': 'django.utils.log.AdminEmailHandler'
    },
    'file':{
      'level': 'INFO',
      'class': 'logging.handlers.RotatingFileHandler',
      'filename': 'info.log',
      'formatter': 'verbose',
      'maxBytes': 10485760,
      'backupCount': 10,
    },
    'console':{
      'level':'DEBUG',
      'class':'logging.StreamHandler',
      'formatter': 'simple'
    },
  },
  'loggers': {
    'django.request': {
      'handlers': ['mail_admins'],
      'level': 'ERROR',
      'propagate': True,
    },
    'subscriptions': {
      'handlers': ['mail_admins'],
      'level': 'INFO',
    },
  }
}

