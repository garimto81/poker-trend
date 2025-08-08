import React, { useState } from 'react';
import { Card, Form, Input, Button, Typography, Alert, Space } from 'antd';
import { UserOutlined, LockOutlined, TrophyOutlined } from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';
import { USE_MOCK_DATA } from '../config/api';
import toast from 'react-hot-toast';

const { Title, Text } = Typography;

interface LoginForm {
  username: string;
  password: string;
}

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const onFinish = async (values: LoginForm) => {
    try {
      setLoading(true);
      await login(values.username, values.password);
      toast.success('로그인 성공!');
    } catch (error) {
      toast.error('로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* 로고 및 제목 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <TrophyOutlined className="text-2xl text-white" />
          </div>
          <Title level={2} className="mb-2">
            Poker Trend
          </Title>
          <Text type="secondary">
            포커 트렌드 쇼츠 자동 제작 시스템
          </Text>
        </div>

        {/* 로그인 카드 */}
        <Card className="shadow-lg">
          {USE_MOCK_DATA && (
            <Alert
              message="데모 모드"
              description="GitHub Pages 데모 버전입니다. 아래 계정으로 로그인해주세요."
              type="info"
              showIcon
              className="mb-6"
            />
          )}

          <Form
            name="login"
            initialValues={{ 
              username: USE_MOCK_DATA ? 'admin' : '',
              password: USE_MOCK_DATA ? 'admin' : ''
            }}
            onFinish={onFinish}
            layout="vertical"
            size="large"
          >
            <Form.Item
              label="사용자 이름"
              name="username"
              rules={[
                { required: true, message: '사용자 이름을 입력해주세요!' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="사용자 이름"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              label="비밀번호"
              name="password"
              rules={[
                { required: true, message: '비밀번호를 입력해주세요!' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="비밀번호"
                autoComplete="current-password"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
              >
                로그인
              </Button>
            </Form.Item>
          </Form>

          {USE_MOCK_DATA && (
            <div className="text-center mt-4 p-4 bg-gray-50 rounded">
              <Text type="secondary" className="text-sm">
                <Space direction="vertical" size="small">
                  <div><strong>데모 계정:</strong></div>
                  <div>아이디: admin</div>
                  <div>비밀번호: admin</div>
                </Space>
              </Text>
            </div>
          )}
        </Card>

        {/* 하단 링크 */}
        <div className="text-center mt-6">
          <Text type="secondary" className="text-sm">
            © 2024 Poker Trend. garimto81과 함께 개발
          </Text>
        </div>
      </div>
    </div>
  );
};

export default Login;