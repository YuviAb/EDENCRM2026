import { ConfigProvider, Layout, Menu } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  TeamOutlined,
  CalendarOutlined,
  DollarOutlined,
} from '@ant-design/icons'

const { Sider, Content } = Layout

const menuItems = [
  { key: '/',         icon: <DashboardOutlined />, label: 'לוח בקרה' },
  { key: '/clients',  icon: <TeamOutlined />,      label: 'לקוחות' },
  { key: '/calendar', icon: <CalendarOutlined />,  label: 'יומן תורים' },
  { key: '/payments', icon: <DollarOutlined />,    label: 'תשלומים' },
]

export default function MainLayout() {
  const navigate      = useNavigate()
  const { pathname }  = useLocation()

  return (
    <Layout style={{ minHeight: '100vh', flexDirection: 'row-reverse' }}>

      {/* ── Sidebar ─────────────────────────────────────── */}
      <Sider
        width={220}
        style={{
          background: 'linear-gradient(180deg, #13111f 0%, #1c1833 50%, #221e42 100%)',
          height: '100vh',
          position: 'sticky',
          top: 0,
          overflow: 'auto',
          boxShadow: '-2px 0 20px rgba(0, 0, 0, 0.25)',
        }}
      >
        {/* Logo */}
        <div
          style={{
            padding: '32px 20px 24px',
            textAlign: 'center',
            borderBottom: '1px solid rgba(255,255,255,0.05)',
            marginBottom: 12,
          }}
        >
          {/* Monogram */}
          <div
            style={{
              width: 42,
              height: 42,
              borderRadius: '50%',
              border: '1px solid rgba(255,215,0,0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 18px',
              color: 'rgba(255,215,0,0.7)',
              fontSize: 16,
              fontWeight: 300,
              letterSpacing: 1,
            }}
          >
            E
          </div>

          {/* Brand name */}
          <span
            style={{
              display: 'block',
              color: 'rgba(255,255,255,0.88)',
              fontSize: 15,
              fontWeight: 300,
              letterSpacing: 7,
              marginBottom: 5,
            }}
          >
            EDEN
          </span>
          <span
            style={{
              display: 'block',
              color: 'rgba(255,255,255,0.28)',
              fontSize: 8,
              fontWeight: 400,
              letterSpacing: 4,
            }}
          >
            COSMETICS
          </span>
        </div>

        {/* Navigation */}
        <ConfigProvider
          theme={{
            components: {
              Menu: {
                darkItemBg:           'transparent',
                darkSubMenuItemBg:    'transparent',
                darkItemColor:        'rgba(255,255,255,0.55)',
                darkItemHoverColor:   'rgba(255,255,255,0.85)',
                darkItemHoverBg:      'rgba(255,255,255,0.07)',
                darkItemSelectedColor: '#ffffff',
                darkItemSelectedBg:   'rgba(139,92,246,0.22)',
              },
            },
          }}
        >
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            className="eden-menu"
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: 13.5,
            }}
          />
        </ConfigProvider>
      </Sider>

      {/* ── Content ──────────────────────────────────────── */}
      <Layout style={{ background: '#f8f6ff', flex: 1 }}>
        <Content style={{ padding: '36px 32px', minHeight: '100vh' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
