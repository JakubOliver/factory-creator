import json

import pytest

from factory_creator.util.file_util import FileUtil


def test_validate_json_file_accepts_valid_json(tmp_path):
    json_file = tmp_path / "valid.json"
    json_file.write_text(json.dumps({"ok": True}), encoding="utf-8")

    FileUtil.validate_json_file(str(json_file))


def test_validate_json_file_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        FileUtil.validate_json_file(str(tmp_path / "missing.json"))


def test_validate_json_file_rejects_invalid_json(tmp_path):
    json_file = tmp_path / "invalid.json"
    json_file.write_text("{invalid", encoding="utf-8")

    with pytest.raises(TypeError):
        FileUtil.validate_json_file(str(json_file))


def test_create_output_dir_creates_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path) 
    # Change the current working directory to the temporary path for testing

    FileUtil.create_output_dir()

    assert (tmp_path / "output").is_dir()
