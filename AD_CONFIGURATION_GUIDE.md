# Active Directory (AD) Sync Configuration Guide

## Overview

The AD Configuration feature allows administrators to configure and manage Windows Active Directory (AD) or LDAP synchronization directly through the admin panel. This enables automatic user provisioning, updating, and deprovisioning based on your organization's AD directory.

## Features

- **Flexible Configuration**: Set up LDAP/AD connection parameters through the UI
- **Attribute Mapping**: Map AD attributes to system user fields
- **Connection Testing**: Test LDAP connectivity before enabling sync
- **Manual Sync**: Trigger immediate synchronization on demand
- **Auto-sync Options**: Configure automatic user creation, update, and disabling
- **Status Tracking**: Monitor sync status and error messages
- **Organization Isolation**: Each organization has its own AD configuration

## Accessing AD Configuration

1. Navigate to **Admin Panel** → **Settings**
2. Select the **Active Directory** tab
3. Click **Edit Configuration** to modify settings

## Configuration Fields

### Server Connection

**AD Server Name/IP** (Required)
- The hostname or IP address of your AD server
- Examples: `ad.company.local`, `192.168.1.10`, `ldap.example.com`

**Port** (Required)
- Port number for LDAP connection
- Default: `389` (standard LDAP)
- Use `636` for LDAP over SSL/TLS

**Use SSL/TLS**
- Toggle to enable SSL/TLS encryption
- Recommended for production environments
- Port 636 typically used with SSL

### Service Account Authentication

**Bind Username** (Required)
- Distinguished Name (DN) of the service account
- Format: `CN=username,DC=company,DC=com`
- Example: `CN=svc_admin,OU=Service Accounts,DC=company,DC=com`
- This account must have permissions to query AD users

**Bind Password** (Required)
- Password for the service account
- Only needs to be entered when creating or updating configuration
- Stored securely and not exposed in API responses

### User Search Configuration

**Search Base DN** (Required)
- Base distinction name where users are located
- Format: `OU=OrgUnit,DC=company,DC=com`
- Example: `OU=Users,DC=company,DC=com`
- The sync will search within this OU and its sub-OUs

**Search Filter** (Optional)
- LDAP filter to identify user objects
- Default: `(objectClass=user)`
- Example: `(&(objectClass=user)(!(userAccountControl=514)))` (excludes disabled accounts)

### AD Attribute Mapping

Maps Active Directory attributes to system user fields. Allows customization for different AD environments:

| Field | Default AD Attribute | Description |
|-------|----------------------|-------------|
| **Username** | `sAMAccountName` | User login name (must be unique) |
| **Email** | `mail` | Email address |
| **First Name** | `givenName` | First/given name |
| **Last Name** | `sn` | Surname/family name |
| **Phone** | `telephoneNumber` | Phone number |

**Common AD Attributes:**
- `sAMAccountName`: Pre-Windows 2000 login (e.g., john.doe)
- `userPrincipalName`: User principal name (e.g., john.doe@company.com)
- `mail`: Email address
- `givenName`: First name
- `sn`: Last name/surname
- `telephoneNumber`: Phone number
- `displayName`: Display name
- `department`: Department
- `title`: Job title

### Group Configuration (Optional)

**Group Base DN**
- Base DN for group search (if using group-based sync)
- Format: `OU=Groups,DC=company,DC=com`

**Group Member Attribute**
- LDAP attribute containing group members
- Default: `member`
- Alternative: `memberOf` (for reverse group membership)

### Sync Settings

**Auto Create Users**
- Automatically create new user accounts for AD users not in the system
- Recommended: Enabled ✓

**Auto Update Users**
- Automatically update user information (name, email, phone) from AD
- Recommended: Enabled ✓

**Auto Disable Missing Users**
- Automatically disable user accounts that no longer exist in AD
- Use with caution - verify sync filters first
- Recommended: Enabled (after verification) ✓

**Enable AD Sync**
- Master toggle to enable/disable all AD synchronization
- Disable if troubleshooting or temporarily pausing sync

## Testing and Sync

### Test Connection

Before enabling sync, test your LDAP connection:

1. Fill in all **Server Connection** and **Service Account** fields
2. Click **Test Connection** button
3. Wait for confirmation message
4. Connection test will verify:
   - Network connectivity to AD server
   - Authentication with service account
   - Basic LDAP protocol support

**Common Connection Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Server unreachable or wrong port | Verify server IP/hostname and port (389/636) |
| `Invalid credentials` | Wrong username or password | Check service account credentials |
| `TLS handshake failed` | SSL/TLS configuration issue | Verify SSL certificate or disable SSL if testing |
| `LDAP_UNAVAILABLE` | LDAP protocol not supported | Ensure server is AD/LDAP compatible |

### Manual Sync

Trigger an immediate synchronization:

1. Ensure all fields are filled correctly
2. Click **Sync Now** button
3. Review **Last Sync** information
4. Check **Sync Status** and **Error** messages if needed

**Sync Status Values:**
- `pending`: Not yet synchronized
- `running`: Sync in progress
- `success`: Last sync completed successfully
- `failed`: Last sync encountered errors (see error message)

## Configuration Examples

### Standard Active Directory (on-premises)

