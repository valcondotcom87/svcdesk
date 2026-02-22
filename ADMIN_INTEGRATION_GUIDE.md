# Admin Panel Integration Guide - AD Configuration

This guide shows you how to integrate the AdminADConfiguration component into your admin panel.

## Option 1: Add to Existing Admin Sidebar Menu

### In your AdminLayout or main admin component:

```javascript
import React from 'react';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  SettingOutlined,
  UsersOutlined,
  LockOutlined,
  DatabaseOutlined
} from '@ant-design/icons';

// Import the new component
import AdminADConfiguration from './AdminADConfiguration';
import AdminSLA from './AdminSLA';
import AdminUsers from './AdminUsers';

const AdminPanel = () => {
  const [selectedKey, setSelectedKey] = React.useState('dashboard');
  const [component, setComponent] = React.useState(null);

  const handleMenuClick = (key) => {
    setSelectedKey(key);
    
    switch (key) {
      case 'dashboard':
        setComponent(<AdminDashboard />);
        break;
      case 'users':
        setComponent(<AdminUsers />);
        break;
      case 'sla':
        setComponent(<AdminSLA />);
        break;
      case 'ad-config':
        setComponent(<AdminADConfiguration />);
        break;
      default:
        setComponent(null);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Layout.Sider>
        <Menu
          selectedKeys={[selectedKey]}
          onClick={(e) => handleMenuClick(e.key)}
          theme="dark"
        >
          <Menu.Item key="dashboard" icon={<DashboardOutlined />}>
            Dashboard
          </Menu.Item>
          
          <Menu.SubMenu key="configuration" icon={<SettingOutlined />} title="Configuration">
            <Menu.Item key="users" icon={<UsersOutlined />}>
              Users
            </Menu.Item>
            <Menu.Item key="ad-config" icon={<DatabaseOutlined />}>
              Active Directory
            </Menu.Item>
            <Menu.Item key="sla" icon={<LockOutlined />}>
              SLA Policies
            </Menu.Item>
          </Menu.SubMenu>
        </Menu>
      </Layout.Sider>
      
      <Layout.Content style={{ padding: '24px' }}>
        {component}
      </Layout.Content>
    </Layout>
  );
};

export default AdminPanel;
```

## Option 2: Add as Tab in Settings Component

### If you have a Settings page with tabs:

```javascript
import { Tabs } from 'antd';
import AdminADConfiguration from './AdminADConfiguration';
import AdminSLA from './AdminSLA';
import AdminUsers from './AdminUsers';

const AdminSettings = () => {
  const tabItems = [
    {
      key: 'users',
      label: 'Users',
      children: <AdminUsers />
    },
    {
      key: 'ad-config',
      label: 'Active Directory',
      children: <AdminADConfiguration />
    },
    {
      key: 'sla',
      label: 'SLA Policies',
      children: <AdminSLA />
    }
  ];

  return <Tabs items={tabItems} />;
};

export default AdminSettings;
```

## Option 3: Separate Route in React Router

### In your routing configuration:

```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AdminADConfiguration from './pages/AdminADConfiguration';
import AdminSLA from './pages/AdminSLA';

const AdminRoutes = () => {
  return (
    <Routes>
      {/* Other admin routes... */}
      <Route path="/admin/ad-config" element={<AdminADConfiguration />} />
      <Route path="/admin/sla" element={<AdminSLA />} />
    </Routes>
  );
};

export default AdminRoutes;
```

### Update your navigation:

```javascript
<Link to="/admin/ad-config">Active Directory</Link>
```

## Complete Admin Sidebar Example

Here's a complete example of a modern admin sidebar with all configuration options:

