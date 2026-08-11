import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Table, Button, Tag, Typography, Modal, Descriptions, message, Popconfirm } from 'antd'
import { FileTextOutlined, EyeOutlined, DeleteOutlined } from '@ant-design/icons'
import { apiClient } from '../api/client'
import dayjs from 'dayjs'

const { Title } = Typography

async function fetchForms() {
  const res = await apiClient.get('/intake/forms')
  return res.data
}

async function fetchPdfUrl(formId) {
  const res = await apiClient.get(`/intake/forms/${formId}/pdf-url`)
  return res.data.url
}

export default function IntakeFormsPage() {
  const [detailForm, setDetailForm] = useState(null)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const qc = useQueryClient()

  const { data: forms = [], isLoading } = useQuery({
    queryKey: ['intake-forms'],
    queryFn: fetchForms,
  })

  const deleteForm = async (formId) => {
    setDeleting(formId)
    try {
      await apiClient.delete(`/intake/forms/${formId}`)
      message.success('הטופס נמחק')
      qc.invalidateQueries({ queryKey: ['intake-forms'] })
    } catch {
      message.error('שגיאה במחיקה')
    } finally {
      setDeleting(false)
    }
  }

  const openPdf = async (formId) => {
    setPdfLoading(formId)
    try {
      const url = await fetchPdfUrl(formId)
      window.open(url, '_blank')
    } catch {
      message.error('לא ניתן לטעון את ה-PDF')
    } finally {
      setPdfLoading(false)
    }
  }

  const columns = [
    {
      title: 'שם לקוח',
      render: (_, r) => r.clients?.full_name || `${r.submitted_first_name || ''} ${r.submitted_last_name || ''}`.trim() || '—',
    },
    {
      title: 'טלפון',
      render: (_, r) => r.clients?.phone || r.submitted_phone || '—',
    },
    {
      title: 'תאריך הגשה',
      dataIndex: 'created_at',
      render: (v) => dayjs(v).format('DD/MM/YYYY HH:mm'),
    },
    {
      title: 'לקוח חדש',
      dataIndex: 'auto_created_client',
      render: (v) => v ? <Tag color="blue">חדש</Tag> : <Tag color="default">קיים</Tag>,
    },
    {
      title: 'פעולות',
      render: (_, r) => (
        <div style={{ display: 'flex', gap: 8 }}>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => setDetailForm(r)}
          >
            פרטים
          </Button>
          {r.pdf_path && (
            <Button
              size="small"
              icon={<FileTextOutlined />}
              loading={pdfLoading === r.id}
              onClick={() => openPdf(r.id)}
            >
              PDF
            </Button>
          )}
          <Popconfirm
            title="למחוק את הטופס?"
            okText="מחק"
            cancelText="ביטול"
            okButtonProps={{ danger: true }}
            onConfirm={() => deleteForm(r.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />} loading={deleting === r.id} />
          </Popconfirm>
        </div>
      ),
    },
  ]

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>טפסי אנמנזה</Title>

      <Table
        dataSource={forms}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        scroll={{ x: 'max-content' }}
        pagination={{ pageSize: 20 }}
        locale={{ emptyText: 'אין טפסים עדיין' }}
      />

      <Modal
        open={!!detailForm}
        onCancel={() => setDetailForm(null)}
        footer={null}
        title="פרטי טופס"
        width="min(700px, 95vw)"
      >
        {detailForm && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="שם">
              {`${detailForm.submitted_first_name || ''} ${detailForm.submitted_last_name || ''}`.trim()}
            </Descriptions.Item>
            <Descriptions.Item label="טלפון">{detailForm.submitted_phone}</Descriptions.Item>
            <Descriptions.Item label="תאריך">{dayjs(detailForm.created_at).format('DD/MM/YYYY HH:mm')}</Descriptions.Item>
            <Descriptions.Item label="נתוני טופס">
              <pre style={{ fontSize: 12, maxHeight: 300, overflow: 'auto', margin: 0 }}>
                {JSON.stringify(detailForm.form_data, null, 2)}
              </pre>
            </Descriptions.Item>
            {detailForm.pdf_path && (
              <Descriptions.Item label="PDF">
                <Button
                  icon={<FileTextOutlined />}
                  loading={pdfLoading === detailForm.id}
                  onClick={() => openPdf(detailForm.id)}
                >
                  פתח PDF
                </Button>
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}
