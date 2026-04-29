import subprocess
import sys
import tempfile
from pathlib import Path


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "src.core.main", *args],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def test_find_novel_command_shows_candidates_from_results_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        result_file = Path(tmpdir) / "results.txt"
        result_file.write_text(
            "1. 红楼梦 | C:/books/hongloumeng.txt\n2. 红楼梦续 | D:/novels/hongloumeng2.txt\n",
            encoding="utf-8",
        )

        result = run_cli(
            "find-novel",
            "--keyword",
            "红楼梦",
            "--results-file",
            str(result_file),
        )

        assert result.returncode == 0, result.stderr
        assert "候选文件" in result.stdout
        assert "1. 红楼梦 | C:/books/hongloumeng.txt" in result.stdout
        assert "2. 红楼梦续 | D:/novels/hongloumeng2.txt" in result.stdout
        assert "请确认要用哪个文件" in result.stdout


def test_run_novel_flow_command_dry_run_uses_selected_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        result_file = Path(tmpdir) / "results.txt"
        result_file.write_text(
            "1. 红楼梦 | C:/books/hongloumeng.txt\n2. 红楼梦续 | D:/novels/hongloumeng2.txt\n",
            encoding="utf-8",
        )

        result = run_cli(
            "run-novel-flow",
            "--keyword",
            "红楼梦",
            "--results-file",
            str(result_file),
            "--select",
            "2",
            "--characters",
            "林黛玉,贾宝玉",
            "--message",
            "让我扮演贾宝玉和林黛玉聊天",
            "--force",
            "--dry-run",
        )

        assert result.returncode == 0, result.stderr
        assert "已选择文件: D:/novels/hongloumeng2.txt" in result.stdout
        assert "[dry-run] distill --novel D:/novels/hongloumeng2.txt --characters '林黛玉,贾宝玉' --force" in result.stdout
        assert "[dry-run] extract --novel D:/novels/hongloumeng2.txt --characters '林黛玉,贾宝玉' --force" in result.stdout
        assert "[dry-run] chat --novel D:/novels/hongloumeng2.txt --mode auto --message '让我扮演贾宝玉和林黛玉聊天'" in result.stdout
