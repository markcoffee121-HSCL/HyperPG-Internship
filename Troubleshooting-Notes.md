# Troubleshooting Notes - HyperPG Internship

## Date: November 12, 2025
## Day: 1 - Environment Setup

---

## Environment Configuration

**Operating System:** Windows 11  
**Development Tools:**
- PowerShell 7
- VS Code
- Docker Desktop 28.4.0
- Git 2.49.0
- Python 3.11, 3.12, 3.13

**Workspace Location:** `C:\HyperPG-Internship`

---

## Installations & Verifications

### Docker
- **Status:** ✓ Working
- **Version:** 28.4.0, build d8eb465
- **Verification:** `docker run hello-world` executed successfully
- **Screenshot:** See `docs/docker-verification.png`
- **Notes:** Docker Desktop must be running before executing commands

### Git
- **Status:** ✓ Configured
- **Version:** 2.49.0.windows.1
- **User:** Mark (markcoffee121@gmail.com)
- **SSH Key Generated:** November 12, 2025
- **Key Type:** ed25519
- **Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHGofe9VnMTFl7Le96YHPEs5SJf7hmwqV32LN5MKaWG8`
- **Action Required:** Add public key to GitHub at https://github.com/settings/keys

### Python
- **Installed Versions:** 3.13 (default), 3.12, 3.11
- **Recommendation:** Use Python 3.11 for AI/ML projects (most stable)
- **Virtual Environment:** Create per-project environments
- **Switch Version:** Use `py -3.11` to explicitly use Python 3.11

### Additional Tools
- **curl:** 8.13.0 ✓
- **jq:** 1.6 ✓

---

## Workspace Structure

```
C:\HyperPG-Internship\
├── AIMs/                          # Workspace for AIM development
├── docs/                          # Documentation and screenshots
│   └── docker-verification.png    # Docker hello-world proof
└── Troubleshooting-Notes.md       # This file
```

---

## Known Issues & Solutions

### Issue 1: Python Version Compatibility
- **Problem:** Python 3.13 sometimes has dependency issues with AI/ML packages
- **Solution:** Use Python 3.11 for AIM development
- **Command:** `py -3.11 -m venv venv`
- **Background:** From previous HSCL projects (Days 18-28), Python 3.11 proved most reliable

### Issue 2: Docker Not Running
- **Problem:** Docker commands fail with "Cannot connect to Docker daemon"
- **Solution:** Ensure Docker Desktop is running in system tray
- **Verification:** `docker ps` should not error

### Issue 3: PowerShell Script Execution
- **Problem:** Scripts won't run due to execution policy
- **Solution:** `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Issue 4: Pydantic Dependency Conflicts (Historical)
- **Problem:** Pydantic 2.x requires Rust compiler on Windows with Python 3.13
- **Solution:** Use Python 3.11 or downgrade Pydantic to 1.10.x
- **Note:** This was encountered during HSCL Days 23-26

### Issue 5: Docker Build Times (Historical)
- **Problem:** Docker builds taking 45+ minutes due to unnecessary compiler installations
- **Solution:** Avoid installing gcc, g++, and build-essential unless absolutely required
- **Optimization:** Use pre-built wheels and minimal base images

---

## HyperPG Architecture Notes

### What is Docker Used For?

Docker is the core containerization technology in HyperPG's architecture:

1. **AIM Encapsulation:** Each AIM (AI Model) is wrapped in its own Docker container, making it:
   - Self-contained and isolated
   - Portable across different environments
   - Easy to deploy and scale
   - Consistent across development, testing, and production

2. **Local Development:** Docker allows developing AIMs locally before deploying to nodes:
   - Build and test AIMs on Windows/macOS
   - Deploy to Ubuntu nodes seamlessly
   - Same container runs everywhere

3. **Docker Registry:** AIMs are stored in Docker registries:
   - **Official:** Hypercycle registry (default)
   - **Local:** `localhost:5000` for development/testing
   - **Custom:** Can configure custom registries in `config.yaml`

4. **Node Management:** The Hypercycle Node Manager uses Docker to:
   - Pull AIM images from registries
   - Run AIM containers with proper resource allocation
   - Manage AIM lifecycle (start, stop, update, health checks)
   - Orchestrate multiple AIMs on a single node

5. **HTTP Interface:** Each AIM container exposes:
   - Primary endpoint (varies by AIM function)
   - `/health` endpoint for monitoring
   - Built using `py-hypercycleaim` library

### Why SSH Keys Instead of Passwords?

1. **Security:**
   - SSH keys use asymmetric cryptography (public/private key pairs)
   - Private key never leaves your machine
   - Much harder to brute force than passwords
   - No password exposure in logs or memory dumps

2. **Automation:**
   - No need to type passwords repeatedly
   - Scripts and CI/CD can authenticate automatically
   - Essential for Git operations in automated workflows
   - Enables seamless AIM deployment pipelines

3. **Access Control:**
   - Public key can be added to multiple services (GitHub, GitLab, servers)
   - Revoke access by removing public key, no password changes needed
   - Each key can have specific permissions and scopes
   - Audit trail of key usage

