"""a4p-reveal 시험: /usr/bin/python3 -I -m unittest discover -s tests (저장소 맨 위에서)"""
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "reveal.py")
spec = importlib.util.spec_from_file_location("reveal", SCRIPT)
reveal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reveal)


class PathFromUrl(unittest.TestCase):
    def test_korean_and_spaces_are_decoded(self):
        self.assertEqual(
            reveal.path_from_url("file:///Users/u/Downloads/Claude_%EA%B2%B0%EA%B3%BC%EB%AC%BC/a%20b.png"),
            "/Users/u/Downloads/Claude_결과물/a b.png",
        )

    def test_localhost_and_tilde_forms(self):
        self.assertEqual(reveal.path_from_url("file://localhost/tmp/a.png"), "/tmp/a.png")
        self.assertEqual(reveal.path_from_url("file://~/a.png"), os.path.expanduser("~/a.png"))

    def test_not_a_local_file_url(self):
        for url in ["https://example.com/a.png", "file://other-mac/tmp/a.png", "file://", ""]:
            self.assertIsNone(reveal.path_from_url(url), url)


class Plan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = os.path.realpath(self.tmp.name)
        self.file = os.path.join(self.dir, "그림.png")
        open(self.file, "w").close()

    def tearDown(self):
        self.tmp.cleanup()

    def url(self, path):
        return "file://" + urllib.parse.quote(path)

    def test_existing_file_is_selected_in_finder(self):
        command, notice = reveal.plan(self.url(self.file))
        self.assertEqual(command, ["/usr/bin/open", "-R", self.file])
        self.assertIsNone(notice)

    def test_missing_file_opens_the_nearest_folder_and_says_why(self):
        missing = os.path.join(self.dir, "없음", "사라진.png")
        command, notice = reveal.plan(self.url(missing))
        self.assertEqual(command, ["/usr/bin/open", self.dir])
        self.assertIn("파일이 없어서", notice)

    def test_web_link_is_left_alone(self):
        command, notice = reveal.plan("https://example.com/a.png")
        self.assertIsNone(command)
        self.assertIn("파일 주소가 아니어서", notice)

    def test_dry_run_prints_the_plan_without_running(self):
        env = dict(os.environ, A4P_REVEAL_DRY_RUN="1", HERDR_PLUGIN_CLICKED_URL=self.url(self.file))
        out = subprocess.run([SCRIPT], env=env, capture_output=True, text=True, check=True).stdout
        self.assertEqual(json.loads(out)["command"], ["/usr/bin/open", "-R", self.file])


if __name__ == "__main__":
    unittest.main()
