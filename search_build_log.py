from pathlib import Path
import re
path = Path(r'c:/Users/macie/Downloads/logs_71706662983/build/9_Build APK.txt')
if not path.exists():
    raise SystemExit(f'File not found: {path}')
pattern = re.compile(r'error|ERROR|FAIL|Exception|Traceback|fatal|undefined macro|autogen\.sh', re.I)
with path.open('r', encoding='utf-8', errors='replace') as f:
    for i, line in enumerate(f, start=1):
        if pattern.search(line):
            print(i, line.rstrip())
            break