```javascript
import React, { useState } from 'react';
import { Layout, Menu, Breadcrumb } from 'antd';
import {
  DashboardOutlined,
  SettingOutlined,
  UsersOutlined,
  LockOutlined,
  DatabaseOutlined,
  TeamOutlined,
  FileTextOutlined,
  BarChartOutlined,
  LogoutOutlined
} from '@ant-design/icons';

import AdminDashboard from './AdminDashboard';
import AdminUsers from './AdminUsers';
import AdminADConfiguration from './AdminADConfiguration';
import AdminSLA from './AdminSLA';
import AdminAudit from './AdminAudit';
import AdminReports from './AdminReports';

const AdminLayout = () => {
  const [selectedKey, setSelectedKey] = useState('dashboard');
  const [breadcrumbs, setBreadcrumbs] = useState(['Admin', 'Dashboard']);
  const [component, setComponent] = useState(<AdminDashboard />);

  const menuConfig = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      breadcrumb: ['Admin', 'Dashboard'],
      component: <AdminDashboard />
    },
    {
      key: 'divider1',
      type: 'divider'
    },
    {
      key: 'config',
      icon: <SettingOutlined />,
      label: 'Configuration',
      children: [
        {
          key: 'users',
          icon: <UsersOutlined />,
          label: 'Users',
          breadcrumb: ['Admin', 'Configuration', 'Users'],
          component: <AdminUsers />
        },
        {
          key: 'ad-config',
          icon: <DatabaseOutlined />,
          label: 'Active Directory',
          breadcrumb: ['Admin', 'Configuration', 'Active Directory'],
          component: <AdminADConfiguration />
        },
        {
          key: 'sla',
          icon: <LockOutlined />,
          label: 'SLA Policies',
          breadcrumb: ['Admin', 'Configuration', 'SLA'],
          component: <AdminSLA />
        }
      ]
    },
    {
      key: 'divider2',
      type: 'divider'
    },
    {
      key: 'management',
      icon: <TeamOutlined />,
      label: 'Management',
      children: [
        {
          key: 'audit',
          icon: <FileTextOutlined />,
          label: 'Audit Logs',
          breadcrumb: ['Admin', 'Management', 'Audit'],
          component: <AdminAudit />
        },
        {
          key: 'reports',
          icon: <BarChartOutlined />,
          label: 'Reports',
          breadcrumb: ['Admin', 'Management', 'Reports'],
          component: <AdminReports />
        }
      ]
    },
    {
      key: 'divider3',
      type: 'divider'
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: () => handleLogout()
    }
  ];

  const handleMenuClick = (e) => {
    setSelectedKey(e.key);
    
    // Find the selected menu item and get its config
    const findMenuItem = (items) => {
      for (let item of items) {
        if (item.key === e.key) {
          if (item.breadcrumb) setBreadcrumbs(item.breadcrumb);
          if (item.component) setComponent(item.component);
          return;
        }
        if (item.children) {
          findMenuItem(item.children);
        }
      }
    };
    
    findMenuItem(menuConfig);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  const menuItems = menuConfig.map(item => {
    if (item.type === 'divider') {
      return item;
    }
    if (item.children) {
      return {
        key: item.key,
        icon: item.icon,
        label: item.label,
        children: item.children.map(child => ({
          key: child.key,
          icon: child.icon,
          label: child.label
        }))
      };
    }
    return {
      key: item.key,
      icon: item.icon,
      label: item.label
    };
  });

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Layout.Sider
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100
        }}
      >
        <div style={{
          height: '64px',
          margin: '16px',
          background: 'rgba(255, 255, 255, 0.2)',
          borderRadius: '4px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '16px',
          fontWeight: 'bold'
        }}>
          Admin Panel
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          onClick={handleMenuClick}
          items={menuItems}
        />
      </Layout.Sider>

      <Layout style={{ marginLeft: 200 }}>
        <Layout.Header
          style={{
            background: '#fff',
            padding: '0 24px',
            boxShadow: '0 1px 4px rgba(0,0,0,0.15)',
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <Breadcrumb items={breadcrumbs.map(b => ({ title: b }))} />
        </Layout.Header>

        <Layout.Content style={{ margin: '24px 16px', padding: '24px', background: '#fff' }}>
          {component}
        </Layout.Content>

        <Layout.Footer style={{ textAlign: 'center' }}>
          Admin Panel © 2025 - All Rights Reserved
        </Layout.Footer>
      </Layout>
    </Layout>
  );
};

export default AdminLayout;
```

## Integration Checklist

- [ ] Import `AdminADConfiguration` component
- [ ] Add menu item/tab for Active Directory
- [ ] Set up routing if using separate routes
- [ ] Verify component loads without errors
- [ ] Test all buttons (Edit, Save, Test Connection, Sync Now)
- [ ] Verify AD configuration is saved properly
- [ ] Test connection to your AD/LDAP server
- [ ] Run initial sync to verify integration

## Styling Notes

The `AdminADConfiguration` component uses Ant Design components, so ensure:
- Ant Design is installed in your project
- CSS/styling is properly imported
- Theme colors match your admin panel

## API Service Configuration

Ensure your `API` service is properly configured in `fe/src/services/api.js`:

```javascript
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default API;
```

## Next Steps

1. Choose integration method (Menu, Tab, or Route)
2. Import the component
3. Add to your admin layout
4. Test component functionality
5. Configure your AD/LDAP server
6. Run initial sync

---

**Version**: 1.0  
**Status**: Ready for Integration  
**Last Updated**: February 2025
