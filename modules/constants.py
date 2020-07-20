""" defines constants"""

class AWS_CONSTANTS:

    SUPER_ACCOUNT = "" # administrative account ID
    ROLE_SUPER_ADMIN = "" # omni-present super admin role

    ROLE_ACCOUNT_ADMIN = "" # customer account admin role
    ROLE_ACCOUNT_USER = "" # customer user account role

    STS_MINIMUM_LIFETIME = 900 # seconds
    STS_MAXIMUM_LIFETIME = 12*3600 # seconds
