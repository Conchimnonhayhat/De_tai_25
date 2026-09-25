"""
Database Connection & Management Module
Supports explicit MySQL or SQLite configuration.
Ensures parameterized queries and transaction safety.
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)
SQLITE_DB_PATH = INSTANCE_DIR / "workshop.db"

# Check if MySQL is configured and requested
USE_MYSQL = os.getenv("USE_MYSQL", "false").lower() in ("true", "1", "yes")

_mysql_connector = None
if USE_MYSQL:
    try:
        import mysql.connector
        _mysql_connector = mysql.connector
    except ImportError as exc:
        raise RuntimeError('USE_MYSQL được bật nhưng chưa cài mysql-connector-python.') from exc


def get_db_connection():
    """Returns a raw database connection based on environment configuration."""
    if USE_MYSQL:
        try:
            conn = _mysql_connector.connect(
                host=os.getenv("MYSQL_HOST", "localhost"),
                user=os.getenv("MYSQL_USER", "root"),
                password=os.getenv("MYSQL_PASSWORD", ""),
                database=os.getenv("MYSQL_DATABASE", "workshop_db"),
                port=int(os.getenv("MYSQL_PORT", 3306)),
                autocommit=False
            )
            return conn, "mysql"
        except Exception as exc:
            raise RuntimeError('Không thể kết nối MySQL; kiểm tra cấu hình và máy chủ. Không chuyển sang SQLite.') from exc
            
    # SQLite connection with dict-like row factory
    conn = sqlite3.connect(str(SQLITE_DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn, "sqlite"


def _adapt_query(query: str, db_type: str) -> str:
    """Adapts query placeholders for SQLite if needed."""
    if db_type == "sqlite":
        # SQLite uses ? instead of %s
        return query.replace("%s", "?")
    return query


def query_db(query: str, args=(), one: bool = False):
    """
    Executes a SELECT query using parameterized arguments.
    Returns list of dicts, or single dict if one=True.
    """
    conn, db_type = get_db_connection()
    adapted_query = _adapt_query(query, db_type)
    cursor = None
    try:
        if db_type == "mysql":
            cursor = conn.cursor(dictionary=True)
            cursor.execute(adapted_query, args)
            results = cursor.fetchall()
        else:
            cursor = conn.cursor()
            cursor.execute(adapted_query, args)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            
        return (results[0] if results else None) if one else results
    finally:
        if cursor:
            cursor.close()
        conn.close()


def execute_db(query: str, args=(), commit: bool = True):
    """
    Executes an INSERT, UPDATE, or DELETE query with parameterized arguments.
    Returns the lastrowid or affected rowcount.
    """
    conn, db_type = get_db_connection()
    adapted_query = _adapt_query(query, db_type)
    cursor = None
    try:
        if db_type == "mysql":
            cursor = conn.cursor()
            cursor.execute(adapted_query, args)
            last_id = cursor.lastrowid
            if commit:
                conn.commit()
            return last_id
        else:
            cursor = conn.cursor()
            cursor.execute(adapted_query, args)
            last_id = cursor.lastrowid
            if commit:
                conn.commit()
            return last_id
    finally:
        if cursor:
            cursor.close()
        conn.close()


@contextmanager
def transaction():
    """Context manager for atomic multi-statement database operations."""
    conn, db_type = get_db_connection()
    cursor = None
    try:
        if db_type == "mysql":
            cursor = conn.cursor(dictionary=True)
        else:
            cursor = conn.cursor()
        
        class TxExecutor:
            def execute(self, q, params=()):
                aq = _adapt_query(q, db_type)
                cursor.execute(aq, params)
                return cursor.rowcount
                
            def query(self, q, params=(), one_row=False):
                aq = _adapt_query(q, db_type)
                cursor.execute(aq, params)
                if db_type == "mysql":
                    res = cursor.fetchall()
                else:
                    rows = cursor.fetchall()
                    res = [dict(r) for r in rows]
                return (res[0] if res else None) if one_row else res
                
        yield TxExecutor()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        conn.close()


def init_db(force: bool = False):
    """Initializes tables and seeds initial data if empty."""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    try:
        schema_file = BASE_DIR / "database" / "schema.sql"
        seed_file = BASE_DIR / "database" / "seed_data.sql"
        
        if db_type == "sqlite":
            # For SQLite, check if TaiKhoan table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TaiKhoan'")
            table_exists = cursor.fetchone()
            
            if force:
                # Drop all tables cleanly in SQLite
                cursor.execute("PRAGMA foreign_keys = OFF;")
                tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'").fetchall()
                for t in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {t['name']}")
                cursor.execute("PRAGMA foreign_keys = ON;")
                table_exists = False

            if not table_exists:
                with open(schema_file, "r", encoding="utf-8") as f:
                    schema_sql = f.read()
                cursor.executescript(schema_sql)
                
                with open(seed_file, "r", encoding="utf-8") as f:
                    seed_sql = f.read()
                cursor.executescript(seed_sql)
                conn.commit()
            else:
                columns = cursor.execute('PRAGMA table_info(TaiKhoan)').fetchall()
                code_type = next((row['type'].upper() for row in columns if row['name'] == 'MaTaiKhoan'), '')
                if code_type != 'VARCHAR(32)':
                    raise RuntimeError('CSDL SQLite cũ dùng mã số. Chạy database/migrate_sqlite_codes.py sau khi sao lưu.')
                cursor.executescript(schema_file.read_text(encoding='utf-8'))
            conn.commit()
        else:
            cursor.execute("SHOW TABLES LIKE 'TaiKhoan'")
            if cursor.fetchone():
                cursor.execute("SHOW COLUMNS FROM TaiKhoan LIKE 'MaTaiKhoan'")
                column = cursor.fetchone()
                if column and column[1].lower() != 'varchar(32)':
                    raise RuntimeError('CSDL MySQL cũ dùng mã số; cần migration trước khi chạy phiên bản này.')
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            schema_sql = '\n'.join(line.split('--', 1)[0] for line in schema_sql.splitlines())
            for stmt in schema_sql.split(";"):
                stmt = stmt.strip()
                if stmt:
                    is_index = stmt.startswith(('CREATE INDEX IF NOT EXISTS',
                                                'CREATE UNIQUE INDEX IF NOT EXISTS'))
                    mysql_stmt = stmt.replace('CREATE UNIQUE INDEX IF NOT EXISTS', 'CREATE UNIQUE INDEX')
                    mysql_stmt = mysql_stmt.replace('CREATE INDEX IF NOT EXISTS', 'CREATE INDEX')
                    try:
                        cursor.execute(mysql_stmt)
                    except _mysql_connector.Error as exc:
                        if not (is_index and exc.errno == 1061):
                            raise
            conn.commit()
    finally:
        cursor.close()
        conn.close()
