import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Switch,
  Select,
  Divider,
  Typography,
  Space,
  Alert,
  Tabs,
  Row,
  Col,
  InputNumber,
  TimePicker,
  Upload,
  Avatar,
  Badge,
} from 'antd';
import {
  UserOutlined,
  SettingOutlined,
  KeyOutlined,
  BellOutlined,
  CloudUploadOutlined,
  SecurityScanOutlined,
  ApiOutlined,
  SaveOutlined,
  UploadOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone,
} from '@ant-design/icons';
import { USE_MOCK_DATA } from '../config/api';
import toast from 'react-hot-toast';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { TextArea } = Input;

const Settings: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [profileForm] = Form.useForm();
  const [apiForm] = Form.useForm();
  const [notificationForm] = Form.useForm();

  const handleSaveProfile = async (values: any) => {
    try {
      setLoading(true);
      // 모의 저장 처리
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('프로필이 업데이트되었습니다.');
    } catch (error) {
      toast.error('프로필 업데이트에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveApiKeys = async (values: any) => {
    try {
      setLoading(true);
      // 모의 저장 처리
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('API 키가 업데이트되었습니다.');
    } catch (error) {
      toast.error('API 키 업데이트에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNotifications = async (values: any) => {
    try {
      setLoading(true);
      // 모의 저장 처리
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('알림 설정이 업데이트되었습니다.');
    } catch (error) {
      toast.error('알림 설정 업데이트에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const testApiConnection = async (apiType: string) => {
    try {
      setLoading(true);
      // 모의 API 테스트
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success(`${apiType} API 연결이 성공했습니다.`);
    } catch (error) {
      toast.error(`${apiType} API 연결에 실패했습니다.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <Title level={2}>설정</Title>
        <Text type="secondary">시스템 설정 및 개인화 옵션</Text>
      </div>

      <Tabs defaultActiveKey="profile" type="card">
        {/* 프로필 설정 */}
        <TabPane tab={<span><UserOutlined />프로필</span>} key="profile">
          <Row gutter={[24, 24]}>
            <Col xs={24} lg={16}>
              <Card title="개인 정보" extra={<UserOutlined />}>
                <Form
                  form={profileForm}
                  layout="vertical"
                  onFinish={handleSaveProfile}
                  initialValues={{
                    username: 'admin',
                    email: 'admin@poker-trend.com',
                    displayName: '관리자',
                    bio: '포커 트렌드 분석 전문가',
                    timezone: 'Asia/Seoul',
                    language: 'ko',
                  }}
                >
                  <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="사용자명"
                        name="username"
                        rules={[{ required: true, message: '사용자명을 입력해주세요!' }]}
                      >
                        <Input />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="이메일"
                        name="email"
                        rules={[
                          { required: true, message: '이메일을 입력해주세요!' },
                          { type: 'email', message: '올바른 이메일 형식을 입력해주세요!' }
                        ]}
                      >
                        <Input />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    label="표시 이름"
                    name="displayName"
                  >
                    <Input />
                  </Form.Item>

                  <Form.Item
                    label="자기소개"
                    name="bio"
                  >
                    <TextArea rows={3} />
                  </Form.Item>

                  <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="시간대"
                        name="timezone"
                      >
                        <Select>
                          <Option value="Asia/Seoul">한국 표준시 (KST)</Option>
                          <Option value="America/New_York">동부 표준시 (EST)</Option>
                          <Option value="Europe/London">그리니치 표준시 (GMT)</Option>
                          <Option value="Asia/Tokyo">일본 표준시 (JST)</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="언어"
                        name="language"
                      >
                        <Select>
                          <Option value="ko">한국어</Option>
                          <Option value="en">English</Option>
                          <Option value="ja">日本語</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                      프로필 저장
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            </Col>

            <Col xs={24} lg={8}>
              <Card title="프로필 사진">
                <div className="text-center">
                  <Badge count={<UploadOutlined />} offset={[-10, 10]}>
                    <Avatar size={100} icon={<UserOutlined />} />
                  </Badge>
                  <div className="mt-4">
                    <Upload>
                      <Button icon={<CloudUploadOutlined />}>
                        사진 업로드
                      </Button>
                    </Upload>
                  </div>
                  <Text type="secondary" className="text-sm mt-2 block">
                    JPG, PNG 파일만 지원 (최대 2MB)
                  </Text>
                </div>
              </Card>

              <Card title="계정 통계" className="mt-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <Text type="secondary">가입일</Text>
                    <Text>2024.01.15</Text>
                  </div>
                  <div className="flex justify-between">
                    <Text type="secondary">마지막 로그인</Text>
                    <Text>{dayjs().format('YYYY.MM.DD HH:mm')}</Text>
                  </div>
                  <div className="flex justify-between">
                    <Text type="secondary">생성한 콘텐츠</Text>
                    <Text strong>245개</Text>
                  </div>
                  <div className="flex justify-between">
                    <Text type="secondary">총 조회수</Text>
                    <Text strong>1.2M</Text>
                  </div>
                </div>
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* API 설정 */}
        <TabPane tab={<span><ApiOutlined />API 키</span>} key="api">
          <Card title="외부 서비스 연동" extra={<KeyOutlined />}>
            {USE_MOCK_DATA && (
              <Alert
                message="데모 모드"
                description="현재 데모 모드에서 실행 중입니다. API 키는 저장되지 않습니다."
                type="info"
                showIcon
                className="mb-6"
              />
            )}

            <Form
              form={apiForm}
              layout="vertical"
              onFinish={handleSaveApiKeys}
              initialValues={{
                youtubeApiKey: USE_MOCK_DATA ? 'demo_youtube_key_***' : '',
                twitterBearerToken: USE_MOCK_DATA ? 'demo_twitter_token_***' : '',
                redditClientId: USE_MOCK_DATA ? 'demo_reddit_id_***' : '',
                redditClientSecret: USE_MOCK_DATA ? 'demo_reddit_secret_***' : '',
                openaiApiKey: USE_MOCK_DATA ? 'demo_openai_key_***' : '',
              }}
            >
              <Row gutter={[16, 16]}>
                <Col xs={24} lg={12}>
                  <Form.Item
                    label="YouTube Data API 키"
                    name="youtubeApiKey"
                    extra="YouTube 트렌드 데이터 수집용"
                  >
                    <Input.Password
                      placeholder="YouTube API 키를 입력하세요"
                      iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                      addonAfter={
                        <Button
                          size="small"
                          type="link"
                          onClick={() => testApiConnection('YouTube')}
                          loading={loading}
                        >
                          테스트
                        </Button>
                      }
                    />
                  </Form.Item>
                </Col>

                <Col xs={24} lg={12}>
                  <Form.Item
                    label="Twitter Bearer Token"
                    name="twitterBearerToken"
                    extra="Twitter 트렌드 모니터링용"
                  >
                    <Input.Password
                      placeholder="Twitter Bearer Token을 입력하세요"
                      iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                      addonAfter={
                        <Button
                          size="small"
                          type="link"
                          onClick={() => testApiConnection('Twitter')}
                          loading={loading}
                        >
                          테스트
                        </Button>
                      }
                    />
                  </Form.Item>
                </Col>

                <Col xs={24} lg={12}>
                  <Form.Item
                    label="Reddit Client ID"
                    name="redditClientId"
                    extra="Reddit 포커 커뮤니티 모니터링용"
                  >
                    <Input.Password
                      placeholder="Reddit Client ID를 입력하세요"
                      iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                    />
                  </Form.Item>
                </Col>

                <Col xs={24} lg={12}>
                  <Form.Item
                    label="Reddit Client Secret"
                    name="redditClientSecret"
                    extra="Reddit API 인증용"
                  >
                    <Input.Password
                      placeholder="Reddit Client Secret을 입력하세요"
                      iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                      addonAfter={
                        <Button
                          size="small"
                          type="link"
                          onClick={() => testApiConnection('Reddit')}
                          loading={loading}
                        >
                          테스트
                        </Button>
                      }
                    />
                  </Form.Item>
                </Col>

                <Col xs={24}>
                  <Form.Item
                    label="OpenAI API 키"
                    name="openaiApiKey"
                    extra="AI 스크립트 생성 및 콘텐츠 분석용"
                  >
                    <Input.Password
                      placeholder="OpenAI API 키를 입력하세요"
                      iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                      addonAfter={
                        <Button
                          size="small"
                          type="link"
                          onClick={() => testApiConnection('OpenAI')}
                          loading={loading}
                        >
                          테스트
                        </Button>
                      }
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                  API 키 저장
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        {/* 알림 설정 */}
        <TabPane tab={<span><BellOutlined />알림</span>} key="notifications">
          <Row gutter={[24, 24]}>
            <Col xs={24} lg={12}>
              <Card title="알림 설정" extra={<BellOutlined />}>
                <Form
                  form={notificationForm}
                  layout="vertical"
                  onFinish={handleSaveNotifications}
                  initialValues={{
                    enableEmailNotifications: true,
                    enablePushNotifications: true,
                    enableTrendAlerts: true,
                    enableContentAlerts: true,
                    enableSystemAlerts: true,
                    trendThreshold: 85,
                    quietHoursStart: dayjs('22:00', 'HH:mm'),
                    quietHoursEnd: dayjs('07:00', 'HH:mm'),
                  }}
                >
                  <div className="space-y-4">
                    <div>
                      <Text strong>일반 알림</Text>
                      <Divider className="my-2" />
                      
                      <div className="space-y-3">
                        <Form.Item name="enableEmailNotifications" valuePropName="checked" className="mb-2">
                          <div className="flex justify-between items-center">
                            <span>이메일 알림</span>
                            <Switch />
                          </div>
                        </Form.Item>

                        <Form.Item name="enablePushNotifications" valuePropName="checked" className="mb-2">
                          <div className="flex justify-between items-center">
                            <span>브라우저 푸시 알림</span>
                            <Switch />
                          </div>
                        </Form.Item>
                      </div>
                    </div>

                    <div>
                      <Text strong>콘텐츠 알림</Text>
                      <Divider className="my-2" />
                      
                      <div className="space-y-3">
                        <Form.Item name="enableTrendAlerts" valuePropName="checked" className="mb-2">
                          <div className="flex justify-between items-center">
                            <span>새로운 트렌드 감지</span>
                            <Switch />
                          </div>
                        </Form.Item>

                        <Form.Item name="enableContentAlerts" valuePropName="checked" className="mb-2">
                          <div className="flex justify-between items-center">
                            <span>콘텐츠 생성 완료</span>
                            <Switch />
                          </div>
                        </Form.Item>

                        <Form.Item name="enableSystemAlerts" valuePropName="checked" className="mb-2">
                          <div className="flex justify-between items-center">
                            <span>시스템 오류 및 경고</span>
                            <Switch />
                          </div>
                        </Form.Item>
                      </div>
                    </div>

                    <div>
                      <Text strong>트렌드 알림 임계값</Text>
                      <Divider className="my-2" />
                      
                      <Form.Item
                        label="트렌드 스코어 임계값"
                        name="trendThreshold"
                        extra="설정한 점수 이상의 트렌드만 알림을 받습니다"
                      >
                        <InputNumber min={50} max={100} style={{ width: '100%' }} />
                      </Form.Item>
                    </div>

                    <Form.Item>
                      <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                        알림 설정 저장
                      </Button>
                    </Form.Item>
                  </div>
                </Form>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="방해 금지 시간" extra={<SecurityScanOutlined />}>
                <Form
                  layout="vertical"
                  initialValues={{
                    quietHoursEnabled: true,
                    quietHoursStart: dayjs('22:00', 'HH:mm'),
                    quietHoursEnd: dayjs('07:00', 'HH:mm'),
                  }}
                >
                  <Form.Item name="quietHoursEnabled" valuePropName="checked">
                    <div className="flex justify-between items-center">
                      <span>방해 금지 시간 활성화</span>
                      <Switch defaultChecked />
                    </div>
                  </Form.Item>

                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <Form.Item label="시작 시간" name="quietHoursStart">
                        <TimePicker format="HH:mm" style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item label="종료 시간" name="quietHoursEnd">
                        <TimePicker format="HH:mm" style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Alert
                    message="방해 금지 시간 안내"
                    description="설정한 시간 동안에는 중요하지 않은 알림이 차단됩니다. 시스템 오류나 중요한 트렌드는 계속 알림을 받습니다."
                    type="info"
                    showIcon
                  />
                </Form>
              </Card>

              <Card title="알림 히스토리" className="mt-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div>
                      <Text className="text-sm">새로운 트렌드 감지</Text>
                      <br />
                      <Text type="secondary" className="text-xs">WSOP 메인 이벤트 관련</Text>
                    </div>
                    <Text type="secondary" className="text-xs">5분 전</Text>
                  </div>
                  
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div>
                      <Text className="text-sm">콘텐츠 생성 완료</Text>
                      <br />
                      <Text type="secondary" className="text-xs">포커 전략 분석 영상</Text>
                    </div>
                    <Text type="secondary" className="text-xs">1시간 전</Text>
                  </div>
                  
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div>
                      <Text className="text-sm">API 사용량 경고</Text>
                      <br />
                      <Text type="secondary" className="text-xs">Twitter API 80% 사용</Text>
                    </div>
                    <Text type="secondary" className="text-xs">2시간 전</Text>
                  </div>
                </div>
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* 시스템 설정 */}
        <TabPane tab={<span><SettingOutlined />시스템</span>} key="system">
          <Row gutter={[24, 24]}>
            <Col xs={24} lg={12}>
              <Card title="자동화 설정">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <Text strong>자동 트렌드 감지</Text>
                      <br />
                      <Text type="secondary" className="text-sm">
                        실시간으로 트렌드를 자동 감지합니다
                      </Text>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <Divider className="my-3" />

                  <div className="flex justify-between items-center">
                    <div>
                      <Text strong>자동 콘텐츠 생성</Text>
                      <br />
                      <Text type="secondary" className="text-sm">
                        고득점 트렌드 감지 시 자동으로 콘텐츠를 생성합니다
                      </Text>
                    </div>
                    <Switch />
                  </div>

                  <Divider className="my-3" />

                  <div className="flex justify-between items-center">
                    <div>
                      <Text strong>자동 업로드</Text>
                      <br />
                      <Text type="secondary" className="text-sm">
                        콘텐츠 생성 완료 시 자동으로 플랫폼에 업로드합니다
                      </Text>
                    </div>
                    <Switch />
                  </div>
                </div>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="성능 설정">
                <Form layout="vertical">
                  <Form.Item
                    label="트렌드 검사 주기"
                    extra="더 자주 검사할수록 실시간성이 향상되지만 API 사용량이 증가합니다"
                  >
                    <Select defaultValue="5">
                      <Option value="1">1분</Option>
                      <Option value="5">5분</Option>
                      <Option value="15">15분</Option>
                      <Option value="30">30분</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    label="최대 동시 생성 수"
                    extra="동시에 생성할 수 있는 콘텐츠의 최대 개수"
                  >
                    <InputNumber min={1} max={10} defaultValue={3} style={{ width: '100%' }} />
                  </Form.Item>

                  <Form.Item
                    label="데이터 보관 기간"
                    extra="트렌드 및 콘텐츠 데이터 보관 기간"
                  >
                    <Select defaultValue="90">
                      <Option value="30">30일</Option>
                      <Option value="90">90일</Option>
                      <Option value="180">180일</Option>
                      <Option value="365">1년</Option>
                    </Select>
                  </Form.Item>
                </Form>
              </Card>
            </Col>
          </Row>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default Settings;