"""
Cross-platform environment configuration for Crane Intelligence Platform
Handles OS-specific paths, commands, and configurations
"""
import os
import sys
import platform
from pathlib import Path
from typing import Dict, Any

class EnvironmentConfig:
    """Cross-platform environment configuration"""
    
    def __init__(self):
        self.os_name = platform.system().lower()
        self.is_windows = self.os_name == 'windows'
        self.is_linux = self.os_name == 'linux'
        self.is_mac = self.os_name == 'darwin'
        
        # Get project root directory
        self.project_root = Path(__file__).parent.parent.absolute()
        
        # Set OS-specific configurations
        self._setup_paths()
        self._setup_commands()
        self._setup_environment()
    
    def _setup_paths(self):
        """Setup OS-specific paths"""
        if self.is_windows:
            self.path_separator = '\\'
            self.venv_activate = self.project_root / 'venv' / 'Scripts' / 'activate'
            self.python_executable = 'python'
            self.python_module = 'python'
        else:
            self.path_separator = '/'
            self.venv_activate = self.project_root / 'venv' / 'bin' / 'activate'
            self.python_executable = 'python3'
            self.python_module = 'python3'
        
        # Common paths
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend'
        self.data_dir = self.project_root / 'data'
        self.logs_dir = self.project_root / 'logs'
        self.temp_dir = self.project_root / 'temp'
        
        # Database paths
        self.database_file = self.project_root / 'crane_intelligence.db'
        self.backup_dir = self.project_root / 'backups'
    
    def _setup_commands(self):
        """Setup OS-specific commands"""
        if self.is_windows:
            self.venv_activate_cmd = f"& '{self.venv_activate}'"
            self.python_cmd = f"python"
            self.pip_cmd = f"pip"
            self.background_cmd = "Start-Process"
        else:
            self.venv_activate_cmd = f"source {self.venv_activate}"
            self.python_cmd = f"python3"
            self.pip_cmd = f"pip3"
            self.background_cmd = "nohup"
    
    def _setup_environment(self):
        """Setup environment variables"""
        self.env_vars = {
            'PROJECT_ROOT': str(self.project_root),
            'BACKEND_DIR': str(self.backend_dir),
            'FRONTEND_DIR': str(self.frontend_dir),
            'DATA_DIR': str(self.data_dir),
            'LOGS_DIR': str(self.logs_dir),
            'OS_NAME': self.os_name,
            'PYTHON_EXECUTABLE': self.python_executable,
            'VENV_ACTIVATE': str(self.venv_activate)
        }
    
    def get_database_url(self) -> str:
        """Get database URL for current environment"""
        if self.is_windows:
            return f"sqlite:///{self.database_file}"
        else:
            return f"sqlite:///{self.database_file}"
    
    def get_static_files_path(self) -> str:
        """Get static files path for FastAPI"""
        return str(self.frontend_dir)
    
    def get_frontend_serve_path(self) -> str:
        """Get frontend serve path"""
        return str(self.frontend_dir)
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            self.logs_dir,
            self.temp_dir,
            self.backup_dir,
            self.data_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_startup_commands(self) -> Dict[str, str]:
        """Get OS-specific startup commands"""
        if self.is_windows:
            return {
                'backend': f"cd {self.project_root} && {self.venv_activate_cmd} && python run_backend.py",
                'frontend': f"cd {self.frontend_dir} && python -m http.server 3000",
                'combined': f"cd {self.project_root} && {self.venv_activate_cmd} && start python run_backend.py && cd {self.frontend_dir} && start python -m http.server 3000"
            }
        else:
            return {
                'backend': f"cd {self.project_root} && {self.venv_activate_cmd} && {self.python_cmd} run_backend.py",
                'frontend': f"cd {self.frontend_dir} && {self.python_cmd} -m http.server 3000",
                'combined': f"cd {self.project_root} && {self.venv_activate_cmd} && {self.background_cmd} {self.python_cmd} run_backend.py & cd {self.frontend_dir} && {self.background_cmd} {self.python_cmd} -m http.server 3000 &"
            }
    
    def get_requirements_file(self) -> str:
        """Get requirements file path"""
        return str(self.backend_dir / 'requirements.txt')
    
    def get_venv_path(self) -> str:
        """Get virtual environment path"""
        return str(self.project_root / 'venv')
    
    def is_venv_activated(self) -> bool:
        """Check if virtual environment is activated"""
        return hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

# Global instance
env_config = EnvironmentConfig()

# Export commonly used values
PROJECT_ROOT = env_config.project_root
BACKEND_DIR = env_config.backend_dir
FRONTEND_DIR = env_config.frontend_dir
DATABASE_URL = env_config.get_database_url()
STATIC_FILES_PATH = env_config.get_static_files_path()
IS_WINDOWS = env_config.is_windows
IS_LINUX = env_config.is_linux
