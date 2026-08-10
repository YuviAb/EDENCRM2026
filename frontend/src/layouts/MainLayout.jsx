import { useState } from 'react'
import { ConfigProvider, Layout, Menu, Drawer, Button, Grid, Popconfirm } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined, TeamOutlined, CalendarOutlined,
  DollarOutlined, MenuOutlined, LogoutOutlined, FileTextOutlined,
} from '@ant-design/icons'
import { authApi } from '../api/auth'

const { Sider, Content } = Layout
const { useBreakpoint }  = Grid

const SIDEBAR_BG = 'linear-gradient(180deg, #13111f 0%, #1c1833 50%, #221e42 100%)'

const menuItems = [
  { key: '/',         icon: <DashboardOutlined />, label: 'לוח בקרה'   },
  { key: '/clients',  icon: <TeamOutlined />,      label: 'לקוחות'      },
  { key: '/calendar', icon: <CalendarOutlined />,  label: 'יומן תורים'  },
  { key: '/payments', icon: <DollarOutlined />,    label: 'תשלומים'     },
  { key: '/intake',   icon: <FileTextOutlined />,  label: 'טפסי אנמנזה' },
]

function LogoutButton() {
  const navigate = useNavigate()
  const handleLogout = () => {
    authApi.logout()
    navigate('/login', { replace: true })
  }
  return (
    <div style={{ padding: '16px 12px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
      <Popconfirm
        title="להתנתק מהמערכת?"
        okText="התנתק"
        cancelText="ביטול"
        okButtonProps={{ danger: true }}
        onConfirm={handleLogout}
        placement="top"
      >
        <Button
          type="text"
          icon={<LogoutOutlined />}
          style={{
            width: '100%', textAlign: 'right', color: 'rgba(255,255,255,0.35)',
            fontSize: 13,
          }}
        >
          התנתקות
        </Button>
      </Popconfirm>
    </div>
  )
}

function SidebarLogo() {
  return (
    <div style={{
      padding: '32px 20px 24px', textAlign: 'center',
      borderBottom: '1px solid rgba(255,255,255,0.05)', marginBottom: 12,
    }}>
      <div style={{
        width: 42, height: 42, borderRadius: '50%',
        border: '1px solid rgba(255,215,0,0.35)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        margin: '0 auto 18px',
        color: 'rgba(255,215,0,0.7)', fontSize: 16, fontWeight: 300, letterSpacing: 1,
      }}>E</div>
      <span style={{
        display: 'block', color: 'rgba(255,255,255,0.88)',
        fontSize: 15, fontWeight: 300, letterSpacing: 7, marginBottom: 5,
      }}>EDEN</span>
      <span style={{
        display: 'block', color: 'rgba(255,255,255,0.28)',
        fontSize: 8, fontWeight: 400, letterSpacing: 4,
      }}>COSMETICS</span>
    </div>
  )
}

function NavMenu({ onSelect }) {
  const navigate     = useNavigate()
  const { pathname } = useLocation()
  return (
    <ConfigProvider theme={{ components: { Menu: {
      darkItemBg:            'transparent',
      darkSubMenuItemBg:     'transparent',
      darkItemColor:         'rgba(255,255,255,0.55)',
      darkItemHoverColor:    'rgba(255,255,255,0.85)',
      darkItemHoverBg:       'rgba(255,255,255,0.07)',
      darkItemSelectedColor: '#ffffff',
      darkItemSelectedBg:    'rgba(139,92,246,0.22)',
    }}}}>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[pathname]}
        items={menuItems}
        onClick={({ key }) => { navigate(key); onSelect?.() }}
        className="eden-menu"
        style={{ background: 'transparent', border: 'none', fontSize: 13.5 }}
      />
    </ConfigProvider>
  )
}

export default function MainLayout() {
  const screens  = useBreakpoint()
  const isMobile = screens.md === false
  const [open, setOpen] = useState(false)

  return (
    <Layout style={{ minHeight: '100vh', flexDirection: isMobile ? 'column' : 'row-reverse' }}>

      {/* ── Mobile header bar ───────────────────────── */}
      {isMobile && (
        <div style={{
          background: '#13111f',
          padding: '0 16px',
          height: 52,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          position: 'sticky', top: 0, zIndex: 200,
          boxShadow: '0 2px 12px rgba(0,0,0,0.35)',
        }}>
          <span style={{
            color: 'rgba(255,255,255,0.88)', fontSize: 11,
            fontWeight: 300, letterSpacing: 5,
          }}>
            EDEN COSMETICS
          </span>
          <Button
            type="text"
            icon={<MenuOutlined style={{ color: '#fff', fontSize: 20 }} />}
            onClick={() => setOpen(true)}
          />
        </div>
      )}

      {/* ── Desktop sidebar ─────────────────────────── */}
      {!isMobile && (
        <Sider width={220} style={{
          background: SIDEBAR_BG,
          height: '100vh', position: 'sticky', top: 0,
          overflow: 'auto',
          boxShadow: '-2px 0 20px rgba(0,0,0,0.25)',
          display: 'flex', flexDirection: 'column',
        }}>
          <div style={{ flex: 1 }}>
            <SidebarLogo />
            <NavMenu />
          </div>
          <LogoutButton />
        </Sider>
      )}

      {/* ── Mobile drawer ───────────────────────────── */}
      <Drawer
        open={isMobile && open}
        onClose={() => setOpen(false)}
        placement="right"
        width={220}
        styles={{ header: { display: 'none' }, body: { padding: 0 } }}
      >
        <div style={{ background: SIDEBAR_BG, minHeight: '100%', display: 'flex', flexDirection: 'column' }}>
          <div style={{ flex: 1 }}>
            <SidebarLogo />
            <NavMenu onSelect={() => setOpen(false)} />
          </div>
          <LogoutButton />
        </div>
      </Drawer>

      {/* ── Page content ────────────────────────────── */}
      <Layout style={{ background: '#f8f6ff', flex: 1 }}>
        <Content style={{
          padding:   isMobile ? '16px 12px' : '36px 32px',
          minHeight: isMobile ? 'calc(100vh - 52px)' : '100vh',
        }}>
          <Outlet />
        </Content>
      </Layout>

    </Layout>
  )
}
