# customadmin/admin.py
from django.contrib.admin import AdminSite
from ecommerce.settings import JAZZMIN_SETTINGS

class customDashboard(AdminSite):
    site_header = JAZZMIN_SETTINGS['site_header']
    site_title = JAZZMIN_SETTINGS['site_title']

custom_admin_site = customDashboard(name='customadmin')

