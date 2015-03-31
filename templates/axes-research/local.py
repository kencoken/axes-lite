#
# Django site administrator and managers
#
ADMINS = (
   ('{admin_name}', '{admin_email}'),
)
MANAGERS = ADMINS

#
# Debugging settings
#
DEBUG = {debug}
TEMPLATE_DEBUG = {debug}

#
# Absolute path of where to store media files (uploaded images, etc.). This 
# should be below your web root so that the web server can be used to host
# these files
#
MEDIA_ROOT = '{axes_research_path}/www/media/'

#
# Base URL for media files (uploaded images, etc.). This URL should correspond
# to the URL for MEDIA_ROOT. 
#
MEDIA_URL = '{mount_point}/media/'

#
# Absolute path of where to store static files (css, javascript, etc.). This 
# should be below your web root so that the web server can be used to host
# these files
#
STATIC_ROOT = '{axes_research_path}/www/static/'

#
# Base URL for static. This URL should correspond to the URL for STATIC_ROOT. 
#
STATIC_URL = '{mount_point}/static/'

#
# Where to store the admin interface static files and media.
#
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

#
# URL of the LIMAS JSON RPC interface to connect to
#
SERVICE_URL = '{service_url}'

#
# Mongo DB database name
#
DATABASE_NAME = '{database_name}'

#
# Time zone of the server
#
TIME_ZONE = '{time_zone}'

#
# Collection name
#
DEFAULT_COLLECTION = '{collection_name}'

#
# Is an access code required for registration
#
REGISTRATION_CODE_REQUIRED = {registration_code_required}

#
# The axes code for registration
#
REGISTRATION_ACCESS_CODE = '{registration_code}'

#
# Randomly generated django secret key
#
SECRET_KEY = '{secret_key}'

#
# Post processing rules for LIMAS responses. A dictionary mapping
# response keys to a list of regular expression replacement rules to the
# corresponding values. For example:
#
# LIMAS_RESPONSE_POSTPROCESSING_RULES = {{
#     'thumbnailUrl': [
#         (r'^(.*)$', r'http://<server>/thumbs/thumbnail?image=\1')
#     ]
# }}
#
LIMAS_RESPONSE_POSTPROCESSING_RULES = {{ }}

