import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Alert } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { authApi } from '../api/auth'

export default function LoginPage() {
  const navigate       = useNavigate()
  const [loading, setLoading]   = useState(false)
  const [error,   setError]     = useState(null)

  const handleLogin = async ({ username, password }) => {
    setLoading(true)
    setError(null)
    try {
      await authApi.login(username, password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.response?.data?.detail || 'שגיאה בהתחברות')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #13111f 0%, #1c1833 50%, #221e42 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24,
    }}>
      <div style={{
        width: '100%',
        maxWidth: 360,
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 16,
        padding: '40px 32px',
        backdropFilter: 'blur(12px)',
        boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
      }}>

        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 36 }}>
          <div style={{
            width: 52, height: 52, borderRadius: '50%',
            border: '1px solid rgba(255,215,0,0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px',
            color: 'rgba(255,215,0,0.75)', fontSize: 20, fontWeight: 300,
          }}>E</div>
          <div style={{
            color: 'rgba(255,255,255,0.9)', fontSize: 16,
            fontWeight: 300, letterSpacing: 8, marginBottom: 4,
          }}>EDEN</div>
          <div style={{
            color: 'rgba(255,255,255,0.25)', fontSize: 9,
            fontWeight: 400, letterSpacing: 4,
          }}>COSMETICS</div>
        </div>

        <p style={{
          color: 'rgba(255,255,255,0.35)', fontSize: 12,
          textAlign: 'center', marginBottom: 24, letterSpacing: 0.5,
        }}>
          כניסה למערכת ניהול
        </p>

        {error && (
          <Alert
            type="error"
            message={error}
            style={{ marginBottom: 20, borderRadius: 8 }}
            showIcon
          />
        )}

        <Form
          layout="vertical"
          onFinish={handleLogin}
          autoComplete="off"
          requiredMark={false}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'יש להזין שם משתמש' }]}
          >
            <Input
              prefix={<UserOutlined style={{ color: 'rgba(255,255,255,0.3)' }} />}
              placeholder="שם משתמש"
              size="large"
              style={{
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 8,
                color: '#fff',
              }}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'יש להזין סיסמה' }]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: 'rgba(255,255,255,0.3)' }} />}
              placeholder="סיסמה"
              size="large"
              style={{
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 8,
                color: '#fff',
              }}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, marginTop: 8 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
              style={{
                background: 'linear-gradient(90deg, #7c3aed, #8b5cf6)',
                border: 'none',
                borderRadius: 8,
                height: 44,
                fontSize: 14,
                fontWeight: 400,
                letterSpacing: 1,
              }}
            >
              כניסה
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  )
}
