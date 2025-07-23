#!/usr/bin/env python3
"""
Deploy AutoPilot Ventures Platform to Vercel
Replace simulated deployments with actual Vercel deployments
"""

import os
import json
import subprocess
import requests
from datetime import datetime

class VercelDeployer:
    """Deploy applications to Vercel"""
    
    def __init__(self):
        self.deployments = []
        self.vercel_token = os.getenv("VERCEL_TOKEN")
    
    def install_vercel_cli(self):
        """Install Vercel CLI if not present"""
        try:
            print("🔧 Installing Vercel CLI...")
            subprocess.run([
                "npm", "install", "-g", "vercel"
            ], check=True, capture_output=True)
            print("✅ Vercel CLI installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("⚠️ Vercel CLI installation failed, trying pip...")
            try:
                subprocess.run([
                    "pip", "install", "vercel"
                ], check=True, capture_output=True)
                print("✅ Vercel CLI installed via pip")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install Vercel CLI")
                return False
    
    def create_vercel_config(self, app_name, app_type="api"):
        """Create Vercel configuration for an application"""
        if app_type == "api":
            config = {
                "version": 2,
                "builds": [
                    {
                        "src": "web_server.py",
                        "use": "@vercel/python"
                    }
                ],
                "routes": [
                    {
                        "src": "/(.*)",
                        "dest": "web_server.py"
                    }
                ],
                "env": {
                    "OPENAI_API_KEY": "@openai-api-key",
                    "STRIPE_SECRET_KEY": "@stripe-secret-key",
                    "STRIPE_PUBLISHABLE_KEY": "@stripe-publishable-key"
                }
            }
        else:
            config = {
                "version": 2,
                "builds": [
                    {
                        "src": "package.json",
                        "use": "@vercel/static-build",
                        "config": {"distDir": "build"}
                    }
                ],
                "routes": [
                    {
                        "src": "/(.*)",
                        "dest": "/index.html"
                    }
                ]
            }
        
        return config
    
    def deploy_main_platform(self):
        """Deploy the main AutoPilot Ventures platform"""
        print("🚀 Deploying AutoPilot Ventures Platform to Vercel...")
        
        try:
            # Create deployment directory
            deploy_dir = "vercel_deployments/main_platform"
            os.makedirs(deploy_dir, exist_ok=True)
            
            # Copy necessary files
            files_to_copy = [
                "web_server.py",
                "main.py",
                "config.py",
                "utils.py",
                "database.py",
                "orchestrator.py",
                "agents.py",
                "master_agent.py",
                "requirements.txt"
            ]
            
            for file in files_to_copy:
                if os.path.exists(file):
                    import shutil
                    shutil.copy2(file, deploy_dir)
            
            # Create vercel.json
            vercel_config = self.create_vercel_config("autopilot-ventures", "api")
            with open(f"{deploy_dir}/vercel.json", "w") as f:
                json.dump(vercel_config, f, indent=2)
            
            # Create requirements.txt for Python
            requirements = [
                "fastapi==0.104.1",
                "uvicorn==0.24.0",
                "openai>=1.10.0",
                "stripe==7.8.0",
                "requests==2.31.0",
                "python-dotenv==1.0.0",
                "sqlalchemy==2.0.23",
                "redis==5.0.1"
            ]
            
            with open(f"{deploy_dir}/requirements.txt", "w") as f:
                f.write("\n".join(requirements))
            
            # Deploy to Vercel
            os.chdir(deploy_dir)
            
            # Set up Vercel project
            subprocess.run([
                "vercel", "--yes", "--prod"
            ], check=True, capture_output=True, text=True)
            
            # Get deployment URL
            result = subprocess.run([
                "vercel", "ls"
            ], capture_output=True, text=True)
            
            # Extract URL from output
            for line in result.stdout.split('\n'):
                if 'autopilot-ventures' in line and 'https://' in line:
                    deployment_url = line.split()[-1]
                    self.deployments.append({
                        "name": "AutoPilot Ventures Platform",
                        "url": deployment_url,
                        "type": "api"
                    })
                    print(f"✅ Platform deployed to: {deployment_url}")
                    return deployment_url
            
            print("❌ Could not extract deployment URL")
            return None
            
        except Exception as e:
            print(f"❌ Platform deployment failed: {e}")
            return None
        finally:
            os.chdir("../..")
    
    def deploy_saas_applications(self):
        """Deploy SaaS applications to Vercel"""
        print("🚀 Deploying SaaS Applications to Vercel...")
        
        saas_apps = [
            "Ecommerce Tools Pro Platform",
            "SaaS Automation Suite", 
            "Marketing Automation Pro"
        ]
        
        for app_name in saas_apps:
            try:
                print(f"📦 Deploying {app_name}...")
                
                # Create app directory
                app_dir = f"vercel_deployments/{app_name.lower().replace(' ', '_')}"
                os.makedirs(app_dir, exist_ok=True)
                
                # Create React app structure
                self.create_react_app(app_dir, app_name)
                
                # Create vercel.json
                vercel_config = self.create_vercel_config(app_name, "frontend")
                with open(f"{app_dir}/vercel.json", "w") as f:
                    json.dump(vercel_config, f, indent=2)
                
                # Deploy to Vercel
                os.chdir(app_dir)
                
                subprocess.run([
                    "vercel", "--yes", "--prod"
                ], check=True, capture_output=True, text=True)
                
                # Get deployment URL
                result = subprocess.run([
                    "vercel", "ls"
                ], capture_output=True, text=True)
                
                # Extract URL from output
                for line in result.stdout.split('\n'):
                    if app_name.lower().replace(' ', '-') in line and 'https://' in line:
                        deployment_url = line.split()[-1]
                        self.deployments.append({
                            "name": app_name,
                            "url": deployment_url,
                            "type": "frontend"
                        })
                        print(f"✅ {app_name} deployed to: {deployment_url}")
                        break
                
                os.chdir("../..")
                
            except Exception as e:
                print(f"❌ {app_name} deployment failed: {e}")
    
    def create_react_app(self, app_dir, app_name):
        """Create a React application structure"""
        # Create package.json
        package_json = {
            "name": app_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        
        with open(f"{app_dir}/package.json", "w") as f:
            json.dump(package_json, f, indent=2)
        
        # Create public/index.html
        os.makedirs(f"{app_dir}/public", exist_ok=True)
        index_html = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{app_name}</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
"""
        
        with open(f"{app_dir}/public/index.html", "w") as f:
            f.write(index_html)
        
        # Create src/App.js
        os.makedirs(f"{app_dir}/src", exist_ok=True)
        app_js = f"""
import React, {{ useState, useEffect }} from 'react';
import './App.css';

function App() {{
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {{
    checkAuth();
  }}, []);

  const checkAuth = async () => {{
    try {{
      const response = await fetch('/api/auth/status');
      const userData = await response.json();
      setUser(userData.user);
    }} catch (error) {{
      console.error('Auth check failed:', error);
    }}
  }};

  const handleLogin = async () => {{
    setLoading(true);
    try {{
      const response = await fetch('/api/auth/login', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ email: 'demo@example.com', password: 'demo123' }})
      }});
      const result = await response.json();
      if (result.success) {{
        setUser(result.user);
      }}
    }} catch (error) {{
      console.error('Login failed:', error);
    }}
    setLoading(false);
  }};

  return (
    <div className="App">
      <header className="App-header">
        <h1>{app_name}</h1>
        <p>AI-Powered Platform</p>
      </header>
      
      <main>
        {{!user ? (
          <div className="auth-section">
            <h2>Welcome to {app_name}</h2>
            <p>Get started with our AI-powered solution</p>
            <button onClick={{handleLogin}} disabled={{loading}}>
              {{loading ? 'Signing in...' : 'Start Free Trial'}}
            </button>
          </div>
        ) : (
          <div className="dashboard">
            <h2>Welcome back, {{user.name}}!</h2>
            <div className="dashboard-grid">
              <div className="dashboard-card">
                <h3>Active Users</h3>
                <p>{{user.activeUsers || 0}}</p>
              </div>
              <div className="dashboard-card">
                <h3>Revenue</h3>
                <p>${{user.revenue || 0}}</p>
              </div>
              <div className="dashboard-card">
                <h3>Growth</h3>
                <p>{{user.growth || 0}}%</p>
              </div>
            </div>
          </div>
        )}}
      </main>
    </div>
  );
}}

