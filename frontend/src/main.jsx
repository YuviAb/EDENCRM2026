import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider, App as AntApp } from 'antd'
import heIL from 'antd/locale/he_IL'
import dayjs from 'dayjs'
import 'dayjs/locale/he'
import App from './App.jsx'
import './index.css'

dayjs.locale('he')

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        direction="rtl"
        locale={heIL}
        theme={{
          token: {
            colorPrimary: '#8b5cf6',
            colorLink: '#8b5cf6',
            fontFamily: "'Noto Sans Hebrew', 'Inter', sans-serif",
            borderRadius: 8,
            colorBgContainer: '#ffffff',
            colorBgLayout: '#f8f6ff',
            fontWeightStrong: 500,
          },
          components: {
            Layout: {
              siderBg: 'transparent',
            },
            Table: {
              headerBg: '#faf8ff',
              headerColor: '#6b7280',
            },
          },
        }}
      >
        <AntApp>
          <App />
        </AntApp>
      </ConfigProvider>
    </QueryClientProvider>
  </React.StrictMode>,
)
