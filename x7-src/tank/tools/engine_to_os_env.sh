# This file is intended to be sourced to convert old-style ENGINE environment
# variables to new-style OS.
#
# The plan is to add this to enginerc, but until that lands, it's useful to have
# this in Tank.
export OS_AUTH_USER=$ENGINE_USERNAME
export OS_AUTH_KEY=$ENGINE_API_KEY
export OS_AUTH_TENANT=$ENGINE_PROJECT_ID
export OS_AUTH_URL=$ENGINE_URL
export OS_AUTH_STRATEGY=$ENGINE_AUTH_STRATEGY