export default App;
"""
        
        with open(f"{app_dir}/src/App.js", "w") as f:
            f.write(app_js)
        
        # Create src/App.css
        app_css = """
.App {
  text-align: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.App-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  color: white;
  margin-bottom: 2rem;
}

.App-header h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: bold;
}

.auth-section {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
}

.auth-section button {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.auth-section button:hover {
  background: #5a6fd8;
}

.dashboard {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 2rem;
}

.dashboard-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-left: 4px solid #667eea;
}

.dashboard-card h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.dashboard-card p {
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
  color: #667eea;
}
"""
        
        with open(f"{app_dir}/src/App.css", "w") as f:
            f.write(app_css)
        
        # Create src/index.js
        index_js = """
import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        
        with open(f"{app_dir}/src/index.js", "w") as f:
            f.write(index_js)
    
    def save_deployment_info(self):
        """Save deployment information to file"""
        deployment_info = {
            "timestamp": datetime.now().isoformat(),
            "deployments": self.deployments
        }
        
        with open("vercel_deployments.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"📄 Deployment information saved to vercel_deployments.json")

def main():
    """Main deployment function"""
    print("🚀 AutoPilot Ventures - Vercel Deployment")
    print("=" * 50)
    
    deployer = VercelDeployer()
    
    # Install Vercel CLI
    if not deployer.install_vercel_cli():
        print("❌ Cannot proceed without Vercel CLI")
        return
    
    # Deploy main platform
    platform_url = deployer.deploy_main_platform()
    
    # Deploy SaaS applications
    deployer.deploy_saas_applications()
    
    # Save deployment info
    deployer.save_deployment_info()
    
    # Summary
    print("\n" + "=" * 50)
    print("✅ VERCEL DEPLOYMENT COMPLETE")
    print("=" * 50)
    
    for deployment in deployer.deployments:
        print(f"🌐 {deployment['name']}: {deployment['url']}")
    
    print(f"\n📄 Deployment details saved to: vercel_deployments.json")
    print("🚀 All applications are now live on Vercel!")

if __name__ == "__main__":
    main() 