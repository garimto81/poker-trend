import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Typography, Space, Badge, Timeline, Button } from 'antd';
import {
  TrendingUpOutlined,
  PlayCircleOutlined,
  EyeOutlined,
  LikeOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';
import { mockApi, USE_MOCK_DATA } from '../services/mockApi';
import { mockData } from '../services/mockApi';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

const { Title: PageTitle, Text } = Typography;

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      if (USE_MOCK_DATA) {
        const data = await mockApi.getDashboard();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock data - 실제로는 API에서 가져올 데이터
  const trendData = dashboardData?.trendData || {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
    datasets: [
      {
        label: '트렌드 스코어',
        data: [65, 78, 82, 95, 88, 92],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
      },
    ],
  };

  const contentDistribution = {
    labels: ['뉴스형', '교육형', '분석형', '엔터테인먼트'],
    datasets: [
      {
        data: [35, 25, 20, 20],
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
        ],
      },
    ],
  };

  const platformPerformance = {
    labels: ['YouTube', 'TikTok', 'Instagram'],
    datasets: [
      {
        label: '조회수 (천)',
        data: [120, 85, 45],
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
      {
        label: '좋아요 (천)',
        data: [8.5, 12.3, 4.2],
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
      },
    ],
  };

  const recentActivities = [
    {
      type: 'success',
      title: '새로운 트렌드 감지',
      description: 'WSOP 메인 이벤트 결승 진출자 발표',
      time: '5분 전',
      icon: <TrendingUpOutlined />,
    },
    {
      type: 'processing',
      title: '쇼츠 제작 중',
      description: '포커 전략 분석 영상 자동 생성 중',
      time: '10분 전',
      icon: <PlayCircleOutlined />,
    },
    {
      type: 'success',
      title: '업로드 완료',
      description: 'YouTube, TikTok에 영상 업로드 완료',
      time: '25분 전',
      icon: <CheckCircleOutlined />,
    },
    {
      type: 'warning',
      title: 'API 제한 알림',
      description: 'Twitter API 일일 제한의 80% 사용',
      time: '1시간 전',
      icon: <ExclamationCircleOutlined />,
    },
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <PageTitle level={2}>대시보드</PageTitle>
        <Text type="secondary">포커 트렌드 쇼츠 제작 시스템 현황</Text>
      </div>

      {/* 주요 지표 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="오늘 감지된 트렌드"
              value={23}
              prefix={<TrendingUpOutlined />}
              valueStyle={{ color: '#3f8600' }}
              suffix={<Badge count={5} style={{ backgroundColor: '#52c41a' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="제작된 쇼츠"
              value={18}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="총 조회수"
              value={234500}
              prefix={<EyeOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="총 좋아요"
              value={12800}
              prefix={<LikeOutlined />}
              valueStyle={{ color: '#eb2f96' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 차트 섹션 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} lg={16}>
          <Card title="실시간 트렌드 스코어" className="h-full">
            <Line data={trendData} options={{ responsive: true }} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="콘텐츠 타입 분포" className="h-full">
            <Doughnut data={contentDistribution} options={{ responsive: true }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <Card title="플랫폼별 성과">
            <Bar data={platformPerformance} options={{ responsive: true }} />
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="최근 활동" className="h-full">
            <Timeline>
              {recentActivities.map((activity, index) => (
                <Timeline.Item
                  key={index}
                  dot={activity.icon}
                  color={
                    activity.type === 'success'
                      ? 'green'
                      : activity.type === 'processing'
                      ? 'blue'
                      : 'orange'
                  }
                >
                  <div>
                    <div className="font-medium">{activity.title}</div>
                    <div className="text-gray-500 text-sm">
                      {activity.description}
                    </div>
                    <div className="text-gray-400 text-xs flex items-center mt-1">
                      <ClockCircleOutlined className="mr-1" />
                      {activity.time}
                    </div>
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

export default Dashboard;