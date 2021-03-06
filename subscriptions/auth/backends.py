import logging
import md5

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from subsf2net.subscriptions.auth import VBULLETIN_CONFIG

logger = logging.getLogger('subscriptions')

class VBulletinBackend(ModelBackend):
    """
    We override ModelBackend to make use of django.contrib.auth permissions
    """

    def authenticate(self, username=None, password=None):
        logger.debug('Using VBulletinBackend')
        email = username
        
        from django.db import connection
        cursor = connection.cursor()

        sql = """SELECT userid, username, password, salt, usergroupid, membergroupids, email
                 FROM """ + VBULLETIN_CONFIG['tableprefix'] + """user WHERE email = %s"""
        cursor.execute(sql, [email])
        allRows = cursor.fetchall()
        if len(allRows) == 0: return None
        else: row = allRows[0]

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
                if int(row[4]) in VBULLETIN_CONFIG['superuser_groupids']:
                    user.is_staff = True    
                    user.is_superuser = True
                elif int(row[4]) in VBULLETIN_CONFIG['staff_groupids']:
                    user.is_staff = True
                
                # Process additional usergroups
                for groupid in row[5].split(','):
                    if groupid == '': continue
                    if int(groupid) in VBULLETIN_CONFIG['superuser_groupids']:
                        user.is_superuser = True
                    if int(groupid) in VBULLETIN_CONFIG['staff_groupids']:
                        user.is_staff = True
                
                user.set_unusable_password()
                user.save()

            logger.debug("User with id " + str(user.id) + " logged in.")
            return user
            
        return None

