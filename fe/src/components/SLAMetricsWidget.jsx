import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Tag, Statistic, Progress, Timeline, Badge, Spin, Button } from 'antd';
import { 
  ClockCircleOutlined, CheckCircleOutlined, ExclamationCircleOutlined, 
  ArrowUpOutlined, RiseOutlined 
} from '@ant-design/icons';
import dayjs from 'dayjs';
import API from '../services/api';

const SLAMetricsWidget = ({ ticketId, ticketType = 'incident' }) => {
  const [slaData, setSlaData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSLAData();
    const interval = setInterval(fetchSLAData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [ticketId]);

  const fetchSLAData = async () => {
    try {
      // Try to get SLA metrics for this ticket
      const response = await API.get(`/sla/metrics/`, {
        params: {
          ticket_type: ticketType,
          ticket_id: ticketId,
          page_size: 1
        }
      });
      
      if (response.data.results && response.data.results.length > 0) {
        setSlaData(response.data.results[0]);
      }
    } catch (error) {
      console.error('Failed to load SLA metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Spin />;
  }

  if (!slaData) {
    return (
      <Card size="small" style={{ marginTop: '1rem' }}>
        <p>No SLA policy assigned to this ticket</p>
      </Card>
    );
  }

  const now = dayjs();
  const responseStatus = slaData.first_response_at ? 'completed' : (
    slaData.response_breached ? 'breached' : 'pending'
  );
  const resolutionStatus = slaData.resolution_at ? 'completed' : (
    slaData.resolution_breached ? 'breached' : 'pending'
  );

  const responseTimeSeconds = slaData.response_time_minutes ? 
    slaData.response_time_minutes * 60 : null;
  const resolutionTimeSeconds = slaData.resolution_time_minutes ? 
    slaData.resolution_time_minutes * 60 : null;

  const responsePercent = responseTimeSeconds ? 
    Math.min(100, Math.max(0, 100 - (slaData.response_time_remaining_hours || 0) / 
      (slaData.response_time_remaining_hours + responseTimeSeconds / 3600) * 100)) : 0;
  
  const resolutionPercent = resolutionTimeSeconds ? 
    Math.min(100, Math.max(0, 100 - (slaData.resolution_time_remaining_hours || 0) / 
      (slaData.resolution_time_remaining_hours + resolutionTimeSeconds / 3600) * 100)) : 0;

  return (
    <Card 
      title={
        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ClockCircleOutlined />
          SLA Metrics
          {slaData.sla_policy_name && (
            <Tag style={{ marginLeft: '8px' }}>{slaData.sla_policy_name}</Tag>
          )}
        </span>
      }
      size="small"
      style={{ marginTop: '1rem' }}
    >
      <Row gutter={[16, 16]}>
        {/* Response SLA */}
        <Col xs={24} sm={12}>
          <div style={{ 
            padding: '12px', 
            border: '1px solid #f0f0f0', 
            borderRadius: '4px',
            backgroundColor: responseStatus === 'breached' ? '#fff2f0' : 
                            responseStatus === 'completed' ? '#f6ffed' : '#fafafa'
          }}>
            <div style={{ marginBottom: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <strong>Response Time SLA</strong>
                {responseStatus === 'completed' && (
                  <Tag color="green" icon={<CheckCircleOutlined />}>Met</Tag>
                )}
                {responseStatus === 'breached' && (
                  <Tag color="red" icon={<ExclamationCircleOutlined />}>Breached</Tag>
                )}
                {responseStatus === 'pending' && (
                  <Tag color="blue">Pending</Tag>
                )}
              </div>
              {slaData.response_due_at && (
                <small>Due: {dayjs(slaData.response_due_at).format('DD/MM/YYYY HH:mm')}</small>
              )}
            </div>

            <Progress 
              percent={responsePercent} 
              status={responseStatus === 'breached' ? 'exception' : 'active'}
              size="small"
              style={{ marginBottom: '8px' }}
            />

            {slaData.first_response_at ? (
              <small style={{ color: '#666' }}>
                Responded: {dayjs(slaData.first_response_at).format('DD/MM/YYYY HH:mm')}
                <br />
                Time to respond: {slaData.response_time_minutes ? 
                  `${Math.round(slaData.response_time_minutes)} min` : '—'}
              </small>
            ) : (
              slaData.response_time_remaining_hours !== null && (
                <small style={{ color: '#666' }}>
                  {slaData.response_time_remaining_hours > 0 ? 
                    `Time remaining: ${Math.round(slaData.response_time_remaining_hours * 60)} min` :
                    'SLA Breached'}
                </small>
              )
            )}
          </div>
        </Col>

        {/* Resolution SLA */}
        <Col xs={24} sm={12}>
          <div style={{ 
            padding: '12px', 
            border: '1px solid #f0f0f0', 
            borderRadius: '4px',
            backgroundColor: resolutionStatus === 'breached' ? '#fff2f0' : 
                            resolutionStatus === 'completed' ? '#f6ffed' : '#fafafa'
          }}>
            <div style={{ marginBottom: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <strong>Resolution Time SLA</strong>
                {resolutionStatus === 'completed' && (
                  <Tag color="green" icon={<CheckCircleOutlined />}>Met</Tag>
                )}
                {resolutionStatus === 'breached' && (
                  <Tag color="red" icon={<ExclamationCircleOutlined />}>Breached</Tag>
                )}
                {resolutionStatus === 'pending' && (
                  <Tag color="blue">Pending</Tag>
                )}
              </div>
              {slaData.resolution_due_at && (
                <small>Due: {dayjs(slaData.resolution_due_at).format('DD/MM/YYYY HH:mm')}</small>
              )}
            </div>

            <Progress 
              percent={resolutionPercent} 
              status={resolutionStatus === 'breached' ? 'exception' : 'active'}
              size="small"
              style={{ marginBottom: '8px' }}
            />

            {slaData.resolution_at ? (
              <small style={{ color: '#666' }}>
                Resolved: {dayjs(slaData.resolution_at).format('DD/MM/YYYY HH:mm')}
                <br />
                Time to resolve: {slaData.resolution_time_minutes ? 
                  `${Math.round(slaData.resolution_time_minutes)} min` : '—'}
              </small>
            ) : (
              slaData.resolution_time_remaining_hours !== null && (
                <small style={{ color: '#666' }}>
                  {slaData.resolution_time_remaining_hours > 0 ? 
                    `Time remaining: ${Math.round(slaData.resolution_time_remaining_hours * 60)} min` :
                    'SLA Breached'}
                </small>
              )
            )}
          </div>
        </Col>

        {/* Escalations */}
        {(slaData.escalation_count > 0 || slaData.escalated_at) && (
          <Col xs={24}>
            <div style={{ 
              padding: '12px', 
              border: '1px solid #fff7e6', 
              borderRadius: '4px',
              backgroundColor: '#fffbe6'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <RiseOutlined style={{ color: '#faad14' }} />
                <strong>Escalations</strong>
                {slaData.escalation_count > 0 && (
                  <Badge count={slaData.escalation_count} style={{ backgroundColor: '#faad14' }} />
                )}
              </div>
              {slaData.escalated_at && (
                <small style={{ color: '#666' }}>
                  Last escalated: {dayjs(slaData.escalated_at).format('DD/MM/YYYY HH:mm')}
                </small>
              )}
            </div>
          </Col>
        )}

        {/* SLA Target Info */}
        {slaData.sla_target_display && (
          <Col xs={24}>
            <small style={{ color: '#999' }}>
              <strong>SLA Target:</strong> {slaData.sla_target_display}
            </small>
          </Col>
        )}
      </Row>

      {/* Refresh Button */}
      <div style={{ marginTop: '12px' }}>
        <Button 
          size="small" 
          onClick={fetchSLAData}
          type="text"
        >
          Refresh
        </Button>
      </div>
    </Card>
  );
};

export default SLAMetricsWidget;