4. **HyperPG Context:**
   - AIMs will be pushed to Git repositories
   - Nodes may need to pull from private repos
   - SSH keys enable secure, automated deployments
   - CI/CD pipelines can build and deploy AIMs without manual intervention

---

## Understanding py-hypercycleaim Library

From the HSCL training (Days 18-28), we extensively used `py-hypercycleaim` for building AIM servers:

### Key Components:

```python
from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS

class MyAIMServer(SimpleServer):
    manifest = {
        "name": "MyAIM",
        "short_name": "myaim",
        "version": "0.1.0",
        "documentation_url": "...",
        "license": "MIT",
        "author": "Mark"
    }
    
    @aim_uri(
        uri="/endpoint",
        methods=["GET", "POST"],
        endpoint_manifest={...},
        is_public=True
    )
    async def my_endpoint(self, request):
        # Handle request
        return JSONResponseCORS({"result": "data"})
```

### Standard Endpoints Pattern:
1. **Main Endpoint:** Primary function (e.g., `/process`, `/analyze`, `/generate`)
2. **Health Endpoint:** `/health` for monitoring

### Installation:
```
# In requirements.txt:
git+https://github.com/hypercycle-development/pyhypercycle-aim.git#egg=pyhypercycle_aim
```

---

## Daily Learnings

### Day 1 Key Takeaways:

1. **Platform Differences:**
   - AIM development: Can be done on Windows
   - Node installation: Ubuntu 22.04 or macOS only
   - Windows users develop AIMs locally, deploy to Ubuntu nodes

2. **Docker as Foundation:**
   - Docker is fundamental to the entire HyperPG ecosystem
   - Every AIM is a Docker container
   - Local registry for testing, production registry for deployment

3. **Development Workflow:**
   ```
   Develop AIM → Build Docker Image → Test Locally → 
   Push to Registry → Deploy to Node → Monitor Health
   ```

4. **Essential Tools:**
   - Docker: Container runtime
   - Git/SSH: Version control and authentication
   - Python 3.11: Most stable for AI/ML work
   - jq: JSON parsing in scripts
   - curl: API testing and debugging

5. **HSCL Experience Applied:**
   - Built 10+ AI agents (Days 18-28)
   - All used py-hypercycleaim framework
   - All containerized with Docker
   - Consistent architecture patterns apply to AIMs

---

## Next Steps for Day 2:

Based on the curriculum structure:
- [ ] Learn Docker basics specific to AIM development
- [ ] Understand AIM manifest format and requirements
- [ ] Study py-hypercycleaim library in depth
- [ ] Practice building simple Docker images
- [ ] Explore AIM architecture patterns

---

## Resources & Links

### Official Documentation:
- HyperPG Documentation: https://hyperpg.site/docs/
- Hypercycle GitHub: https://github.com/hypercycle-development
- py-hypercycleaim: https://github.com/hypercycle-development/pyhypercycle-aim

### General Tools:
- Docker Documentation: https://docs.docker.com/
- Docker Hub: https://hub.docker.com/
- Git Documentation: https://git-scm.com/doc

### HSCL Project References:
- GitHub Organization: https://github.com/markcoffee121-HSCL
- Previous Projects: ComparisonAgent, SQLQueryAgent, ResearchAgent, TradingSignalAgent, TaskPlanningAgent, SocialMediaAgent, Multi-Agent Research System, Capstone Multi-Agent System

---

## Personal Notes

### SSH Key Management:
- **Generated:** November 12, 2025
- **Location:** `C:\Users\msi\.ssh\id_ed25519`
- **Public Key:** Added to GitHub account
- **Usage:** All Git operations now use SSH authentication

### Development Environment Preferences:
- **Editor:** VS Code
- **Shell:** PowerShell 7
- **Python:** 3.11 for production, 3.13 available
- **Workflow:** Phase-by-phase development (not step-by-step)
- **Testing:** After each phase, comprehensive test suite

### From HSCL Training Experience:
- Groq API with llama-3.1-8b-instant model (consistent across all projects)
- py-hypercycleaim for REST API servers
- LangChain for agent orchestration
- Docker for containerization
- Comprehensive testing before deployment
- GitHub for version control (markcoffee121-HSCL organization)

---

## Verification Checklist - Day 1

- [x] Docker installed and verified
- [x] Git installed and configured
- [x] Python 3.10+ available (3.11, 3.12, 3.13)
- [x] curl installed and working
- [x] jq installed and working
- [x] SSH key generated (ed25519)
- [ ] SSH key added to GitHub account
- [x] Workspace folder created (`C:\HyperPG-Internship`)
- [x] AIMs subfolder created
- [x] docs subfolder created
- [x] Docker screenshot captured
- [x] Troubleshooting Notes created
- [ ] Internship resources repo cloned (if available)

---

## End of Day 1 Status: COMPLETE ✓

**Date Completed:** November 12, 2025  
**Next Session:** Day 2 - Docker & AIM Fundamentals