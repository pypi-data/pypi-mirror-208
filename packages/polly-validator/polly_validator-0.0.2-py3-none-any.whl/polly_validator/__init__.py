from pathlib import Path

from appdirs import user_config_dir

folder_path = Path(Path(user_config_dir()) / 'polly-validator')
if not folder_path.is_dir():
    folder_path.mkdir()
valid_names_file_path = Path(folder_path / 'valid_names.json')
if not valid_names_file_path.is_file():
    from polly_validator.downloader.get_valid_names import collect_valid_names

    collect_valid_names()
