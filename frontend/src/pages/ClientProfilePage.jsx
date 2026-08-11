import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Tabs, Form, Input, Select, DatePicker, Button, Table, Modal,
  Upload, Image, Tag, Space, Typography, message, Popconfirm, Spin,
  Card, Descriptions,
} from 'antd'
import {
  ArrowRightOutlined, EditOutlined, DeleteOutlined, PlusOutlined,
  UploadOutlined, PictureOutlined, VideoCameraOutlined,
} from '@ant-design/icons'
import { apiClient } from '../api/client'
import { clientsApi } from '../api/clients'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { TextArea } = Input

const SKIN_TYPES = ['יבש', 'שמן', 'מעורב', 'רגיש', 'נורמלי']
const TREATMENT_TYPES = [
  'פנים', 'מיצוק', 'לייזר', 'פילינג', 'מסכה', 'הזרקה', 'בוטוקס',
  'פלזמה', 'RF', 'הידרה', 'ניקוי עמוק', 'אחר',
]

// ── API helpers ────────────────────────────────────────────────────────
const api = {
  getClient:        (id) => apiClient.get(`/clients/${id}`).then(r => r.data),
  getTreatments:    (id) => apiClient.get(`/clients/${id}/treatments`).then(r => r.data),
  addTreatment:     (id, d) => apiClient.post(`/clients/${id}/treatments`, d).then(r => r.data),
  updateTreatment:  (cid, tid, d) => apiClient.patch(`/clients/${cid}/treatments/${tid}`, d).then(r => r.data),
  deleteTreatment:  (cid, tid) => apiClient.delete(`/clients/${cid}/treatments/${tid}`),
  getMedia:         (id) => apiClient.get(`/clients/${id}/media`).then(r => r.data),
  deleteMedia:      (cid, mid) => apiClient.delete(`/clients/${cid}/media/${mid}`),
}

// ── Details Tab ────────────────────────────────────────────────────────
function DetailsTab({ client, clientId, onUpdated }) {
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()

  const startEdit = () => {
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
    setEditing(true)
  }

  const save = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      await clientsApi.update(clientId, {
        ...values,
        date_of_birth: values.date_of_birth ? values.date_of_birth.format('YYYY-MM-DD') : null,
      })
      message.success('הפרטים עודכנו')
      setEditing(false)
      onUpdated()
    } catch (err) {
      if (!err?.errorFields) message.error('שגיאה בשמירה')
    } finally {
      setSaving(false)
    }
  }

  if (editing) {
    return (
      <Form form={form} layout="vertical" style={{ maxWidth: 500 }}>
        <Form.Item name="full_name" label="שם מלא" rules={[{ required: true, min: 2 }]}>
          <Input />
        </Form.Item>
        <Form.Item name="phone" label="טלפון" rules={[{ required: true, min: 9 }]}>
          <Input />
        </Form.Item>
        <Form.Item name="email" label="אימייל">
          <Input type="email" />
        </Form.Item>
        <Form.Item name="date_of_birth" label="תאריך לידה">
          <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item name="skin_type" label="סוג עור">
          <Select allowClear options={SKIN_TYPES.map(s => ({ value: s, label: s }))} />
        </Form.Item>
        <Form.Item name="allergies" label="אלרגיות">
          <TextArea rows={2} />
        </Form.Item>
        <Form.Item name="medical_notes" label="הערות רפואיות">
          <TextArea rows={2} />
        </Form.Item>
        <Form.Item name="referral_source" label="מקור הגעה">
          <Input />
        </Form.Item>
        <Form.Item name="general_notes" label="הערות כלליות">
          <TextArea rows={2} />
        </Form.Item>
        <Space>
          <Button type="primary" onClick={save} loading={saving}>שמור</Button>
          <Button onClick={() => setEditing(false)}>ביטול</Button>
        </Space>
      </Form>
    )
  }

  return (
    <div>
      <Button icon={<EditOutlined />} onClick={startEdit} style={{ marginBottom: 16 }}>
        ערוך פרטים
      </Button>
      <Descriptions column={1} bordered size="small" style={{ maxWidth: 500 }}>
        <Descriptions.Item label="שם מלא">{client.full_name}</Descriptions.Item>
        <Descriptions.Item label="טלפון">{client.phone || '—'}</Descriptions.Item>
        <Descriptions.Item label="אימייל">{client.email || '—'}</Descriptions.Item>
        <Descriptions.Item label="תאריך לידה">
          {client.date_of_birth ? dayjs(client.date_of_birth).format('DD/MM/YYYY') : '—'}
        </Descriptions.Item>
        <Descriptions.Item label="סוג עור">{client.skin_type || '—'}</Descriptions.Item>
        <Descriptions.Item label="אלרגיות">{client.allergies || '—'}</Descriptions.Item>
        <Descriptions.Item label="הערות רפואיות">{client.medical_notes || '—'}</Descriptions.Item>
        <Descriptions.Item label="מקור הגעה">{client.referral_source || '—'}</Descriptions.Item>
        <Descriptions.Item label="הערות">{client.general_notes || '—'}</Descriptions.Item>
        <Descriptions.Item label="הצטרפות">
          {dayjs(client.created_at).format('DD/MM/YYYY')}
        </Descriptions.Item>
      </Descriptions>
    </div>
  )
}

