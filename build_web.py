"""웹(브라우저) 버전 만들기: python build_web.py
shooter.py와 assets를 임시 폴더에 main.py 이름으로 모아 pygbag으로 빌드하고, 결과를 docs/에 복사한다 (GitHub Pages가 docs/를 보여준다)."""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(tempfile.mkdtemp(prefix="astroid_build_"), "astroid")  # 빌드 작업 폴더 (OneDrive 밖, 매번 새 폴더)
OUT = os.path.join(HERE, "docs")

os.makedirs(SRC)
shutil.copy(os.path.join(HERE, "shooter.py"), os.path.join(SRC, "main.py"))
shutil.copytree(os.path.join(HERE, "assets"), os.path.join(SRC, "assets"))
subprocess.run([sys.executable, "-X", "utf8", "-m", "pygbag", "--build", SRC], check=True)  # -X utf8: 한글 소스를 읽게
shutil.rmtree(OUT, ignore_errors=True)  # 폴더가 다른 프로그램에 잡혀 있으면 안 지워질 수 있어서 덮어쓰기로 복사한다
shutil.copytree(os.path.join(SRC, "build", "web"), OUT, dirs_exist_ok=True)
open(os.path.join(OUT, ".nojekyll"), "w").close()  # GitHub Pages가 파일을 가공하지 않게
print("웹 버전:", OUT)
