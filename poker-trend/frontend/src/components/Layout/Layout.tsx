import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Layout as AntLayout,
  Menu,
  Avatar,
  Dropdown,
  Button,
  Typography,
  Badge,
  Space,
} from 'antd';
import {
  DashboardOutlined,
  TrendingUpOutlined,
  PlayCircleOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../hooks/useAuth';
import toast from 'react-hot-toast';

const { Header, Sider, Content } = AntLayout;
const { Text } = Typography;

const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '대시보드',
    },
    {
      key: '/trends',
      icon: <TrendingUpOutlined />,
      label: '트렌드 모니터링',
    },
    {
      key: '/content',
      icon: <PlayCircleOutlined />,
      label: '콘텐츠 생성',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: '분석',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '설정',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('로그아웃되었습니다.');
      navigate('/login');
    } catch (error) {
      toast.error('로그아웃 중 오류가 발생했습니다.');
    }
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '프로필',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '설정',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '로그아웃',
      onClick: handleLogout,
    },
  ];

  return (
    <AntLayout className="min-h-screen">
      {/* 사이드바 */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        theme="light"
        className="shadow-lg"
        width={256}
      >
        {/* 로고 */}
        <div className="h-16 flex items-center justify-center border-b border-gray-200">
          {collapsed ? (
            <TrophyOutlined className="text-xl text-blue-600" />
          ) : (
            <Space>
              <TrophyOutlined className="text-xl text-blue-600" />
              <Text strong className="text-lg">
                Poker Trend
              </Text>
            </Space>
          )}
        </div>

        {/* 메뉴 */}
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          className="border-r-0 mt-4"
        />
      </Sider>

      {/* 메인 레이아웃 */}
      <AntLayout>
        {/* 헤더 */}
        <Header className="bg-white shadow-sm px-4 flex items-center justify-between">
          <div className="flex items-center">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="mr-4"
            />
          </div>

          <div className="flex items-center space-x-4">
            {/* 알림 */}
            <Badge count={3} size="small">
              <Button
                type="text"
                icon={<BellOutlined />}
                className="text-gray-600"
              />
            </Badge>

            {/* 사용자 메뉴 */}
            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              arrow
            >
              <div className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 px-2 py-1 rounded">
                <Avatar
                  size="small"
                  icon={<UserOutlined />}
                  src={user?.avatar}
                />
                <div className="hidden sm:block">
                  <Text className="text-sm font-medium">
                    {user?.username || 'Admin'}
                  </Text>
                  <br />
                  <Text type="secondary" className="text-xs">
                    {user?.role || 'Administrator'}
                  </Text>
                </div>
              </div>
            </Dropdown>
          </div>
        </Header>

        {/* 콘텐츠 */}
        <Content className="bg-gray-50 min-h-[calc(100vh-64px)] overflow-auto">
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;