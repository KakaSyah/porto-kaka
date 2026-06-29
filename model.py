import logging
import time

import pymysql
import pymysql.cursors

from config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _get_connection():
    """Buat koneksi baru ke TiDB/MySQL (cocok untuk serverless Vercel)."""
    cfg = Config.MYSQL_CONFIG.copy()

    ssl_opts = None
    if cfg.get('ssl_ca'):
        ssl_opts = {'ca': cfg['ssl_ca']}

    conn = pymysql.connect(
        host=cfg['host'],
        port=int(cfg['port']),
        user=cfg['user'],
        password=cfg['password'],
        database=cfg['database'],
        ssl=ssl_opts,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
        autocommit=False,
    )
    return conn


class Database:
    """
    Wrapper database tanpa connection pool — kompatibel dengan Vercel serverless.
    Setiap pemanggilan membuka koneksi baru dan menutupnya setelah selesai.
    """

    _initialized = False

    def __new__(cls):
        # Tidak perlu singleton ketat; cukup pastikan init hanya sekali per cold start
        instance = super().__new__(cls)
        return instance

    def __init__(self):
        if Config.DB_DRIVER != 'mysql':
            raise ValueError("DB_DRIVER harus 'mysql'")

        missing = [
            name for name, value in {
                'DB_HOST': Config.DB_HOST,
                'DB_USER': Config.DB_USER,
                'DB_PASSWORD': Config.DB_PASSWORD,
                'DB_NAME': Config.DB_NAME,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Konfigurasi MySQL belum lengkap: {', '.join(missing)}")

        if not Database._initialized:
            self._init_mysql()
            Database._initialized = True

    def get_connection(self):
        return _get_connection()

    def execute_query(self, query, params=None, fetch=False):
        """Menjalankan query untuk MySQL/TiDB."""
        start_time = time.time()
        conn = _get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch:
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = cursor.lastrowid if cursor.lastrowid else True

            elapsed = time.time() - start_time
            logger.debug("Query executed in %.3fs: %s...", elapsed, query.strip()[:50])
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _normalize_query(self, query):
        return query

    def _init_mysql(self):
        statements = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(30) NOT NULL DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                nama_lengkap VARCHAR(150),
                nama_panggilan VARCHAR(100),
                tempat_lahir VARCHAR(100),
                email VARCHAR(150),
                telepon VARCHAR(50),
                universitas VARCHAR(150),
                fakultas VARCHAR(150),
                prodi VARCHAR(150),
                semester VARCHAR(20),
                alamat TEXT,
                foto_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_profiles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS experiences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                posisi VARCHAR(150) NOT NULL,
                perusahaan VARCHAR(150) NOT NULL,
                durasi VARCHAR(100) NOT NULL,
                deskripsi TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_experiences_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                judul VARCHAR(150) NOT NULL,
                deskripsi TEXT NOT NULL,
                gambar_url TEXT,
                link_project TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_projects_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS skills (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                nama_skill VARCHAR(120) NOT NULL,
                icon_class VARCHAR(120),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_skills_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            INSERT INTO users (username, password_hash, role)
            VALUES ('admin', 'admin123', 'admin')
            ON DUPLICATE KEY UPDATE
                password_hash = VALUES(password_hash),
                role = VALUES(role)
            """
        ]

        conn = _get_connection()
        try:
            with conn.cursor() as cursor:
                for statement in statements:
                    cursor.execute(statement)

                if not Config.SEED_DEMO_DATA:
                    cursor.execute("DELETE FROM skills WHERE user_id = 1 AND nama_skill IN ('Python', 'Flask', 'MySQL')")
                    cursor.execute("DELETE FROM projects WHERE user_id = 1 AND judul = 'Website Portofolio'")
                    cursor.execute("DELETE FROM experiences WHERE user_id = 1 AND posisi = 'Mahasiswa'")

                if Config.SEED_DEMO_DATA:
                    cursor.execute("""
                        INSERT INTO profiles (
                            user_id, nama_lengkap, nama_panggilan, email, telepon,
                            universitas, fakultas, prodi, semester, alamat, foto_url
                        )
                        SELECT 1, 'Nama Lengkap Anda', 'Admin', 'admin@example.com',
                            '08xxxxxxxxxx', 'Nama Universitas', 'Nama Fakultas',
                            'Program Studi', '1', 'Alamat Anda', ''
                        WHERE NOT EXISTS (SELECT 1 FROM profiles WHERE user_id = 1)
                    """)
                    cursor.execute("""
                        INSERT INTO skills (user_id, nama_skill, icon_class)
                        SELECT 1, 'Python', 'fab fa-python'
                        WHERE NOT EXISTS (SELECT 1 FROM skills WHERE user_id = 1 AND nama_skill = 'Python')
                    """)
                    cursor.execute("""
                        INSERT INTO skills (user_id, nama_skill, icon_class)
                        SELECT 1, 'Flask', 'fas fa-server'
                        WHERE NOT EXISTS (SELECT 1 FROM skills WHERE user_id = 1 AND nama_skill = 'Flask')
                    """)
                    cursor.execute("""
                        INSERT INTO skills (user_id, nama_skill, icon_class)
                        SELECT 1, 'MySQL', 'fas fa-database'
                        WHERE NOT EXISTS (SELECT 1 FROM skills WHERE user_id = 1 AND nama_skill = 'MySQL')
                    """)
                    cursor.execute("""
                        INSERT INTO projects (user_id, judul, deskripsi, gambar_url, link_project)
                        SELECT 1, 'Website Portofolio',
                            'Project portofolio yang bisa dikelola dari halaman admin.',
                            '', ''
                        WHERE NOT EXISTS (SELECT 1 FROM projects WHERE user_id = 1 AND judul = 'Website Portofolio')
                    """)
                    cursor.execute("""
                        INSERT INTO experiences (user_id, posisi, perusahaan, durasi, deskripsi)
                        SELECT 1, 'Mahasiswa', 'Nama Kampus', '2024 - Sekarang',
                            'Contoh pengalaman awal. Silakan ubah dari halaman admin.'
                        WHERE NOT EXISTS (SELECT 1 FROM experiences WHERE user_id = 1 AND posisi = 'Mahasiswa')
                    """)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
