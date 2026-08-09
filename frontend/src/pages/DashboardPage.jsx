import { useQuery } from '@tanstack/react-query'
import { Row, Col, Card, Statistic, Table, Tag, Typography, Spin, Alert, Empty } from 'antd'
import { CalendarOutlined, DollarOutlined, UserAddOutlined } from '@ant-design/icons'
import { dashboardApi } from '../api/dashboard'
import dayjs from 'dayjs'

const { Title, Text } = Typography

const STATUS_MAP = {
  scheduled: { label: 'נקבע',    color: 'blue'    },
  confirmed: { label: 'אושר',    color: 'green'   },
  completed: { label: 'הושלם',   color: 'default' },
  cancelled: { label: 'בוטל',    color: 'red'     },
  no_show:   { label: 'לא הגיעה', color: 'orange'  },
}

const columns = [
  {
    title: 'שעה',
    dataIndex: 'start_time',
    width: 75,
    render: (t) => (
      <Text style={{ color: '#8b5cf6', fontWeight: 500 }}>
        {dayjs(t).format('HH:mm')}
      </Text>
    ),
  },
  {
    title: 'לקוחה',
    dataIndex: 'client_name',
    render: (name) => <Text>{name}</Text>,
  },
  {
    title: 'טיפול',
    dataIndex: 'treatment_name',
    responsive: ['sm'],
    render: (t) => <Text type="secondary">{t}</Text>,
  },
  {
    title: 'מחיר',
    dataIndex: 'price',
    width: 80,
    responsive: ['sm'],
    render: (p) =>
      p != null
        ? <Text style={{ color: '#10b981' }}>₪{p}</Text>
        : <Text type="secondary">—</Text>,
  },
  {
    title: 'סטטוס',
    dataIndex: 'status',
    width: 95,
    render: (s) => {
      const { label, color } = STATUS_MAP[s] || { label: s, color: 'default' }
      return <Tag color={color}>{label}</Tag>
    },
  },
]

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard', 'today'],
    queryFn: dashboardApi.getToday,
    refetchInterval: 60_000,
  })

  if (isLoading)
    return (
      <div style={{ textAlign: 'center', paddingTop: 100 }}>
        <Spin size="large" />
      </div>
    )

  if (error)
    return (
      <Alert
        type="error"
        message="שגיאה בטעינת הדשבורד"
        description={error.message}
        style={{ marginTop: 24 }}
      />
    )

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <Title level={4} style={{ margin: 0, fontWeight: 400, color: '#1c1833' }}>
          {dayjs().format('dddd, D בMMMM')}
        </Title>
        <Text style={{ color: '#a78bfa', fontSize: 12, fontWeight: 300, letterSpacing: 1 }}>
          EDEN COSMETICS — CRM
        </Text>
      </div>

      {/* Stat Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>

        <Col xs={24} sm={8}>
          <Card
            bordered={false}
            className="stat-card stat-card-rose"
            style={{ borderRadius: 12, background: '#fff' }}
          >
            <Statistic
              title={
                <span style={{ color: '#9ca3af', fontWeight: 400, fontSize: 12 }}>
                  <CalendarOutlined style={{ marginLeft: 6 }} />
                  תורים היום
                </span>
              }
              value={data.total_appointments_today}
              valueStyle={{ color: '#f43f5e', fontSize: 30, fontWeight: 500 }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card
            bordered={false}
            className="stat-card stat-card-green"
            style={{ borderRadius: 12, background: '#fff' }}
          >
            <Statistic
              title={
                <span style={{ color: '#9ca3af', fontWeight: 400, fontSize: 12 }}>
                  <DollarOutlined style={{ marginLeft: 6 }} />
                  הכנסות היום
                </span>
              }
              value={data.total_revenue_today}
              prefix="₪"
              precision={0}
              valueStyle={{ color: '#10b981', fontSize: 30, fontWeight: 500 }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card
            bordered={false}
            className="stat-card stat-card-violet"
            style={{ borderRadius: 12, background: '#fff' }}
          >
            <Statistic
              title={
                <span style={{ color: '#9ca3af', fontWeight: 400, fontSize: 12 }}>
                  <UserAddOutlined style={{ marginLeft: 6 }} />
                  לקוחות חדשות החודש
                </span>
              }
              value={data.new_clients_this_month}
              valueStyle={{ color: '#8b5cf6', fontSize: 30, fontWeight: 500 }}
            />
          </Card>
        </Col>

      </Row>

      {/* Schedule */}
      <Card
        className="schedule-card"
        bordered={false}
        title={
          <span style={{ fontSize: 14, fontWeight: 400, color: '#374151' }}>
            <CalendarOutlined style={{ marginLeft: 8, color: '#a78bfa' }} />
            לוח זמנים להיום
          </span>
        }
        style={{ borderRadius: 12 }}
      >
        {data.appointments_today.length === 0 ? (
          <Empty
            description={<Text type="secondary">אין תורים מתוכננים להיום</Text>}
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{ padding: '24px 0' }}
          />
        ) : (
          <Table
            dataSource={data.appointments_today}
            columns={columns}
            rowKey="id"
            pagination={false}
            size="small"
            scroll={{ x: 'max-content' }}
          />
        )}
      </Card>
    </div>
  )
}
