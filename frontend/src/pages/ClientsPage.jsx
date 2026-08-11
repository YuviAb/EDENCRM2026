import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Table, Button, Modal, Form, Input, Select, DatePicker,
  Tag, Space, Typography, Popconfirm, message, Tooltip,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, FolderOpenOutlined } from '@ant-design/icons'
import { clientsApi } from '../api/clients'
import dayjs from 'dayjs'

const { Title } = Typography
const { TextArea } = Input
const { Search } = Input

const SKIN_TYPES = ['יבש', 'שמן', 'מעורב', 'רגיש', 'נורמלי']

export default function ClientsPage() {
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()
  const qc = useQueryClient()
  const navigate = useNavigate()

  const { data: clients = [], isLoading } = useQuery({
    queryKey: ['clients', search],
    queryFn: () => clientsApi.list({ search: search || undefined }),
  })

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setModalOpen(true)
  }

  const openEdit = (client) => {
    setEditing(client)
    form.setFieldsValue({
      full_name: client.full_name,
      phone: client.phone,
      email: client.email,
      date_of_birth: client.date_of_birth ? dayjs(client.date_of_birth) : null,
      skin_type: client.skin_type,
      allergies: client.allergies,
      medical_notes: client.medical_notes,
      referral_source: client.referral_source,
      general_notes: client.general_notes,
    })
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setEditing(null)
    form.resetFields()
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      const payload = {
        ...values,
        date_of_birth: values.date_of_birth ? values.date_of_birth.format('YYYY-MM-DD') : null,
      }
      if (editing) {
        await clientsApi.update(editing.id, payload)
        message.success('הפרטים עודכנו')
        qc.invalidateQueries({ queryKey: ['clients'] })
        closeModal()
      } else {
        const newClient = await clientsApi.create(payload)
        message.success('לקוחה נוספה בהצלחה')
        qc.invalidateQueries({ queryKey: ['clients'] })
        closeModal()
        navigate(`/clients/${newClient.id}`)
      }
    } catch (err) {
      if (err?.errorFields) return  // validation error - form handles display
      message.error(err.message || 'שגיאה בשמירה')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (clientId) => {
    try {
      await clientsApi.delete(clientId, false)
      qc.invalidateQueries({ queryKey: ['clients'] })
      message.success('לקוחה הוסרה מהמערכת')
    } catch (err) {
      if (err.response?.status === 409) {
        const detail = err.response.data?.detail || 'ללקוחה יש תורים עתידיים פתוחים'
        Modal.confirm({
          title: 'ישנם תורים עתידיים',
          content: detail,
          okText: 'מחק בכל זאת',
          cancelText: 'ביטול',
          okButtonProps: { danger: true },
          async onOk() {
            try {
              await clientsApi.delete(clientId, true)
              qc.invalidateQueries({ queryKey: ['clients'] })
              message.success('לקוחה נמחקה')
            } catch (e2) {
              message.error(e2.message || 'שגיאה במחיקה')
            }
          },
        })
      } else {
        message.error(err.message || 'שגיאה במחיקת לקוחה')
      }
    }
  }

  const columns = [
    {
      title: 'שם מלא',
      dataIndex: 'full_name',
      sorter: (a, b) => a.full_name.localeCompare(b.full_name),
      render: (name, record) => (
        <span>
          <a onClick={() => navigate(`/clients/${record.id}`)} style={{ fontWeight: 600 }}>{name}</a>
          {!record.is_active && (
            <Tag color="red" style={{ marginRight: 8 }}>לא פעיל</Tag>
          )}
        </span>
      ),
    },
    {
      title: 'טלפון',
      dataIndex: 'phone',
    },
    {
      title: 'אימייל',
      dataIndex: 'email',
      render: (e) => e || '—',
    },
    {
      title: 'סוג עור',
      dataIndex: 'skin_type',
      render: (s) => s || '—',
      responsive: ['md'],
    },
    {
      title: 'הצטרפות',
      dataIndex: 'created_at',
      render: (d) => dayjs(d).format('DD/MM/YYYY'),
      responsive: ['lg'],
    },
    {
      title: 'פעולות',
      key: 'actions',
      width: 130,
      render: (_, record) => (
        <Space>
          <Tooltip title="תיק לקוח">
            <Button
              size="small"
              icon={<FolderOpenOutlined />}
              onClick={() => navigate(`/clients/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="עריכה">
            <Button
              size="small"
              icon={<EditOutlined />}
              onClick={() => openEdit(record)}
            />
          </Tooltip>
          <Tooltip title="מחיקה">
            <Popconfirm
              title="למחוק את הלקוחה?"
              description="הלקוחה תסומן כלא פעילה (מחיקה רכה)"
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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
        <Title level={4} style={{ margin: 0 }}>לקוחות</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          לקוחה חדשה
        </Button>
      </div>

      <Search
        placeholder="חיפוש לפי שם או טלפון..."
        allowClear
        onSearch={setSearch}
        onChange={(e) => !e.target.value && setSearch('')}
        style={{ maxWidth: 360, marginBottom: 16 }}
      />

      <Table
        dataSource={clients}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        pagination={{ pageSize: 20, showTotal: (t) => `סה"כ ${t} לקוחות` }}
        locale={{ emptyText: search ? 'לא נמצאו לקוחות' : 'אין עדיין לקוחות במערכת' }}
        scroll={{ x: 'max-content' }}
      />

      <Modal
        title={editing ? `עריכת לקוחה — ${editing.full_name}` : 'לקוחה חדשה'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={closeModal}
        okText={editing ? 'שמור שינויים' : 'הוסף לקוחה'}
        cancelText="ביטול"
        confirmLoading={saving}
        width="min(600px, 95vw)"
        destroyOnClose
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="full_name"
            label="שם מלא"
            rules={[
              { required: true, message: 'שם מלא הוא שדה חובה' },
              { min: 2, message: 'שם חייב להכיל לפחות 2 תווים' },
            ]}
          >
            <Input placeholder="שרה כהן" />
          </Form.Item>

          <Form.Item
            name="phone"
            label="טלפון"
            rules={[
              { required: true, message: 'טלפון הוא שדה חובה' },
              { min: 9, message: 'מספר טלפון חייב להכיל לפחות 9 ספרות' },
            ]}
          >
            <Input placeholder="050-1234567" />
          </Form.Item>

          <Form.Item name="email" label="אימייל">
            <Input placeholder="sarah@example.com" type="email" />
          </Form.Item>

          <Form.Item name="date_of_birth" label="תאריך לידה">
            <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} placeholder="בחרי תאריך" />
          </Form.Item>

          <Form.Item name="skin_type" label="סוג עור">
            <Select allowClear placeholder="בחרי סוג עור" options={SKIN_TYPES.map((s) => ({ value: s, label: s }))} />
          </Form.Item>

          <Form.Item name="allergies" label="אלרגיות">
            <TextArea rows={2} placeholder="אלרגיות ידועות..." />
          </Form.Item>

          <Form.Item name="medical_notes" label="הערות רפואיות">
            <TextArea rows={2} placeholder="תרופות, הריון, רגישויות..." />
          </Form.Item>

          <Form.Item name="referral_source" label="מקור הגעה">
            <Input placeholder="אינסטגרם, חברה, גוגל..." />
          </Form.Item>

          <Form.Item name="general_notes" label="הערות כלליות">
            <TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
