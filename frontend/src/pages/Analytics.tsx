import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Select,
  DatePicker,
  Space,
  Table,
  Progress,
  Tag,
  Button,
  Tabs,
} from 'antd';
import {
  TrendingUpOutlined,
  EyeOutlined,
  LikeOutlined,
  ShareAltOutlined,
  DownloadOutlined,
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title as ChartTitle,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
} from 'chart.js';
import { mockApi, USE_MOCK_DATA } from '../services/mockApi';
import { mockData } from '../services/mockApi';
import dayjs from 'dayjs';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ChartTitle,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale
);

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { TabPane } = Tabs;

interface AnalyticsData {
  performance: {
    totalViews: number;
    totalLikes: number;
    totalShares: number;
    averageEngagement: number;
    topPerformingContent: Array<{
      id: number;
      title: string;
      views: number;
      engagement: number;
    }>;
  };
  trendPrediction: {
    nextWeek: Array<{
      topic: string;
      probability: number;
    }>;
  };
}

const Analytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('7days');
  const [platform, setPlatform] = useState('all');

  useEffect(() => {
    loadAnalytics();
  }, [timeRange, platform]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      if (USE_MOCK_DATA) {
        const data = await mockApi.getAnalytics();
        setAnalyticsData(data);
      }
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  // 시간별 성과 데이터
  const performanceData = {
    labels: ['월', '화', '수', '목', '금', '토', '일'],
    datasets: [
      {
        label: '조회수',
        data: [12000, 19000, 15000, 25000, 22000, 30000, 28000],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        yAxisID: 'y',
      },
      {
        label: '좋아요',
        data: [800, 1200, 900, 1500, 1300, 1800, 1600],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        yAxisID: 'y1',
      },
    ],
  };

  // 플랫폼별 성과 데이터
  const platformData = {
    labels: ['YouTube', 'TikTok', 'Instagram'],
    datasets: [
      {
        label: '조회수',
        data: [120000, 85000, 45000],
        backgroundColor: ['#FF0000', '#000000', '#E4405F'],
      },
    ],
  };

  // 콘텐츠 타입별 분포
  const contentTypeData = {
    labels: ['뉴스형', '교육형', '분석형', '엔터테인먼트'],
    datasets: [
      {
        data: [35, 25, 20, 20],
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
      },
    ],
  };

  // 참여도 분석 (레이더 차트)
  const engagementData = {
    labels: ['조회수', '좋아요', '댓글', '공유', '구독'],
    datasets: [
      {
        label: '이번 주',
        data: [85, 92, 78, 65, 88],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
      },
      {
        label: '지난 주',
        data: [75, 85, 70, 60, 80],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
      },
    ],
  };

  const topContentColumns = [
    {
      title: '순위',
      dataIndex: 'rank',
      key: 'rank',
      width: 60,
      render: (_, __, index: number) => (
        <div className="flex items-center justify-center">
          <span className={`font-bold ${index < 3 ? 'text-yellow-500' : ''}`}>
            {index + 1}
          </span>
        </div>
      ),
    },
    {
      title: '콘텐츠',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '조회수',
      dataIndex: 'views',
      key: 'views',
      render: (views: number) => views.toLocaleString(),
    },
    {
      title: '참여도',
      dataIndex: 'engagement',
      key: 'engagement',
      render: (engagement: number) => (
        <div className="flex items-center space-x-2">
          <Progress
            percent={engagement * 10}
            size="small"
            showInfo={false}
            strokeColor={engagement > 10 ? '#52c41a' : engagement > 8 ? '#faad14' : '#ff4d4f'}
          />
          <Text className="text-sm">{engagement}%</Text>
        </div>
      ),
    },
  ];

  const trendPredictionColumns = [
    {
      title: '순위',
      dataIndex: 'rank',
      key: 'rank',
      width: 60,
      render: (_, __, index: number) => (
        <Text strong>#{index + 1}</Text>
      ),
    },
    {
      title: '예상 트렌드',
      dataIndex: 'topic',
      key: 'topic',
    },
    {
      title: '확률',
      dataIndex: 'probability',
      key: 'probability',
      render: (probability: number) => (
        <div className="flex items-center space-x-2">
          <Progress
            percent={probability}
            size="small"
            strokeColor={probability > 80 ? '#52c41a' : probability > 60 ? '#faad14' : '#ff4d4f'}
          />
          <Text className="text-sm">{probability}%</Text>
        </div>
      ),
    },
  ];

  return (
    <div className="p-6">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <Title level={2}>분석 대시보드</Title>
          <Text type="secondary">콘텐츠 성과 분석 및 트렌드 예측</Text>
        </div>
        
        <Space>
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 120 }}
          >
            <Option value="7days">최근 7일</Option>
            <Option value="30days">최근 30일</Option>
            <Option value="90days">최근 90일</Option>
            <Option value="1year">1년</Option>
          </Select>
          
          <Select
            value={platform}
            onChange={setPlatform}
            style={{ width: 120 }}
          >
            <Option value="all">모든 플랫폼</Option>
            <Option value="youtube">YouTube</Option>
            <Option value="tiktok">TikTok</Option>
            <Option value="instagram">Instagram</Option>
          </Select>
          
          <RangePicker />
          
          <Button icon={<DownloadOutlined />}>
            리포트 다운로드
          </Button>
        </Space>
      </div>

      {/* 주요 지표 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="총 조회수"
              value={analyticsData?.performance.totalViews || 1234567}
              prefix={<EyeOutlined />}
              valueStyle={{ color: '#3f8600' }}
              suffix={
                <span className="text-sm">
                  <TrendingUpOutlined className="text-green-500" /> +12.5%
                </span>
              }
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="총 좋아요"
              value={analyticsData?.performance.totalLikes || 45678}
              prefix={<LikeOutlined />}
              valueStyle={{ color: '#cf1322' }}
              suffix={
                <span className="text-sm">
                  <TrendingUpOutlined className="text-green-500" /> +8.3%
                </span>
              }
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="총 공유"
              value={analyticsData?.performance.totalShares || 8900}
              prefix={<ShareAltOutlined />}
              valueStyle={{ color: '#1890ff' }}
              suffix={
                <span className="text-sm">
                  <TrendingUpOutlined className="text-green-500" /> +15.7%
                </span>
              }
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="평균 참여도"
              value={analyticsData?.performance.averageEngagement || 7.2}
              precision={1}
              suffix="%"
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Tabs defaultActiveKey="performance">
        <TabPane tab={<span><LineChartOutlined />성과 분석</span>} key="performance">
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={16}>
              <Card title="시간별 성과 추이" className="mb-4">
                <Line
                  data={performanceData}
                  options={{
                    responsive: true,
                    interaction: {
                      mode: 'index' as const,
                      intersect: false,
                    },
                    scales: {
                      y: {
                        type: 'linear' as const,
                        display: true,
                        position: 'left' as const,
                      },
                      y1: {
                        type: 'linear' as const,
                        display: true,
                        position: 'right' as const,
                        grid: {
                          drawOnChartArea: false,
                        },
                      },
                    },
                  }}
                />
              </Card>
              
              <Card title="참여도 분석">
                <Radar
                  data={engagementData}
                  options={{
                    responsive: true,
                    scales: {
                      r: {
                        beginAtZero: true,
                        max: 100,
                      },
                    },
                  }}
                />
              </Card>
            </Col>

            <Col xs={24} lg={8}>
              <Card title="플랫폼별 성과" className="mb-4">
                <Bar
                  data={platformData}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                  }}
                />
              </Card>
              
              <Card title="콘텐츠 타입 분포">
                <Doughnut
                  data={contentTypeData}
                  options={{
                    responsive: true,
                  }}
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane tab={<span><BarChartOutlined />상위 콘텐츠</span>} key="top-content">
          <Card title="최고 성과 콘텐츠">
            <Table
              columns={topContentColumns}
              dataSource={analyticsData?.performance.topPerformingContent || []}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </TabPane>

        <TabPane tab={<span><PieChartOutlined />트렌드 예측</span>} key="trends">
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title="다음 주 예상 트렌드" extra={<CalendarOutlined />}>
                <Table
                  columns={trendPredictionColumns}
                  dataSource={analyticsData?.trendPrediction.nextWeek || []}
                  rowKey="topic"
                  pagination={false}
                  size="small"
                />
              </Card>
            </Col>
            
            <Col xs={24} lg={12}>
              <Card title="트렌드 예측 정확도">
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <Text>지난 주 예측</Text>
                      <Text strong>87%</Text>
                    </div>
                    <Progress percent={87} strokeColor="#52c41a" />
                  </div>
                  
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <Text>지난 달 예측</Text>
                      <Text strong>74%</Text>
                    </div>
                    <Progress percent={74} strokeColor="#faad14" />
                  </div>
                  
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <Text>평균 정확도</Text>
                      <Text strong>81%</Text>
                    </div>
                    <Progress percent={81} strokeColor="#1890ff" />
                  </div>
                </div>
              </Card>
            </Col>
          </Row>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default Analytics;