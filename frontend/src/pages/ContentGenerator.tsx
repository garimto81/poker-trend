import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Progress,
  Tag,
  Space,
  Upload,
  Typography,
  Row,
  Col,
  Steps,
  Statistic,
  List,
  Avatar,
} from 'antd';
import {
  PlayCircleOutlined,
  PlusOutlined,
  UploadOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  ShareAltOutlined,
  VideoCameraOutlined,
  FileImageOutlined,
  SoundOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { mockApi, USE_MOCK_DATA } from '../services/mockApi';
import { mockData } from '../services/mockApi';
import toast from 'react-hot-toast';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { Step } = Steps;

interface Content {
  id: number;
  title: string;
  type: string;
  duration: number;
  status: 'draft' | 'generating' | 'completed' | 'uploading' | 'published';
  platforms: string[];
  views: number;
  likes: number;
  createdAt: string;
  thumbnail?: string;
  script?: string;
}

interface Template {
  id: number;
  name: string;
  description: string;
  duration: string;
  usage: number;
}

const ContentGenerator: React.FC = () => {
  const [contents, setContents] = useState<Content[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [previewModalVisible, setPreviewModalVisible] = useState(false);
  const [selectedContent, setSelectedContent] = useState<Content | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      if (USE_MOCK_DATA) {
        const data = await mockApi.getContent();
        setContents(data.generated);
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Failed to load content data:', error);
      toast.error('데이터 로딩에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateContent = async (values: any) => {
    try {
      setLoading(true);
      
      // 모의 콘텐츠 생성
      const newContent: Content = {
        id: Date.now(),
        title: values.title,
        type: values.type,
        duration: 60,
        status: 'generating',
        platforms: values.platforms,
        views: 0,
        likes: 0,
        createdAt: new Date().toISOString(),
        script: values.script,
      };

      setContents(prev => [newContent, ...prev]);
      setCreateModalVisible(false);
      form.resetFields();
      
      toast.success('콘텐츠 생성을 시작했습니다!');
      
      // 3초 후 상태를 완료로 변경 (시뮬레이션)
      setTimeout(() => {
        setContents(prev => 
          prev.map(content => 
            content.id === newContent.id 
              ? { ...content, status: 'completed' as const }
              : content
          )
        );
        toast.success('콘텐츠 생성이 완료되었습니다!');
      }, 3000);
      
    } catch (error) {
      toast.error('콘텐츠 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'published':
        return 'success';
      case 'generating':
      case 'uploading':
        return 'processing';
      case 'draft':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'draft':
        return '초안';
      case 'generating':
        return '생성중';
      case 'completed':
        return '완료';
      case 'uploading':
        return '업로드중';
      case 'published':
        return '게시됨';
      default:
        return status;
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'youtube':
        return '🔴';
      case 'tiktok':
        return '⚫';
      case 'instagram':
        return '📷';
      default:
        return '📺';
    }
  };

  const columns = [
    {
      title: '콘텐츠',
      key: 'content',
      render: (_, record: Content) => (
        <div className="flex items-center space-x-3">
          <Avatar
            size={48}
            icon={<VideoCameraOutlined />}
            src={record.thumbnail}
            className="bg-blue-500"
          />
          <div>
            <Text strong>{record.title}</Text>
            <br />
            <Text type="secondary" className="text-sm">
              {record.type} • {record.duration}초
            </Text>
          </div>
        </div>
      ),
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '플랫폼',
      dataIndex: 'platforms',
      key: 'platforms',
      width: 150,
      render: (platforms: string[]) => (
        <Space wrap>
          {platforms.map((platform, index) => (
            <span key={index} className="text-lg">
              {getPlatformIcon(platform)}
            </span>
          ))}
        </Space>
      ),
    },
    {
      title: '성과',
      key: 'performance',
      width: 150,
      render: (_, record: Content) => (
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <EyeOutlined className="text-gray-500" />
            <Text className="text-sm">{record.views.toLocaleString()}</Text>
          </div>
          <div className="flex items-center space-x-2">
            <Text className="text-red-500">❤️</Text>
            <Text className="text-sm">{record.likes.toLocaleString()}</Text>
          </div>
        </div>
      ),
    },
    {
      title: '생성일',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 120,
      render: (createdAt: string) => (
        <Text className="text-sm">
          {new Date(createdAt).toLocaleDateString()}
        </Text>
      ),
    },
    {
      title: '액션',
      key: 'action',
      width: 200,
      render: (_, record: Content) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedContent(record);
              setPreviewModalVisible(true);
            }}
          >
            미리보기
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            disabled={record.status === 'generating'}
          >
            편집
          </Button>
          <Button
            type="link"
            size="small"
            icon={<ShareAltOutlined />}
            disabled={record.status !== 'completed'}
          >
            공유
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <Title level={2}>콘텐츠 생성</Title>
        <Text type="secondary">AI 기반 자동 쇼츠 제작 및 관리</Text>
      </div>

      {/* 통계 카드 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="총 콘텐츠"
              value={contents.length}
              prefix={<VideoCameraOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="생성중"
              value={contents.filter(c => c.status === 'generating').length}
              prefix={<PlayCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="총 조회수"
              value={contents.reduce((sum, c) => sum + c.views, 0)}
              prefix={<EyeOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="총 좋아요"
              value={contents.reduce((sum, c) => sum + c.likes, 0)}
              prefix={<Text className="text-red-500">❤️</Text>}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={18}>
          {/* 콘텐츠 목록 */}
          <Card
            title="생성된 콘텐츠"
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
              >
                새 콘텐츠 생성
              </Button>
            }
          >
            <Table
              columns={columns}
              dataSource={contents}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (total, range) =>
                  `${range[0]}-${range[1]} / ${total}개`,
              }}
            />
          </Card>
        </Col>

        <Col xs={24} lg={6}>
          {/* 템플릿 목록 */}
          <Card title="템플릿" className="mb-4">
            <List
              dataSource={templates}
              renderItem={(template) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar icon={<FileImageOutlined />} />}
                    title={template.name}
                    description={
                      <div>
                        <Text type="secondary" className="text-xs">
                          {template.description}
                        </Text>
                        <br />
                        <Text className="text-xs">
                          사용: {template.usage}회 • {template.duration}
                        </Text>
                      </div>
                    }
                  />
                </List.Item>
              )}
              size="small"
            />
          </Card>

          {/* 생성 진행률 */}
          <Card title="생성 진행률">
            <div className="space-y-4">
              {contents
                .filter(c => c.status === 'generating')
                .map((content) => (
                  <div key={content.id}>
                    <Text className="text-sm font-medium">
                      {content.title}
                    </Text>
                    <Progress
                      percent={65}
                      size="small"
                      status="active"
                      className="mt-1"
                    />
                  </div>
                ))}
              {contents.filter(c => c.status === 'generating').length === 0 && (
                <Text type="secondary" className="text-sm">
                  진행 중인 생성 작업이 없습니다.
                </Text>
              )}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 새 콘텐츠 생성 모달 */}
      <Modal
        title="새 콘텐츠 생성"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateContent}
        >
          <Form.Item
            label="제목"
            name="title"
            rules={[{ required: true, message: '제목을 입력해주세요!' }]}
          >
            <Input placeholder="콘텐츠 제목을 입력하세요" />
          </Form.Item>

          <Form.Item
            label="콘텐츠 타입"
            name="type"
            rules={[{ required: true, message: '타입을 선택해주세요!' }]}
          >
            <Select placeholder="콘텐츠 타입을 선택하세요">
              <Option value="뉴스형">뉴스형</Option>
              <Option value="교육형">교육형</Option>
              <Option value="분석형">분석형</Option>
              <Option value="엔터테인먼트">엔터테인먼트</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="배포 플랫폼"
            name="platforms"
            rules={[{ required: true, message: '플랫폼을 선택해주세요!' }]}
          >
            <Select mode="multiple" placeholder="배포할 플랫폼을 선택하세요">
              <Option value="YouTube">YouTube</Option>
              <Option value="TikTok">TikTok</Option>
              <Option value="Instagram">Instagram</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="스크립트"
            name="script"
          >
            <TextArea
              rows={4}
              placeholder="스크립트를 입력하거나 AI가 자동 생성하도록 비워두세요"
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button onClick={() => setCreateModalVisible(false)}>
                취소
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                생성 시작
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 미리보기 모달 */}
      <Modal
        title="콘텐츠 미리보기"
        open={previewModalVisible}
        onCancel={() => setPreviewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewModalVisible(false)}>
            닫기
          </Button>,
          <Button key="download" icon={<DownloadOutlined />}>
            다운로드
          </Button>,
          <Button key="edit" type="primary" icon={<EditOutlined />}>
            편집
          </Button>,
        ]}
        width={800}
      >
        {selectedContent && (
          <div>
            <div className="bg-gray-100 h-64 flex items-center justify-center mb-4 rounded">
              <div className="text-center">
                <VideoCameraOutlined className="text-4xl text-gray-400 mb-2" />
                <Text type="secondary">비디오 미리보기</Text>
              </div>
            </div>

            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Text strong>제목:</Text>
                <br />
                <Text>{selectedContent.title}</Text>
              </Col>
              <Col span={12}>
                <Text strong>타입:</Text>
                <br />
                <Text>{selectedContent.type}</Text>
              </Col>
              <Col span={12}>
                <Text strong>길이:</Text>
                <br />
                <Text>{selectedContent.duration}초</Text>
              </Col>
              <Col span={12}>
                <Text strong>상태:</Text>
                <br />
                <Tag color={getStatusColor(selectedContent.status)}>
                  {getStatusText(selectedContent.status)}
                </Tag>
              </Col>
            </Row>

            {selectedContent.script && (
              <div className="mt-4">
                <Text strong>스크립트:</Text>
                <div className="bg-gray-50 p-3 rounded mt-2">
                  <Text>{selectedContent.script}</Text>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ContentGenerator;