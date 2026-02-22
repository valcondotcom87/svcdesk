import React, { useState, useEffect } from 'react';
import {
  Card, Form, Input, Button, Switch, Space, Spin, message, Divider,
  Table, Tag, Alert, Row, Col, Modal, Tooltip, InputNumber
} from 'antd';
import {
  SaveOutlined, TestOutlined, SyncOutlined, EditOutlined,
  CheckCircleOutlined, ExclamationCircleOutlined, ClockCircleOutlined
} from '@ant-design/icons';
import API from '../services/api';

const AdminADConfiguration = () => {
  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [config, setConfig] = useState(null);
  const [form] = Form.useForm();
  const [editable, setEditable] = useState(false);

  useEffect(() => {
    fetchADConfiguration();
  }, []);

  const fetchADConfiguration = async () => {
    setLoading(true);
    try {
      const response = await API.get('/users/ad-configuration/');
      if (response.data.results && response.data.results.length > 0) {
        const adConfig = response.data.results[0];
        setConfig(adConfig);
        populateForm(adConfig);
      }
    } catch (error) {
      console.error('Failed to load AD configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const populateForm = (data) => {
    form.setFieldsValue({
      server_name: data.server_name,
      server_port: data.server_port,
      use_ssl: data.use_ssl,
      bind_username: data.bind_username,
      search_base: data.search_base,
      search_filter: data.search_filter,
      username_attribute: data.username_attribute,
      email_attribute: data.email_attribute,
      first_name_attribute: data.first_name_attribute,
      last_name_attribute: data.last_name_attribute,
      phone_attribute: data.phone_attribute,
      group_base: data.group_base,
      group_member_attribute: data.group_member_attribute,
      auto_create_users: data.auto_create_users,
      auto_update_users: data.auto_update_users,
      auto_disable_missing_users: data.auto_disable_missing_users,
      is_enabled: data.is_enabled,
    });
  };

  const handleSave = async (values) => {
    setLoading(true);
    try {
      if (config?.id) {
        const response = await API.patch(
          `/users/ad-configuration/${config.id}/`,
          {
            ...values,
            bind_password: values.bind_password || config.bind_password,
          }
        );
        setConfig(response.data);
        message.success('AD configuration saved successfully');
      } else {
        const response = await API.post('/users/ad-configuration/', values);
        setConfig(response.data);
        message.success('AD configuration created successfully');
      }
      setEditable(false);
      fetchADConfiguration();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to save configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async () => {
    if (!config?.id) {
      message.error('Please save configuration first');
      return;
    }

    setTestLoading(true);
    try {
      const response = await API.post(
        `/users/ad-configuration/${config.id}/test_connection/`
      );
      if (response.data.success) {
        message.success(response.data.message);
      } else {
        message.error(response.data.detail);
      }
    } catch (error) {
      message.error(error.response?.data?.detail || 'Connection test failed');
    } finally {
      setTestLoading(false);
    }
  };

  const handleSyncNow = async () => {
    if (!config?.id) {
      message.error('Please save configuration first');
      return;
    }

    Modal.confirm({
      title: 'Start AD Sync?',
      content: 'This will sync users from Active Directory. Continue?',
      okText: 'Yes',
      cancelText: 'No',
      onOk: async () => {
        setSyncLoading(true);
        try {
          const response = await API.post(
            `/users/ad-configuration/${config.id}/sync_now/`
          );
          if (response.data.success) {
            message.success(response.data.message);
          }
        } catch (error) {
          message.error(error.response?.data?.detail || 'Failed to start sync');
        } finally {
          setSyncLoading(false);
        }
      },
    });
  };

  if (loading) return <Spin />;

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title="Active Directory (AD) Configuration"
        extra={
          <Space>
            {!editable ? (
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => setEditable(true)}
              >
                Edit Configuration
              </Button>
            ) : (
              <>
                <Button onClick={() => setEditable(false)}>Cancel</Button>
                <Button type="primary" loading={loading} onClick={() => form.submit()}>
                  Save Changes
                </Button>
              </>
            )}
          </Space>
        }
      >
        {/* Status Section */}
        {config && (
          <>
            <Row gutter={16} style={{ marginBottom: '24px' }}>
              <Col xs={24} sm={12} md={6}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                    Status
                  </div>
                  <Tag color={config.is_enabled ? 'green' : 'red'} style={{ fontSize: '14px' }}>
                    {config.is_enabled ? 'Enabled' : 'Disabled'}
                  </Tag>
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                    Configuration
                  </div>
                  <Tag
                    color={config.is_configured ? 'green' : 'orange'}
                    style={{ fontSize: '14px' }}
                  >
                    {config.is_configured ? 'Complete' : 'Incomplete'}
                  </Tag>
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                    Last Sync
                  </div>
                  <div style={{ fontSize: '14px' }}>
                    {config.last_sync_at
                      ? new Date(config.last_sync_at).toLocaleDateString()
                      : 'Never'}
                  </div>
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                    Sync Status
                  </div>
                  <Tag
                    color={
                      config.last_sync_status === 'success' ? 'green' :
                      config.last_sync_status === 'failed' ? 'red' :
                      'blue'
                    }
                    style={{ fontSize: '14px' }}
                  >
                    {config.last_sync_status}
                  </Tag>
                </Card>
              </Col>
            </Row>

            {config.last_sync_error && (
              <Alert
                message="Last Sync Error"
                description={config.last_sync_error}
                type="error"
                closable
                style={{ marginBottom: '24px' }}
              />
            )}

            <Divider>Connection Error Message (if any)</Divider>
          </>
        )}

        {/* Configuration Form */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          disabled={!editable}
        >
          {/* Server Connection */}
          <h3>Server Connection</h3>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                label="AD Server Name/IP"
                name="server_name"
                rules={[{ required: true, message: 'Server name is required' }]}
                tooltip="AD server hostname or IP address (e.g., 192.168.1.10 or ad.company.local)"
              >
                <Input placeholder="ad.company.local" />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item
                label="Port"
                name="server_port"
                rules={[{ required: true }]}
                tooltip="389 for plain LDAP, 636 for SSL"
              >
                <InputNumber min={1} max={65535} placeholder="389" />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item
                label="Use SSL/TLS"
                name="use_ssl"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          {/* Authentication */}
          <h3>Service Account (Authentication)</h3>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                label="Bind Username"
                name="bind_username"
                rules={[{ required: true, message: 'Username is required' }]}
                tooltip="Service account DN (e.g., CN=admin,DC=company,DC=com)"
              >
                <Input placeholder="CN=admin,DC=company,DC=com" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                label="Bind Password"
                name="bind_password"
                tooltip="Service account password (only required when creating/changing)"
              >
                <Input.Password placeholder="Leave blank to keep existing password" />
              </Form.Item>
            </Col>
          </Row>

          {/* Search Configuration */}
          <h3>User Search Configuration</h3>
          <Row gutter={16}>
            <Col xs={24}>
              <Form.Item
                label="Search Base DN"
                name="search_base"
                rules={[{ required: true, message: 'Search base is required' }]}
                tooltip="Base DN for user search (e.g., OU=Users,DC=company,DC=com)"
              >
                <Input placeholder="OU=Users,DC=company,DC=com" />
              </Form.Item>
            </Col>
            <Col xs={24}>
              <Form.Item
                label="Search Filter"
                name="search_filter"
                tooltip="LDAP filter to find users (default: (objectClass=user))"
              >
                <Input placeholder="(objectClass=user)" />
              </Form.Item>
            </Col>
          </Row>

          {/* Attribute Mapping */}
          <h3>AD Attribute Mapping</h3>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                label="Username Attribute"
                name="username_attribute"
                tooltip="AD attribute for username (typically sAMAccountName)"
              >
                <Input placeholder="sAMAccountName" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                label="Email Attribute"
                name="email_attribute"
                tooltip="AD attribute for email (typically mail)"
              >
                <Input placeholder="mail" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                label="First Name Attribute"
                name="first_name_attribute"
                tooltip="AD attribute for first name (typically givenName)"
              >
                <Input placeholder="givenName" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                label="Last Name Attribute"
                name="last_name_attribute"
                tooltip="AD attribute for last name (typically sn)"
              >
                <Input placeholder="sn" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                label="Phone Attribute"
                name="phone_attribute"
                tooltip="AD attribute for phone (typically telephoneNumber)"
              >
                <Input placeholder="telephoneNumber" />
              </Form.Item>
            </Col>
          </Row>

          {/* Group Configuration */}
          <h3>Group Configuration (Optional)</h3>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                label="Group Base DN"
                name="group_base"
                tooltip="Base DN for group search (e.g., OU=Groups,DC=company,DC=com)"
              >
                <Input placeholder="OU=Groups,DC=company,DC=com" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                label="Group Member Attribute"
                name="group_member_attribute"
                tooltip="Attribute that contains group members (typically member)"
              >
                <Input placeholder="member" />
              </Form.Item>
            </Col>
          </Row>

          {/* Sync Settings */}
          <h3>Sync Settings</h3>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item
                label="Auto Create Users"
                name="auto_create_users"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                label="Auto Update Users"
                name="auto_update_users"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                label="Auto Disable Missing"
                name="auto_disable_missing_users"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          {/* Enable/Disable */}
          <h3>Configuration Status</h3>
          <Form.Item
            label="Enable AD Sync"
            name="is_enabled"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>

        {/* Action Buttons */}
        {editable === false && config && (
          <>
            <Divider />
            <Space style={{ width: '100%', justifyContent: 'center' }}>
              <Button
                icon={<TestOutlined />}
                loading={testLoading}
                onClick={handleTestConnection}
              >
                Test Connection
              </Button>
              <Button
                type="primary"
                icon={<SyncOutlined />}
                loading={syncLoading}
                onClick={handleSyncNow}
                disabled={!config.is_enabled || !config.is_configured}
              >
                Sync Now
              </Button>
            </Space>
          </>
        )}
      </Card>

      {/* Configuration Guide */}
      <Card
        title="Configuration Guide & Sample Values"
        style={{ marginTop: '24px' }}
      >
        <Alert
          message="Active Directory Synchronization"
          description="Configure your AD/LDAP server settings here. Users will be automatically synced based on these settings."
          type="info"
          showIcon
          style={{ marginBottom: '16px' }}
        />

        <h4>Common Field Values:</h4>
        <ul>
          <li><strong>Server Name:</strong> Your AD server's hostname or IP (e.g., ad.company.local or 192.168.1.10)</li>
          <li><strong>Port:</strong> 389 (standard LDAP) or 636 (LDAP over SSL)</li>
          <li><strong>Bind Username:</strong> AD service account in DN format (e.g., CN=svc_account,OU=Service Accounts,DC=company,DC=com)</li>
          <li><strong>Bind Password:</strong> Password for the service account</li>
          <li><strong>Search Base DN:</strong> Base DN where users are located (e.g., OU=Users,DC=company,DC=com)</li>
        </ul>

        <h4>Standard AD Attributes:</h4>
        <ul>
          <li><strong>sAMAccountName:</strong> User login name (e.g., john.doe)</li>
          <li><strong>mail:</strong> Email address</li>
          <li><strong>givenName:</strong> First name</li>
          <li><strong>sn:</strong> Last name (surname)</li>
          <li><strong>telephoneNumber:</strong> Phone number</li>
        </ul>

        <h4>Sync Options:</h4>
        <ul>
          <li><strong>Auto Create Users:</strong> Automatically create new users found in AD</li>
          <li><strong>Auto Update Users:</strong> Automatically update user info from AD</li>
          <li><strong>Auto Disable Missing:</strong> Disable users not found in AD during sync</li>
        </ul>
      </Card>
    </div>
  );
};

export default AdminADConfiguration;
