import logging
logging.warning('Inside auth.__init__')

import settings

VBULLETIN_CONFIG = {
    'tableprefix': settings.cfgTablePrefix,
    'superuser_groupids': settings.cfgSuGids,
    'staff_groupids': settings.cfgStaffGids,
}

#if hasattr(settings, 'VBULLETIN_CONFIG'):
#    VBULLETIN_CONFIG.update(settings.VBULLETIN_CONFIG)
