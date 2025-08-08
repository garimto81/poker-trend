// GitHub Pages용 모의 API 데이터
export const mockData = {
  // 대시보드 데이터
  dashboard: {
    stats: {
      trendsDetected: 23,
      shortsCreated: 18,
      totalViews: 234500,
      totalLikes: 12800,
    },
    trendData: {
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
    },
    contentDistribution: {
      labels: ['뉴스형', '교육형', '분석형', '엔터테인먼트'],
      datasets: [
        {
          data: [35, 25, 20, 20],
          backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
        },
      ],
    },
    platformPerformance: {
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
    },
    recentActivities: [
      {
        id: 1,
        type: 'success',
        title: '새로운 트렌드 감지',
        description: 'WSOP 메인 이벤트 결승 진출자 발표',
        time: '5분 전',
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      },
      {
        id: 2,
        type: 'processing',
        title: '쇼츠 제작 중',
        description: '포커 전략 분석 영상 자동 생성 중',
        time: '10분 전',
        timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
      },
      {
        id: 3,
        type: 'success',
        title: '업로드 완료',
        description: 'YouTube, TikTok에 영상 업로드 완료',
        time: '25분 전',
        timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
      },
      {
        id: 4,
        type: 'warning',
        title: 'API 제한 알림',
        description: 'Twitter API 일일 제한의 80% 사용',
        time: '1시간 전',
        timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
      },
    ],
  },

  // 트렌드 모니터링 데이터
  trends: {
    latest: [
      {
        id: 1,
        title: 'WSOP 메인 이벤트 파이널 테이블',
        description: '2024 WSOP 메인 이벤트 파이널 테이블 진출자 9명 확정',
        score: 95,
        platform: 'YouTube',
        keywords: ['WSOP', '메인이벤트', '파이널테이블'],
        sentiment: 'positive',
        views: 45600,
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        status: 'processed',
      },
      {
        id: 2,
        title: '포커 AI vs 프로 대결',
        description: 'AI가 포커 세계 챔피언을 상대로 승리',
        score: 88,
        platform: 'Twitter',
        keywords: ['AI', '포커', '프로선수'],
        sentiment: 'neutral',
        views: 23400,
        timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        status: 'generating',
      },
      {
        id: 3,
        title: '새로운 포커 전략 공개',
        description: '수학적 분석을 통한 혁신적인 포커 전략',
        score: 76,
        platform: 'Reddit',
        keywords: ['전략', '수학', '분석'],
        sentiment: 'positive',
        views: 12800,
        timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
        status: 'pending',
      },
    ],
    stats: {
      total: 156,
      today: 23,
      highScore: 95,
      averageScore: 73.5,
    },
  },

  // 콘텐츠 생성 데이터
  content: {
    generated: [
      {
        id: 1,
        title: 'WSOP 파이널 테이블 하이라이트',
        type: '뉴스형',
        duration: 58,
        status: 'completed',
        platforms: ['YouTube', 'TikTok'],
        views: 15600,
        likes: 892,
        createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        thumbnail: '/api/placeholder/300/169',
      },
      {
        id: 2,
        title: '초보자를 위한 포커 기본 전략',
        type: '교육형',
        duration: 45,
        status: 'uploading',
        platforms: ['YouTube'],
        views: 0,
        likes: 0,
        createdAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        thumbnail: '/api/placeholder/300/169',
      },
    ],
    templates: [
      {
        id: 1,
        name: '뉴스형 템플릿',
        description: '포커 뉴스 및 이벤트용 템플릿',
        duration: '30-60초',
        usage: 45,
      },
      {
        id: 2,
        name: '교육형 템플릿',
        description: '포커 전략 및 팁 설명용 템플릿',
        duration: '45-90초',
        usage: 32,
      },
    ],
  },

  // 분석 데이터
  analytics: {
    performance: {
      totalViews: 1234567,
      totalLikes: 45678,
      totalShares: 8900,
      averageEngagement: 7.2,
      topPerformingContent: [
        {
          id: 1,
          title: 'WSOP 챔피언 승부수',
          views: 89000,
          engagement: 12.5,
        },
        {
          id: 2,
          title: '포커 블러프 마스터하기',
          views: 67000,
          engagement: 9.8,
        },
      ],
    },
    trendPrediction: {
      nextWeek: [
        { topic: 'EPT 바르셀로나', probability: 85 },
        { topic: '온라인 포커 규제', probability: 72 },
        { topic: '새로운 포커 앱', probability: 68 },
      ],
    },
  },

  // 사용자 인증
  auth: {
    user: {
      id: 1,
      username: 'admin',
      email: 'admin@poker-trend.com',
      role: 'admin',
      avatar: '/api/placeholder/50/50',
    },
    permissions: ['read', 'write', 'admin'],
  },
};

// 모의 API 함수들
export const mockApi = {
  // 인증 관련
  login: async (credentials: { username: string; password: string }) => {
    await new Promise(resolve => setTimeout(resolve, 1000)); // 로딩 시뮬레이션
    if (credentials.username === 'admin' && credentials.password === 'admin') {
      localStorage.setItem('auth_token', 'mock_token_123');
      return { success: true, user: mockData.auth.user };
    }
    throw new Error('Invalid credentials');
  },

  logout: async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
    localStorage.removeItem('auth_token');
    return { success: true };
  },

  // 대시보드 데이터
  getDashboard: async () => {
    await new Promise(resolve => setTimeout(resolve, 800));
    return mockData.dashboard;
  },

  // 트렌드 데이터
  getTrends: async () => {
    await new Promise(resolve => setTimeout(resolve, 600));
    return mockData.trends;
  },

  // 콘텐츠 데이터
  getContent: async () => {
    await new Promise(resolve => setTimeout(resolve, 700));
    return mockData.content;
  },

  // 분석 데이터
  getAnalytics: async () => {
    await new Promise(resolve => setTimeout(resolve, 900));
    return mockData.analytics;
  },

  // 헬스 체크
  healthCheck: async () => {
    await new Promise(resolve => setTimeout(resolve, 200));
    return {
      status: 'OK (Mock Mode)',
      timestamp: new Date().toISOString(),
      service: 'poker-trend-frontend',
      version: '1.0.0',
    };
  },
};

export default mockApi;