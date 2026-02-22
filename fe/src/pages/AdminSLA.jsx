import React, { useState, useEffect } from 'react';
import {
  Card, Tabs, Button, Table, Form, Modal, Input, Select, InputNumber,
  Space, Tag, Statistic, Row, Col, Spin, message, Transfer, TimePicker,
  Tooltip, Popconfirm, Drawer, Divider
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined,
  AlertOutlined, ClockCircleOutlined, FileTextOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import API from '../services/api';

const AdminSLA = () => {
  const [activeTab, setActiveTab] = useState('1');
  const [loading, setLoading] = useState(false);
  const [policies, setPolicies] = useState([]);
  const [breaches, setBreaches] = useState([]);
  const [metrics, setMetrics] = useState([]);

  // Policy Management State
  const [showPolicyModal, setShowPolicyModal] = useState(false);
  const [policyForm] = Form.useForm();
  const [editingPolicy, setEditingPolicy] = useState(null);

  // Target Management State
  const [showTargetModal, setShowTargetModal] = useState(false);
  const [targetForm] = Form.useForm();
  const [selectedPolicy, setSelectedPolicy] = useState(null);
  const [policyTargets, setPolicyTargets] = useState([]);

  // Escalation State
  const [showEscalationModal, setShowEscalationModal] = useState(false);
  const [escalationForm] = Form.useForm();
  const [policyEscalations, setPolicyEscalations] = useState([]);

  // Detail Drawer
  const [showDetailDrawer, setShowDetailDrawer] = useState(false);
  const [detailPolicy, setDetailPolicy] = useState(null);

  // Statistics
  const [stats, setStats] = useState({
    totalPolicies: 0,
    activePolicies: 0,
    currentMonth: { compliance: 0, breaches: 0 }
  });

  // Fetch policies
  useEffect(() => {
    fetchPolicies();
    fetchBreaches();
    fetchMetrics();
  }, []);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const response = await API.get('/sla/policies/', {
        params: { is_active: true }
      });
      setPolicies(response.data.results || []);
      setStats(prev => ({
        ...prev,
        totalPolicies: response.data.count || 0,
        activePolicies: response.data.results?.filter(p => p.is_active).length || 0
      }));
    } catch (error) {
      message.error('Failed to load SLA policies');
    } finally {
      setLoading(false);
    }
  };

  const fetchBreaches = async () => {
    try {
      const response = await API.get('/sla/breaches/', {
        params: { page_size: 50 }
      });
      setBreaches(response.data.results || []);
    } catch (error) {
      console.error('Failed to load breaches:', error);
    }
  };

  const fetchMetrics = async () => {
    try {
      const now = new Date();
      const response = await API.get('/sla/metrics/', {
        params: {
          year: now.getFullYear(),
          month: now.getMonth() + 1,
          page_size: 1
        }
      });
      if (response.data.results?.length > 0) {
        const metric = response.data.results[0];
        setStats(prev => ({
          ...prev,
          currentMonth: {
            compliance: metric.compliance_percentage,
            breaches: metric.breached_incidents
          }
        }));
      }
      setMetrics(response.data.results || []);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };

  // POLICIES TAB
  const handleCreatePolicy = async (values) => {
    try {
      if (editingPolicy) {
        await API.patch(`/sla/policies/${editingPolicy.id}/`, values);
        message.success('SLA Policy updated successfully');
      } else {
        await API.post('/sla/policies/', values);
        message.success('SLA Policy created successfully');
      }
      setShowPolicyModal(false);
      policyForm.resetFields();
      setEditingPolicy(null);
      fetchPolicies();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to save SLA policy');
    }
  };

  const handleEditPolicy = (policy) => {
    setEditingPolicy(policy);
    policyForm.setFieldsValue({
      name: policy.name,
      description: policy.description,
      coverage: policy.coverage,
      response_time: policy.response_time,
      resolution_time: policy.resolution_time,
      applies_to_priority: policy.applies_to_priority,
      is_active: policy.is_active
    });
    setShowPolicyModal(true);
  };

  const handleDeletePolicy = async (policyId) => {
    try {
      await API.delete(`/sla/policies/${policyId}/`);
      message.success('SLA Policy deleted');
      fetchPolicies();
    } catch (error) {
      message.error('Failed to delete SLA policy');
    }
  };

  const handleViewPolicy = (policy) => {
    setDetailPolicy(policy);
    setShowDetailDrawer(true);
  };

  // TARGETS TAB
  const handleAddTarget = async (values) => {
    try {
      const data = {
        sla_policy: selectedPolicy.id,
        severity: values.severity,
        response_time_minutes: values.response_time_minutes,
        resolution_time_minutes: values.resolution_time_minutes
      };
      await API.post('/sla/targets/', data);
      message.success('SLA Target added successfully');
      setShowTargetModal(false);
      targetForm.resetFields();
      fetchPolicyTargets(selectedPolicy.id);
    } catch (error) {
      message.error('Failed to add SLA target');
    }
  };

  const fetchPolicyTargets = async (policyId) => {
    try {
      const response = await API.get('/sla/targets/', {
        params: { sla_policy: policyId }
      });
      setPolicyTargets(response.data.results || []);
    } catch (error) {
      console.error('Failed to load targets:', error);
    }
  };

  const handleDeleteTarget = async (targetId) => {
    try {
      await API.delete(`/sla/targets/${targetId}/`);
      message.success('SLA Target deleted');
      if (selectedPolicy) {
        fetchPolicyTargets(selectedPolicy.id);
      }
    } catch (error) {
      message.error('Failed to delete target');
    }
  };

  // ESCALATIONS TAB
  const handleAddEscalation = async (values) => {
    try {
      const data = {
        sla_policy: selectedPolicy.id,
        level: values.level,
        escalate_after_minutes: values.escalate_after_minutes,
        escalate_to_team: values.escalate_to_team,
        escalate_to_user: values.escalate_to_user,
        notify_managers: values.notify_managers,
        action_description: values.action_description
      };
      await API.post('/sla/escalations/', data);
      message.success('Escalation rule added');
      setShowEscalationModal(false);
      escalationForm.resetFields();
      fetchPolicyEscalations(selectedPolicy.id);
    } catch (error) {
      message.error('Failed to add escalation rule');
    }
  };

  const fetchPolicyEscalations = async (policyId) => {
    try {
      const response = await API.get('/sla/escalations/', {
        params: { sla_policy: policyId }
      });
      setPolicyEscalations(response.data.results || []);
    } catch (error) {
      console.error('Failed to load escalations:', error);
    }
  };

  // BREACHES TABLE
  const breachColumns = [
    {
      title: 'Ticket',
      dataIndex: 'ticket_number',
      key: 'ticket',
      render: (_, record) => (
        <span>{record.incident?.ticket_number || 'N/A'}</span>
      )
    },
    {
      title: 'Type',
      dataIndex: 'breach_type',
      key: 'type',
      render: (type) => (
        <Tag color={type === 'response' ? 'red' : 'orange'}>
          {type === 'response' ? 'Response Time' : 'Resolution Time'}
        </Tag>
      )
    },
    {
      title: 'Target Time',
      dataIndex: 'target_time',
      key: 'target',
      render: (date) => dayjs(date).format('DD/MM/YYYY HH:mm')
    },
    {
      title: 'Breached At',
      dataIndex: 'breached_at',
      key: 'breached',
      render: (date) => dayjs(date).format('DD/MM/YYYY HH:mm')
    },
    {
      title: 'Duration (min)',
      dataIndex: 'breach_duration_minutes',
      key: 'duration',
      render: (minutes) => (
        <span>{minutes} mins</span>
      )
    },
    {
      title: 'Status',
      dataIndex: 'is_acknowledged',
      key: 'status',
      render: (acknowledged) => (
        <Tag color={acknowledged ? 'blue' : 'red'}>
          {acknowledged ? 'Acknowledged' : 'Unresolved'}
        </Tag>
      )
    }
  ];

  // POLICY COLUMNS
  const policyColumns = [
    {
      title: 'Policy Name',
      dataIndex: 'name',
      key: 'name',
      width: 200
    },
    {
      title: 'Service',
      dataIndex: ['service', 'name'],
      key: 'service',
      render: (name) => name || '—'
    },
    {
      title: 'Coverage',
      dataIndex: 'coverage_display',
      key: 'coverage',
      render: (coverage) => (
        <Tag>{coverage}</Tag>
      )
    },
    {
      title: 'Response Time',
      dataIndex: 'response_time',
      key: 'response',
      render: (minutes) => (
        <Tooltip title={`${minutes} minutes`}>
          <span>{(minutes / 60).toFixed(1)}h</span>
        </Tooltip>
      )
    },
    {
      title: 'Resolution Time',
      dataIndex: 'resolution_time',
      key: 'resolution',
      render: (minutes) => (
        <Tooltip title={`${minutes} minutes`}>
          <span>{(minutes / 60).toFixed(1)}h</span>
        </Tooltip>
      )
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'status',
      render: (active) => (
        <Tag color={active ? 'green' : 'red'}>
          {active ? 'Active' : 'Inactive'}
        </Tag>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="View Details">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewPolicy(record)}
            />
          </Tooltip>
          <Tooltip title="Edit">
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEditPolicy(record)}
            />
          </Tooltip>
          <Popconfirm
            title="Delete Policy?"
            description="This will remove all targets and escalations"
            onConfirm={() => handleDeletePolicy(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button
              type="text"
              size="small"
              danger
              icon={<DeleteOutlined />}
            />
          </Popconfirm>
        </Space>
      )
    }
  ];

  // TARGET COLUMNS
  const targetColumns = [
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity) => (
        <Tag color={
          severity === 'critical' ? 'red' :
          severity === 'high' ? 'orange' :
          severity === 'medium' ? 'blue' :
          'green'
        }>
          {severity.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Response (mins)',
      dataIndex: 'response_time_minutes',
      key: 'response',
      render: (mins) => (
        <span>{mins}</span>
      )
    },
    {
      title: 'Resolution (mins)',
      dataIndex: 'resolution_time_minutes',
      key: 'resolution',
      render: (mins) => (
        <span>{mins}</span>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 80,
      render: (_, record) => (
        <Popconfirm
          title="Delete?"
          onConfirm={() => handleDeleteTarget(record.id)}
          okText="Yes"
          cancelText="No"
        >
          <Button type="text" size="small" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      )
    }
  ];

  // ESCALATION COLUMNS
  const escalationColumns = [
    {
      title: 'Level',
      dataIndex: 'level',
      key: 'level',
      width: 80,
      render: (level) => (
        <Tag color="blue">Level {level}</Tag>
      )
    },
    {
      title: 'Escalate After (mins)',
      dataIndex: 'escalate_after_minutes',
      key: 'after',
      width: 150
    },
    {
      title: 'Team/User',
      key: 'escalate_to',
      render: (_, record) => (
        <span>
          {record.escalate_to_team_name && `Team: ${record.escalate_to_team_name}`}
          {record.escalate_to_user_name && `User: ${record.escalate_to_user_name}`}
        </span>
      )
    },
    {
      title: 'Notify Managers',
      dataIndex: 'notify_managers',
      key: 'notify',
      render: (notify) => (
        <Tag color={notify ? 'green' : 'gray'}>
          {notify ? 'Yes' : 'No'}
        </Tag>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <ClockCircleOutlined style={{ fontSize: 24 }} />
            <span>SLA Management</span>
          </Space>
        }
      >
        {/* STATISTICS */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Total Policies"
                value={stats.totalPolicies}
                prefix={<FileTextOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Active Policies"
                value={stats.activePolicies}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="This Month Compliance"
                value={stats.currentMonth.compliance}
                suffix="%"
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Breaches (Current Month)"
                value={stats.currentMonth.breaches}
                prefix={<AlertOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
        </Row>

        {/* TABS */}
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: '1',
              label: 'SLA Policies',
              children: (
                <div>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => {
                      setEditingPolicy(null);
                      policyForm.resetFields();
                      setShowPolicyModal(true);
                    }}
                    style={{ marginBottom: 16 }}
                  >
                    New Policy
                  </Button>
                  <Table
                    columns={policyColumns}
                    dataSource={policies}
                    loading={loading}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                  />
                </div>
              )
            },
            {
              key: '2',
              label: 'Targets & Escalations',
              children: (
                <div>
                  <div style={{ marginBottom: 16 }}>
                    <Select
                      placeholder="Select a policy..."
                      value={selectedPolicy?.id}
                      onChange={(policyId) => {
                        const policy = policies.find(p => p.id === policyId);
                        setSelectedPolicy(policy);
                        fetchPolicyTargets(policyId);
                        fetchPolicyEscalations(policyId);
                      }}
                      style={{ width: 300, marginRight: 16 }}
                      options={policies.map(p => ({ label: p.name, value: p.id }))}
                    />
                    {selectedPolicy && (
                      <>
                        <Button
                          type="primary"
                          icon={<PlusOutlined />}
                          onClick={() => setShowTargetModal(true)}
                          style={{ marginRight: 8 }}
                        >
                          Add Target
                        </Button>
                        <Button
                          type="primary"
                          icon={<PlusOutlined />}
                          onClick={() => setShowEscalationModal(true)}
                        >
                          Add Escalation
                        </Button>
                      </>
                    )}
                  </div>
                  {selectedPolicy && (
                    <>
                      <h3>Response & Resolution Targets</h3>
                      <Table
                        columns={targetColumns}
                        dataSource={policyTargets}
                        rowKey="id"
                        pagination={false}
                        style={{ marginBottom: 24 }}
                      />
                      <h3>Escalation Rules</h3>
                      <Table
                        columns={escalationColumns}
                        dataSource={policyEscalations}
                        rowKey="id"
                        pagination={false}
                      />
                    </>
                  )}
                </div>
              )
            },
            {
              key: '3',
              label: 'SLA Breaches',
              children: (
                <Table
                  columns={breachColumns}
                  dataSource={breaches}
                  rowKey="id"
                  pagination={{ pageSize: 20 }}
                />
              )
            }
          ]}
        />
      </Card>

      {/* POLICY MODAL */}
      <Modal
        title={editingPolicy ? 'Edit SLA Policy' : 'Create New SLA Policy'}
        open={showPolicyModal}
        onOk={() => policyForm.submit()}
        onCancel={() => {
          setShowPolicyModal(false);
          policyForm.resetFields();
          setEditingPolicy(null);
        }}
        width={600}
      >
        <Form
          form={policyForm}
          layout="vertical"
          onFinish={handleCreatePolicy}
        >
          <Form.Item
            label="Policy Name"
            name="name"
            rules={[{ required: true, message: 'Please enter policy name' }]}
          >
            <Input placeholder="e.g., Standard Service Policy" />
          </Form.Item>

          <Form.Item
            label="Description"
            name="description"
          >
            <Input.TextArea rows={3} />
          </Form.Item>

          <Form.Item
            label="Coverage"
            name="coverage"
            rules={[{ required: true }]}
          >
            <Select
              options={[
                { label: '24x7', value: '24x7' },
                { label: 'Business Hours (9-5)', value: 'business' },
                { label: 'Extended Hours (8-8)', value: 'extended' }
              ]}
            />
          </Form.Item>

          <Form.Item
            label="Applies to Priority"
            name="applies_to_priority"
          >
            <Select
              options={[
                { label: 'Critical', value: 'critical' },
                { label: 'High', value: 'high' },
                { label: 'Medium', value: 'medium' },
                { label: 'Low', value: 'low' }
              ]}
              placeholder="Leave empty for all"
            />
          </Form.Item>

          <Form.Item
            label="Response Time (minutes)"
            name="response_time"
            rules={[{ required: true, message: 'Required' }]}
          >
            <InputNumber min={1} />
          </Form.Item>

          <Form.Item
            label="Resolution Time (minutes)"
            name="resolution_time"
            rules={[{ required: true, message: 'Required' }]}
          >
            <InputNumber min={1} />
          </Form.Item>

          <Form.Item
            label="Active"
            name="is_active"
            valuePropName="checked"
          >
            <input type="checkbox" />
          </Form.Item>
        </Form>
      </Modal>

      {/* TARGET MODAL */}
      <Modal
        title="Add SLA Target"
        open={showTargetModal}
        onOk={() => targetForm.submit()}
        onCancel={() => {
          setShowTargetModal(false);
          targetForm.resetFields();
        }}
        width={500}
      >
        <Form
          form={targetForm}
          layout="vertical"
          onFinish={handleAddTarget}
        >
          <Form.Item
            label="Severity Level"
            name="severity"
            rules={[{ required: true }]}
          >
            <Select
              options={[
                { label: 'Critical', value: 'critical' },
                { label: 'High', value: 'high' },
                { label: 'Medium', value: 'medium' },
                { label: 'Low', value: 'low' }
              ]}
            />
          </Form.Item>

          <Form.Item
            label="Response Time (minutes)"
            name="response_time_minutes"
            rules={[{ required: true }]}
          >
            <InputNumber min={1} />
          </Form.Item>

          <Form.Item
            label="Resolution Time (minutes)"
            name="resolution_time_minutes"
            rules={[{ required: true }]}
          >
            <InputNumber min={1} />
          </Form.Item>
        </Form>
      </Modal>

      {/* ESCALATION MODAL */}
      <Modal
        title="Add Escalation Rule"
        open={showEscalationModal}
        onOk={() => escalationForm.submit()}
        onCancel={() => {
          setShowEscalationModal(false);
          escalationForm.resetFields();
        }}
        width={600}
      >
        <Form
          form={escalationForm}
          layout="vertical"
          onFinish={handleAddEscalation}
        >
          <Form.Item
            label="Escalation Level"
            name="level"
            rules={[{ required: true }]}
          >
            <Select
              options={[
                { label: 'Level 1', value: 1 },
                { label: 'Level 2', value: 2 },
                { label: 'Level 3', value: 3 }
              ]}
            />
          </Form.Item>

          <Form.Item
            label="Escalate After (minutes)"
            name="escalate_after_minutes"
            rules={[{ required: true }]}
          >
            <InputNumber min={1} />
          </Form.Item>

          <Form.Item
            label="Escalate to Team"
            name="escalate_to_team"
          >
            <Select placeholder="Select team" />
          </Form.Item>

          <Form.Item
            label="Escalate to User"
            name="escalate_to_user"
          >
            <Select placeholder="Select user" />
          </Form.Item>

          <Form.Item
            label="Notify Managers"
            name="notify_managers"
            valuePropName="checked"
          >
            <input type="checkbox" />
          </Form.Item>

          <Form.Item
            label="Action Description"
            name="action_description"
          >
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      {/* DETAIL DRAWER */}
      <Drawer
        title="SLA Policy Details"
        onClose={() => setShowDetailDrawer(false)}
        open={showDetailDrawer}
        width={700}
      >
        {detailPolicy && (
          <div>
            <div style={{ marginBottom: 24 }}>
              <h3>{detailPolicy.name}</h3>
              <p>{detailPolicy.description}</p>
              <Divider />
            </div>

            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col xs={24} sm={12}>
                <Card size="small">
                  <Statistic
                    title="Response Time"
                    value={(detailPolicy.response_time / 60).toFixed(1)}
                    suffix="hours"
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12}>
                <Card size="small">
                  <Statistic
                    title="Resolution Time"
                    value={(detailPolicy.resolution_time / 60).toFixed(1)}
                    suffix="hours"
                  />
                </Card>
              </Col>
            </Row>

            <Card size="small" title="Configuration">
              <p><strong>Coverage:</strong> {detailPolicy.coverage_display}</p>
              <p><strong>Priority:</strong> {detailPolicy.applies_to_priority || 'All' }</p>
              <p><strong>Active:</strong> <Tag color={detailPolicy.is_active ? 'green' : 'red'}>
                {detailPolicy.is_active ? 'Yes' : 'No'}
              </Tag></p>
            </Card>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default AdminSLA;