```
Server Name:           ad.company.local
Port:                  389
Use SSL/TLS:           No
Bind Username:         CN=svc_ldap,OU=Service Accounts,DC=company,DC=com
Bind Password:         ••••••••••
Search Base DN:        OU=Users,DC=company,DC=com
Search Filter:         (objectClass=user)
Username Attribute:    sAMAccountName
Email Attribute:       mail
First Name Attribute:  givenName
Last Name Attribute:   sn
Phone Attribute:       telephoneNumber
Auto Create Users:     ✓
Auto Update Users:     ✓
Auto Disable Missing:  ✓
Enable AD Sync:        ✓
```

### Azure AD (with specific filters)

```
Server Name:           ldap.company.onmicrosoft.com
Port:                  636
Use SSL/TLS:           ✓
Bind Username:         CN=ldap_admin,OU=Admins,DC=company,DC=com
Bind Password:         ••••••••••
Search Base DN:        OU=Users,DC=company,DC=com
Search Filter:         (&(objectClass=user)(enabled=TRUE))
Username Attribute:    userPrincipalName
Email Attribute:       mail
First Name Attribute:  givenName
Last Name Attribute:   sn
Phone Attribute:       telephoneNumber
Auto Create Users:     ✓
Auto Update Users:     ✓
Auto Disable Missing:  ✓
Enable AD Sync:        ✓
```

### Multiple Sites/Forests

```
Server Name:           192.168.1.10 (or site-specific server)
Port:                  389
Use SSL/TLS:           No
Bind Username:         FOREST\svc_account
Bind Password:         ••••••••••
Search Base DN:        OU=Branch,OU=Company,DC=forest,DC=local
Search Filter:         (&(objectClass=user)(!(description=Contractor)))
Username Attribute:    sAMAccountName
Email Attribute:       mail
First Name Attribute:  givenName
Last Name Attribute:   sn
Phone Attribute:       telephoneNumber
```

## Best Practices

### Security

1. **Use a dedicated service account** for AD sync, not a personal admin account
2. **Enable SSL/TLS** for all production environments
3. **Use a strong password** for the bind account
4. **Restrict service account permissions** to read-only on user objects
5. **Monitor sync logs** for unauthorized access attempts
6. **Change password regularly** for the service account

### Performance

1. **Use specific Search Base DN** to narrow the search scope
2. **Implement search filters** to exclude unnecessary objects
3. **Schedule syncs during off-hours** if using auto-sync
4. **Start with Auto Create disabled** until you verify the filter works correctly
5. **Test search filters** before enabling auto-disable

### Quality Control

1. **Test connection first** before running actual sync
2. **Review expected matches** in Test Connection logs
3. **Run manual sync in review mode** first time
4. **Monitor sync status** for the first few sync cycles
5. **Maintain a backup list** of admins in case sync causes issues

## Troubleshooting

### Connection Testing

**Issue**: Test Connection fails

**Steps to resolve:**
1. Verify network connectivity: `ping ad.company.local`
2. Check firewall rules (port 389 or 636)
3. Verify service account credentials
4. Confirm AD server hostname/IP
5. Check SSL/TLS port setting (636 for TLS)

### Sync Issues

**Issue**: Users not syncing

**Check:**
1. Is AD Sync enabled?
2. Is configuration marked as complete?
3. Verify search base DN exists in AD
4. Check search filter syntax (use LDAP control panel to test)
5. Verify service account has permission to read user objects

**Issue**: Wrong users syncing

**Solutions:**
1. Refine the search filter (e.g., exclude contractors, disabled accounts)
2. Change the search base DN to specific OU
3. Test filter: `(&(objectClass=user)(department=Engineering))`

**Issue**: Sync fails with error

**Actions:**
1. Check **Last Sync Error** message
2. Review service account permissions
3. Verify search base DN is correct
4. Check for timeout issues (large AD forests)
5. Contact AD administrator

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/ad-configuration/` | List AD configurations |
| POST | `/api/v1/users/ad-configuration/` | Create AD configuration |
| GET | `/api/v1/users/ad-configuration/{id}/` | Get configuration details |
| PATCH | `/api/v1/users/ad-configuration/{id}/` | Update configuration |
| DELETE | `/api/v1/users/ad-configuration/{id}/` | Delete configuration |
| POST | `/api/v1/users/ad-configuration/{id}/test_connection/` | Test LDAP connection |
| POST | `/api/v1/users/ad-configuration/{id}/sync_now/` | Trigger immediate sync |

## Automatic Sync Scheduling

By default, manual sync via `sync_now` is supported. For scheduled automatic syncing:

1. Configure a Celery Beat schedule in `backend/settings.py`
2. Add task: `sync_users_from_ad` to run at desired intervals
3. Tasks automatically use the enabled ADConfiguration

Example Celery schedule:

```python
# In backend/settings.py
CELERY_BEAT_SCHEDULE = {
    'sync-ad-users-hourly': {
        'task': 'apps.users.tasks.sync_users_from_ad',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

## Support & Documentation

- **LDAP Filter Testing**: Use LDAP Admin, LDP.exe (Windows), or online LDAP filter validators
- **Active Directory PowerShell**: Use `Get-ADUser` to verify users match your filters
- **Python LDAP Library**: python-ldap documentation for advanced LDAP queries
- **AD Attributes Reference**: Microsoft Active Directory Schema documentation

## Permissions

- View AD configuration: `users.view_adconfiguration`
- Edit AD configuration: `users.change_adconfiguration`
- Create AD configuration: `users.add_adconfiguration`
- Delete AD configuration: `users.delete_adconfiguration`
- Sync users: `users.ad.sync` (tested via test_connection and sync_now actions)

---

**Version**: 1.0  
**Last Updated**: February 2025  
**Status**: Production Ready
