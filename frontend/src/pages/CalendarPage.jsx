import { useState, useMemo } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Row, Col, Card, Table, Button, Modal, Form, Input, Select, DatePicker,
  Tag, Space, Typography, Popconfirm, message, Tooltip, InputNumber, Calendar,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, LeftOutlined, RightOutlined } from '@ant-design/icons'
import { appointmentsApi } from '../api/appointments'
import { clientsApi } from '../api/clients'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { TextArea } = Input

const STATUS_MAP = {
  scheduled: { label: 'נקבע',    color: 'blue'    },
  confirmed: { label: 'אושר',    color: 'green'   },
  completed: { label: 'הושלם',   color: 'default' },
  cancelled: { label: 'בוטל',    color: 'red'     },
  no_show:   { label: 'לא הגיעה', color: 'orange'  },
}

const STATUS_OPTIONS = Object.entries(STATUS_MAP).map(([value, { label }]) => ({ value, label }))

export default function CalendarPage() {
  const [selectedDate,  setSelectedDate]  = useState(dayjs())
  const [calendarMonth, setCalendarMonth] = useState(dayjs().startOf('month'))
  const [modalOpen,     setModalOpen]     = useState(false)
  const [editing,       setEditing]       = useState(null)
  const [saving,        setSaving]        = useState(false)
  const [form] = Form.useForm()
  const qc = useQueryClient()

  /* ── Queries ──────────────────────────────────────────────── */

  // Appointments for the selected day
  const { data: appointments = [], isLoading } = useQuery({
    queryKey: ['appointments', selectedDate.format('YYYY-MM-DD')],
    queryFn: () =>
      appointmentsApi.list({
        date_from: selectedDate.startOf('day').toISOString(),
        date_to:   selectedDate.endOf('day').toISOString(),
      }),
  })

  // All appointments in the visible month (for dots)
  const { data: monthAppointments = [] } = useQuery({
    queryKey: ['appointments', 'month', calendarMonth.format('YYYY-MM')],
    queryFn: () =>
      appointmentsApi.list({
        date_from: calendarMonth.startOf('month').toISOString(),
        date_to:   calendarMonth.endOf('month').toISOString(),
      }),
  })

  // Clients list (for the form select)
  const { data: allClients = [] } = useQuery({
    queryKey: ['clients', ''],
    queryFn: () => clientsApi.list(),
  })

  // Group monthly appointments by date  → { 'YYYY-MM-DD': count }
  const countByDate = useMemo(() => {
    const map = {}
    monthAppointments.forEach((a) => {
      const key = dayjs(a.start_time).format('YYYY-MM-DD')
      map[key] = (map[key] || 0) + 1
    })
    return map
  }, [monthAppointments])

  /* ── Helpers ──────────────────────────────────────────────── */

  const selectDate = (date) => {
    setSelectedDate(date)
    if (!date.isSame(calendarMonth, 'month')) {
      setCalendarMonth(date.startOf('month'))
    }
  }

  const clientOptions = allClients.map((c) => ({
    value: c.id,
    label: `${c.full_name} · ${c.phone}`,
  }))

  /* ── Calendar cell renderer ───────────────────────────────── */

  const cellRender = (current, info) => {
    if (info.type !== 'date') return info.originNode
    const count = countByDate[current.format('YYYY-MM-DD')]
    if (!count) return null
    return (
      <div className="cal-count">
        {count > 9 ? '9+' : count}
      </div>
    )
  }

  /* ── Modal handlers ───────────────────────────────────────── */

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({
      start_time: selectedDate.hour(10).minute(0).second(0),
      end_time:   selectedDate.hour(11).minute(0).second(0),
      status: 'scheduled',
    })
    setModalOpen(true)
  }

  const openEdit = (appt) => {
    setEditing(appt)
    form.setFieldsValue({
      client_id:      appt.client_id,
      treatment_name: appt.treatment_name,
      start_time:     dayjs(appt.start_time),
      end_time:       dayjs(appt.end_time),
      price:          appt.price,
      status:         appt.status,
      notes:          appt.notes,
    })
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setEditing(null)
    form.resetFields()
  }

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['appointments'] })
    qc.invalidateQueries({ queryKey: ['dashboard'] })
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      const payload = {
        ...values,
        start_time: values.start_time.toISOString(),
        end_time:   values.end_time.toISOString(),
      }
      if (editing) {
        await appointmentsApi.update(editing.id, payload)
        message.success('התור עודכן')
      } else {
        await appointmentsApi.create(payload)
        message.success('תור נוסף בהצלחה')
      }
      invalidate()
      closeModal()
    } catch (err) {
      if (err?.errorFields) return
      message.error(err.message || 'שגיאה בשמירת התור')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await appointmentsApi.delete(id)
      invalidate()
      message.success('התור נמחק')
    } catch (err) {
      message.error(err.message || 'שגיאה במחיקת תור')
    }
  }

  /* ── Table columns ────────────────────────────────────────── */

  const columns = [
    {
      title: 'שעה',
      dataIndex: 'start_time',
      width: 105,
      render: (t, r) => (
        <Text style={{ color: '#8b5cf6', fontWeight: 500 }}>
          {dayjs(t).format('HH:mm')} – {dayjs(r.end_time).format('HH:mm')}
        </Text>
      ),
    },
    {
      title: 'לקוחה',
      dataIndex: 'client_id',
      render: (id) => {
        const c = allClients.find((x) => x.id === id)
        return c ? <Text strong>{c.full_name}</Text> : <Text type="secondary">{id}</Text>
      },
    },
    {
      title: 'טיפול',
      dataIndex: 'treatment_name',
      render: (t) => <Text type="secondary">{t}</Text>,
    },
    {
      title: 'מחיר',
      dataIndex: 'price',
      width: 75,
      render: (p) =>
        p != null ? <Text style={{ color: '#10b981' }}>₪{p}</Text> : <Text type="secondary">—</Text>,
    },
    {
      title: 'סטטוס',
      dataIndex: 'status',
      width: 100,
      render: (s) => {
        const { label, color } = STATUS_MAP[s] || { label: s, color: 'default' }
        return <Tag color={color}>{label}</Tag>
      },
    },
    {
      title: '',
      key: 'actions',
      width: 80,
      render: (_, record) => (
        <Space>
          <Tooltip title="עריכה">
            <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
          </Tooltip>
          <Tooltip title="מחיקה">
            <Popconfirm
              title="למחוק את התור?"
              okText="מחק"
              cancelText="ביטול"
              okButtonProps={{ danger: true }}
              onConfirm={() => handleDelete(record.id)}
            >
              <Button size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ]

  /* ── Render ───────────────────────────────────────────────── */

  return (
    <div>
      {/* Page header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, fontWeight: 400, color: '#1c1833' }}>
          יומן תורים
        </Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          תור חדש
        </Button>
      </div>

      <Row gutter={[20, 20]} align="top">

        {/* ── Monthly Calendar ──────────────────────────────── */}
        <Col xs={24} lg={9}>
          <Card
            bordered={false}
            style={{
              borderRadius: 12,
              boxShadow: '0 2px 16px rgba(139, 92, 246, 0.08)',
              border: '1px solid rgba(139, 92, 246, 0.1)',
            }}
            bodyStyle={{ padding: 0 }}
          >
            <Calendar
              fullscreen={false}
              value={selectedDate}
              onSelect={(date, info) => {
                if (info?.source === 'date') selectDate(date)
              }}
              onPanelChange={(date) => setCalendarMonth(date.startOf('month'))}
              cellRender={cellRender}
              style={{ borderRadius: 12 }}
            />
          </Card>
        </Col>

        {/* ── Day View ──────────────────────────────────────── */}
        <Col xs={24} lg={15}>

          {/* Date navigation */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
            <Button
              icon={<RightOutlined />}
              onClick={() => selectDate(selectedDate.subtract(1, 'day'))}
            />
            <Text style={{ fontSize: 15, fontWeight: 400, color: '#374151', minWidth: 200 }}>
              {selectedDate.format('dddd, D בMMMM YYYY')}
            </Text>
            <Button
              icon={<LeftOutlined />}
              onClick={() => selectDate(selectedDate.add(1, 'day'))}
            />
            <Button
              onClick={() => selectDate(dayjs())}
              type={selectedDate.isSame(dayjs(), 'day') ? 'primary' : 'default'}
              size="small"
            >
              היום
            </Button>
          </div>

          {/* Appointments Table */}
          <Card
            bordered={false}
            style={{
              borderRadius: 12,
              boxShadow: '0 2px 16px rgba(0, 0, 0, 0.06)',
              border: '1px solid #f3f0ff',
            }}
            bodyStyle={{ padding: '12px 16px' }}
          >
            <Table
              dataSource={appointments}
              columns={columns}
              rowKey="id"
              loading={isLoading}
              pagination={false}
              size="small"
              locale={{
                emptyText: `אין תורים ביום ${selectedDate.format('D/M/YYYY')}`,
              }}
            />
          </Card>

        </Col>
      </Row>

      {/* ── Appointment Modal ────────────────────────────────── */}
      <Modal
        title={editing ? 'עריכת תור' : 'תור חדש'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={closeModal}
        okText={editing ? 'שמור שינויים' : 'צור תור'}
        cancelText="ביטול"
        confirmLoading={saving}
        width={540}
        destroyOnClose
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="client_id"
            label="לקוחה"
            rules={[{ required: true, message: 'יש לבחור לקוחה' }]}
          >
            <Select
              showSearch
              placeholder="חפשי לפי שם..."
              options={clientOptions}
              filterOption={(input, opt) =>
                opt.label.toLowerCase().includes(input.toLowerCase())
              }
            />
          </Form.Item>

          <Form.Item
            name="treatment_name"
            label="סוג טיפול"
            rules={[{ required: true, message: 'יש להזין סוג טיפול' }]}
          >
            <Input placeholder="ניקוי פנים, מיקרודרמהברזיה..." />
          </Form.Item>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item
                name="start_time"
                label="שעת התחלה"
                rules={[{ required: true, message: 'חובה' }]}
              >
                <DatePicker
                  showTime={{ format: 'HH:mm', minuteStep: 15 }}
                  format="DD/MM/YYYY HH:mm"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="end_time"
                label="שעת סיום"
                rules={[{ required: true, message: 'חובה' }]}
              >
                <DatePicker
                  showTime={{ format: 'HH:mm', minuteStep: 15 }}
                  format="DD/MM/YYYY HH:mm"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="price" label="מחיר (₪)">
                <InputNumber min={0} style={{ width: '100%' }} placeholder="150" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="status" label="סטטוס">
                <Select options={STATUS_OPTIONS} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="notes" label="הערות">
            <TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
