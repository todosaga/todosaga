# TodoSaga

TodoSaga는 AI를 활용한 스마트한 할 일 관리 애플리케이션입니다. 사용자의 TODO 리스트를 분석하여 새로운 할 일을 추천하고, 카테고리별로 분류하여 효율적인 작업 관리를 도와줍니다.

## 주요 기능

- AI 기반 TODO 추천
- 카테고리별 할 일 분류
- RESTful API 제공
- Docker 기반 배포 지원

## 기술 스택

- Python 3.12
- Django 4.2
- PostgreSQL
- Docker & Docker Compose
- Nginx
- LangChain & OpenAI
- UV (Python 패키지 관리자)

## 시작하기

### 사전 요구사항

- Python 3.12 이상
- Docker & Docker Compose
- OpenAI API 키

### 로컬 개발 환경 설정

1. 저장소 클론
```bash
git clone https://github.com/yourusername/todosaga.git
cd todosaga
```

2. UV 설치 (선택사항)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. 가상환경 생성 및 활성화
```bash
# UV 사용시
uv venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

# 또는 pip 사용시
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows
```

4. 의존성 설치
```bash
# UV 사용시 (pyproject.toml 사용)
uv pip install .

# 또는 UV 사용시 (requirements.txt 사용)
uv pip install -r requirements.txt

# 또는 pip 사용시 (requirements.txt 사용)
pip install -r requirements.txt
```

5. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 수정하여 필요한 값 설정
```

6. 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

7. 개발 서버 실행
```bash
python manage.py runserver
```

### Docker를 사용한 실행

1. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 수정하여 필요한 값 설정
```

2. Docker 컨테이너 실행
```bash
docker-compose up --build
```

## 프로젝트 구조

```
todosaga/
├── todosaga/          # Django 프로젝트 설정
│   ├── settings/      # 환경별 설정 파일
│   ├── urls.py        # URL 설정
│   └── wsgi.py        # WSGI 설정
├── todos/             # TODO 앱
├── poc/               # 개념 증명 코드
├── nginx/             # Nginx 설정
├── docker-compose.yml # Docker Compose 설정
├── Dockerfile         # Docker 이미지 설정
├── pyproject.toml     # Python 프로젝트 설정
└── requirements.txt   # Python 의존성 (대체 옵션)
```

## 의존성 관리

이 프로젝트는 두 가지 방식으로 의존성을 관리할 수 있습니다:

### 1. pyproject.toml 사용 (권장)
```bash
uv pip install .
```

### 2. requirements.txt 사용
```bash
uv pip install -r requirements.txt
# 또는
pip install -r requirements.txt
```

## API 엔드포인트

- `POST /api/todos/recommend/`: 새로운 TODO 추천
- `POST /api/todos/classify/`: TODO 카테고리 분류

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 연락처

프로젝트 관리자 - [@yourusername](https://github.com/yourusername)

프로젝트 링크: [https://github.com/yourusername/todosaga](https://github.com/yourusername/todosaga)