// ── Treatments Tab ─────────────────────────────────────────────────────
function TreatmentsTab({ clientId }) {
  const qc = useQueryClient()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()

  const { data: treatments = [], isLoading } = useQuery({
    queryKey: ['treatments', clientId],
    queryFn: () => api.getTreatments(clientId),
  })

  const openAdd = () => { setEditing(null); form.resetFields(); setModalOpen(true) }
  const openEdit = (t) => {
    setEditing(t)
    form.setFieldsValue({
      treatment_date: dayjs(t.treatment_date),
      treatment_type: t.treatment_type,
      notes: t.notes,
    })
    setModalOpen(true)
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      const payload = { ...values, treatment_date: values.treatment_date.format('YYYY-MM-DD') }
      if (editing) {
        await api.updateTreatment(clientId, editing.id, payload)
        message.success('טיפול עודכן')
      } else {
        await api.addTreatment(clientId, payload)
        message.success('טיפול נוסף')
      }
      qc.invalidateQueries({ queryKey: ['treatments', clientId] })
      setModalOpen(false)
    } catch (err) {
      if (!err?.errorFields) message.error('שגיאה בשמירה')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await api.deleteTreatment(clientId, id)
      qc.invalidateQueries({ queryKey: ['treatments', clientId] })
      message.success('טיפול נמחק')
    } catch { message.error('שגיאה במחיקה') }
  }

  const columns = [
    { title: 'תאריך', dataIndex: 'treatment_date', render: d => dayjs(d).format('DD/MM/YYYY'), sorter: (a,b) => a.treatment_date.localeCompare(b.treatment_date) },
    { title: 'סוג טיפול', dataIndex: 'treatment_type' },
    { title: 'הערות', dataIndex: 'notes', render: n => n || '—' },
    {
      title: '', width: 80,
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="למחוק?" okText="מחק" cancelText="ביטול" okButtonProps={{ danger: true }} onConfirm={() => handleDelete(r.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Button type="primary" icon={<PlusOutlined />} onClick={openAdd} style={{ marginBottom: 16 }}>
        הוסף טיפול
      </Button>
      <Table
        dataSource={treatments} columns={columns} rowKey="id"
        loading={isLoading} pagination={{ pageSize: 20 }}
        locale={{ emptyText: 'אין טיפולים עדיין' }}
        defaultSortOrder="descend"
      />
      <Modal
        open={modalOpen} onOk={handleSave} onCancel={() => setModalOpen(false)}
        okText={editing ? 'עדכן' : 'הוסף'} cancelText="ביטול"
        confirmLoading={saving} title={editing ? 'עריכת טיפול' : 'טיפול חדש'} destroyOnClose
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="treatment_date" label="תאריך" rules={[{ required: true }]}>
            <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="treatment_type" label="סוג טיפול" rules={[{ required: true }]}>
            <Select showSearch options={TREATMENT_TYPES.map(t => ({ value: t, label: t }))} />
          </Form.Item>
          <Form.Item name="notes" label="הערות">
            <TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

// ── Media Tab ──────────────────────────────────────────────────────────
function MediaTab({ clientId }) {
  const qc = useQueryClient()
  const [uploading, setUploading] = useState(false)

  const { data: media = [], isLoading } = useQuery({
    queryKey: ['media', clientId],
    queryFn: () => api.getMedia(clientId),
  })

  const handleUpload = async ({ file }) => {
    const isVideo = file.type.startsWith('video/')
    const formData = new FormData()
    formData.append('file', file)
    formData.append('media_type', isVideo ? 'video' : 'image')
    setUploading(true)
    try {
      await apiClient.post(`/clients/${clientId}/media`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      qc.invalidateQueries({ queryKey: ['media', clientId] })
      message.success('הקובץ הועלה')
    } catch { message.error('שגיאה בהעלאה') }
    finally { setUploading(false) }
    return false
  }

  const handleDelete = async (id) => {
    try {
      await api.deleteMedia(clientId, id)
      qc.invalidateQueries({ queryKey: ['media', clientId] })
      message.success('נמחק')
    } catch { message.error('שגיאה במחיקה') }
  }

  return (
    <div>
      <Upload
        accept="image/*,video/*"
        showUploadList={false}
        customRequest={handleUpload}
        multiple
      >
        <Button icon={<UploadOutlined />} loading={uploading} style={{ marginBottom: 16 }}>
          העלה תמונה / סרטון
        </Button>
      </Upload>

      {isLoading ? <Spin /> : media.length === 0 ? (
        <Text type="secondary">אין מדיה עדיין</Text>
      ) : (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
          {media.map(item => (
            <Card
              key={item.id}
              style={{ width: 160 }}
              bodyStyle={{ padding: 8 }}
              cover={
                item.media_type === 'video' ? (
                  <video
                    src={item.public_url}
                    style={{ width: '100%', height: 120, objectFit: 'cover', display: 'block' }}
                    controls
                  />
                ) : (
                  <Image
                    src={item.public_url}
                    alt={item.caption || ''}
                    style={{ width: '100%', height: 120, objectFit: 'cover' }}
                    preview
                  />
                )
              }
              actions={[
                <Popconfirm
                  key="del"
                  title="למחוק?" okText="מחק" cancelText="ביטול" okButtonProps={{ danger: true }}
                  onConfirm={() => handleDelete(item.id)}
                >
                  <DeleteOutlined style={{ color: '#ff4d4f' }} />
                </Popconfirm>,
              ]}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                {item.media_type === 'video' ? <VideoCameraOutlined /> : <PictureOutlined />}
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {dayjs(item.created_at).format('DD/MM/YY')}
                </Text>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Main Page ──────────────────────────────────────────────────────────
export default function ClientProfilePage() {
  const { clientId } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: client, isLoading } = useQuery({
    queryKey: ['client', clientId],
    queryFn: () => api.getClient(clientId),
  })

  if (isLoading) return <Spin style={{ display: 'block', marginTop: 60 }} />
  if (!client) return <Text type="danger">לקוח לא נמצא</Text>

  const tabs = [
    { key: 'details', label: 'פרטים', children: <DetailsTab client={client} clientId={clientId} onUpdated={() => qc.invalidateQueries({ queryKey: ['client', clientId] })} /> },
    { key: 'treatments', label: 'היסטוריית טיפולים', children: <TreatmentsTab clientId={clientId} /> },
    { key: 'media', label: 'תמונות וסרטונים', children: <MediaTab clientId={clientId} /> },
  ]

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <Button icon={<ArrowRightOutlined />} onClick={() => navigate('/clients')} />
        <Title level={4} style={{ margin: 0 }}>{client.full_name}</Title>
        {!client.is_active && <Tag color="red">לא פעיל</Tag>}
        <Tag color={client.is_active ? 'green' : 'default'}>{client.phone}</Tag>
      </div>
      <Tabs items={tabs} />
    </div>
  )
}
