#!/usr/bin/env python3
"""
Cross-platform deployment script for Crane Intelligence Platform
Supports Windows, Linux, and macOS deployments
"""
import os
import sys
import subprocess
import platform
import json
from pathlib import Path

class CrossPlatformDeployer:
    """Cross-platform deployment manager"""
    
    def __init__(self):
        self.os_name = platform.system().lower()
        self.is_windows = self.os_name == 'windows'
        self.is_linux = self.os_name == 'linux'
        self.is_mac = self.os_name == 'darwin'
        
        self.project_root = Path(__file__).parent.parent
        self.deploy_config = self.load_deploy_config()
    
    def load_deploy_config(self):
        """Load deployment configuration"""
        config_file = self.project_root / 'deploy' / 'deploy_config.json'
        
        default_config = {
            "environments": {
                "development": {
                    "host": "localhost",
                    "backend_port": 8003,
                    "frontend_port": 3000,
                    "database_url": "sqlite:///./crane_intelligence.db",
                    "debug": True
                },
                "production": {
                    "host": "0.0.0.0",
                    "backend_port": 8000,
                    "frontend_port": 80,
                    "database_url": "sqlite:///./crane_intelligence.db",
                    "debug": False
                }
            },
            "services": {
                "backend": {
                    "command": "python run_backend.py",
                    "working_dir": ".",
                    "environment": "development"
                },
                "frontend": {
                    "command": "python -m http.server",
                    "working_dir": "frontend",
                    "environment": "development"
                }
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load deploy config: {e}")
                return default_config
        else:
            # Create default config
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def get_os_specific_commands(self, environment="development"):
        """Get OS-specific deployment commands"""
        env_config = self.deploy_config["environments"][environment]
        
        if self.is_windows:
            return {
                "backend": f"cd {self.project_root} && venv\\Scripts\\activate && python run_backend.py",
                "frontend": f"cd {self.project_root}\\frontend && python -m http.server {env_config['frontend_port']}",
                "install": "venv\\Scripts\\activate && pip install -r backend\\requirements.txt",
                "test": "venv\\Scripts\\activate && python -m pytest tests/"
            }
        else:
            return {
                "backend": f"cd {self.project_root} && source venv/bin/activate && python run_backend.py",
                "frontend": f"cd {self.project_root}/frontend && python -m http.server {env_config['frontend_port']}",
                "install": "source venv/bin/activate && pip install -r backend/requirements.txt",
                "test": "source venv/bin/activate && python -m pytest tests/"
            }
    
    def create_systemd_service(self, service_name, command, working_dir):
        """Create systemd service file for Linux"""
        if not self.is_linux:
            return False
        
        service_content = f"""[Unit]
Description=Crane Intelligence {service_name.title()}
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={working_dir}
ExecStart={command}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path(f"/etc/systemd/system/{service_name}.service")
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            print(f"✅ Created systemd service: {service_file}")
            return True
        except PermissionError:
            print(f"❌ Permission denied. Run with sudo to create systemd service")
            return False
    
    def create_windows_service(self, service_name, command, working_dir):
        """Create Windows service (requires NSSM or similar)"""
        if not self.is_windows:
            return False
        
        print(f"📝 Windows service creation for {service_name}:")
        print(f"   Working Directory: {working_dir}")
        print(f"   Command: {command}")
        print("   Note: Use NSSM or Windows Service Manager to create the service")
        return True
    
    def deploy_development(self):
        """Deploy for development environment"""
        print("🚀 Deploying for development environment...")
        
        commands = self.get_os_specific_commands("development")
        
        # Install dependencies
        print("📦 Installing dependencies...")
        if not self.run_command(commands["install"]):
            return False
        
        # Test the installation
        print("🧪 Testing installation...")
        if not self.run_command(commands["test"]):
            print("⚠️  Tests failed, but continuing with deployment")
        
        print("✅ Development deployment completed")
        return True
    
    def deploy_production(self):
        """Deploy for production environment"""
        print("🚀 Deploying for production environment...")
        
        commands = self.get_os_specific_commands("production")
        
        # Install dependencies
        print("📦 Installing production dependencies...")
        if not self.run_command(commands["install"]):
            return False
        
        # Create services
        print("🔧 Creating system services...")
        
        if self.is_linux:
            # Create systemd services
            self.create_systemd_service(
                "crane-backend",
                commands["backend"],
                str(self.project_root)
            )
            self.create_systemd_service(
                "crane-frontend", 
                commands["frontend"],
                str(self.project_root / "frontend")
            )
        elif self.is_windows:
            # Create Windows services
            self.create_windows_service(
                "crane-backend",
                commands["backend"],
                str(self.project_root)
            )
            self.create_windows_service(
                "crane-frontend",
                commands["frontend"], 
                str(self.project_root / "frontend")
            )
        
        print("✅ Production deployment completed")
        return True
    
    def run_command(self, command):
        """Run a command and return success status"""
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e.stderr}")
            return False
    
    def show_deployment_info(self, environment):
        """Show deployment information"""
        env_config = self.deploy_config["environments"][environment]
        
        print("\n" + "="*60)
        print(f"🎉 CRANE INTELLIGENCE PLATFORM - {environment.upper()} DEPLOYMENT")
        print("="*60)
        print(f"🌐 Frontend: http://{env_config['host']}:{env_config['frontend_port']}")
        print(f"🔧 Backend API: http://{env_config['host']}:{env_config['backend_port']}")
        print(f"📚 API Docs: http://{env_config['host']}:{env_config['backend_port']}/docs")
        print(f"❤️  Health Check: http://{env_config['host']}:{env_config['backend_port']}/health")
        print("="*60)

def main():
    """Main deployment function"""
    if len(sys.argv) < 2:
        print("Usage: python cross_platform_deploy.py [development|production]")
        sys.exit(1)
    
    environment = sys.argv[1].lower()
    if environment not in ["development", "production"]:
        print("Error: Environment must be 'development' or 'production'")
        sys.exit(1)
    
    deployer = CrossPlatformDeployer()
    
    if environment == "development":
        success = deployer.deploy_development()
    else:
        success = deployer.deploy_production()
    
    if success:
        deployer.show_deployment_info(environment)
    else:
        print("❌ Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
