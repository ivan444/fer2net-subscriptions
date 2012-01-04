import logging
import md5

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from subscriptions.auth import VBULLETIN_CONFIG

class VBulletinBackend(ModelBackend):
    """
    We override ModelBackend to make use of django.contrib.auth permissions
    """
    
    def authenticate(self, username=None, password=None):
        logging.debug('Using VBulletinBackend')
        email = username
        
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute("""SELECT userid, username, password, salt, usergroupid, membergroupids, email
                          FROM %suser WHERE email = '%s'"""
                       % (VBULLETIN_CONFIG['tableprefix'], email))
        row = cursor.fetchone()
        
        hashed = md5.new(md5.new(password).hexdigest() + row[3]).hexdigest()
        
        id = int(row[0])
        if row[2] == hashed:
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                user = User(id=id, username=row[1], email=email)

                user.is_staff = False
                user.is_superuser = False

                # Process primary usergroup
                if row[4] in VBULLETIN_CONFIG['superuser_groupids']:
                    user.is_staff = True    
                    user.is_superuser = True
                elif row[4] in VBULLETIN_CONFIG['staff_groupids']:
                    user.is_staff = True
                
                # Process addtional usergroups
                for groupid in row[5].split(','):
                    if groupid in VBULLETIN_CONFIG['superuser_groupids']:
                        user.is_superuser = True
                    if groupid in VBULLETIN_CONFIG['staff_groupids']:
                        user.is_staff = True
                
                user.set_unusable_password()
                user.save()
            return user
            
        return None

