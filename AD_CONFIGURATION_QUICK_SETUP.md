# AD Configuration Quick Setup Guide

## 5-Minute Setup

### Step 1: Run Database Migration

```bash
# Navigate to backend directory
cd backend

# Create and run migrations
python manage.py makemigrations users
python manage.py migrate users
```

### Step 2: Add Admin Route (React)

Update your admin routing to include the AD Configuration component.

In `fe/src/pages/AdminLayout.jsx` or your admin routing file:

```javascript
import AdminADConfiguration from './AdminADConfiguration';

const adminPages = [
  // ... existing pages
  {
    key: 'ad-config',
    label: 'Active Directory',
    path: 'ad-config',
    component: AdminADConfiguration
  },
];
```

Or in your navigation menu:

```javascript
<Menu.Item key="ad-config" icon={<DatabaseOutlined />}>
  Active Directory
</Menu.Item>
```

### Step 3: Verify Backend Setup

The following files should already be in place:

- ✓ `backend/apps/users/ad_config.py` - ADConfiguration model
- ✓ `backend/apps/users/ad_config_serializers.py` - ADConfigurationSerializer
- ✓ `backend/apps/users/views.py` - ADConfigurationViewSet (with test_connection and sync_now)
- ✓ `backend/apps/users/urls.py` - Router registration
- ✓ `backend/apps/users/migrations/0003_ad_configuration.py` - Migration file

### Step 4: Install Dependencies (if needed)

```bash
pip install python-ldap  # For LDAP/AD support
```

### Step 5: Test the Configuration

1. Log in to Admin Panel
2. Navigate to **Active Directory** tab
3. Click **Edit Configuration**
4. Fill in your AD/LDAP server details
5. Click **Test Connection** to verify connectivity
6. Save configuration
7. Click **Sync Now** to trigger initial sync

## Common Issues & Solutions

### "Test Connection" returns "python-ldap not installed"

**Solution**: Install the python-ldap package:
```bash
pip install python-ldap
```

On Windows, you may need precompiled wheels:
```bash
pip install python-ldap-3.4.x-cp311-cp311-win_amd64.whl
```

### Sync not starting

**Check**:
1. Is AD Sync **Enabled**? (Toggle switch)
2. Is configuration marked as **Complete**?
3. Verify search base DN is correct

### Users not being created

**Solutions**:
1. Enable **Auto Create Users** option
2. Verify search filter matches users in AD
3. Check if service account has read permission
4. Review sync error message for details

## Configuration via API

### Create/Update Configuration

```bash
curl -X POST http://localhost:8000/api/v1/users/ad-configuration/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server_name": "ad.company.local",
    "server_port": 389,
    "use_ssl": false,
    "bind_username": "CN=admin,DC=company,DC=com",
    "bind_password": "password123",
    "search_base": "OU=Users,DC=company,DC=com",
    "search_filter": "(objectClass=user)",
    "username_attribute": "sAMAccountName",
    "email_attribute": "mail",
    "first_name_attribute": "givenName",
    "last_name_attribute": "sn",
    "phone_attribute": "telephoneNumber",
    "auto_create_users": true,
    "auto_update_users": true,
    "auto_disable_missing_users": false,
    "is_enabled": true
  }'
```

### Test Connection

```bash
curl -X POST http://localhost:8000/api/v1/users/ad-configuration/1/test_connection/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Trigger Sync

```bash
curl -X POST http://localhost:8000/api/v1/users/ad-configuration/1/sync_now/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Feature Checklist

- [x] ADConfiguration model created
- [x] Serializer with validation
- [x] ViewSet with CRUD operations
- [x] test_connection action
- [x] sync_now action
- [x] Organization isolation
- [x] Permission controls
- [x] Admin UI component (AdminADConfiguration.jsx)
- [x] Database migration
- [x] Documentation

## Next Steps

1. Test with your actual AD/LDAP server
2. Run initial sync to verify configuration
3. Monitor sync status and error messages
4. Configure Celery Beat for scheduled syncs (optional)
5. Set up email notifications for sync failures (optional)

## File Locations

```
Backend:
  backend/apps/users/
    ├── ad_config.py                      (Model)
    ├── ad_config_serializers.py          (Serializer)
    ├── views.py                          (ViewSet - updated)
    ├── urls.py                           (Router - updated)
    └── migrations/0003_ad_configuration.py

Frontend:
  fe/src/pages/
    └── AdminADConfiguration.jsx          (React component)

Documentation:
  AD_CONFIGURATION_GUIDE.md               (Comprehensive guide)
  AD_CONFIGURATION_QUICK_SETUP.md         (This file)
```

## Performance Considerations

- **Large Directories**: If AD has 10,000+ users, sync may take several minutes
- **Network Latency**: High-latency connections may require timeout adjustment
- **Search Filters**: Complex filters may impact performance
- **Background Task**: Syncs run via Celery, not blocking the UI

## Support

For issues or questions:
1. Check **Last Sync Error** in configuration status
2. Review **AD_CONFIGURATION_GUIDE.md** for troubleshooting
3. Verify AD service account permissions
4. Check network connectivity to AD server
5. Review Django logs for detailed error messages

---

**Version**: 1.0  
**Setup Time**: ~5 minutes  
**Status**: Ready for Production
