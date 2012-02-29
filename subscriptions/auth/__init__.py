from subsf2net import settings

VBULLETIN_CONFIG = {
    'tableprefix': settings.cfgTablePrefix,
    'superuser_groupids': settings.cfgSuGids,
    'staff_groupids': settings.cfgStaffGids,
    'standard_groupids': settings.cfgStandardGids,
    'paid_groupid': settings.cfgPaidGid,
    'not_paid_groupid': settings.cfgNotPaidGid,
    'banned_groupid': settings.cfgBannedGid
}

if hasattr(settings, 'VBULLETIN_CONFIG'):
    VBULLETIN_CONFIG.update(settings.VBULLETIN_CONFIG)
