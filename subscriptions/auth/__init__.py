import settings

VBULLETIN_CONFIG = {
    'tableprefix': settings.cfgTablePrefix,
    'superuser_groupids': settings.cfgSuGids,
    'staff_groupids': settings.cfgStaffGids,
    'standard_groupids': settings.cfgStandardGids,
    'paid_03_2013_groupid': settings.cfgPaid032013Gid,
    'not_paid_groupid': settings.cfgNotPaidGid
}

if hasattr(settings, 'VBULLETIN_CONFIG'):
    VBULLETIN_CONFIG.update(settings.VBULLETIN_CONFIG)
