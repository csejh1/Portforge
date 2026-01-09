/**
 * TeamSpacePage - 팀 스페이스 메인 페이지
 * 
 * 기능:
 * - 대시보드: 팀 현황, 활동 내역, 팀원 목록
 * - 팀 채팅: 실시간 채팅 + 회의 시작/종료 기능
 * - 회의록 관리: AI 생성 회의록 목록/상세 조회
 * - 업무 현황: 칸반 보드
 * - 파일 공유: 팀 파일 업로드/다운로드
 * - 포트폴리오: AI 자동 완성 포트폴리오 생성
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import Card from '../components/Card';
import { useAuth } from '../contexts/AuthContext';
import { generatePortfolio, PortfolioResult } from '../api/aiClient';
import { generateDailyMinutes, getDailyMinutesList, getMinutesContent, MinutesResponse, saveChatMessage, getChatMessages } from '../api/chatClient';
import { teamAPI } from '../api/apiClient';

interface ChatMessage {
  user: string;
  msg: string;
  time: string;
  timestamp: number;
  isInMeeting?: boolean;
}

// 토스트 알림 타입
interface Toast {
  id: number;
  type: 'info' | 'success' | 'error' | 'loading';
  message: string;
  step?: number;
  totalSteps?: number;
}

// 토스트 컴포넌트
const ToastContainer = ({ toasts, onRemove }: { toasts: Toast[], onRemove: (id: number) => void }) => (
  <div className="fixed bottom-6 right-6 z-50 space-y-3">
    {toasts.map(toast => (
      <div
        key={toast.id}
        className={`
          flex items-center gap-3 px-5 py-4 rounded-2xl shadow-xl min-w-[320px] max-w-[400px]
          animate-slideUp backdrop-blur-sm border
          ${toast.type === 'loading' ? 'bg-blue-50/95 border-blue-200 text-blue-800' : ''}
          ${toast.type === 'success' ? 'bg-green-50/95 border-green-200 text-green-800' : ''}
          ${toast.type === 'error' ? 'bg-red-50/95 border-red-200 text-red-800' : ''}
          ${toast.type === 'info' ? 'bg-gray-50/95 border-gray-200 text-gray-800' : ''}
        `}
      >
        <div className="flex-shrink-0">
          {toast.type === 'loading' && (
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          )}
          {toast.type === 'success' && <span className="text-xl">✅</span>}
          {toast.type === 'error' && <span className="text-xl">❌</span>}
          {toast.type === 'info' && <span className="text-xl">💬</span>}
        </div>
        <div className="flex-1">
          <p className="font-bold text-sm">{toast.message}</p>
          {toast.step && toast.totalSteps && (
            <div className="mt-2">
              <div className="flex justify-between text-xs mb-1">
                <span>진행 중...</span>
                <span>{toast.step}/{toast.totalSteps}</span>
              </div>
              <div className="h-1.5 bg-blue-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full transition-all duration-500"
                  style={{ width: `${(toast.step / toast.totalSteps) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
        {toast.type !== 'loading' && (
          <button
            onClick={() => onRemove(toast.id)}
            className="text-gray-400 hover:text-gray-600 text-lg"
          >
            ×
          </button>
        )}
      </div>
    ))}
  </div>
);

// 토스트 훅
const useToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const idRef = useRef(0);

  const addToast = useCallback((type: Toast['type'], message: string, step?: number, totalSteps?: number): number => {
    const id = ++idRef.current;
    setToasts(prev => [...prev, { id, type, message, step, totalSteps }]);

    // 성공/에러는 4초 후 자동 제거
    if (type === 'success' || type === 'error' || type === 'info') {
      setTimeout(() => removeToast(id), 4000);
    }
    return id;
  }, []);

  const updateToast = useCallback((id: number, updates: Partial<Toast>) => {
    setToasts(prev => prev.map(t => t.id === id ? { ...t, ...updates } : t));
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return { toasts, addToast, updateToast, removeToast };
};

const TeamSpacePage: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialTab = queryParams.get('tab') as 'dashboard' | 'chat' | 'meetings' | 'jira' | 'files' | 'portfolio' || 'dashboard';

  const [activeTab, setActiveTab] = useState<'dashboard' | 'chat' | 'meetings' | 'jira' | 'files' | 'portfolio'>(initialTab);
  const { toasts, addToast, updateToast, removeToast } = useToast();

  // URL 쿼리 파라미터 변경 시 탭 업데이트
  useEffect(() => {
    const tab = queryParams.get('tab') as 'dashboard' | 'chat' | 'meetings' | 'jira' | 'files' | 'portfolio';
    if (tab && ['dashboard', 'chat', 'meetings', 'jira', 'files', 'portfolio'].includes(tab)) {
      setActiveTab(tab);
    }
  }, [location.search]);

  return (
    <div className="flex flex-col lg:flex-row gap-8 animate-fadeIn py-6">
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <aside className="lg:w-64 space-y-2">
        <SidebarItem active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} label="대시보드" icon="📊" />
        <SidebarItem active={activeTab === 'chat'} onClick={() => setActiveTab('chat')} label="팀 채팅" icon="💬" />
        <SidebarItem active={activeTab === 'meetings'} onClick={() => setActiveTab('meetings')} label="회의록 관리" icon="📄" />
        <SidebarItem active={activeTab === 'jira'} onClick={() => setActiveTab('jira')} label="업무 현황" icon="📋" />
        <SidebarItem active={activeTab === 'files'} onClick={() => setActiveTab('files')} label="파일 공유" icon="📁" />
        <SidebarItem active={activeTab === 'portfolio'} onClick={() => setActiveTab('portfolio')} label="포트폴리오" icon="💼" />
      </aside>

      <main className="flex-1 bg-white rounded-[2.5rem] shadow-sm border border-gray-100 overflow-hidden min-h-[700px]">
        {activeTab === 'dashboard' && <TeamDashboard isAdmin={user?.role === 'ADMIN' || true} />}
        {activeTab === 'meetings' && <MeetingManager />}
        {activeTab === 'jira' && <JiraBoard />}
        {activeTab === 'files' && <FileStorage />}
        {activeTab === 'portfolio' && <ProjectPortfolio />}
        {activeTab === 'chat' && <TeamChat addToast={addToast} updateToast={updateToast} removeToast={removeToast} />}
      </main>
    </div>
  );
};

const SidebarItem = ({ active, onClick, label, icon }: any) => (
  <button
    onClick={onClick}
    className={`w-full text-left px-6 py-4 rounded-2xl font-bold transition-all flex items-center gap-3 ${active ? 'bg-primary text-white shadow-lg' : 'text-text-sub hover:bg-gray-50'
      }`}
  >
    <span className="text-lg">{icon}</span>
    {label}
  </button>
);


const TeamDashboard = ({ isAdmin }: { isAdmin: boolean }) => {
  const { id } = useParams();
  const [projectInfo, setProjectInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [invitationCode, setInvitationCode] = useState('');

  // 정적 데모 데이터 (백엔드 연결 실패 시 사용)
  const DEMO_PROJECT_INFO = {
    project: {
      id: 9999,
      title: '[UI 테스트] Portforge 팀 스페이스 데모',
      type: 'PROJECT',
      status: '진행중',
      start_date: '2026-02-01',
      end_date: '2026-06-30'
    },
    team: {
      id: 1,
      name: 'Portforge Demo Team'
    },
    members: [
      { user_id: 'admin_id', nickname: '관리자', role: 'LEADER', position_type: 'PM' },
      { user_id: 'user_2', nickname: '김철수', role: 'MEMBER', position_type: '프론트엔드' },
      { user_id: 'user_3', nickname: '이영희', role: 'MEMBER', position_type: '백엔드' }
    ]
  };

  // 프로젝트 정보 로드 (실패 시 정적 데이터 사용)
  useEffect(() => {
    const loadProjectInfo = async () => {
      if (!id) {
        // id가 없으면 데모 데이터 사용
        setProjectInfo(DEMO_PROJECT_INFO);
        setLoading(false);
        return;
      }

      try {
        console.log('🔄 프로젝트 팀 정보 로드 중...');
        const response = await fetch(`/api/v1/integration/project-team-info/${id}`);

        if (response.ok) {
          const result = await response.json();
          if (result.status === 'success') {
            console.log('✅ 프로젝트 팀 정보 로드 성공:', result.data);
            
            // 멤버 닉네임이 user_id와 같으면 Auth 서비스에서 닉네임 조회
            let projectData = result.data;
            if (projectData.members && projectData.members.length > 0) {
              const needsNickname = projectData.members.some((m: any) => 
                m.nickname === m.user_id || !m.nickname
              );
              
              if (needsNickname) {
                try {
                  const { authAPI } = await import('../api/apiClient');
                  const userIds = projectData.members.map((m: any) => m.user_id);
                  const usersData = await authAPI.getUsersBatch(userIds);
                  
                  if (usersData && usersData.length > 0) {
                    const usersMap: Record<string, string> = {};
                    usersData.forEach((u: any) => {
                      usersMap[u.user_id] = u.nickname || u.email?.split('@')[0] || u.user_id;
                    });
                    
                    projectData = {
                      ...projectData,
                      members: projectData.members.map((m: any) => ({
                        ...m,
                        nickname: usersMap[m.user_id] || m.nickname || m.user_id
                      }))
                    };
                  }
                } catch (e) {
                  console.warn('닉네임 조회 실패:', e);
                }
              }
            }
            
            setProjectInfo(projectData);
            setLoading(false);
            return;
          }
        }

        // 백엔드 실패 시 정적 데이터 사용
        console.log('⚠️ 백엔드 연결 실패, 정적 데이터 사용');
        setProjectInfo(DEMO_PROJECT_INFO);
      } catch (error) {
        console.error('❌ 프로젝트 팀 정보 로드 실패:', error);
        setProjectInfo(DEMO_PROJECT_INFO);
      } finally {
        setLoading(false);
      }
    };

    loadProjectInfo();
  }, [id]);

  const generateCode = () => {
    const code = Math.random().toString(36).substring(2, 8).toUpperCase();
    setInvitationCode(code);
  };

  // D-day 계산
  const calculateDDay = (endDate: string) => {
    if (!endDate) return 'D-?';
    const today = new Date();
    const end = new Date(endDate);
    const diffTime = end.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? `D-${diffDays}` : '완료';
  };

  // 진행률 계산
  const calculateProgress = (startDate: string, endDate: string) => {
    if (!startDate || !endDate) return 0;
    const today = new Date();
    const start = new Date(startDate);
    const end = new Date(endDate);
    const totalDays = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);
    const passedDays = (today.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);
    return Math.max(0, Math.min(100, Math.round((passedDays / totalDays) * 100)));
  };

  if (loading) {
    return (
      <div className="p-10 space-y-10">
        <div className="text-center py-20 text-gray-400">
          <p className="text-2xl mb-2">⏳</p>
          <p>프로젝트 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (!projectInfo) {
    return (
      <div className="p-10 space-y-10">
        <div className="text-center py-20 text-gray-400">
          <p className="text-2xl mb-2">❌</p>
          <p>프로젝트 정보를 찾을 수 없습니다.</p>
        </div>
      </div>
    );
  }

  const project = projectInfo.project;
  const team = projectInfo.team;
  const members = projectInfo.members || [];

  return (
    <div className="p-10 space-y-10">
      <div className="flex justify-between items-center">
        <div className="space-y-1">
          <h2 className="text-3xl font-black text-text-main tracking-tight">팀 대시보드</h2>
          <p className="text-text-sub font-bold text-sm">{project.title}</p>
        </div>
        {isAdmin && (
          <div className="flex items-center gap-3">
            {invitationCode ? (
              <div className="bg-secondary/10 text-secondary px-4 py-2 rounded-xl text-sm font-black border border-secondary/20 animate-slideDown">
                초대 코드: <span className="underline select-all">{invitationCode}</span>
              </div>
            ) : (
              <button onClick={generateCode} className="bg-secondary text-white px-5 py-2.5 rounded-xl text-sm font-black shadow-lg shadow-secondary/10">+ 팀원 초대</button>
            )}
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-4 gap-6">
        <StatCard
          label="마감일"
          value={calculateDDay(project.end_date)}
          sub={project.end_date}
        />
        <StatCard
          label="전체 진행률"
          value={`${calculateProgress(project.start_date, project.end_date)}%`}
        />
        <StatCard
          label="팀원"
          value={`${members.length}명`}
          sub={`${project.type === 'PROJECT' ? '프로젝트' : '스터디'} 팀`}
        />
        <StatCard
          label="상태"
          value={project.status || '진행중'}
        />
      </div>

      <div className="grid lg:grid-cols-3 gap-10 pt-4">
        <section className="lg:col-span-2 space-y-6">
          <h3 className="text-xl font-black text-text-main flex items-center gap-2">
            <span className="w-1.5 h-6 bg-primary rounded-full"></span>
            최근 활동
          </h3>
          <div className="space-y-4">
            {/* 팀장 정보를 members 배열에서 찾아서 표시 */}
            {(() => {
              const leader = members.find((m: any) => (m.role || '').toUpperCase() === 'LEADER');
              const leaderName = leader ? leader.nickname || leader.user_id : '팀장';
              return (
                <>
                  <ActivityItem user={`${leaderName}(팀장)`} action="팀 스페이스를 생성했습니다." time="방금 전" icon="🚀" />
                  <ActivityItem user="시스템" action="프로젝트가 시작되었습니다." time="오늘" icon="📋" />
                </>
              );
            })()}
          </div>
        </section>

        <section className="space-y-6">
          <h3 className="text-xl font-black text-text-main">참여 팀원</h3>
          <div className="bg-gray-50/50 p-6 rounded-[2rem] border border-gray-100 space-y-4">
            {/* 팀장과 팀원들을 members 배열에서 가져와서 표시 */}
            {members.map((member: any, idx: number) => {
              const isLeader = (member.role || '').toUpperCase() === 'LEADER';
              // 팀장인 경우 무조건 PM으로 표시, 아니면 실제 포지션 사용
              const roleDisplay = isLeader ? '팀장 / PM' : `팀원 / ${member.position_type}`;

              return (
                <MemberListItem
                  key={idx}
                  name={member.nickname || member.user_id}
                  role={roleDisplay}
                  avatar={member.nickname || member.user_id}
                  isMe={false}
                />
              );
            })}

            {/* 팀원이 없는 경우 */}
            {members.length === 0 && (
              <div className="text-center py-8 text-gray-400">
                <p className="text-sm">아직 팀원이 없습니다.</p>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, sub }: any) => (
  <div className="bg-white p-6 rounded-[2rem] border border-gray-100 shadow-sm">
    <p className="text-[10px] font-black text-text-sub uppercase tracking-widest">{label}</p>
    <p className="text-3xl font-black text-primary mt-1">{value}</p>
    {sub && <p className="text-[10px] text-gray-300 font-bold mt-1">{sub}</p>}
  </div>
);

