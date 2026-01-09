"""
메모리 기반 데이터 저장소
데이터베이스 연결 문제 해결 전까지 임시로 사용
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

class MemoryStore:
    def __init__(self):
        self.projects: List[Dict[str, Any]] = []
        self.next_id = 1
        self.data_file = "temp_projects.json"
        self.load_from_file()
    
    def load_from_file(self):
        """파일에서 데이터 로드 (서버 재시작 시 데이터 유지)"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.projects = data.get('projects', [])
                    self.next_id = data.get('next_id', 1)
        except Exception as e:
            print(f"데이터 로드 실패: {e}")
            self.init_sample_data()
    
    def save_to_file(self):
        """파일에 데이터 저장"""
        try:
            data = {
                'projects': self.projects,
                'next_id': self.next_id
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"데이터 저장 실패: {e}")
    
    def init_sample_data(self):
        """초기 샘플 데이터"""
        self.projects = [
            {
                "id": 1,
                "title": "🚀 팀으로 기획부터 배포까지 완주하는 사이드 프로젝트 멤버 구함",
                "description": "실제 서비스를 목표로 기획부터 디자인, 개발, 배포까지 함께하실 열정적인 분들을 찾습니다. 현재 백엔드 개발자 1명이 있으며, 프론트엔드 개발자와 디자이너를 모집하고 있습니다.",
                "type": "PROJECT",
                "status": "RECRUITING",
                "method": "ONLINE",
                "views": 2450,
                "user_id": 1,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "start_date": "2024-06-01",
                "end_date": "2024-08-30",
                "test_required": True,
                "recruitment_positions": [
                    {
                        "id": 1,
                        "position_name": "프론트엔드 개발자",
                        "tech_stack": "React",
                        "required_count": 2,
                        "current_count": 0
                    },
                    {
                        "id": 2,
                        "position_name": "백엔드 개발자",
                        "tech_stack": "Node.js",
                        "required_count": 1,
                        "current_count": 1
                    },
                    {
                        "id": 3,
                        "position_name": "UI/UX 디자이너",
                        "tech_stack": "Figma",
                        "required_count": 1,
                        "current_count": 0
                    }
                ]
            },
            {
                "id": 2,
                "title": "AI 기반 공동구매 플랫폼 프론트엔드 개발자 긴급 모집합니다",
                "description": "현재 백엔드 2명, 디자이너 1명이 있습니다. React와 TypeScript를 활용한 모던 웹 개발에 관심있는 분들을 찾고 있습니다.",
                "type": "PROJECT",
                "status": "RECRUITING",
                "method": "OFFLINE",
                "views": 1880,
                "user_id": 2,
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
                "start_date": "2024-07-15",
                "end_date": "2024-10-15",
                "test_required": False,
                "recruitment_positions": [
                    {
                        "id": 4,
                        "position_name": "프론트엔드 개발자",
                        "tech_stack": "React",
                        "required_count": 2,
                        "current_count": 0
                    },
                    {
                        "id": 5,
                        "position_name": "백엔드 개발자",
                        "tech_stack": "Python",
                        "required_count": 2,
                        "current_count": 2
                    },
                    {
                        "id": 6,
                        "position_name": "UI/UX 디자이너",
                        "tech_stack": "Figma",
                        "required_count": 1,
                        "current_count": 1
                    }
                ]
            },
            {
                "id": 3,
                "title": "React 스터디 그룹 - 초급자 환영",
                "description": "React 기초부터 고급 기능까지 함께 학습할 스터디 그룹입니다. 매주 토요일 오후 2시에 모여서 공부합니다.",
                "type": "STUDY",
                "status": "RECRUITING",
                "method": "MIXED",
                "views": 1200,
                "user_id": 3,
                "created_at": "2024-01-03T00:00:00",
                "updated_at": "2024-01-03T00:00:00",
                "start_date": "2024-06-10",
                "end_date": "2024-08-10",
                "test_required": False,
                "recruitment_positions": [
                    {
                        "id": 7,
                        "position_name": "스터디원",
                        "tech_stack": "React",
                        "required_count": 5,
                        "current_count": 2
                    }
                ]
            }
        ]
        self.next_id = 4
        self.save_to_file()
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """모든 프로젝트 조회"""
        return self.projects
    
    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """ID로 프로젝트 조회"""
        for project in self.projects:
            if project["id"] == project_id:
                return project
        return None
    
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """새 프로젝트 생성"""
        project = {
            "id": self.next_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "views": 0,
            **project_data
        }
        self.projects.append(project)
        self.next_id += 1
        self.save_to_file()
        return project
    
    def update_project(self, project_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """프로젝트 업데이트"""
        for i, project in enumerate(self.projects):
            if project["id"] == project_id:
                self.projects[i].update(update_data)
                self.projects[i]["updated_at"] = datetime.now().isoformat()
                self.save_to_file()
                return self.projects[i]
        return None
    
    def delete_project(self, project_id: int) -> bool:
        """프로젝트 삭제"""
        for i, project in enumerate(self.projects):
            if project["id"] == project_id:
                del self.projects[i]
                self.save_to_file()
                return True
        return False

# 전역 인스턴스
memory_store = MemoryStore()