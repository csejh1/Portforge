
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI, projectAPI, teamAPI } from '../api/apiClient';

export interface TestResult {
  skill: string;
  score: number;
  date: string;
  feedback: string;
  level: string;
}

export interface Applicant {
  userId: string;
  userName: string;
  position: string;
  message: string;
  status: 'pending' | 'accepted' | 'rejected';
  score?: number;
  level?: string;
  feedback?: string;
}

export interface Project {
  id: number;
  type: '프로젝트' | '스터디';
  title: string;
  description: string;
  deadline: string;
  views: number;
  members: string;
  tags: string[];
  position: string;
  method: string;
  status: '모집중' | '모집완료';
  authorId: string;
  authorName: string;
  startDate: string;
  endDate: string;
  testRequired?: boolean;
  applicants?: Applicant[];
}

export interface TeamTask {
  id: number;
  projectId: number;
  title: string;
  status: '준비중' | '진행중' | '완료';
  priority: 'High' | 'Medium' | 'Low';
  owner: string;
}

export interface TeamMeeting {
  id: number;
  projectId: number;
  title: string;
  date: string;
  content: string;
  summary?: string;
}

export interface TeamFile {
  id: number;
  projectId: number;
  name: string;
  size: string;
  date: string;
  type: string;
}

export interface Notice {
  id: number;
  title: string;
  content: string;
  date: string;
}

export interface Banner {
  id: number;
  title: string;
  link: string;
  active: boolean;
}

export interface EventItem {
  id: number;
  category: '해커톤' | '컨퍼런스' | '공모전' | '부트캠프';
  title: string;
  date: string;
  method: string;
  imageUrl: string;
  description?: string;
}

export interface Notification {
  id: number;
  userId: string;
  role: 'USER' | 'ADMIN';
  message: string;
  link: string;
  read: boolean;
  date: string;
}

export interface Report {
  id: number;
  title: string;
  content: string;
  reporter: string;
  date: string;
  type: '신고' | '문의' | '버그';
  status: 'pending' | 'resolved';
  targetProjectId?: number;
  resolutionType?: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'USER' | 'ADMIN';
  avatarUrl?: string;
  myStacks?: string[];
  appliedProjects?: { id: number; status: 'pending' | 'accepted' | 'rejected'; userRole: 'Leader' | 'Member'; selectedPosition?: string }[];
  likedProjects?: number[];
  testResults?: TestResult[];
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  projects: Project[];
  notices: Notice[];
  banners: Banner[];
  reports: Report[];
  events: EventItem[];
  notifications: Notification[];
  teamTasks: TeamTask[];
  teamMeetings: TeamMeeting[];
  teamFiles: TeamFile[];

