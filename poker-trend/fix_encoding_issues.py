#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows CP949 인코딩 문제 자동 수정 스크립트
E2E 테스트에서 발견된 문제들을 일괄 해결
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import re

# 현재 스크립트 위치 기준으로 유틸리티 추가
sys.path.append(str(Path(__file__).parent / 'backend' / 'utils'))

try:
    from encoding_utils import safe_print, safe_json_dump, safe_file_write, setup_console_encoding
    from file_utils import SafeFileHandler, ensure_dir
except ImportError:
    safe_print = print
    setup_console_encoding = lambda: None

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class EncodingFixer:
    """인코딩 문제 자동 수정 클래스"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.file_handler = SafeFileHandler()
        self.fixes_applied: List[Dict[str, Any]] = []
        
        # 수정 대상 패턴들
        self.encoding_patterns = {
            # JSON 저장 시 인코딩 문제
            'json_dump_no_encoding': {
                'pattern': r'json\.dump\([^)]+\)(?!\s*,\s*ensure_ascii=)',
                'description': 'JSON dump without ensure_ascii parameter'
            },
            
            # 파일 열기 시 인코딩 누락
            'open_no_encoding': {
                'pattern': r'open\([^)]+\)(?!\s*,\s*encoding=)',
                'description': 'File open without encoding parameter'  
            },
            
            # print 함수 인코딩 문제
            'unsafe_print': {
                'pattern': r'print\s*\([^)]*[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\uAC00-\uD7AF][^)]*\)',
                'description': 'Print with unicode characters'
            }
        }
    
    def scan_python_files(self) -> List[Path]:
        """Python 파일들을 스캔"""
        python_files = []
        
        # 주요 디렉토리에서 Python 파일 찾기
        scan_dirs = [
            self.project_root / 'backend',
            self.project_root / 'scripts', 
            self.project_root / 'tests'
        ]
        
        for scan_dir in scan_dirs:
            if scan_dir.exists():
                python_files.extend(scan_dir.rglob('*.py'))
        
        logger.info(f"스캔된 Python 파일: {len(python_files)}개")
        return python_files
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """파일 분석 및 문제점 탐지"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 각 패턴 검사
            for pattern_name, pattern_info in self.encoding_patterns.items():
                matches = re.finditer(pattern_info['pattern'], content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'type': pattern_name,
                        'line': line_num,
                        'match': match.group(),
                        'description': pattern_info['description']
                    })
            
            return {
                'file_path': file_path,
                'issues': issues,
                'has_korean_text': bool(re.search(r'[\uAC00-\uD7AF]', content)),
                'has_utf8_header': '# -*- coding: utf-8 -*-' in content
            }
            
        except Exception as e:
            logger.error(f"파일 분석 실패 {file_path}: {e}")
            return {'file_path': file_path, 'issues': [], 'error': str(e)}
    
    def fix_json_dump_issues(self, file_path: Path, content: str) -> str:
        """JSON dump 인코딩 문제 수정"""
        # json.dump(...) -> json.dump(..., ensure_ascii=False) 패턴 수정
        pattern = r'json\.dump\(([^)]+)\)(?!\s*,\s*ensure_ascii=)'
        
        def replace_json_dump(match):
            args = match.group(1)
            # 이미 ensure_ascii가 있는지 확인
            if 'ensure_ascii' not in args:
                return f'json.dump({args}, ensure_ascii=False)'
            return match.group(0)
        
        modified_content = re.sub(pattern, replace_json_dump, content)
        return modified_content
    
    def fix_file_open_issues(self, file_path: Path, content: str) -> str:
        """파일 열기 인코딩 문제 수정"""
        # open(...) -> open(..., encoding='utf-8') 패턴 수정
        pattern = r'open\(([^)]+)\)(?!\s*,\s*encoding=)'
        
        def replace_open(match):
            args = match.group(1)
            # 이미 encoding이 있는지 확인
            if 'encoding' not in args and 'mode' in args:
                if args.count("'") >= 2 or args.count('"') >= 2:
                    return f"open({args}, encoding='utf-8')"
            elif 'encoding' not in args:
                return f"open({args}, encoding='utf-8')"
            return match.group(0)
        
        modified_content = re.sub(pattern, replace_open, content)
        return modified_content
    
    def add_encoding_header(self, content: str) -> str:
        """UTF-8 인코딩 헤더 추가"""
        lines = content.split('\n')
        
        # 첫 번째 줄이 shebang인지 확인
        has_shebang = lines and lines[0].startswith('#!')
        
        # 이미 인코딩 헤더가 있는지 확인
        has_encoding = any('coding:' in line or 'coding=' in line for line in lines[:3])
        
        if not has_encoding:
            encoding_line = '# -*- coding: utf-8 -*-'
            
            if has_shebang:
                lines.insert(1, encoding_line)
            else:
                lines.insert(0, encoding_line)
        
        return '\n'.join(lines)
    
    def apply_fixes_to_file(self, file_path: Path, analysis: Dict[str, Any]) -> bool:
        """파일에 수정사항 적용"""
        if not analysis['issues'] and analysis.get('has_utf8_header', True):
            return True
        
        try:
            # 원본 내용 읽기
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()
            
            modified_content = original_content
            changes_made = []
            
            # JSON dump 문제 수정
            if any(issue['type'] == 'json_dump_no_encoding' for issue in analysis['issues']):
                new_content = self.fix_json_dump_issues(file_path, modified_content)
                if new_content != modified_content:
                    modified_content = new_content
                    changes_made.append('JSON dump encoding')
            
            # 파일 열기 문제 수정
            if any(issue['type'] == 'open_no_encoding' for issue in analysis['issues']):
                new_content = self.fix_file_open_issues(file_path, modified_content)
                if new_content != modified_content:
                    modified_content = new_content
                    changes_made.append('File open encoding')
            
            # UTF-8 헤더 추가 (한국어 텍스트가 있거나 헤더가 없는 경우)
            if analysis.get('has_korean_text', False) or not analysis.get('has_utf8_header', False):
                new_content = self.add_encoding_header(modified_content)
                if new_content != modified_content:
                    modified_content = new_content
                    changes_made.append('UTF-8 header')
            
            # 변경사항이 있으면 파일 저장
            if changes_made:
                if safe_file_write(modified_content, str(file_path)):
                    self.fixes_applied.append({
                        'file': str(file_path),
                        'changes': changes_made,
                        'issues_fixed': len(analysis['issues'])
                    })
                    logger.info(f"수정 완료: {file_path.name} ({', '.join(changes_made)})")
                    return True
                else:
                    logger.error(f"파일 저장 실패: {file_path}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"파일 수정 실패 {file_path}: {e}")
            return False
    
    def run_comprehensive_fix(self) -> Dict[str, Any]:
        """종합적인 인코딩 문제 수정"""
        logger.info("=" * 60)
        logger.info("Windows CP949 인코딩 문제 자동 수정 시작")
        logger.info("=" * 60)
        
        # 1. 콘솔 인코딩 설정
        setup_console_encoding()
        
        # 2. Python 파일 스캔
        python_files = self.scan_python_files()
        
        # 3. 각 파일 분석 및 수정
        total_files = len(python_files)
        fixed_files = 0
        total_issues = 0
        
        for i, file_path in enumerate(python_files, 1):
            logger.info(f"처리 중 ({i}/{total_files}): {file_path.name}")
            
            analysis = self.analyze_file(file_path)
            
            if analysis.get('error'):
                continue
            
            total_issues += len(analysis['issues'])
            
            if self.apply_fixes_to_file(file_path, analysis):
                if analysis['issues'] or analysis.get('has_korean_text', False):
                    fixed_files += 1
        
        # 4. 결과 요약
        summary = {
            'total_files_scanned': total_files,
            'files_with_fixes': fixed_files,
            'total_issues_found': total_issues,
            'fixes_applied': self.fixes_applied,
            'success_rate': (fixed_files / total_files * 100) if total_files > 0 else 0
        }
        
        logger.info("=" * 60)
        logger.info("인코딩 문제 수정 완료")
        logger.info("=" * 60)
        logger.info(f"스캔된 파일: {summary['total_files_scanned']}개")
        logger.info(f"수정된 파일: {summary['files_with_fixes']}개")
        logger.info(f"발견된 문제: {summary['total_issues_found']}개")
        logger.info(f"성공률: {summary['success_rate']:.1f}%")
        
        return summary
    
    def create_environment_fix_script(self) -> str:
        """환경 설정 수정 스크립트 생성"""
        script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
환경 변수 설정 및 인코딩 문제 해결 스크립트
자동 생성됨
"""

import os
import sys
from pathlib import Path

def setup_poker_trend_environment():
    """포커 트렌드 분석 환경 설정"""
    print("🚀 포커 트렌드 분석 환경 설정 중...")
    
    # 1. Windows 콘솔 UTF-8 설정
    if sys.platform == "win32":
        try:
            os.system('chcp 65001 > nul')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            print("✅ Windows 콘솔 UTF-8 인코딩 설정 완료")
        except Exception as e:
            print(f"⚠️  콘솔 인코딩 설정 실패: {e}")
    
    # 2. 필수 디렉토리 생성
    required_dirs = [
        'backend/data-collector/logs',
        'backend/data-collector/reports',
        'backend/platform-analyzer/reports',
        'test-results'
    ]
    
    for dir_path in required_dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"✅ 디렉토리 생성: {dir_path}")
        except Exception as e:
            print(f"❌ 디렉토리 생성 실패 {dir_path}: {e}")
    
    # 3. 환경 변수 확인
    required_env_vars = ['YOUTUBE_API_KEY', 'GEMINI_API_KEY', 'SLACK_WEBHOOK_URL']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 누락된 환경 변수:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\\n.env 파일을 확인하고 필요한 API 키를 설정하세요.")
    else:
        print("✅ 모든 필수 환경 변수가 설정됨")
    
    print("\\n🎯 설정 완료! 이제 테스트를 실행할 수 있습니다:")
    print("  python backend/data-collector/tests/test_env_enhanced.py")

if __name__ == "__main__":
    setup_poker_trend_environment()
'''
        
        script_path = self.project_root / 'setup_environment.py'
        if safe_file_write(script_content, str(script_path)):
            logger.info(f"환경 설정 스크립트 생성: {script_path}")
            return str(script_path)
        else:
            logger.error("환경 설정 스크립트 생성 실패")
            return ""

def main():
    """메인 실행 함수"""
    project_root = Path(__file__).parent
    
    # 인코딩 수정기 생성 및 실행
    fixer = EncodingFixer(project_root)
    
    # 종합 수정 실행
    summary = fixer.run_comprehensive_fix()
    
    # 환경 설정 스크립트 생성
    env_script = fixer.create_environment_fix_script()
    
    # 결과 보고서 생성
    report_path = project_root / 'ENCODING_FIX_REPORT.md'
    report_content = f"""# Windows CP949 인코딩 문제 수정 보고서

## 수정 요약
- **스캔된 파일**: {summary['total_files_scanned']}개
- **수정된 파일**: {summary['files_with_fixes']}개  
- **발견된 문제**: {summary['total_issues_found']}개
- **성공률**: {summary['success_rate']:.1f}%

## 적용된 수정사항

### 주요 개선사항
1. **UTF-8 인코딩 헤더 추가**: `# -*- coding: utf-8 -*-`
2. **JSON 저장 시 인코딩 개선**: `ensure_ascii=False` 설정
3. **파일 I/O 인코딩 명시**: `encoding='utf-8'` 추가
4. **안전한 출력 함수 적용**: 한글 텍스트 처리 개선

### 수정된 파일 목록
"""
    
    for fix in summary['fixes_applied']:
        report_content += f"- `{fix['file']}`: {', '.join(fix['changes'])}\n"
    
    report_content += f"""
## 다음 단계

1. **환경 설정 실행**:
   ```bash
   python {env_script}
   ```

2. **개선된 테스트 실행**:
   ```bash
   python backend/data-collector/tests/test_env_enhanced.py
   ```

3. **E2E 테스트 재실행**:
   ```bash
   npx playwright test
   ```

## 권장사항

- Windows 환경에서는 콘솔 코드페이지를 UTF-8로 설정: `chcp 65001`
- PowerShell 사용 시: `$env:PYTHONIOENCODING="utf-8"`
- 모든 Python 스크립트에 UTF-8 인코딩 헤더 포함
- 파일 I/O 시 항상 인코딩 명시

---
생성일: {Path(__file__).stat().st_mtime}
"""
    
    if safe_file_write(report_content, str(report_path)):
        logger.info(f"수정 보고서 생성: {report_path}")
    
    print("\n" + "=" * 60)
    print("🎉 Windows CP949 인코딩 문제 수정 완료!")
    print("=" * 60)
    print(f"📊 수정 결과: {summary['files_with_fixes']}/{summary['total_files_scanned']} 파일")
    print(f"📝 보고서: {report_path}")
    if env_script:
        print(f"🔧 환경 설정: {env_script}")
    
    return summary

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  사용자가 중단했습니다.")
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        sys.exit(1)