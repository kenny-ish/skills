import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import orchestrator


class ParseApplicationModulesTest(unittest.TestCase):

  def test_version_catalog_application_aliases_are_detected(self):
    for alias in ("androidApplication", "releaseApp"):
      with self.subTest(alias=alias), tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        (root / "gradle").mkdir()
        module = root / "app"
        module.mkdir()
        (root / "gradle" / "libs.versions.toml").write_text(
            "[plugins]\n"
            f'{alias} = {{ id = "com.android.application", '
            'version.ref = "agp" }}\n',
            encoding="utf-8",
        )
        build_file = module / "build.gradle.kts"
        build_file.write_text(
            "plugins {\n"
            f"  alias(libs.plugins.{alias})\n"
            "}\n"
            "android {\n"
            '  defaultConfig { applicationId = "com.example.app" }\n'
            "}\n",
            encoding="utf-8",
        )

        modules = orchestrator.parse_application_modules(
            [str(build_file)], [], {}, orchestrator.load_version_catalog(str(root))
        )

        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0]["application_id"], "com.example.app")

  def test_application_alias_with_apply_false_is_not_a_module(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      build_file = Path(temp_dir) / "build.gradle.kts"
      build_file.write_text(
          "plugins { alias(libs.plugins.releaseApp) apply false }\n",
          encoding="utf-8",
      )

      modules = orchestrator.parse_application_modules(
          [str(build_file)], [], {}, {"plugin.releaseApp": "com.android.application"}
      )

      self.assertEqual(modules, [])


if __name__ == "__main__":
  unittest.main()