const ActivityItem = ({ user, action, time, icon }: any) => (
  <div className="flex gap-4 p-5 bg-gray-50 rounded-2xl border border-transparent hover:border-gray-100 transition-all">
    <div className="w-10 h-10 bg-white rounded-xl shadow-sm flex items-center justify-center text-xl">{icon}</div>
    <div className="flex-grow">
      <p className="text-sm font-bold text-text-main"><span className="text-primary">{user}</span>님이 {action}</p>
      <p className="text-[10px] text-gray-400 font-medium mt-0.5">{time}</p>
    </div>
  </div>
);

const MemberListItem = ({ name, role, avatar, isMe }: any) => (
  <div className="flex items-center gap-3">
    <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${avatar}`} className="w-8 h-8 rounded-full border border-gray-100" alt={name} />
    <div className="flex-grow">
      <p className={`text-xs font-black ${isMe ? 'text-primary' : 'text-text-main'}`}>{name}</p>
      <p className="text-[10px] text-gray-400 font-medium">{role}</p>
    </div>
    {isMe && <span className="text-[9px] bg-primary/10 text-primary px-1.5 py-0.5 rounded font-black">ME</span>}
  </div>
);


// 팀 채팅 컴포넌트 (회의 시작/종료 기능 포함)
const TeamChat = ({
  addToast,
  updateToast,
  removeToast
}: {
  addToast: (type: Toast['type'], message: string, step?: number, totalSteps?: number) => number;
  updateToast: (id: number, updates: Partial<Toast>) => void;
  removeToast: (id: number) => void;
}) => {
  const { user } = useAuth();
  const { id } = useParams(); // URL에서 프로젝트 ID 가져오기

  // URL 파라미터에서 projectId 가져오기 (팀별 고유 채팅)
  const projectId = Number(id) || 1;
  const teamId = projectId; // 팀 ID는 프로젝트 ID와 동일하게 사용

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  // user 정보에서 현재 사용자 이름 가져오기
  const currentUser = user?.nickname || user?.name || user?.email?.split('@')[0] || '익명';

  // WebSocket 연결 상태
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // 초기 메시지 로드
  useEffect(() => {
    const loadMessages = async () => {
      try {
        const { messages: loadedMessages } = await getChatMessages(teamId, projectId);
        // ChatMessage 타입 변환 (필드명 매핑)
        const mappedMessages: ChatMessage[] = loadedMessages.map((m: any) => ({
          user: m.user,
          msg: m.msg,
          time: m.time,
          timestamp: m.timestamp,
          isInMeeting: m.isInMeeting
        }));
        setMessages(mappedMessages);
      } catch (error) {
        console.error('채팅 로드 실패:', error);
      }
    };
    loadMessages();
  }, [teamId, projectId]);

  // WebSocket 연결 (실시간 채팅)
  useEffect(() => {
    // WebSocket 서버 URL (Support Service)
    const wsUrl = `ws://localhost:8004/ws/chat/${projectId}`;

    console.log('🔌 WebSocket 연결 시도:', wsUrl);

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('✅ WebSocket 연결됨');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📩 새 메시지 수신:', data);

        // 다른 사용자가 보낸 메시지만 추가 (내가 보낸 건 이미 UI에 있음)
        const senderName = data.senderName || data.user_id;
        if (senderName !== currentUser) {
          const newMessage: ChatMessage = {
            user: senderName,
            msg: data.message,
            time: data.timestamp ? new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            timestamp: data.timestamp ? new Date(data.timestamp).getTime() : Date.now(),
            isInMeeting: false
          };
          setMessages(prev => [...prev, newMessage]);
        }
      } catch (e) {
        console.error('메시지 파싱 오류:', e);
      }
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket 연결 끊김');
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket 오류:', error);
      setIsConnected(false);
    };

    // 컴포넌트 언마운트 시 연결 종료
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [projectId, currentUser]);

  // 회의 상태 초기화 (localStorage 확인 등 필요 시 구현)

  // 회의 상태
  const [isMeetingActive, setIsMeetingActive] = useState(false);
  const [meetingStartTime, setMeetingStartTime] = useState<Date | null>(null);
  const [meetingMessages, setMeetingMessages] = useState<ChatMessage[]>([]);
  const [elapsedTime, setElapsedTime] = useState('00:00');
  const [isGenerating, setIsGenerating] = useState(false);

  const chatContainerRef = useRef<HTMLDivElement>(null);

  // 자동 스크롤
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // 회의 시간 타이머
  useEffect(() => {
    if (!isMeetingActive || !meetingStartTime) return;

    const interval = setInterval(() => {
      const now = new Date();
      const diff = Math.floor((now.getTime() - meetingStartTime.getTime()) / 1000);
      const mins = Math.floor(diff / 60).toString().padStart(2, '0');
      const secs = (diff % 60).toString().padStart(2, '0');
      setElapsedTime(`${mins}:${secs}`);
    }, 1000);

    return () => clearInterval(interval);
  }, [isMeetingActive, meetingStartTime]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    try {
      const now = new Date();
      const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const messageText = input;

      const newMessage: ChatMessage = {
        user: currentUser,
        msg: messageText,
        time,
        timestamp: now.getTime(),
        isInMeeting: isMeetingActive
      };

      // UI 즉시 업데이트 (낙관적 업데이트)
      setMessages(prev => [...prev, newMessage]);
      setInput('');

      // WebSocket으로 메시지 전송 (실시간 브로드캐스트)
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          user_id: currentUser,
          senderName: currentUser,
          message: messageText,
          timestamp: now.toISOString()
        }));
        console.log('📤 WebSocket으로 메시지 전송');
      } else {
        // WebSocket이 연결되지 않은 경우 REST API로 저장
        await saveChatMessage(teamId, projectId, currentUser, messageText, isMeetingActive);
        console.log('📤 REST API로 메시지 저장');
      }

      // 회의 중이면 회의 메시지에도 추가
      if (isMeetingActive) {
        setMeetingMessages(prev => [...prev, newMessage]);
      }
    } catch (error) {
      console.error('메시지 전송 실패:', error);
      addToast('error', '메시지 전송에 실패했습니다.');
    }
  };

  const handleStartMeeting = () => {
    setIsMeetingActive(true);
    setMeetingStartTime(new Date());
    setMeetingMessages([]);
    setElapsedTime('00:00');
    addToast('info', '🎙️ 회의가 시작되었습니다. 대화 내용이 기록됩니다.');
  };

  const handleEndMeeting = async () => {
    if (meetingMessages.length === 0) {
      addToast('error', '회의 중 대화 내용이 없습니다.');
      return;
    }

    if (!confirm(`회의를 종료하고 ${meetingMessages.length}개의 메시지로 회의록을 생성하시겠습니까?`)) return;

    // 회의 종료 처리
    setIsMeetingActive(false);
    setMeetingStartTime(null);
    setIsGenerating(true);

    // localStorage에 생성 중 상태 저장
    localStorage.setItem('minutes_generating', 'true');
    localStorage.setItem('minutes_generating_time', new Date().toISOString());

    // 토스트로 단계별 진행 표시
    const toastId = addToast('loading', '📝 채팅 로그 수집 중...', 1, 3);

    try {
      // 단계 1: 채팅 로그 수집 (최소 2초 표시)
      await new Promise(resolve => setTimeout(resolve, 2000));
      updateToast(toastId, { message: '🤖 AI가 회의록 작성 중...', step: 2 });

      // 단계 2: AI 회의록 생성 (실제 API 호출)
      await generateDailyMinutes(teamId, projectId, meetingMessages);

      // 단계 3: 저장 완료
      updateToast(toastId, { message: '💾 저장 완료!', step: 3 });
      await new Promise(resolve => setTimeout(resolve, 800));

      // 성공 토스트
      removeToast(toastId);
      addToast('success', '✅ 회의록이 생성되었습니다! 회의록 관리 탭에서 확인하세요.');

      setMeetingMessages([]);

      // localStorage 정리
      localStorage.removeItem('minutes_generating');
      localStorage.removeItem('minutes_generating_time');
    } catch (e: any) {
      removeToast(toastId);
      addToast('error', `회의록 생성 실패: ${e.message || e}`);

      // localStorage 정리
      localStorage.removeItem('minutes_generating');
      localStorage.removeItem('minutes_generating_time');
    } finally {
      setIsGenerating(false);
    }
  };

  const users = ['김민준', '박지민', '이서윤', '혁신가(나)'];

  return (
    <div className="flex flex-col h-full min-h-[700px]">
      {/* 회의 상태 헤더 */}
      <div className={`p-4 border-b ${isMeetingActive ? 'bg-red-50 border-red-200' : 'bg-white border-gray-100'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* WebSocket 연결 상태 */}
            <div className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium ${isConnected ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-400'}`}></div>
              {isConnected ? '실시간 연결됨' : '연결 중...'}
            </div>

            {isMeetingActive ? (
              <>
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <span className="font-bold text-red-600">🎙️ 회의 진행 중</span>
                <span className="text-red-500 font-mono bg-red-100 px-2 py-1 rounded">{elapsedTime}</span>
                <span className="text-sm text-red-400">({meetingMessages.length}개 메시지 기록됨)</span>
              </>
            ) : (
              <>
                <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                <span className="font-bold text-gray-500">회의 대기 중</span>
                <span className="text-xs text-gray-400">회의 시작 버튼을 눌러 회의를 시작하세요</span>
              </>
            )}
          </div>
          <div className="flex gap-2">
            {!isMeetingActive ? (
              <button
                onClick={handleStartMeeting}
                className="bg-green-500 text-white px-5 py-2.5 rounded-xl font-bold hover:bg-green-600 transition-colors flex items-center gap-2 shadow-lg shadow-green-500/20"
              >
                <span>🎙️</span> 회의 시작
              </button>
            ) : (
              <button
                onClick={handleEndMeeting}
                disabled={isGenerating}
                className="bg-red-500 text-white px-5 py-2.5 rounded-xl font-bold hover:bg-red-600 transition-colors disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-red-500/20"
              >
                <span>⏹️</span> 회의 종료 및 회의록 생성
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 채팅 영역 */}
      <div ref={chatContainerRef} className="flex-1 p-6 overflow-y-auto space-y-4 bg-gray-50/50">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-4xl mb-4">💬</p>
            <p className="font-bold">채팅을 시작하세요</p>
            <p className="text-sm mt-2">회의 시작 버튼을 누르면 해당 시점부터의 대화가 회의록에 기록됩니다</p>
          </div>
        )}
        {messages.map((m, i) => {
          const isMyMessage = m.user === '혁신가(나)' || m.user === currentUser;
          return (
            <div key={i} className={`flex flex-col ${isMyMessage ? 'items-end' : 'items-start'}`}>
              <span className="text-xs text-gray-400 mb-1 flex items-center gap-1">
                {m.isInMeeting && <span className="w-2 h-2 bg-red-500 rounded-full" title="회의 중 메시지"></span>}
                {m.user} • {m.time}
              </span>
              <div className={`px-4 py-3 rounded-2xl max-w-[70%] font-medium shadow-sm ${isMyMessage
                ? 'bg-primary text-white'
                : 'bg-white border border-gray-100'
                } ${m.isInMeeting ? 'ring-2 ring-red-200' : ''}`}>
                {m.msg}
              </div>
            </div>
          );
        })}
      </div>

      {/* 사용자 + 입력 영역 */}
      <div className="p-4 bg-white border-t border-gray-100 space-y-3">
        <div className="flex gap-2 text-sm items-center">
          <span className="text-gray-400 font-medium">보내는 사람:</span>
          <span className="px-3 py-1 rounded-lg font-bold bg-primary text-white">
            {currentUser}
          </span>
        </div>
        <div className="flex gap-2">
          <input
            className="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary transition-colors"
            placeholder={isMeetingActive ? "회의 중... 메시지를 입력하세요 (회의록에 기록됩니다)" : "메시지 입력..."}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && sendMessage()}
          />
          <button
            onClick={sendMessage}
            className="bg-primary text-white px-6 rounded-xl font-bold hover:bg-primary/90 transition-colors"
          >
            전송
          </button>
        </div>
      </div>
    </div>
  );
};


