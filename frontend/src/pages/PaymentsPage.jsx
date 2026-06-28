import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Table, Button, Modal, Form, Select, InputNumber,
  DatePicker, Tag, Space, Typography, Popconfirm, message, Tooltip,
} from 'antd'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import { paymentsApi } from '../api/payments'
import { clientsApi } from '../api/clients'
import { appointmentsApi } from '../api/appointments'
import dayjs from 'dayjs'

const { Title, Text } = Typography

const METHOD_MAP = {
  cash: { label: 'מזומן', color: 'green' },
  credit_card: { label: 'אשראי', color: 'blue' },
  bit: { label: 'ביט', color: 'purple' },
  bank_transfer: { label: 'העברה', color: 'cyan' },
  other: { label: 'אחר', color: 'default' },
}

const METHOD_OPTIONS = Object.entries(METHOD_MAP).map(([value, { label }]) => ({ value, label }))

export default function PaymentsPage() {
  const [filterClientId, setFilterClientId] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [selectedClientId, setSelectedClientId] = useState(null)
  const [form] = Form.useForm()
  const qc = useQueryClient()

  const { data: payments = [], isLoading } = useQuery({
    queryKey: ['payments', filterClientId],
    queryFn: () => paymentsApi.list({ client_id: filterClientId || undefined }),
  })

  const { data: allClients = [] } = useQuery({
    queryKey: ['clients', ''],
    queryFn: () => clientsApi.list(),
  })

  const { data: clientAppointments = [] } = useQuery({
    queryKey: ['appointments-for-client', selectedClientId],
    queryFn: () => appointmentsApi.list({ client_id: selectedClientId }),
    enabled: !!selectedClientId,
  })

  const clientOptions = allClients.map((c) => ({ value: c.id, label: `${c.full_name} · ${c.phone}` }))

  const appointmentOptions = clientAppointments.map((a) => ({
    value: a.id,
    label: `${dayjs(a.start_time).format('DD/MM/YYYY HH:mm')} — ${a.treatment_name}`,
  }))

  const openCreate = () => {
    setSelectedClientId(null)
    form.resetFields()
    form.setFieldsValue({ paid_at: dayjs(), method: 'cash' })
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setSelectedClientId(null)
    form.resetFields()
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      await paymentsApi.create({
        ...values,
        paid_at: values.paid_at.toISOString(),
      })
      message.success('תשלום נרשם בהצלחה')
      qc.invalidateQueries({ queryKey: ['payments'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      closeModal()
    } catch (err) {
      if (err?.errorFields) return
      message.error(err.message || 'שגיאה ברישום תשלום')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await paymentsApi.delete(id)
      qc.invalidateQueries({ queryKey: ['payments'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      message.success('תשלום נמחק')
    } catch (err) {
      message.error(err.message || 'שגיאה במחיקת תשלום')
    }
  }

  const columns = [
    {
      title: 'תאריך',
      dataIndex: 'paid_at',
      defaultSortOrder: 'descend',
      sorter: (a, b) => dayjs(a.paid_at).unix() - dayjs(b.paid_at).unix(),
      render: (d) => dayjs(d).format('DD/MM/YYYY HH:mm'),
    },
    {
      title: 'לקוחה',
      dataIndex: 'client_id',
      render: (id) => {
        const client = allClients.find((c) => c.id === id)
        return client ? <Text strong>{client.full_name}</Text> : id
      },
    },
    {
      title: 'סכום',
      dataIndex: 'amount',
      render: (a) => <Text strong style={{ color: '#16a34a' }}>{`₪${a}`}</Text>,
    },
    {
      title: 'אמצעי תשלום',
      dataIndex: 'method',
      render: (m) => {
        const { label, color } = METHOD_MAP[m] || { label: m, color: 'default' }
        return <Tag color={color}>{label}</Tag>
      },
    },
    {
      title: 'הערות',
      dataIndex: 'notes',
      render: (n) => n || '—',
      responsive: ['md'],
    },
    {
      title: 'פעולות',
      key: 'actions',
      width: 70,
      render: (_, record) => (
        <Tooltip title="מחיקה">
          <Popconfirm
            title="למחוק את התשלום?"
            okText="מחק"
            cancelText="ביטול"
            okButtonProps={{ danger: true }}
            onConfirm={() => handleDelete(record.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Tooltip>
      ),
    },
  ]

  const total = payments.reduce((sum, p) => sum + p.amount, 0)

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <Title level={3} style={{ margin: 0 }}>תשלומים</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          רשום תשלום
        </Button>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="סינון לפי לקוחה"
          options={clientOptions}
          onChange={setFilterClientId}
          style={{ minWidth: 240 }}
          showSearch
          filterOption={(input, opt) => opt.label.toLowerCase().includes(input.toLowerCase())}
        />
        {payments.length > 0 && (
          <Text type="secondary" style={{ lineHeight: '32px' }}>
            סה"כ: <Text strong style={{ color: '#16a34a' }}>₪{total.toLocaleString()}</Text>
            {' '}({payments.length} תשלומים)
          </Text>
        )}
      </div>

      <Table
        dataSource={payments}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        pagination={{ pageSize: 25, showTotal: (t) => `סה"כ ${t} תשלומים` }}
        locale={{ emptyText: 'אין תשלומים רשומים' }}
      />

      <Modal
        title="רישום תשלום"
        open={modalOpen}
        onOk={handleSave}
        onCancel={closeModal}
        okText="שמור תשלום"
        cancelText="ביטול"
        confirmLoading={saving}
        width={480}
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
              filterOption={(input, opt) => opt.label.toLowerCase().includes(input.toLowerCase())}
              onChange={(val) => {
                setSelectedClientId(val)
                form.setFieldValue('appointment_id', undefined)
              }}
            />
          </Form.Item>

          <Form.Item name="appointment_id" label="תור קשור (אופציונלי)">
            <Select
              allowClear
              placeholder="בחרי תור..."
              options={appointmentOptions}
              disabled={!selectedClientId}
              notFoundContent={selectedClientId ? 'אין תורים ללקוחה זו' : 'בחרי לקוחה קודם'}
            />
          </Form.Item>

          <Form.Item
            name="amount"
            label="סכום (₪)"
            rules={[{ required: true, message: 'יש להזין סכום' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} placeholder="200" />
          </Form.Item>

          <Form.Item name="method" label="אמצעי תשלום">
            <Select options={METHOD_OPTIONS} />
          </Form.Item>

          <Form.Item
            name="paid_at"
            label="תאריך ושעת תשלום"
            rules={[{ required: true, message: 'יש לבחור תאריך' }]}
          >
            <DatePicker
              showTime={{ format: 'HH:mm' }}
              format="DD/MM/YYYY HH:mm"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