  filterResetKey: number;
  resetAllFilters: () => void;
  login: (email: string, pass: string) => Promise<void>;
  loginWithSocial: (provider: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  validateName: (name: string) => { available: boolean; message: string };
  checkNickname: (name: string) => Promise<{ available: boolean; message: string }>;
  applyToProject: (projectId: number, position: string, message: string) => Promise<void>;
  handleApplication: (projectId: number, userId: string, action: 'accepted' | 'rejected') => void;
  toggleLike: (projectId: number) => void;
  addProject: (newProject: Omit<Project, 'id' | 'views' | 'status' | 'authorId' | 'authorName' | 'applicants'>) => void;
  updateProjectStatus: (projectId: number, status: '모집중' | '모집완료') => void;
  deleteProject: (projectId: number) => void;
  addNotice: (notice: Omit<Notice, 'id' | 'date'>) => void;
  updateNotice: (id: number, notice: Partial<Notice>) => void;
  deleteNotice: (id: number) => void;
  addBanner: (banner: Omit<Banner, 'id'>) => void;
  updateBanner: (id: number, banner: Partial<Banner>) => void;
  deleteBanner: (id: number) => void;
  addReport: (report: Omit<Report, 'id' | 'date' | 'status'>) => void;
  resolveReport: (id: number, resolutionType: string) => void;
  addEvent: (event: Omit<EventItem, 'id'>) => void;
  markNotificationsRead: () => void;
  changePassword: (oldPw: string, newPw: string) => Promise<void>;
  addTestResult: (result: TestResult) => void;
  addTeamTask: (task: Omit<TeamTask, 'id'>) => void;
  updateTeamTask: (id: number, updates: Partial<TeamTask>) => void;
  addTeamMeeting: (meeting: Omit<TeamMeeting, 'id'>) => void;
  updateTeamMeeting: (id: number, updates: Partial<TeamMeeting>) => void;
  addTeamFile: (file: Omit<TeamFile, 'id'>) => void;
}

const getToday = () => new Date().toISOString().split('T')[0];

const INITIAL_PROJECTS: Project[] = [
  {
    id: 1, type: '프로젝트', title: '🚀 팀으로 기획부터 배포까지 완주하는 사이드 프로젝트 멤버 구함', description: '실제 서비스를 목표로 기획부터 디자인, 개발, 배포까지 함께하실 열정적인 분들을 찾습니다.', deadline: 'D-21', views: 2450, members: '프론트엔드 0/4, 백엔드 0/2, 디자인 0/1', tags: ['TypeScript', 'Nodejs', 'React'], position: '프론트엔드', method: '온라인', status: '모집중', authorId: 'admin_id', authorName: '관리자', startDate: '2026-06-01', endDate: '2026-08-30', testRequired: true,
    applicants: [
      {
        userId: 'dummy_user_1', userName: '김코딩', position: '프론트엔드', message: '프론트엔드 리드 개발 경험이 있습니다. 열심히 하겠습니다!', status: 'pending', score: 85, level: '고급 (Expert)',
        feedback: JSON.stringify({
          summary: "React와 TypeScript에 대한 이해도가 매우 높으며, 상태 관리 및 최적화 패턴에 능숙합니다. 다만 백엔드 API 연동 경험은 다소 부족할 수 있어 보입니다.",
          growth_guide: "Next.js의 SSR/ISR 심화 개념을 학습하고, GraphQL이나 tRPC 같은 다양한 통신 방식을 익히면 풀스택으로 성장할 수 있습니다.",
          hiring_guide: "즉시 전력감입니다. 프론트엔드 리드 역할을 맡겨도 손색이 없으며, 팀 내 기술 리딩이 가능할 것으로 보입니다."
        })
      },
      {
        userId: 'dummy_user_2', userName: '이디자', position: '디자인', message: '사용자 경험을 최우선으로 생각하는 디자이너입니다.', status: 'pending', score: 65, level: '중급 (Intermediate)',
        feedback: JSON.stringify({
          summary: "디자인 원칙에 대한 이해가 탄탄하고 Figma 툴 사용이 능숙합니다. 하지만 디자인 시스템 구축 경험은 부족해 보입니다.",
          growth_guide: "Atomic Design 패턴을 적용한 디자인 시스템 구축을 연습하고, 프로토타이핑 툴 활용 능력을 키우는 것을 추천합니다.",
          hiring_guide: "기본기가 튼튼한 중급 디자이너입니다. 시니어의 가이드가 있다면 빠르게 성장하여 1인분을 충분히 해낼 재목입니다."
        })
      }
    ]
  },
  { id: 2, type: '프로젝트', title: 'AI 기반 공동구매 플랫폼 프론트엔드 개발자 긴급 모집합니다', description: '현재 백엔드 2명, 디자이너 1명이 있습니다.', deadline: 'D-29', views: 1880, members: '프론트엔드 0/3, 디자인 0/1', tags: ['JavaScript', 'AWS', 'Nextjs'], position: '프론트엔드', method: '오프라인', status: '모집중', authorId: 'user_dev_01', authorName: '박개발', startDate: '2026-07-15', endDate: '2026-10-15', testRequired: false, applicants: [] },
];

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [projects, setProjects] = useState<Project[]>(() => {
    const saved = localStorage.getItem('portforge_v9_projects');
    return saved ? JSON.parse(saved) : INITIAL_PROJECTS;
  });