const MeetingManager = () => {
  const { id } = useParams(); // URL에서 프로젝트 ID 가져오기
  const [minutesList, setMinutesList] = useState<MinutesResponse[]>([]);
  const [selectedMinutes, setSelectedMinutes] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [viewLoading, setViewLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // URL 파라미터에서 projectId 가져오기 (팀별 고유 회의록)
  const projectId = Number(id) || 1;
  const teamId = projectId; // 팀 ID는 프로젝트 ID와 동일하게 사용

  // localStorage에서 생성 중 상태 확인
  const [isMinutesGenerating, setIsMinutesGenerating] = useState(() => {
    const generating = localStorage.getItem('minutes_generating');
    return generating === 'true';
  });

  const handleCancelMinutesGeneration = () => {
    if (confirm('회의록 생성을 취소하시겠습니까?')) {
      setIsMinutesGenerating(false);
      localStorage.removeItem('minutes_generating');
      localStorage.removeItem('minutes_generating_time');
    }
  };

  useEffect(() => {
    const loadMinutesList = async () => {
      setLoading(true);
      setError(null);
      try {
        const list = await getDailyMinutesList(teamId, projectId);
        setMinutesList(list);

        // 목록이 로드되면 생성 중 상태 해제
        if (isMinutesGenerating) {
          setIsMinutesGenerating(false);
          localStorage.removeItem('minutes_generating');
          localStorage.removeItem('minutes_generating_time');
        }
      } catch (e: any) {
        console.error('회의록 목록 조회 실패:', e);
        setError('회의록 목록을 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    loadMinutesList();

    // 생성 중일 때 5초마다 목록 새로고침
    let interval: NodeJS.Timeout | null = null;
    if (isMinutesGenerating) {
      interval = setInterval(loadMinutesList, 5000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [teamId, projectId, isMinutesGenerating]);

  const loadMinutesList = async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await getDailyMinutesList(teamId, projectId);
      setMinutesList(list);
    } catch (e: any) {
      console.error('회의록 목록 조회 실패:', e);
      setError('회의록 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewMinutes = async (reportId: number) => {
    setViewLoading(true);
    setError(null);
    try {
      const content = await getMinutesContent(reportId);
      console.log('Loaded minutes content:', content);
      if (!content || (typeof content === 'object' && Object.keys(content).length === 0)) {
        setError('회의록 내용이 비어있습니다.');
        return;
      }
      setSelectedMinutes(content);
    } catch (e: any) {
      console.error('회의록 내용 조회 실패:', e);
      setError(`회의록 내용 조회 실패: ${e.message || e}`);
    } finally {
      setViewLoading(false);
    }
  };

  return (
    <div className="p-10 space-y-8 animate-slideDown">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">회의록 관리</h2>
        <button
          onClick={loadMinutesList}
          className="bg-gray-100 text-gray-600 px-4 py-2 rounded-xl font-bold hover:bg-gray-200 transition-colors"
        >
          🔄 새로고침
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl">
          ⚠️ {error}
        </div>
      )}

      {isMinutesGenerating && (
        <div className="bg-blue-50 border border-blue-200 text-blue-600 px-4 py-3 rounded-xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <span>🤖 AI가 회의록을 생성하는 중입니다... (자동으로 업데이트됩니다)</span>
          </div>
          <button
            onClick={handleCancelMinutesGeneration}
            className="text-red-600 hover:text-red-800 font-bold text-sm underline"
          >
            취소
          </button>
        </div>
      )}

      {loading ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-2xl mb-2">⏳</p>
          <p>회의록 목록을 불러오는 중...</p>
        </div>
      ) : minutesList.length === 0 ? (
        <div className="p-12 border-2 border-dashed border-gray-100 rounded-[2.5rem] text-center space-y-4 bg-gray-50/30">
          <div className="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center text-3xl mx-auto mb-2">📄</div>
          <p className="text-text-secondary font-medium">아직 등록된 회의록이 없습니다.</p>
          <p className="text-sm text-gray-400">팀 채팅에서 회의를 시작하고 종료하면 회의록이 자동으로 생성됩니다.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {minutesList.map(minutes => (
            <div
              key={minutes.report_id}
              className="flex items-center justify-between p-5 border border-gray-100 rounded-2xl hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center text-xl">📄</div>
                <div>
                  <p className="font-bold text-text-main">{minutes.title}</p>
                  <p className="text-[10px] text-gray-400 font-bold">
                    {new Date(minutes.created_at).toLocaleString('ko-KR')} • {minutes.status}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleViewMinutes(minutes.report_id)}
                disabled={viewLoading}
                className="text-primary font-black text-sm hover:underline disabled:opacity-50"
              >
                {viewLoading ? '로딩...' : '보기'}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* 회의록 내용 모달 */}
      {selectedMinutes && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedMinutes(null)}>
          <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-8" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">회의록 내용</h3>
              <button onClick={() => setSelectedMinutes(null)} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
            </div>
            <div className="prose max-w-none space-y-6">
              {/* 날짜 */}
              {selectedMinutes.date && (
                <div className="bg-gray-50 p-4 rounded-xl">
                  <span className="text-sm text-gray-500">📅 날짜:</span>
                  <span className="ml-2 font-bold">{selectedMinutes.date}</span>
                </div>
              )}

              {/* 참석자 */}
              {selectedMinutes.attendees && selectedMinutes.attendees.length > 0 && (
                <div>
                  <h4 className="font-bold text-primary mb-2">👥 참석자</h4>
                  <p className="text-gray-700">{selectedMinutes.attendees.join(', ')}</p>
                </div>
              )}

              {/* 안건 */}
              {selectedMinutes.agenda && (
                <div>
                  <h4 className="font-bold text-primary mb-2">📌 안건</h4>
                  <p className="text-gray-700">{selectedMinutes.agenda}</p>
                </div>
              )}

              {/* 요약 */}
              {selectedMinutes.summary && (
                <div>
                  <h4 className="font-bold text-primary mb-2">📋 회의 요약</h4>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedMinutes.summary}</p>
                </div>
              )}

              {/* 결정사항 */}
              {selectedMinutes.decisions && selectedMinutes.decisions.length > 0 && (
                <div>
                  <h4 className="font-bold text-primary mb-2">✅ 주요 결정 사항</h4>
                  <ul className="list-disc list-inside text-gray-700 space-y-1">
                    {(Array.isArray(selectedMinutes.decisions) ? selectedMinutes.decisions : [selectedMinutes.decisions]).map((d: string, i: number) => (
                      <li key={i}>{d}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* 액션 아이템 */}
              {selectedMinutes.action_items && selectedMinutes.action_items.length > 0 && (
                <div>
                  <h4 className="font-bold text-primary mb-2">📝 액션 아이템</h4>
                  <ul className="space-y-2">
                    {(Array.isArray(selectedMinutes.action_items) ? selectedMinutes.action_items : [selectedMinutes.action_items]).map((item: any, i: number) => (
                      <li key={i} className="bg-gray-50 p-3 rounded-lg">
                        {typeof item === 'object' ? (
                          <>
                            <span className="font-medium">{item.task || item.description || JSON.stringify(item)}</span>
                            {item.assignee && <span className="text-primary ml-2">→ {item.assignee}</span>}
                          </>
                        ) : (
                          <span>{item}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* 원본 JSON (디버깅용 - 위 필드가 모두 없을 때만 표시) */}
              {!selectedMinutes.summary && !selectedMinutes.decisions && !selectedMinutes.agenda && (
                <div>
                  <h4 className="font-bold text-gray-500 mb-2">📄 원본 데이터</h4>
                  <pre className="bg-gray-50 p-4 rounded-xl text-sm overflow-auto">
                    {JSON.stringify(selectedMinutes, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};


const ProjectPortfolio = () => {
  const { id } = useParams(); // URL에서 프로젝트 ID 가져오기
  const { user } = useAuth();
  const projectId = Number(id) || 1;

  // 토스트 훅 사용
  const { addToast, updateToast, removeToast, toasts } = useToast();

  // 포트폴리오 목록 및 생성 상태
  const [portfolioList, setPortfolioList] = useState<PortfolioResult[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<PortfolioResult | null>(null);
  const [isGenerating, setIsGenerating] = useState(() => {
    const saved = localStorage.getItem(`portfolio_generating_${projectId}`);
    return saved === 'true';
  });

  // 포트폴리오 목록 로드
  useEffect(() => {
    loadPortfolioList();
  }, [projectId]);

  const loadPortfolioList = async () => {
    // TODO: API 구현 후 실제 목록 조회
    // 현재는 localStorage에서 복원 (프로젝트별로 분리)
    const saved = localStorage.getItem(`portfolio_list_${projectId}`);
    if (saved) {
      const list = JSON.parse(saved);
      setPortfolioList(list);
      if (list.length > 0) {
        setSelectedPortfolio(list[0]); // 최신 포트폴리오 선택
      }
    }
  };

  // 포트폴리오 생성
  const handleGenerate = async () => {
    if (!user?.id) {
      addToast('error', '로그인이 필요합니다.');
      return;
    }

    if (isGenerating) {
      addToast('error', '이미 포트폴리오를 생성 중입니다.');
      return;
    }

    setIsGenerating(true);
    localStorage.setItem(`portfolio_generating_${projectId}`, 'true');

    const toastId = addToast('loading', '포트폴리오를 생성하는 중입니다...');

    try {
      const data = await generatePortfolio(user.id, projectId);

      // 생성 날짜 추가
      const portfolioWithDate = {
        ...data,
        created_at: new Date().toISOString()
      };

      // 목록에 추가 (최신이 맨 위)
      const newList = [portfolioWithDate, ...portfolioList];
      setPortfolioList(newList);
      setSelectedPortfolio(portfolioWithDate);

      // localStorage에 저장 (프로젝트별로 분리)
      localStorage.setItem(`portfolio_list_${projectId}`, JSON.stringify(newList));

      removeToast(toastId);
      addToast('success', '포트폴리오가 생성되었습니다! 🎉');
    } catch (error: any) {
      console.error("Portfolio generation error:", error);
      removeToast(toastId);
      addToast('error', `포트폴리오 생성 실패: ${error.message || error}`);
    } finally {
      setIsGenerating(false);
      localStorage.removeItem(`portfolio_generating_${projectId}`);
    }
  };

  const handleCancelGeneration = () => {
    setIsGenerating(false);
    localStorage.removeItem(`portfolio_generating_${projectId}`);
    addToast('info', '포트폴리오 생성이 취소되었습니다.');
  };

  // 날짜 포맷 함수
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // 포트폴리오 다운로드 함수
  const downloadPortfolio = (portfolio: PortfolioResult, format: 'markdown' | 'text') => {
    let content = '';
    const filename = `${portfolio.title.replace(/[^a-zA-Z0-9가-힣]/g, '_')}_${new Date().toISOString().split('T')[0]}`;

    if (format === 'markdown') {
      content = `# ${portfolio.title}

## 프로젝트 요약
${portfolio.summary}

---

## 담당 역할
${portfolio.role_description}

---

## 사용 기술
${portfolio.tech_stack_usage}

---

## 문제 해결 (STAR)
${portfolio.problem_solving}

---

## 성장 포인트
${portfolio.growth_point}

---

*생성일: ${portfolio.created_at ? formatDate(portfolio.created_at) : new Date().toLocaleDateString('ko-KR')}*
`;
    } else {
      content = `${portfolio.title}
${'='.repeat(portfolio.title.length)}

[프로젝트 요약]
${portfolio.summary}

────────────────────────────────────────

[담당 역할]
${portfolio.role_description}

────────────────────────────────────────

[사용 기술]
${portfolio.tech_stack_usage}

────────────────────────────────────────

[문제 해결 (STAR)]
${portfolio.problem_solving}

────────────────────────────────────────

[성장 포인트]
${portfolio.growth_point}

────────────────────────────────────────

생성일: ${portfolio.created_at ? formatDate(portfolio.created_at) : new Date().toLocaleDateString('ko-KR')}
`;
    }

    // 파일 다운로드
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}.${format === 'markdown' ? 'md' : 'txt'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    addToast('success', `포트폴리오가 ${format === 'markdown' ? 'Markdown' : '텍스트'} 파일로 다운로드되었습니다!`);
  };

  return (
    <div className="p-10 space-y-8 animate-slideDown">
      {/* 토스트 컨테이너 */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div className="space-y-1">
          <h2 className="text-2xl font-black text-text-main">AI 자동 완성 포트폴리오</h2>
          <p className="text-sm text-text-sub font-bold">참여한 프로젝트 활동과 회의록을 분석하여 성과를 정리합니다.</p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className={`px-6 py-3 rounded-2xl font-black shadow-lg transition-all flex items-center gap-2 ${isGenerating
            ? 'bg-gray-400 text-white cursor-not-allowed'
            : 'bg-indigo-600 text-white shadow-indigo-200 hover:bg-indigo-700'
            }`}
        >
          <span>🪄</span> {isGenerating ? '생성 중...' : '새 포트폴리오 생성'}
        </button>
      </div>

      {/* 생성 중 알림 */}
      {isGenerating && (
        <div className="bg-blue-50 border border-blue-200 text-blue-600 px-4 py-3 rounded-xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <span>🤖 AI가 포트폴리오를 생성하는 중입니다... (잠시만 기다려주세요)</span>
          </div>
          <button
            onClick={handleCancelGeneration}
            className="text-red-600 hover:text-red-800 font-bold text-sm underline"
          >
            취소
          </button>
        </div>
      )}

      {/* 포트폴리오 목록 */}
      <div className="bg-white rounded-[2rem] border border-gray-100 shadow-xl overflow-hidden">
        <div className="bg-gray-50/50 p-6 border-b border-gray-100">
          <h3 className="font-black text-lg text-text-main">📋 생성된 포트폴리오 목록</h3>
        </div>
        <div className="p-6">
          {portfolioList.length === 0 ? (
            <div className="text-center py-12 text-text-sub">
              <p className="text-4xl mb-4">📝</p>
              <p className="font-bold">아직 생성된 포트폴리오가 없습니다.</p>
              <p className="text-sm mt-2">위의 "새 포트폴리오 생성" 버튼을 눌러 시작하세요.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {portfolioList.map((portfolio, index) => (
                <div
                  key={portfolio.portfolio_id}
                  onClick={() => setSelectedPortfolio(portfolio)}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${selectedPortfolio?.portfolio_id === portfolio.portfolio_id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'
                    }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-black text-text-main">{portfolio.title}</h4>
                        <span className="text-xs bg-indigo-100 text-indigo-600 px-2 py-1 rounded-full font-bold">
                          v{portfolioList.length - index}
                        </span>
                      </div>
                      <p className="text-sm text-text-sub mt-1 line-clamp-1">{portfolio.summary}</p>
                      {portfolio.created_at && (
                        <p className="text-xs text-gray-400 mt-2">
                          📅 {formatDate(portfolio.created_at)}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 선택된 포트폴리오 상세 */}
      {selectedPortfolio && (
        <div className="space-y-8 animate-scaleIn">
          {/* 다운로드 버튼 */}
          <div className="flex justify-end gap-3">
            <button
              onClick={() => downloadPortfolio(selectedPortfolio, 'markdown')}
              className="bg-green-600 text-white px-5 py-2.5 rounded-xl font-bold shadow-lg hover:bg-green-700 transition-all flex items-center gap-2"
            >
              <span>📄</span> Markdown 다운로드
            </button>
            <button
              onClick={() => downloadPortfolio(selectedPortfolio, 'text')}
              className="bg-blue-600 text-white px-5 py-2.5 rounded-xl font-bold shadow-lg hover:bg-blue-700 transition-all flex items-center gap-2"
            >
              <span>📝</span> 텍스트 다운로드
            </button>
          </div>

          {/* 요약 테이블 */}
          <div className="bg-white rounded-[2rem] border border-gray-100 shadow-xl overflow-hidden">
            <div className="bg-gray-50/50 p-6 border-b border-gray-100">
              <h4 className="font-black text-lg text-text-main">📌 {selectedPortfolio.title || '프로젝트 성과 요약서'}</h4>
            </div>
            <div className="p-8">
              <table className="w-full text-left border-collapse">
                <tbody>
                  <tr className="border-b border-gray-50">
                    <th className="py-4 w-32 text-sm font-black text-text-sub uppercase">역할</th>
                    <td className="py-4 font-bold text-text-main">
                      <span className="text-indigo-600">{selectedPortfolio.role_description}</span>
                    </td>
                  </tr>
                  <tr className="border-b border-gray-50">
                    <th className="py-4 text-sm font-black text-text-sub uppercase">사용 기술</th>
                    <td className="py-4 font-bold text-text-main">{selectedPortfolio.tech_stack_usage}</td>
                  </tr>
                  <tr className="border-b border-gray-50">
                    <th className="py-4 text-sm font-black text-text-sub uppercase align-top pt-6">문제 해결<br /><span className="text-[10px] text-indigo-500 font-medium">(AI 추출)</span></th>
                    <td className="py-4">
                      <p className="text-sm text-text-main font-bold leading-relaxed whitespace-pre-wrap">{selectedPortfolio.problem_solving}</p>
                    </td>
                  </tr>
                  <tr className="border-b border-gray-50">
                    <th className="py-4 text-sm font-black text-text-sub uppercase align-top pt-6">성장 포인트</th>
                    <td className="py-4">
                      <p className="text-sm text-text-main font-bold leading-relaxed whitespace-pre-wrap">{selectedPortfolio.growth_point}</p>
                    </td>
                  </tr>
                  <tr>
                    <th className="py-4 text-sm font-black text-text-sub uppercase align-top pt-6">요약</th>
                    <td className="py-4 text-sm text-text-main leading-relaxed bg-gray-50 p-4 rounded-xl mt-2 font-medium">
                      💡 {selectedPortfolio.summary}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* 외부 링크 입력 */}
          <div className="bg-gray-50 p-6 rounded-[2rem] flex items-center gap-4">
            <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center text-2xl shadow-sm">🔗</div>
            <div className="flex-1 space-y-1">
              <p className="text-xs font-black text-text-sub uppercase">증빙 자료 링크 (선택)</p>
              <input type="text" placeholder="Notion, GitHub, Blog 등 URL을 입력하세요" className="w-full bg-transparent border-none focus:ring-0 p-0 text-sm font-bold text-text-main placeholder-gray-400" />
            </div>
            <button className="bg-text-main text-white px-6 py-3 rounded-xl font-black shadow-lg hover:bg-black transition-all">저장하기</button>
          </div>
        </div>
      )}
    </div>
  );
};

// 태스크 인터페이스
interface Task {
  task_id: number;
  title: string;
  description?: string;
  status: 'TODO' | 'IN_PROGRESS' | 'DONE';
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  assignee_id?: string;
  created_by: string;
  due_date?: string;
  created_at?: string;
  updated_at?: string;
}

interface TasksByStatus {
  TODO: Task[];
  IN_PROGRESS: Task[];
  DONE: Task[];
}

const JiraBoard = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [tasks, setTasks] = useState<TasksByStatus>({
    TODO: [],
    IN_PROGRESS: [],
    DONE: []
  });
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [draggedTask, setDraggedTask] = useState<Task | null>(null);

  // 태스크 목록 로드
  const loadTasks = async () => {
    if (!id) return;

    try {
      console.log('🔄 태스크 목록 로드 중...');
      const tasksList = await teamAPI.getTasks(parseInt(id));

      // 태스크를 상태별로 분류
      const newTasks: TasksByStatus = {
        TODO: [],
        IN_PROGRESS: [],
        DONE: []
      };

      if (Array.isArray(tasksList)) {
        tasksList.forEach((task: any) => {
          if (task.status === 'TODO') newTasks.TODO.push(task);
          else if (task.status === 'IN_PROGRESS') newTasks.IN_PROGRESS.push(task);
          else if (task.status === 'DONE' || task.status === 'COMPLETED') newTasks.DONE.push(task);
          else newTasks.TODO.push(task);
        });
      }

      console.log('✅ 태스크 목록 로드 성공:', newTasks);
      setTasks(newTasks);
    } catch (error) {
      console.error('❌ 태스크 목록 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [id]);

  // 태스크 생성
  const createTask = async (taskData: any) => {
    if (!id || !user) return;

    try {
      console.log('🔄 태스크 생성 중...');
      await teamAPI.createTask(parseInt(id), {
        ...taskData,
        created_by: user.id
      });

      console.log('✅ 태스크 생성 성공');
      await loadTasks(); // 목록 새로고침
      setShowCreateModal(false);
    } catch (error) {
      console.error('❌ 태스크 생성 실패:', error);
      alert('태스크 생성 중 오류가 발생했습니다.');
    }
  };

  // 태스크 상태 변경 (드래그 앤 드롭)
  const updateTaskStatus = async (taskId: number, newStatus: string) => {
    if (!id) return;
    try {
      console.log('🔄 태스크 상태 변경 중...');
      await teamAPI.updateTask(parseInt(id), taskId, { status: newStatus });
      console.log('✅ 태스크 상태 변경 성공');
      await loadTasks(); // 목록 새로고침
    } catch (error) {
      console.error('❌ 태스크 상태 변경 실패:', error);
      alert('태스크 상태 변경 중 오류가 발생했습니다.');
    }
  };

  // 태스크 수정
  const updateTask = async (taskId: number, taskData: any) => {
    if (!id) return;
    try {
      console.log('🔄 태스크 수정 중...');
      await teamAPI.updateTask(parseInt(id), taskId, taskData);
      console.log('✅ 태스크 수정 성공');
      await loadTasks(); // 목록 새로고침
      setShowEditModal(false);
      setSelectedTask(null);
    } catch (error) {
      console.error('❌ 태스크 수정 실패:', error);
      alert('태스크 수정 중 오류가 발생했습니다.');
    }
  };

  // 태스크 삭제
  const deleteTask = async (taskId: number) => {
    if (!confirm('이 태스크를 삭제하시겠습니까?')) return;

    try {
      console.log('🔄 태스크 삭제 중...');
      await teamAPI.deleteTask(parseInt(id), taskId);
      console.log('✅ 태스크 삭제 성공');
      await loadTasks(); // 목록 새로고침
    } catch (error) {
      console.error('❌ 태스크 삭제 실패:', error);
      alert('태스크 삭제 중 오류가 발생했습니다.');
    }
  };

  // 드래그 앤 드롭 핸들러
  const handleDragStart = (e: React.DragEvent, task: Task) => {
    setDraggedTask(task);
    e.dataTransfer.effectAllowed = 'move';
    // 드래그 중인 요소에 스타일 추가
    (e.target as HTMLElement).classList.add('dragging');
  };

  const handleDragEnd = (e: React.DragEvent) => {
    // 드래그 종료 시 스타일 제거
    (e.target as HTMLElement).classList.remove('dragging');
    setDraggedTask(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    // 드롭 영역 하이라이트
    (e.currentTarget as HTMLElement).classList.add('drop-zone-active');
  };

  const handleDragLeave = (e: React.DragEvent) => {
    // 드롭 영역 하이라이트 제거
    (e.currentTarget as HTMLElement).classList.remove('drop-zone-active');
  };

  const handleDrop = (e: React.DragEvent, newStatus: string) => {
    e.preventDefault();
    // 드롭 영역 하이라이트 제거
    (e.currentTarget as HTMLElement).classList.remove('drop-zone-active');

    if (draggedTask && draggedTask.status !== newStatus) {
      updateTaskStatus(draggedTask.task_id, newStatus);
    }
    setDraggedTask(null);
  };

  if (loading) {
    return (
      <div className="p-10 space-y-8 animate-slideDown">
        <div className="text-center py-20 text-gray-400">
          <p className="text-2xl mb-2">⏳</p>
          <p>태스크 목록을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-10 space-y-8 animate-slideDown overflow-x-auto">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">업무 칸반 보드</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-primary text-white px-6 py-3 rounded-xl font-bold hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20"
        >
          + 새 태스크
        </button>
      </div>

      <div className="flex gap-6 min-w-[800px] h-[550px]">
        <KanbanColumn
          title="준비 중"
          status="TODO"
          color="bg-gray-50"
          tasks={tasks.TODO}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onTaskClick={(task) => {
            setSelectedTask(task);
            setShowEditModal(true);
          }}
          onTaskDragStart={handleDragStart}
          onTaskDragEnd={handleDragEnd}
          onDeleteTask={deleteTask}
        />
        <KanbanColumn
          title="진행 중"
          status="IN_PROGRESS"
          color="bg-blue-50"
          tasks={tasks.IN_PROGRESS}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onTaskClick={(task) => {
            setSelectedTask(task);
            setShowEditModal(true);
          }}
          onTaskDragStart={handleDragStart}
          onTaskDragEnd={handleDragEnd}
          onDeleteTask={deleteTask}
        />
        <KanbanColumn
          title="완료"
          status="DONE"
          color="bg-green-50"
          tasks={tasks.DONE}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onTaskClick={(task) => {
            setSelectedTask(task);
            setShowEditModal(true);
          }}
          onTaskDragStart={handleDragStart}
          onTaskDragEnd={handleDragEnd}
          onDeleteTask={deleteTask}
        />
      </div>

      {/* 태스크 생성 모달 */}
      {showCreateModal && (
        <TaskModal
          title="새 태스크 생성"
          onClose={() => setShowCreateModal(false)}
          onSubmit={createTask}
        />
      )}

      {/* 태스크 수정 모달 */}
      {showEditModal && selectedTask && (
        <TaskModal
          title="태스크 수정"
          task={selectedTask}
          onClose={() => {
            setShowEditModal(false);
            setSelectedTask(null);
          }}
          onSubmit={(data) => updateTask(selectedTask.task_id, data)}
        />
      )}
    </div>
  );
};

// 칸반 컬럼 컴포넌트
const KanbanColumn = ({
  title,
  status,
  color,
  tasks,
  onDragOver,
  onDragEnter,
  onDragLeave,
  onDrop,
  onTaskClick,
  onTaskDragStart,
  onTaskDragEnd,
  onDeleteTask
}: any) => (
  <div
    className={`${color} p-6 rounded-[2rem] flex-1 border border-gray-100/50 flex flex-col transition-all duration-200`}
    onDragOver={onDragOver}
    onDragEnter={onDragEnter}
    onDragLeave={onDragLeave}
    onDrop={(e) => onDrop(e, status)}
  >
    {/* 헤더 - 고정 */}
    <div className="flex justify-between items-center mb-4 flex-shrink-0">
      <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest px-2">{title}</h4>
      <span className="text-xs font-bold text-gray-500 bg-white px-2 py-1 rounded-full">{tasks.length}</span>
    </div>

    {/* 태스크 영역 - 스크롤 가능 */}
    <div className="flex-1 overflow-y-auto max-h-[450px] space-y-4 pr-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
      {tasks.length === 0 ? (
        <div className="text-center py-8 text-gray-400 border-2 border-dashed border-gray-200 rounded-xl">
          <p className="text-xs">태스크를 드롭하세요</p>
        </div>
      ) : (
        tasks.map((task: Task) => (
          <TaskCard
            key={task.task_id}
            task={task}
            onClick={() => onTaskClick(task)}
            onDragStart={(e) => onTaskDragStart(e, task)}
            onDragEnd={onTaskDragEnd}
            onDelete={() => onDeleteTask(task.task_id)}
          />
        ))
      )}
    </div>
  </div>
);

// 태스크 카드 컴포넌트
const TaskCard = ({ task, onClick, onDragStart, onDragEnd, onDelete }: any) => {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH': return 'bg-red-100 text-red-600';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-600';
      case 'LOW': return 'bg-green-100 text-green-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'HIGH': return '높음';
      case 'MEDIUM': return '보통';
      case 'LOW': return '낮음';
      default: return '보통';
    }
  };

  return (
    <div
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 cursor-grab hover:shadow-md transition-all group active:cursor-grabbing hover:border-primary/20"
    >
      <div className="flex justify-between items-start mb-2">
        <h5
          className="font-bold text-sm text-gray-800 flex-1 cursor-pointer hover:text-primary transition-colors"
          onClick={onClick}
          title="클릭하여 수정"
        >
          {task.title}
        </h5>
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onClick();
            }}
            className="text-blue-400 hover:text-blue-600 transition-colors text-sm"
            title="수정"
          >
            ✏️
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="text-red-400 hover:text-red-600 transition-colors text-sm"
            title="삭제"
          >
            🗑️
          </button>
        </div>
      </div>

      {task.description && (
        <p className="text-xs text-gray-500 mb-2 line-clamp-2">{task.description}</p>
      )}

      <div className="flex justify-between items-center">
        <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${getPriorityColor(task.priority)}`}>
          {getPriorityText(task.priority)}
        </span>

        {task.due_date && (
          <span className="text-[10px] text-gray-400 font-medium">
            {new Date(task.due_date).toLocaleDateString()}
          </span>
        )}
      </div>

      {task.assignee_id && (
        <div className="mt-2 flex items-center gap-2">
          <img
            src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${task.assignee_id}`}
            className="w-5 h-5 rounded-full border border-gray-200"
            alt="담당자"
          />
          <span className="text-[10px] text-gray-500 font-medium">{task.assignee_id}</span>
        </div>
      )}
    </div>
  );
};

// 태스크 생성/수정 모달
const TaskModal = ({ title, task, onClose, onSubmit }: any) => {
  const [formData, setFormData] = useState({
    title: task?.title || '',
    description: task?.description || '',
    priority: task?.priority || 'MEDIUM',
    assignee_id: task?.assignee_id || '',
    due_date: task?.due_date ? task.due_date.split('T')[0] : ''
  });

  // task가 변경될 때마다 formData 업데이트
  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title || '',
        description: task.description || '',
        priority: task.priority || 'MEDIUM',
        assignee_id: task.assignee_id || '',
        due_date: task.due_date ? task.due_date.split('T')[0] : ''
      });
    }
  }, [task]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      alert('태스크 제목을 입력해주세요.');
      return;
    }
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-[2rem] p-8 w-full max-w-md mx-4 shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold">{title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-2">제목 *</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary"
              placeholder="태스크 제목을 입력하세요"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-700 mb-2">설명</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary h-20 resize-none"
              placeholder="태스크 설명을 입력하세요"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">우선순위</label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary"
              >
                <option value="LOW">낮음</option>
                <option value="MEDIUM">보통</option>
                <option value="HIGH">높음</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">마감일</label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-700 mb-2">담당자</label>
            <input
              type="text"
              value={formData.assignee_id}
              onChange={(e) => setFormData({ ...formData, assignee_id: e.target.value })}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary"
              placeholder="담당자 ID를 입력하세요"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 border border-gray-200 rounded-xl font-bold text-gray-600 hover:bg-gray-50 transition-colors"
            >
              취소
            </button>
            <button
              type="submit"
              className="flex-1 py-3 bg-primary text-white rounded-xl font-bold hover:bg-primary/90 transition-colors"
            >
              {task ? '수정 완료' : '생성'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const FileStorage = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [files, setFiles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  // 파일 목록 로드
  useEffect(() => {
    const loadFiles = async () => {
      if (!id) return;

      try {
        console.log('🔄 파일 목록 로드 중...');
        const response = await fetch(`/api/v1/teams/${id}/files`);

        if (response.ok) {
          const result = await response.json();
          if (result.success) {
            console.log('✅ 파일 목록 로드 성공:', result.files);
            setFiles(result.files || []);
          } else {
            console.error('❌ 파일 목록 로드 실패:', result.message);
          }
        } else {
          console.error('❌ HTTP 오류:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('❌ 파일 목록 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadFiles();
  }, [id]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !id || !user) return;

    if (file.size > 10 * 1024 * 1024) {
      alert('10MB 이상의 파일은 업로드할 수 없습니다.');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', user.id);
      formData.append('description', '');

      console.log('🔄 파일 업로드 중...');
      const response = await fetch(`/api/v1/teams/${id}/files/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          console.log('✅ 파일 업로드 성공');
          // 파일 목록 새로고침
          const listResponse = await fetch(`/api/v1/teams/${id}/files`);
          if (listResponse.ok) {
            const listResult = await listResponse.json();
            if (listResult.success) {
              setFiles(listResult.files || []);
            }
          }
        } else {
          console.error('❌ 파일 업로드 실패:', result.message);
          alert(result.message || '파일 업로드에 실패했습니다.');
        }
      } else {
        console.error('❌ HTTP 오류:', response.status, response.statusText);
        alert('파일 업로드 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('❌ 파일 업로드 실패:', error);
      alert('파일 업로드 중 오류가 발생했습니다.');
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (fileId: number, fileName: string) => {
    if (!id || !user) return;

    try {
      console.log('🔄 파일 다운로드 중...');
      const response = await fetch(`/api/v1/integration/project/${id}/files/${fileId}/download?user_id=${user.id}`);

      if (response.ok) {
        const result = await response.json();
        if (result.status === 'success' && result.data.download_url) {
          // 새 창에서 다운로드 URL 열기
          window.open(result.data.download_url, '_blank');
        } else {
          console.error('❌ 다운로드 URL 생성 실패:', result.message);
          alert('파일 다운로드에 실패했습니다.');
        }
      } else {
        console.error('❌ HTTP 오류:', response.status, response.statusText);
        alert('파일 다운로드 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('❌ 파일 다운로드 실패:', error);
      alert('파일 다운로드 중 오류가 발생했습니다.');
    }
  };

  const handleDelete = async (fileId: number, fileName: string) => {
    if (!id || !user) return;

    if (!confirm(`'${fileName}' 파일을 삭제하시겠습니까?`)) return;

    try {
      console.log('🔄 파일 삭제 중...');
      const response = await fetch(`/api/v1/integration/project/${id}/files/${fileId}?user_id=${user.id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        const result = await response.json();
        if (result.status === 'success') {
          console.log('✅ 파일 삭제 성공');
          // 파일 목록에서 제거
          setFiles(prev => prev.filter(f => f.file_id !== fileId));
        } else {
          console.error('❌ 파일 삭제 실패:', result.message);
          alert(result.message || '파일 삭제에 실패했습니다.');
        }
      } else {
        console.error('❌ HTTP 오류:', response.status, response.statusText);
        alert('파일 삭제 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('❌ 파일 삭제 실패:', error);
      alert('파일 삭제 중 오류가 발생했습니다.');
    }
  };

  // 파일 크기 포맷팅
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // 파일 타입 아이콘
  const getFileIcon = (fileType: string) => {
    if (fileType.includes('image')) return '🖼️';
    if (fileType.includes('pdf')) return '📄';
    if (fileType.includes('word')) return '📝';
    if (fileType.includes('excel') || fileType.includes('spreadsheet')) return '📊';
    if (fileType.includes('zip') || fileType.includes('rar')) return '📦';
    return '📁';
  };

  if (loading) {
    return (
      <div className="p-10 space-y-8 animate-slideDown">
        <div className="text-center py-20 text-gray-400">
          <p className="text-2xl mb-2">⏳</p>
          <p>파일 목록을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-10 space-y-8 animate-slideDown">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">공유 파일함</h2>
        <label className={`px-6 py-3 rounded-2xl font-black cursor-pointer shadow-lg transition-all ${uploading ? 'bg-gray-400 text-white cursor-not-allowed' : 'bg-primary text-white shadow-primary/10 hover:bg-primary-dark'}`}>
          {uploading ? '업로드 중...' : '파일 업로드'}
          <input
            type="file"
            className="hidden"
            onChange={handleUpload}
            disabled={uploading}
          />
        </label>
      </div>

      <div className="grid gap-4">
        {files.length > 0 ? files.map(f => (
          <div key={f.file_id} className="flex items-center justify-between p-5 border border-gray-100 rounded-2xl hover:bg-gray-50 transition-colors">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center text-xl">
                {getFileIcon(f.file_type)}
              </div>
              <div>
                <p className="font-bold text-text-main">{f.file_name}</p>
                <p className="text-[10px] text-text-sub font-bold">
                  {formatFileSize(f.file_size)} • {f.uploaded_by} • {new Date(f.created_at).toLocaleDateString()}
                </p>
                {f.description && (
                  <p className="text-xs text-gray-500 mt-1">{f.description}</p>
                )}
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleDownload(f.file_id, f.file_name)}
                className="text-primary font-black text-sm hover:underline"
              >
                다운로드
              </button>
              {(user?.id === f.uploaded_by_id) && (
                <button
                  onClick={() => handleDelete(f.file_id, f.file_name)}
                  className="text-red-500 font-black text-sm hover:underline ml-2"
                >
                  삭제
                </button>
              )}
            </div>
          </div>
        )) : (
          <div className="py-20 text-center text-gray-400">
            <p className="text-4xl mb-4">📁</p>
            <p className="font-bold">아직 업로드된 파일이 없습니다.</p>
            <p className="text-sm mt-2">위의 "파일 업로드" 버튼을 눌러 파일을 공유해보세요.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeamSpacePage;
