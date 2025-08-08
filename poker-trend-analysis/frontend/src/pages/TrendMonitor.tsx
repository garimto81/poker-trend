import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Tag,
  Space,
  Button,
  Input,
  Select,
  Badge,
  Progress,
  Typography,
  Statistic,
  Row,
  Col,
  Timeline,
  Tooltip,
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  PlayCircleOutlined,
  ClockCircleOutlined,
  TrendingUpOutlined,
  YoutubeOutlined,
  TwitterOutlined,
  RedditOutlined,
} from '@ant-design/icons';
import { mockApi, USE_MOCK_DATA } from '../services/mockApi';
import { mockData } from '../services/mockApi';

const { Title, Text } = Typography;
const { Option } = Select;

interface Trend {
  id: number;
  title: string;
  description: string;
  score: number;
  platform: string;
  keywords: string[];
  sentiment: 'positive' | 'negative' | 'neutral';
  views: number;
  timestamp: string;
  status: 'pending' | 'processing' | 'processed' | 'generating';
}

const TrendMonitor: React.FC = () => {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [platformFilter, setPlatformFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    loadTrends();
  }, []);

  const loadTrends = async () => {
    try {
      setLoading(true);
      if (USE_MOCK_DATA) {
        const data = await mockApi.getTrends();
        setTrends(data.latest);
      }
    } catch (error) {
      console.error('Failed to load trends:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'youtube':
        return <YoutubeOutlined style={{ color: '#ff0000' }} />;
      case 'twitter':
        return <TwitterOutlined style={{ color: '#1da1f2' }} />;
      case 'reddit':
        return <RedditOutlined style={{ color: '#ff4500' }} />;
      default:
        return <TrendingUpOutlined />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'success';
      case 'processing':
      case 'generating':
        return 'processing';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'processed':
        return '완료';
      case 'processing':
        return '처리중';
      case 'generating':
        return '생성중';
      case 'pending':
        return '대기';
      default:
        return status;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'success';
      case 'negative':
        return 'error';
      case 'neutral':
        return 'default';
      default:
        return 'default';
    }
  };

  const getSentimentText = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return '긍정';
      case 'negative':
        return '부정';
      case 'neutral':
        return '중립';
      default:
        return sentiment;
    }
  };

  const columns = [
    {
      title: '플랫폼',
      dataIndex: 'platform',
      key: 'platform',
      width: 100,
      render: (platform: string) => (
        <Space>
          {getPlatformIcon(platform)}
          <Text>{platform}</Text>
        </Space>
      ),
    },
    {
      title: '트렌드',
      dataIndex: 'title',
      key: 'title',
      render: (title: string, record: Trend) => (
        <div>
          <Text strong>{title}</Text>
          <br />
          <Text type="secondary" className="text-sm">
            {record.description.substring(0, 60)}...
          </Text>
        </div>
      ),
    },
    {
      title: '스코어',
      dataIndex: 'score',
      key: 'score',
      width: 120,
      render: (score: number) => (
        <div>
          <Progress
            percent={score}
            size="small"
            status={score >= 85 ? 'success' : score >= 70 ? 'normal' : 'exception'}
          />
          <Text className="text-sm">{score}</Text>
        </div>
      ),
    },
    {
      title: '키워드',
      dataIndex: 'keywords',
      key: 'keywords',
      render: (keywords: string[]) => (
        <Space wrap>
          {keywords.slice(0, 3).map((keyword, index) => (
            <Tag key={index} size="small">
              {keyword}
            </Tag>
          ))}
          {keywords.length > 3 && <Tag size="small">+{keywords.length - 3}</Tag>}
        </Space>
      ),
    },
    {
      title: '감정',
      dataIndex: 'sentiment',
      key: 'sentiment',
      width: 80,
      render: (sentiment: string) => (
        <Tag color={getSentimentColor(sentiment)}>
          {getSentimentText(sentiment)}
        </Tag>
      ),
    },
    {
      title: '조회수',
      dataIndex: 'views',
      key: 'views',
      width: 100,
      render: (views: number) => (
        <Space>
          <EyeOutlined />
          <Text>{views.toLocaleString()}</Text>
        </Space>
      ),
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Badge
          status={getStatusColor(status) as any}
          text={getStatusText(status)}
        />
      ),
    },
    {
      title: '시간',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 120,
      render: (timestamp: string) => (
        <Tooltip title={new Date(timestamp).toLocaleString()}>
          <Space>
            <ClockCircleOutlined />
            <Text className="text-sm">
              {new Date(timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Text>
          </Space>
        </Tooltip>
      ),
    },
    {
      title: '액션',
      key: 'action',
      width: 120,
      render: (_, record: Trend) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<PlayCircleOutlined />}
            disabled={record.status === 'processing' || record.status === 'generating'}
          >
            생성
          </Button>
        </Space>
      ),
    },
  ];

  // 필터링된 데이터
  const filteredTrends = trends.filter((trend) => {
    const matchesSearch = trend.title
      .toLowerCase()
      .includes(searchText.toLowerCase());
    const matchesPlatform =
      platformFilter === 'all' || trend.platform === platformFilter;
    const matchesStatus = statusFilter === 'all' || trend.status === statusFilter;

    return matchesSearch && matchesPlatform && matchesStatus;
  });

  return (
    <div className="p-6">
      <div className="mb-6">
        <Title level={2}>트렌드 모니터링</Title>
        <Text type="secondary">실시간 포커 트렌드 감지 및 분석</Text>
      </div>

      {/* 통계 카드 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="총 트렌드"
              value={mockData.trends.stats.total}
              prefix={<TrendingUpOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="오늘 감지"
              value={mockData.trends.stats.today}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="최고 스코어"
              value={mockData.trends.stats.highScore}
              suffix="점"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="평균 스코어"
              value={mockData.trends.stats.averageScore}
              precision={1}
              suffix="점"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={18}>
          {/* 트렌드 테이블 */}
          <Card
            title="실시간 트렌드"
            extra={
              <Space>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={loadTrends}
                  loading={loading}
                >
                  새로고침
                </Button>
              </Space>
            }
          >
            {/* 필터 */}
            <div className="mb-4">
              <Space wrap>
                <Input
                  placeholder="트렌드 검색..."
                  prefix={<SearchOutlined />}
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  style={{ width: 200 }}
                />
                <Select
                  value={platformFilter}
                  onChange={setPlatformFilter}
                  style={{ width: 120 }}
                >
                  <Option value="all">모든 플랫폼</Option>
                  <Option value="YouTube">YouTube</Option>
                  <Option value="Twitter">Twitter</Option>
                  <Option value="Reddit">Reddit</Option>
                </Select>
                <Select
                  value={statusFilter}
                  onChange={setStatusFilter}
                  style={{ width: 120 }}
                >
                  <Option value="all">모든 상태</Option>
                  <Option value="pending">대기</Option>
                  <Option value="processing">처리중</Option>
                  <Option value="generating">생성중</Option>
                  <Option value="processed">완료</Option>
                </Select>
              </Space>
            </div>

            <Table
              columns={columns}
              dataSource={filteredTrends}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) =>
                  `${range[0]}-${range[1]} / ${total}개`,
              }}
              scroll={{ x: 1200 }}
            />
          </Card>
        </Col>

        <Col xs={24} lg={6}>
          {/* 최근 활동 */}
          <Card title="최근 활동" className="h-full">
            <Timeline size="small">
              {mockData.dashboard.recentActivities.slice(0, 8).map((activity, index) => (
                <Timeline.Item
                  key={index}
                  color={
                    activity.type === 'success'
                      ? 'green'
                      : activity.type === 'processing'
                      ? 'blue'
                      : 'orange'
                  }
                >
                  <div>
                    <Text strong className="text-sm">
                      {activity.title}
                    </Text>
                    <br />
                    <Text type="secondary" className="text-xs">
                      {activity.description}
                    </Text>
                    <br />
                    <Text type="secondary" className="text-xs">
                      {activity.time}
                    </Text>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default TrendMonitor;