  useEffect(() => {
    localStorage.setItem('portforge_v9_projects', JSON.stringify(projects));
  }, [projects]);
  const [notices, setNotices] = useState<Notice[]>([{ id: 1, title: 'Portforge 정식 오픈!', content: '환영합니다. Portforge는 여러분의 프로젝트 여정을 응원합니다.', date: '2024-05-20' }]);
  const [banners, setBanners] = useState<Banner[]>([{ id: 2, title: '해커톤 팀원 모집 게시판 활성화', link: '/events', active: true }]);
  const [reports, setReports] = useState<Report[]>([]);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterResetKey, setFilterResetKey] = useState(0);

  const [teamTasks, setTeamTasks] = useState<TeamTask[]>([
    { id: 1, projectId: 1, title: '메인 페이지 UI 개발', status: '진행중', priority: 'High', owner: '관리자' },
    { id: 2, projectId: 1, title: 'API 명세서 작성', status: '완료', priority: 'Medium', owner: '김철수' }
  ]);
  const [teamMeetings, setTeamMeetings] = useState<TeamMeeting[]>([
    { id: 1, projectId: 1, title: '킥오프 기획 미팅', date: '2024-05-15', content: '프로젝트의 주요 목표와 타겟 유저를 정의함. MVP 기능 리스트를 확정함.', summary: 'AI 요약: MVP 기능 정의 및 타겟 고객 설정 완료.' }
  ]);
  const [teamFiles, setTeamFiles] = useState<TeamFile[]>([
    { id: 1, projectId: 1, name: 'UI_Concept_V1.pdf', size: '4.2MB', date: '2024-05-20', type: 'PDF' }
  ]);

  // 자동 마감 로직 실행
  useEffect(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    setProjects(prev => prev.map(p => {
      const start = new Date(p.startDate);
      start.setHours(0, 0, 0, 0);
      if (start < today && p.status === '모집중') {
        return { ...p, status: '모집완료' as const };
      }
      return p;
    }));
  }, []);

  useEffect(() => {
    const restoreUserSession = async () => {
      const savedUser = localStorage.getItem('portforge_v8_user');
      if (savedUser) {
        const parsedUser = JSON.parse(savedUser);

        // 저장된 사용자 정보로 일단 복원
        setUser(parsedUser);

        // appliedProjects를 API에서 새로 로드 (백그라운드)
        try {
          console.log('🔄 앱 시작 - appliedProjects 갱신 중...');
          const applicationsResponse = await projectAPI.getMyApplications(parsedUser.id);
          let appliedProjects: any[] = [];

          if (applicationsResponse?.data?.applications) {
            appliedProjects = applicationsResponse.data.applications.map((app: any) => ({
              id: app.project_id,
              status: app.status.toLowerCase() as 'pending' | 'accepted' | 'rejected',
              userRole: 'Member' as const,
              selectedPosition: app.position_type,
              projectTitle: app.project_title,
            }));
          }

          // 리더로 생성한 프로젝트도 조회
          try {
            const allProjects = await projectAPI.getProjects();
            const myProjects = allProjects.filter((p: any) => p.user_id === parsedUser.id);
            myProjects.forEach((project: any) => {
              if (!appliedProjects.some(ap => ap.id === project.project_id)) {
                appliedProjects.push({
                  id: project.project_id,
                  status: 'accepted' as const,
                  userRole: 'Leader' as const,
                  selectedPosition: '팀장 / PM',
                  projectTitle: project.title,
                });
              }
            });
          } catch (e) {
            console.warn('프로젝트 목록 조회 실패:', e);
          }

          // 참여 중인 팀(팀원) 조회
          try {
            const teamsResponse = await teamAPI.getUserTeams(parsedUser.id);
            if (teamsResponse?.status === 'success' && teamsResponse.data) {
              teamsResponse.data.forEach((team: any) => {
                if (!appliedProjects.some(ap => ap.id === team.project_id)) {
                  appliedProjects.push({
                    id: team.project_id,
                    status: 'accepted' as const,
                    userRole: team.role === 'LEADER' ? 'Leader' : 'Member',
                    selectedPosition: team.position,
                    projectTitle: team.name, // 팀 이름 = 프로젝트 이름
                  });
                }
              });
            }
          } catch (e) {
            console.warn('팀 목록 조회 실패:', e);
          }

          console.log('✅ appliedProjects 갱신 완료:', appliedProjects);

          if (appliedProjects.length > 0 || (parsedUser.appliedProjects?.length || 0) !== appliedProjects.length) {
            const updatedUser = { ...parsedUser, appliedProjects };
            setUser(updatedUser);
            localStorage.setItem('portforge_v8_user', JSON.stringify(updatedUser));
          }
        } catch (e) {
          console.warn('appliedProjects 갱신 실패:', e);
        }
      }
      setLoading(false);
    };

    restoreUserSession();
  }, []);

  const resetAllFilters = () => setFilterResetKey(prev => prev + 1);

  const login = async (email: string, pass: string) => {
    setLoading(true);
    try {
      // 개발용 비밀번호면 devLogin 사용
      const isDevLogin = pass === 'devpass123';
      const response = isDevLogin
        ? await authAPI.devLogin({ email, password: pass })
        : await authAPI.login({ email, password: pass });

      // 토큰 저장
      localStorage.setItem('access_token', response.access_token);
      if (response.id_token) {
        localStorage.setItem('id_token', response.id_token);
      }

      const userId = response.user.user_id;

      // 사용자 지원 내역 조회
      let appliedProjects: any[] = [];
      try {
        const applicationsResponse = await projectAPI.getMyApplications(userId);
        if (applicationsResponse?.data?.applications) {
          appliedProjects = applicationsResponse.data.applications.map((app: any) => ({
            id: app.project_id,
            status: app.status.toLowerCase() as 'pending' | 'accepted' | 'rejected',
            userRole: 'Member' as const,
            selectedPosition: app.position_type,
            projectTitle: app.project_title,
          }));
        }
      } catch (e) {
        console.warn('지원 내역 조회 실패:', e);
      }

      // 사용자가 생성한 프로젝트(리더) 조회
      try {
        const allProjects = await projectAPI.getProjects();
        const myProjects = allProjects.filter((p: any) => p.user_id === userId);

        // 리더로 생성한 프로젝트 추가 (중복 제외)
        myProjects.forEach((project: any) => {
          if (!appliedProjects.some(ap => ap.id === project.project_id)) {
            appliedProjects.push({
              id: project.project_id,
              status: 'accepted' as const,
              userRole: 'Leader' as const,
              selectedPosition: '팀장 / PM',
              projectTitle: project.title,
            });
          }
        });
      } catch (e) {
        console.warn('프로젝트 목록 조회 실패:', e);
      }

      // 참여 중인 팀(팀원) 조회
      try {
        const teamsResponse = await teamAPI.getUserTeams(userId);
        if (teamsResponse?.status === 'success' && teamsResponse.data) {
          teamsResponse.data.forEach((team: any) => {
            if (!appliedProjects.some(ap => ap.id === team.project_id)) {
              appliedProjects.push({
                id: team.project_id,
                status: 'accepted' as const,
                userRole: team.role === 'LEADER' ? 'Leader' : 'Member',
                selectedPosition: team.position,
                projectTitle: team.name, // 팀 이름 = 프로젝트 이름
              });
            }
          });
        }
      } catch (e) {
        console.warn('팀 목록 조회 실패:', e);
      }

      // 사용자 정보 구성
      const loggedInUser: User = {
        id: userId,
        name: response.user.nickname,
        email: response.user.email,
        role: response.user.role === 'ADMIN' ? 'ADMIN' : 'USER',
        myStacks: response.user.myStacks || [],
        appliedProjects: appliedProjects,
        testResults: []
      };

      console.log('✅ 로그인 완료 - appliedProjects:', appliedProjects);
      console.log('✅ 로그인 완료 - 전체 사용자 정보:', loggedInUser);

      setUser(loggedInUser);
      localStorage.setItem('portforge_v8_user', JSON.stringify(loggedInUser));
    } catch (error: any) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const loginWithSocial = async (provider: string) => {
    try {
      // 백엔드에서 Cognito 설정 가져오기
      const response = await fetch('/auth/social/config');
      if (!response.ok) {
        throw new Error('소셜 로그인 설정을 가져오는데 실패했습니다. 백엔드 서비스가 실행 중인지 확인하세요.');
      }

      const config = await response.json();

      // 설정 검증
      if (!config.cognito_domain || !config.config_status.client_id_set) {
        alert('소셜 로그인 설정이 완료되지 않았습니다.\n\n백엔드 Auth/.env 파일에서 COGNITO_DOMAIN과 COGNITO_APP_CLIENT_ID를 설정해주세요.');
        throw new Error('Cognito 설정이 백엔드에 완료되지 않았습니다.');
      }

      // 백엔드에서 full client_id를 가져와야 하므로 별도 API 호출
      // 보안상 client_id는 마스킹되어 오므로, 백엔드에서 auth URL을 직접 생성하는 것이 좋음
      // 임시로 redirect_uri와 domain만 사용
      const cognitoDomain = config.cognito_domain;
      const redirectUri = config.redirect_uri || (window.location.origin + '/#/auth/callback');

      // 소셜 프로바이더 매핑
      const providerMap: { [key: string]: string } = {
        'Google': 'Google',
        'Kakao': 'Kakao',
        'Naver': 'Naver',
        'GitHub': 'GitHub'
      };

      const identityProvider = providerMap[provider];

      if (!identityProvider) {
        throw new Error(`지원하지 않는 소셜 로그인입니다: ${provider}`);
      }

      // 백엔드에서 소셜 로그인 URL을 가져오는 API 호출
      const urlResponse = await fetch(`/auth/social/login-url?provider=${provider}`);
      if (urlResponse.ok) {
        const urlData = await urlResponse.json();
        window.location.href = urlData.auth_url;
      } else {
        // 백엔드 API가 없으면 에러 메시지 표시
        alert('소셜 로그인 기능이 아직 완전히 구현되지 않았습니다.\n\n백엔드에 /auth/social/login-url API를 추가하거나, 이메일로 로그인해주세요.');
        throw new Error('소셜 로그인 URL API가 백엔드에 구현되어 있지 않습니다.');
      }
    } catch (error: any) {
      console.error('Social login error:', error);
      if (error.message.includes('fetch')) {
        alert('백엔드 서버에 연결할 수 없습니다.\nAuth 서비스가 실행 중인지 확인하세요.');
      }
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (e) {
      console.warn('Logout API failed, clearing local state anyway');
    }
    setUser(null);
    localStorage.removeItem('portforge_v8_user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
  };

  const addProject = (p: any) => {
    if (!user) return;
    const newProj: Project = { ...p, id: Date.now(), views: 0, status: '모집중', authorId: user.id, authorName: user.name, applicants: [] };
    setProjects(prev => [newProj, ...prev]);
    const updatedUser = { ...user, appliedProjects: [...(user.appliedProjects || []), { id: newProj.id, status: 'accepted' as const, userRole: 'Leader' as const }] };
    setUser(updatedUser);
    localStorage.setItem('portforge_v8_user', JSON.stringify(updatedUser));
  };

  const updateProjectStatus = (projectId: number, status: '모집중' | '모집완료') => {
    setProjects(prev => prev.map(p => p.id === projectId ? { ...p, status } : p));
  };

  const applyToProject = async (projectId: number, position: string, message: string) => {
    if (!user) return;

    try {
      // 백엔드 API 호출하여 지원 저장
      await projectAPI.applyToProject(projectId, position, message);

      // 로컬 상태도 업데이트
      setProjects(prev => prev.map(p => {
        if (p.id === projectId) {
          return { ...p, applicants: [...(p.applicants || []), { userId: user.id, userName: user.name, position, message, status: 'pending' as const }] };
        }
        return p;
      }));

      const updatedUser = { ...user, appliedProjects: [...(user.appliedProjects || []), { id: projectId, status: 'pending' as const, userRole: 'Member' as const, selectedPosition: position }] };
      setUser(updatedUser);
      localStorage.setItem('portforge_v8_user', JSON.stringify(updatedUser));
    } catch (error: any) {
      console.error('Failed to apply to project:', error);
      throw error;
    }
  };

  const handleApplication = (projectId: number, targetUserId: string, action: 'accepted' | 'rejected') => {
    setProjects(prev => prev.map(p => {
      if (p.id === projectId) {
        let updatedMembers = p.members;
        const applicant = p.applicants?.find(a => a.userId === targetUserId);

        if (action === 'accepted' && applicant) {
          const parts = p.members.split(', ');
          const newParts = parts.map(part => {
            if (part.includes(applicant.position)) {
              const countMatch = part.match(/(\d+)\/(\d+)/);
              if (countMatch) {
                const curr = parseInt(countMatch[1]);
                const target = parseInt(countMatch[2]);
                return part.replace(`${curr}/${target}`, `${curr + 1}/${target}`);
              }
            }
            return part;
          });
          updatedMembers = newParts.join(', ');
        }

        return {
          ...p,
          members: updatedMembers,
          applicants: p.applicants?.map(a => a.userId === targetUserId ? { ...a, status: action } : a)
        };
      }
      return p;
    }));
  };

  const resolveReport = (id: number, resolutionType: string) => {
    const report = reports.find(r => r.id === id);
    if (!report) return;

    if (resolutionType === 'deleted' && report.targetProjectId) {
      setProjects(prev => prev.filter(p => p.id !== report.targetProjectId));
    }

    setReports(prev => prev.map(r => r.id === id ? { ...r, status: 'resolved', resolutionType } : r));
  };

  const addReport = (report: Omit<Report, 'id' | 'date' | 'status'>) => {
    const newReport: Report = { ...report, id: Date.now(), date: getToday(), status: 'pending' };
    setReports(prev => [newReport, ...prev]);
  };

  const addNotice = (n: any) => setNotices(prev => [{ ...n, id: Date.now(), date: getToday() }, ...prev]);
  const updateNotice = (id: number, n: any) => setNotices(prev => prev.map(x => x.id === id ? { ...x, ...n } : x));
  const deleteNotice = (id: number) => setNotices(prev => prev.filter(x => x.id !== id));

  const addBanner = (b: any) => setBanners(prev => [{ ...b, id: Date.now() }, ...prev]);
  const updateBanner = (id: number, b: any) => setBanners(prev => prev.map(x => x.id === id ? { ...x, ...b } : x));
  const deleteBanner = (id: number) => setBanners(prev => prev.filter(x => x.id !== id));

  const markNotificationsRead = () => {
    if (!user) return;
    setNotifications(prev => prev.map(n => (n.userId === user.id || (user.role === 'ADMIN' && n.role === 'ADMIN')) ? { ...n, read: true } : n));
  };

  const changePassword = async (old: string, newP: string) => {
    if (!newP) throw new Error('새 비밀번호를 입력해주세요.');
    if (!user) throw new Error('로그인이 필요합니다.');
    await authAPI.changePassword(user.id, old, newP);
  };

  const addEvent = (event: Omit<EventItem, 'id'>) => {
    setEvents(prev => [{ ...event, id: Date.now() }, ...prev]);
  };

  const checkNickname = async (name: string) => {
    try {
      const result = await authAPI.checkNickname(name);
      return { available: result.available, message: result.message };
    } catch (error) {
      console.error('Nickname check failed:', error);
      return { available: false, message: '닉네임 확인에 실패했습니다.' };
    }
  };

  const addTestResult = (result: TestResult) => {
    if (!user) return;
    const updatedUser = {
      ...user,
      testResults: [...(user.testResults || []), result]
    };
    setUser(updatedUser);
    localStorage.setItem('portforge_v8_user', JSON.stringify(updatedUser));
  };

  const addTeamTask = (task: Omit<TeamTask, 'id'>) => setTeamTasks(prev => [...prev, { ...task, id: Date.now() }]);
  const updateTeamTask = (id: number, updates: Partial<TeamTask>) => setTeamTasks(prev => prev.map(t => t.id === id ? { ...t, ...updates } : t));
  const addTeamMeeting = (meeting: Omit<TeamMeeting, 'id'>) => setTeamMeetings(prev => [...prev, { ...meeting, id: Date.now() }]);
  const updateTeamMeeting = (id: number, updates: Partial<TeamMeeting>) => setTeamMeetings(prev => prev.map(m => m.id === id ? { ...m, ...updates } : m));
  const addTeamFile = (file: Omit<TeamFile, 'id'>) => setTeamFiles(prev => [...prev, { ...file, id: Date.now() }]);

  return (
    <AuthContext.Provider value={{
      user, loading, projects, notices, banners, reports, events, notifications, filterResetKey,
      teamTasks, teamMeetings, teamFiles,
      resetAllFilters,
      login, logout, updateProfile: async (d) => {
        await authAPI.updateProfile(d);
        setUser(u => {
          if (!u) return null;
          const updated = { ...u, ...d };
          localStorage.setItem('portforge_v8_user', JSON.stringify(updated));
          return updated;
        });
      }, validateName: (n) => ({ available: true, message: '' }),
      applyToProject, handleApplication, toggleLike: (id) => {
        if (!user) return;
        const liked = user.likedProjects || [];
        const updated = liked.includes(id) ? liked.filter(x => x !== id) : [...liked, id];
        setUser({ ...user, likedProjects: updated });
      }, addProject, updateProjectStatus, deleteProject: (id) => setProjects(p => p.filter(x => x.id !== id)),
      addNotice, updateNotice, deleteNotice, addBanner, updateBanner, deleteBanner,
      addReport, resolveReport, addEvent, markNotificationsRead, changePassword,
      loginWithSocial, checkNickname, addTestResult,
      addTeamTask, updateTeamTask, addTeamMeeting, updateTeamMeeting, addTeamFile
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth error');
  return context;
};
