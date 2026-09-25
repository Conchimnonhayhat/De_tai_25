"""Copy a legacy SQLite database to the VARCHAR(32) business-code schema.

Run while the web server is stopped. The original data is backed up before the
new database replaces it. Numeric legacy codes remain the same text, so every
existing relationship and visible reference continues to work.
"""

import argparse
import os
import sqlite3
import sys
import tempfile
from contextlib import closing
from datetime import datetime
from pathlib import Path


TABLES = (
    'TaiKhoan', 'SanPham', 'NguyenLieu', 'DinhMucNguyenLieu',
    'DonSanXuat', 'CongDoan', 'KeHoachSanXuat', 'PhanCong',
    'TienDoCongDoan', 'SuDungNguyenLieu', 'LoiSanXuat', 'BaoCaoNgay', 'BaoVatTu', 'ThanhVienTo',
)
SCHEMA = Path(__file__).with_name('schema.sql')
DEFAULT_DATABASE = Path(__file__).resolve().parent.parent / 'instance' / 'workshop.db'


def migrate(db_path: Path, apply: bool = False):
    db_path = db_path.resolve()
    if not db_path.is_file():
        raise ValueError(f'Không tìm thấy CSDL: {db_path}')
    with closing(sqlite3.connect(db_path)) as source:
        source.row_factory = sqlite3.Row
        columns = source.execute('PRAGMA table_info(TaiKhoan)').fetchall()
        code_type = next((row['type'].upper() for row in columns if row['name'] == 'MaTaiKhoan'), '')
        if not code_type:
            raise ValueError('CSDL không có bảng TaiKhoan.')
        if code_type == 'VARCHAR(32)':
            return 'CSDL đã dùng mã VARCHAR(32); không cần chuyển.'
        present = {row['name'] for row in source.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        unexpected = present - set(TABLES) - {'sqlite_sequence'}
        if unexpected:
            raise ValueError(f'CSDL có bảng chưa được ánh xạ: {sorted(unexpected)}')
        counts = {table: source.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                  for table in TABLES if table in present}
        if not apply:
            return f'Sẽ chuyển {counts}; chạy lại với --apply khi web đã dừng.'

        stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup_path = db_path.with_name(f'{db_path.stem}.backup-{stamp}.db')
        if backup_path.exists():
            raise ValueError(f'File sao lưu đã tồn tại: {backup_path}')
        backup = sqlite3.connect(backup_path)
        try:
            source.backup(backup)
        finally:
            backup.close()

    handle = tempfile.NamedTemporaryFile(prefix='workshop-migrating-', suffix='.db',
                                         dir=db_path.parent, delete=False)
    temporary_path = Path(handle.name)
    handle.close()
    try:
        old = sqlite3.connect(backup_path)
        old.row_factory = sqlite3.Row
        new = sqlite3.connect(temporary_path)
        new.row_factory = sqlite3.Row
        try:
            new.executescript(SCHEMA.read_text(encoding='utf-8'))
            for table in TABLES:
                if table not in present:
                    continue
                old_columns = {row['name'] for row in old.execute(f'PRAGMA table_info("{table}")')}
                new_columns = [row['name'] for row in new.execute(f'PRAGMA table_info("{table}")')]
                columns = [name for name in new_columns if name in old_columns]
                names = ', '.join(f'"{name}"' for name in columns)
                markers = ', '.join('?' for _ in columns)
                statement = f'INSERT INTO "{table}" ({names}) VALUES ({markers})'
                for row in old.execute(f'SELECT {names} FROM "{table}"'):
                    new.execute(statement, tuple(row))
            new.commit()
            new.execute('PRAGMA foreign_keys = ON')
            if new.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Liên kết khóa ngoại không hợp lệ; CSDL gốc vẫn nguyên.')
            if new.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Kiểm tra toàn vẹn thất bại; CSDL gốc vẫn nguyên.')
            for table, expected in counts.items():
                actual = new.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                if actual != expected:
                    raise ValueError(f'Số bản ghi {table} sai sau chuyển đổi.')
        finally:
            old.close()
            new.close()
        os.replace(temporary_path, db_path)
        return f'Đã chuyển CSDL. Bản sao lưu: {backup_path}'
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=Path, default=DEFAULT_DATABASE)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    print(migrate(args.path, args.apply))
