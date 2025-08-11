# Data Engineering Platform
# Comprehensive Setup, Configuration, and Usage Guide

**Version**: 1.0  
**Last Updated**: January 2024  
**Platform Components**: Apache Airflow, PostgreSQL, Apache Spark, Jupyter, pgAdmin, dbt

---

# Table of Contents

1. [Introduction and Overview](#1-introduction-and-overview)
2. [Platform Architecture and Components](#2-platform-architecture-and-components)
3. [Prerequisites and System Requirements](#3-prerequisites-and-system-requirements)
4. [Windows Detailed Setup Guide](#4-windows-detailed-setup-guide)
5. [Mac Detailed Setup Guide](#5-mac-detailed-setup-guide)
6. [Platform File Structure and Configuration](#6-platform-file-structure-and-configuration)
7. [Starting and Accessing Services](#7-starting-and-accessing-services)
8. [Detailed Service Usage Guide](#8-detailed-service-usage-guide)
9. [Creating Data Pipelines](#9-creating-data-pipelines)
10. [Database Operations and Management](#10-database-operations-and-management)
11. [Troubleshooting Guide](#11-troubleshooting-guide)
12. [Best Practices and Tips](#12-best-practices-and-tips)
13. [Appendix: Complete Setup Scripts](#13-appendix-complete-setup-scripts)

---

# 1. Introduction and Overview

## What This Guide Provides

This comprehensive guide provides complete, step-by-step instructions for setting up a production-ready data engineering platform on your personal computer. Every command, every click, and every configuration is documented in detail.

## What You Will Build

A complete data engineering environment featuring:

- **Apache Airflow 2.8.1**: Enterprise-grade workflow orchestration for scheduling and monitoring data pipelines
- **PostgreSQL 15**: High-performance analytical database optimized for data warehouse workloads
- **Apache Spark 3.5.1**: Distributed computing framework for big data processing
- **Jupyter Lab**: Interactive development environment with PySpark integration
- **pgAdmin 4**: Comprehensive PostgreSQL management interface
- **dbt (Data Build Tool)**: Modern data transformation framework integrated with Airflow

## Why This Platform

This platform provides:
- **Production-Ready Architecture**: Same tools and patterns used by Fortune 500 companies
- **Local Development**: Everything runs on your computer - no cloud costs
- **One-Command Setup**: Automated installation and configuration
- **Hot Reload Development**: Code changes reflect immediately without restart
- **Resource Optimization**: Automatically detects and allocates system resources
- **Comprehensive Integration**: All tools are pre-configured to work together

## Time Investment

- **First-Time Setup**: 45-60 minutes
- **Daily Startup**: 2-3 minutes
- **Learning Curve**: Basic operations in 1 day, proficiency in 1-2 weeks

---

# 2. Platform Architecture and Components

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Access Layer                        │
│                    (Web Browser & VS Code)                      │
├─────────────────────────────────────────────────────────────────┤
│  Airflow UI  │  pgAdmin UI  │  Jupyter Lab  │  Spark Master UI  │
│  Port: 8080  │  Port: 8081  │  Port: 8888   │   Port: 8082      │
└──────┬───────┴──────┬───────┴──────┬────────┴────────┬──────────┘
       │              │              │                 │
┌──────┴──────────────┴──────────────┴─────────────────┴──────────┐
│                    Docker Container Network                     │
│                       (data_network)                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐             │
│  │  PostgreSQL │  │   Airflow    │  │    Spark    │             │
│  │  Analytics  │  │  ┌─────────┐ │  │  ┌────────┐ │             │
│  │  Database   │  │  │Webserver│ │  │  │ Master │ │             │
│  │             │  │  ├─────────┤ │  │  ├────────┤ │             │
│  │  Optimized  │  │  │Scheduler│ │  │  │ Worker │ │             │
│  │  for OLAP   │  │  ├─────────┤ │  │  └────────┘ │             │
│  │             │  │  │ Worker  │ │  │             │             │
│  └─────────────┘  │  └─────────┘ │  └─────────────┘             │
│                   └──────────────┘                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐             │
│  │   pgAdmin   │  │   Jupyter    │  │     dbt     │             │
│  │     Web     │  │     Lab      │  │ (integrated │             │
│  │  Interface  │  │   PySpark    │  │   w/Airflow)│             │
│  └─────────────┘  └──────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
       │                    │                    │
┌──────┴────────────────────┴────────────────────┴─────────────────┐
│                     Persistent Storage Layer                     │
├──────────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Airflow    │   Spark    │  Notebooks │   dbt     │
│  Data Files  │  DAGs/Logs  │   Jobs     │   .ipynb   │  Models   │
└──────────────┴─────────────┴────────────┴────────────┴───────────┘
```

## Component Specifications

### PostgreSQL Database
- **Version**: 15-alpine (latest stable)
- **Configuration**: Optimized for analytics with 2GB shared buffers
- **Extensions**: pg_stat_statements, uuid-ossp, hstore, pg_trgm
- **Features**: Parallel query execution, partitioning support
- **Access**: Direct connection on port 5432, managed via pgAdmin

### Apache Airflow
- **Version**: 2.8.1 with Python 3.10
- **Executor**: LocalExecutor (upgradeable to Celery/Kubernetes)
- **Features**: Auto-reload DAGs, integrated dbt, PostgreSQL operators
- **Database**: Separate PostgreSQL instance for metadata
- **UI**: Full-featured web interface with admin capabilities

### Apache Spark
- **Version**: 3.5.1 with Scala 2.12
- **Mode**: Standalone cluster with master and worker
- **Memory**: Configurable (default 2GB for worker)
- **Integration**: JDBC PostgreSQL connector pre-installed
- **Libraries**: PySpark, Spark SQL, MLlib available

### Jupyter Lab
- **Base Image**: jupyter/pyspark-notebook
- **Kernel**: Python 3.10 with PySpark
- **Libraries**: pandas, numpy, matplotlib, seaborn, scikit-learn
- **Features**: Direct Spark context, PostgreSQL connectivity

### pgAdmin 4
- **Version**: Latest
- **Features**: Query tool, ERD visualization, backup/restore
- **Pre-configured**: Automatic connection to PostgreSQL
- **Access**: Web-based interface, no client installation needed

### dbt (Data Build Tool)
- **Version**: Latest
- **Integration**: Embedded in Airflow container
- **Features**: Model compilation, testing, documentation
- **Database**: Connected to PostgreSQL analytics database

---

# 3. Prerequisites and System Requirements

## Hardware Requirements

### Minimum Requirements
- **RAM**: 8GB (system will allocate 6GB to services)
- **CPU**: 4 cores (2.0GHz or higher)
- **Storage**: 20GB free space
- **Network**: Broadband internet for initial download

### Recommended Requirements
- **RAM**: 16GB or more
- **CPU**: 6+ cores (3.0GHz or higher)
- **Storage**: 50GB+ free SSD space
- **Network**: High-speed internet

## Operating System Requirements

### Windows
- **Minimum**: Windows 10 version 2004 (Build 19041)
- **Recommended**: Windows 11 or Windows 10 22H2
- **Required Features**: WSL2, Virtualization enabled in BIOS

### macOS
- **Minimum**: macOS 10.15 (Catalina)
- **Recommended**: macOS 12+ (Monterey or newer)
- **Architecture**: Intel or Apple Silicon (M1/M2)

## Software Prerequisites

The following will be installed during setup:
- Docker Desktop (latest version)
- Visual Studio Code
- Git
- Python 3.8+
- WSL2 (Windows only)
- Homebrew (macOS only)

---

# 4. Windows Detailed Setup Guide

## Step 1: Check System Requirements

### 1.1 Verify Windows Version
1. Press `Windows Key + R`
2. Type `winver` and press Enter
3. Verify you have Version 2004 or higher
4. If not, update Windows:
   - Settings → Update & Security → Windows Update
   - Check for updates and install
   - Restart when complete

### 1.2 Check Virtualization
1. Press `Ctrl + Shift + Esc` to open Task Manager
2. Click "Performance" tab
3. Click "CPU" on the left
4. Look for "Virtualization: Enabled"
5. If disabled, enable in BIOS:
   - Restart computer
   - Press F2/F10/DEL during boot (varies by manufacturer)
   - Find "Virtualization Technology" or "VT-x"
   - Enable and save

## Step 2: Install WSL2

### 2.1 Open PowerShell as Administrator
1. Right-click Start button
2. Select "Windows PowerShell (Admin)"
3. Click "Yes" when prompted for permissions

### 2.2 Install WSL2
```powershell
# Enable WSL feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Download and install WSL2
wsl --install

# Set WSL2 as default
wsl --set-default-version 2
```

### 2.3 Restart Computer
- Save all work
- Click Start → Power → Restart
- Wait for complete restart

### 2.4 Complete Ubuntu Setup
After restart:
1. Ubuntu terminal opens automatically
2. Wait for "Installing, this may take a few minutes..."
3. Create UNIX username:
   - Use lowercase, no spaces (e.g., "dataeng")
   - Press Enter
4. Create password:
   - Type a secure password
   - Nothing appears while typing (this is normal!)
   - Press Enter
5. Confirm password:
   - Type the same password again
   - Press Enter

### 2.5 Configure WSL2 Resources
1. Create WSL config file:
```powershell
# In PowerShell (not as admin)
notepad "$env:USERPROFILE\.wslconfig"
```

2. Add this configuration:
```ini
[wsl2]
memory=6GB
processors=4
localhostForwarding=true
kernelCommandLine=cgroup_no_v1=all
swap=2GB
```

3. Save and close Notepad

4. Apply changes:
```powershell
wsl --shutdown
```

## Step 3: Install Docker Desktop

### 3.1 Download Docker Desktop
1. Open web browser
2. Navigate to: https://www.docker.com/products/docker-desktop/
3. Click "Download for Windows"
4. Save Docker Desktop Installer.exe (about 500MB)

### 3.2 Install Docker Desktop
1. Locate downloaded file in Downloads folder
2. Double-click "Docker Desktop Installer.exe"
3. Installation options:
   - ✓ **Enable WSL 2 Windows Features** (must be checked)
   - ✓ Add shortcut to desktop (optional)
4. Click "Ok"
5. Wait for installation (5-10 minutes)
6. Click "Close and restart" when prompted

### 3.3 Configure Docker Desktop
After restart:
1. Docker Desktop starts automatically
2. Accept Docker Subscription Service Agreement
3. Skip tutorial if offered
4. Click Settings (gear icon)
5. General settings:
   - ✓ Start Docker Desktop when you log in
   - ✓ Use the WSL 2 based engine
6. Resources → WSL Integration:
   - ✓ Enable integration with my default WSL distro
   - ✓ Ubuntu (should be checked)
7. Apply & Restart

### 3.4 Verify Docker Installation
1. Look for whale icon in system tray
2. Right-click whale → "About Docker Desktop"
3. Verify version information displays

## Step 4: Install Visual Studio Code

### 4.1 Download VS Code
1. Navigate to: https://code.visualstudio.com/
2. Click "Download for Windows"
3. Save VSCodeUserSetup-x64.exe

### 4.2 Install VS Code
1. Run downloaded installer
2. Accept license agreement
3. Installation options:
   - ✓ Add to PATH (important!)
   - ✓ Add "Open with Code" to context menu
   - ✓ Register Code as editor for supported files
4. Click Install
5. Launch Visual Studio Code when complete
6. On Windows PowerShell
  ```bash
  alias vscode='"/c/Users/YourUsername/AppData/Local/Programs/Microsoft VS Code/Code.exe"'
  ```

### 4.3 Install Essential Extensions
1. Open VS Code
2. Click Extensions icon (four squares) on left sidebar
3. Search and install each:
   - **WSL** by Microsoft
   - **Docker** by Microsoft
   - **Python** by Microsoft
   - **PostgreSQL** by Chris Kolkman
   - **YAML** by Red Hat
   - **GitLens** by GitKraken

## Step 5: Prepare Ubuntu Environment

### 5.1 Open Ubuntu Terminal
1. Click Start button
2. Type "Ubuntu"
3. Click Ubuntu app
4. Terminal window opens with prompt like: `dataeng@computer:~$`

### 5.2 Update Ubuntu Packages
```bash
# Update package lists
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y
```
This takes 5-10 minutes first time.

### 5.3 Install Required Tools
```bash
# Install essential development tools
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    nano \
    vim \
    htop \
    jq \
    postgresql-client

# Verify installations
python3 --version
git --version
docker --version
```

### 5.4 Configure Git
```bash
# Set your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Enable credential storage
git config --global credential.helper store
```

## Step 6: Create the Data Engineering Platform

### 6.1 Create Project Structure
```bash
# Navigate to home directory
cd ~

# Create projects folder
mkdir -p projects
cd projects

# Create platform directory
mkdir data-engineering-platform
cd data-engineering-platform

# Verify location
pwd
# Should show: /home/yourusername/projects/data-engineering-platform
```

### 6.2 Download Setup Script
```bash
# Create the comprehensive setup script
nano setup_complete_platform.sh
```

Copy and paste the entire setup script from the appendix section, then:
- Press `Ctrl + O` to save
- Press Enter to confirm
- Press `Ctrl + X` to exit

### 6.3 Run Platform Setup
```bash
# Make script executable
chmod +x setup_complete_platform.sh

# Run the setup
./setup_complete_platform.sh
```

This script will:
- Create all directory structures
- Generate all configuration files
- Set up Docker Compose
- Create helper scripts
- Configure VS Code integration

### 6.4 Start the Platform
```bash
# Use the simple setup for first run
./scripts/simple-setup.sh
```

What happens:
1. Generates secure passwords automatically
2. Creates environment configuration
3. Downloads all Docker images (10-15 minutes first time)
4. Starts all services
5. Displays access credentials

**IMPORTANT**: Save the displayed passwords!

## Step 7: Verify Installation

### 7.1 Check Service Status
```bash
# Check all services are running
docker-compose ps

# Should show all services as "Up"
```

### 7.2 Test Service Access
Open web browser and verify each URL loads:
1. http://localhost:8080 (Airflow)
2. http://localhost:8081 (pgAdmin)
3. http://localhost:8888 (Jupyter)
4. http://localhost:8082 (Spark)

### 7.3 Open VS Code
```bash
# From platform directory
vscode .
```
VS Code should open with WSL: Ubuntu shown in bottom-left corner.

---

# 5. Mac Detailed Setup Guide

## Step 1: Check System Requirements

### 1.1 Verify macOS Version
1. Click Apple logo (🍎) in top-left corner
2. Select "About This Mac"
3. Check macOS version (need 10.15+)
4. If older, update:
   - System Preferences → Software Update
   - Install available updates
   - Restart when complete

### 1.2 Check Available Resources
1. About This Mac → More Info → System Report
2. Check Memory (need 8GB minimum)
3. Check Storage (need 20GB free)

## Step 2: Open Terminal

### 2.1 Using Spotlight
1. Press `Command + Space`
2. Type "Terminal"
3. Press Enter

### 2.2 First Time Terminal Setup
When Terminal opens:
- You see prompt like: `username@MacBook ~ %`
- This is your command line interface
- Commands are typed here and executed with Enter

## Step 3: Install Homebrew

### 3.1 Install Homebrew Package Manager
```bash
# Install Homebrew (copy entire command)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

What happens:
1. Asks for your Mac login password
2. Downloads and installs Homebrew
3. Shows progress with ==> markers
4. Takes 5-10 minutes

### 3.2 Add Homebrew to PATH
After installation completes:
```bash
# For Apple Silicon Macs (M1/M2)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# For Intel Macs
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

### 3.3 Verify Homebrew
```bash
# Check installation
brew --version
# Should show: Homebrew 4.x.x

# Update Homebrew
brew update
```

## Step 4: Install Required Software

### 4.1 Install Docker Desktop
```bash
# Install Docker Desktop via Homebrew
brew install --cask docker

# Alternative: Manual installation
# 1. Go to docker.com/products/docker-desktop
# 2. Download for Mac (choose Intel or Apple chip)
# 3. Open .dmg file
# 4. Drag Docker to Applications
```

### 4.2 Start Docker Desktop
1. Open Finder → Applications
2. Double-click Docker
3. If security warning appears:
   - Click "Open"
   - Enter Mac password if requested
4. Wait for Docker to start:
   - Menu bar shows whale icon
   - Icon stops animating when ready

### 4.3 Configure Docker Desktop
1. Click Docker whale icon → Preferences
2. General:
   - ✓ Start Docker Desktop when you log in
3. Resources:
   - CPUs: Set to half your Mac's cores
   - Memory: 6GB minimum (8GB recommended)
   - Swap: 1GB
   - Disk image size: 60GB
4. Apply & Restart

### 4.4 Install VS Code
```bash
# Install via Homebrew
brew install --cask visual-studio-code

# Open VS Code
open -a "Visual Studio Code"

# Create alias
alias vscode='"/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
```

### 4.5 Install Additional Tools
```bash
# Install development tools
brew install \
    git \
    python@3.11 \
    postgresql \
    wget \
    jq \
    htop

# Verify installations
git --version
python3 --version
psql --version
```

## Step 5: Configure Development Environment

### 5.1 Configure Git
```bash
# Set identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# macOS-specific settings
git config --global core.ignorecase false
git config --global init.defaultBranch main
```

### 5.2 Create SSH Key (Optional)
```bash
# Generate SSH key for GitHub
ssh-keygen -t ed25519 -C "your.email@example.com"
# Press Enter for default location
# Enter passphrase (optional)

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
pbcopy < ~/.ssh/id_ed25519.pub
# Now paste in GitHub settings
```

## Step 6: Create the Data Engineering Platform

### 6.1 Create Project Structure
```bash
# Navigate to home directory
cd ~

# Create projects directory
mkdir -p projects
cd projects

# Create platform directory
mkdir data-engineering-platform
cd data-engineering-platform

# Verify location
pwd
# Should show: /Users/yourusername/projects/data-engineering-platform
```

### 6.2 Create Setup Script
```bash
# Create comprehensive setup script
nano setup_complete_platform.sh
```

Copy and paste the entire setup script from the appendix, then:
- Press `Control + O` (not Command)
- Press Enter
- Press `Control + X`

### 6.3 Run Platform Setup
```bash
# Make executable
chmod +x setup_complete_platform.sh

# Run setup
./setup_complete_platform.sh
```

### 6.4 Start the Platform
```bash
# First time setup
./scripts/simple-setup.sh
```

Save the displayed passwords!

## Step 7: Verify Installation

### 7.1 Check Docker
```bash
# Verify Docker is running
docker info

# Check service status
docker-compose ps
```

### 7.2 Test Service Access
Open Safari/Chrome and test each:
1. http://localhost:8080 (Airflow)
2. http://localhost:8081 (pgAdmin)
3. http://localhost:8888 (Jupyter)
4. http://localhost:8082 (Spark)

### 7.3 Open in VS Code
```bash
# From project directory
vscode .
```

---

# 6. Platform File Structure and Configuration

## Complete Directory Structure

```
data-engineering-platform/
├── docker-compose.yml         # Main orchestration file
├── .env                       # Environment variables (auto-generated)
├── .env.template              # Template for environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
├── LICENSE                    # Apache 2.0 license
├── CONTRIBUTING.md            # Contribution guidelines
│
├── airflow/                   # Apache Airflow files
│   ├── dags/                  # DAG definitions go here
│   │   └── example_pipeline.py
│   ├── plugins/               # Custom operators and hooks
│   ├── config/                # Airflow configuration
│   │   └── airflow.cfg
│   ├── logs/                  # Execution logs (gitignored)
│   └── tests/                 # Airflow tests
│
├── spark/                     # Apache Spark files
│   └── jobs/                  # PySpark job scripts
│       └── customer_segmentation.py
│
├── dbt/                       # dbt project files
│   ├── dbt_project.yml        # dbt configuration
│   ├── profiles.yml           # Connection profiles
│   ├── models/                # SQL transformations
│   │   ├── staging/           # Staging models
│   │   └── marts/             # Business logic models
│   ├── tests/                 # Data quality tests
│   ├── macros/                # Reusable SQL macros
│   ├── seeds/                 # Static data files
│   └── snapshots/             # SCD Type 2 history
│
├── notebooks/                 # Jupyter notebooks
│   └── examples/
│       └── getting_started.ipynb
│
├── data/                      # Data storage
│   ├── raw/                   # Incoming raw data
│   ├── processed/             # Transformed data
│   └── archive/               # Historical data
│
├── sql/                       # SQL scripts
│   ├── schemas/               # DDL scripts
│   │   └── init_warehouse.sql
│   ├── migrations/            # Schema migrations
│   ├── functions/             # Stored procedures
│   └── views/                 # View definitions
│
├── docker/                    # Docker configurations
│   ├── postgres/              # PostgreSQL configs
│   │   └── postgresql.conf
│   └── pgadmin/               # pgAdmin configs
│       └── servers.json
│
├── scripts/                   # Utility scripts
│   ├── setup.sh               # Full setup script
│   ├── simple-setup.sh        # Quick setup
│   ├── start.sh               # Start services
│   ├── stop.sh                # Stop services
│   ├── status.sh              # Check status
│   ├── logs.sh                # View logs
│   ├── backup.sh              # Backup data
│   └── restore.sh             # Restore data
│
├── tests/                     # Project tests
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
│
├── backups/                   # Database backups
│
├── docs/                      # Documentation
│   ├── SETUP.md               # Setup guide
│   ├── USAGE.md               # Usage guide
│   ├── ARCHITECTURE.md        # Architecture details
│   └── DATA_MODELING.md       # Data modeling guide
│
├── .vscode/                   # VS Code settings
│   ├── settings.json          # Workspace settings
│   ├── extensions.json        # Recommended extensions
│   └── tasks.json             # Build tasks
│
└── .github/                   # GitHub configurations
    └── workflows/             # CI/CD pipelines
        └── ci.yml
```

## Key Configuration Files

### docker-compose.yml
The main orchestration file defining all services:
- Service definitions
- Network configuration
- Volume mappings
- Resource limits
- Health checks

### .env File
Auto-generated file containing:
- Database passwords
- Service configurations
- Resource allocations
- Ports and endpoints

### PostgreSQL Configuration
Optimized for analytics workloads:
- 2GB shared buffers
- Parallel query execution
- Analytics-focused extensions
- Performance monitoring

### Airflow Configuration
- LocalExecutor for single-machine setup
- Auto-reload for DAG development
- PostgreSQL backend
- Integrated authentication

---

# 7. Starting and Accessing Services

## Starting the Platform

### First Time Startup
```bash
# Navigate to platform directory
cd ~/projects/data-engineering-platform

# Run initial setup (creates passwords)
./scripts/simple-setup.sh
```

This process:
1. Checks Docker is running
2. Generates secure passwords
3. Creates .env configuration
4. Downloads Docker images (10-15 minutes)
5. Starts all containers
6. Shows access information

### Daily Startup
```bash
# Quick start (uses existing config)
cd ~/projects/data-engineering-platform
./scripts/start.sh
```

Takes 1-2 minutes as images are already downloaded.

### Verifying Services
```bash
# Check all services are running
docker-compose ps

# Output should show:
NAME                    STATUS    PORTS
postgres_dw             Up        0.0.0.0:5432->5432/tcp
postgres_airflow        Up        5432/tcp
airflow_webserver       Up        0.0.0.0:8080->8080/tcp
airflow_scheduler       Up        
spark_master            Up        0.0.0.0:7077->7077/tcp, 0.0.0.0:8082->8080/tcp
spark_worker            Up        0.0.0.0:8083->8081/tcp
jupyter_pyspark         Up        0.0.0.0:8888->8888/tcp
pgadmin4                Up        0.0.0.0:8081->80/tcp
```

## Accessing Services

### Apache Airflow - Workflow Management
- **URL**: http://localhost:8080
- **Default Username**: admin
- **Default Password**: SecurePass123! (or check your .env)
- **Purpose**: Create, schedule, and monitor data pipelines
- **First Time**:
  1. Login with credentials
  2. You'll see the DAGs list page
  3. Look for "example_pipeline" to start
  4. Click toggle to enable (turns blue)
  5. Click play button to run manually

### pgAdmin - Database Management
- **URL**: http://localhost:8081
- **Default Email**: admin@admin.com
- **Default Password**: admin
- **Purpose**: Visual PostgreSQL management
- **First Time**:
  1. Login with email/password
  2. Click "Servers" in left panel
  3. Right-click "PostgreSQL Analytics"
  4. Click "Connect"
  5. Enter password: SecurePass123!
  6. Check "Save Password"
  7. Browse databases and tables

### Jupyter Lab - Interactive Development
- **URL**: http://localhost:8888
- **Token**: SecurePass123! (or check your .env)
- **Purpose**: Interactive data analysis with Python/PySpark
- **First Time**:
  1. Enter token when prompted
  2. JupyterLab interface opens
  3. Click "Python 3" to create notebook
  4. Try: `print("Hello Data Engineering!")`
  5. Press Shift+Enter to run

### Spark UI - Cluster Monitoring
- **URL**: http://localhost:8082
- **No authentication required**
- **Purpose**: Monitor Spark jobs and resources
- **Shows**:
  - Worker nodes status
  - Running applications
  - Completed jobs
  - Resource utilization

### PostgreSQL Direct Access
- **Host**: localhost
- **Port**: 5432
- **Database**: datawarehouse
- **Username**: postgres
- **Password**: SecurePass123!
- **Connection String**: 
  ```
  postgresql://postgres:SecurePass123!@localhost:5432/datawarehouse
  ```

### VS Code Integration
```bash
# Open project in VS Code
cd ~/projects/data-engineering-platform
code .
```

Features:
- Syntax highlighting for SQL, Python
- Integrated terminal
- Git integration
- Database connections
- Debugging support

## Stopping Services

### Graceful Shutdown
```bash
# Stop all services
./scripts/stop.sh
```

### Force Stop (if needed)
```bash
# Force stop and remove containers
docker-compose down

# Also remove volumes (deletes data!)
docker-compose down -v
```

---

# 8. Detailed Service Usage Guide

## Apache Airflow

### Understanding Airflow
Airflow orchestrates data pipelines using:
- **DAGs**: Directed Acyclic Graphs defining workflow
- **Tasks**: Individual units of work
- **Operators**: Pre-built task templates
- **Schedulers**: Time-based execution

### Creating Your First DAG

1. **Create DAG File**
```bash
nano airflow/dags/my_first_dag.py
```

2. **Basic DAG Structure**
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Define default arguments
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Create DAG
dag = DAG(
    'my_first_pipeline',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval='@daily',  # Run daily
    catchup=False,  # Don't run for past dates
    tags=['tutorial'],
)

# Define tasks
def print_date(**context):
    """Python function to print date"""
    print(f"Execution date: {context['ds']}")
    return 'Date printed successfully!'

# Task 1: Python operator
print_date_task = PythonOperator(
    task_id='print_date',
    python_callable=print_date,
    dag=dag,
)

# Task 2: Bash operator
bash_task = BashOperator(
    task_id='print_hello',
    bash_command='echo "Hello from Bash!"',
    dag=dag,
)

# Task 3: SQL operator
create_table_task = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='postgres_default',
    sql="""
    CREATE TABLE IF NOT EXISTS daily_stats (
        date DATE PRIMARY KEY,
        record_count INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    dag=dag,
)

# Set dependencies
print_date_task >> bash_task >> create_table_task
```

3. **Save and Activate**
- Save file (Ctrl+O, Enter, Ctrl+X)
- Refresh Airflow UI
- Find "my_first_pipeline"
- Toggle ON
- Click "Trigger DAG"

### Airflow Best Practices

1. **DAG Design**
   - Keep DAGs simple and focused
   - Use meaningful task IDs
   - Set proper dependencies
   - Include documentation

2. **Error Handling**
   - Set appropriate retries
   - Use email alerts for critical DAGs
   - Implement data quality checks
   - Log important information

3. **Performance**
   - Avoid heavy processing in DAGs
   - Use appropriate pool sizes
   - Monitor task duration
   - Optimize SQL queries

## PostgreSQL Database

### Connecting via pgAdmin

> **⚠️ IMPORTANT**: If you get "connection refused" errors, verify that PostgreSQL is listening on all network interfaces by running:
> ```bash
> docker exec postgres_dw netstat -tlnp | grep 5432
> ```
> You should see `0.0.0.0:5432`. If you see `127.0.0.1:5432`, add `listen_addresses = '*'` to your PostgreSQL configuration and restart the container.


1. **First Connection**
   - Open http://localhost:8081
   - Login with admin@admin.com / admin
   - Right-click Servers → Create → Server
   - General tab:
     - Name: Local PostgreSQL
   - Connection tab:
     - Host: postgres
     - Port: 5432
     - Database: datawarehouse
     - Username: postgres
     - Password: SecurePass123!
     - Save password: Yes

2. **Using Query Tool**
   - Right-click database → Query Tool
   - Write and execute SQL
   - View results in grid
   - Save queries for reuse

### Creating Database Schema

```sql
-- Create schemas for organization
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Create a dimension table
CREATE TABLE marts.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    address_line1 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a fact table
CREATE TABLE marts.fct_sales (
    sale_key SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    customer_key INTEGER REFERENCES marts.dim_customer(customer_key),
    product_key INTEGER,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_fct_sales_date ON marts.fct_sales(date_key);
CREATE INDEX idx_fct_sales_customer ON marts.fct_sales(customer_key);

-- Insert sample data
INSERT INTO marts.dim_customer (customer_id, first_name, last_name, email) VALUES
('C001', 'John', 'Doe', 'john.doe@email.com'),
('C002', 'Jane', 'Smith', 'jane.smith@email.com'),
('C003', 'Bob', 'Johnson', 'bob.johnson@email.com');

-- Verify data
SELECT * FROM marts.dim_customer;
```

### PostgreSQL Performance Tips

1. **Indexing Strategy**
   ```sql
   -- Create covering index
   CREATE INDEX idx_customer_email 
   ON marts.dim_customer(email) 
   INCLUDE (first_name, last_name);
   
   -- Partial index for filtered queries
   CREATE INDEX idx_active_customers 
   ON marts.dim_customer(customer_id) 
   WHERE is_active = true;
   ```

2. **Query Optimization**
   ```sql
   -- Check query plan
   EXPLAIN (ANALYZE, BUFFERS) 
   SELECT * FROM marts.fct_sales 
   WHERE date_key = 20240115;
   
   -- Update statistics
   ANALYZE marts.fct_sales;
   ```

## Jupyter Notebooks

### Getting Started with Jupyter

1. **Access Jupyter Lab**
   - Open http://localhost:8888
   - Enter token: SecurePass123!
   - Interface loads

2. **Create First Notebook**
   - Click "Python 3" under Notebook
   - Rename: Right-click tab → Rename

3. **Basic Data Operations**
```python
# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

# Connect to PostgreSQL
engine = create_engine(
    'postgresql://postgres:SecurePass123!@postgres:5432/datawarehouse'
)

# Read data
query = "SELECT * FROM marts.dim_customer"
df_customers = pd.read_sql(query, engine)

# Display info
print(f"Shape: {df_customers.shape}")
print(f"\nColumns: {df_customers.columns.tolist()}")
print(f"\nFirst 5 rows:")
df_customers.head()
```

### Working with PySpark

```python
# Initialize Spark session
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("DataExploration") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

# Read data from PostgreSQL
jdbc_url = "jdbc:postgresql://postgres:5432/datawarehouse"
connection_properties = {
    "user": "postgres",
    "password": "SecurePass123!",
    "driver": "org.postgresql.Driver"
}

# Load customer data
df_customers_spark = spark.read.jdbc(
    url=jdbc_url,
    table="marts.dim_customer",
    properties=connection_properties
)

# Show schema
df_customers_spark.printSchema()

# Basic operations
print(f"Count: {df_customers_spark.count()}")
df_customers_spark.show(5)

# SQL operations
df_customers_spark.createOrReplaceTempView("customers")
spark.sql("SELECT count(*) as total_customers FROM customers").show()
```

### Data Visualization

```python
# Create sample data
dates = pd.date_range('2024-01-01', periods=30, freq='D')
sales = np.random.randint(1000, 5000, size=30)
df_sales = pd.DataFrame({'date': dates, 'sales': sales})

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Line plot
axes[0, 0].plot(df_sales['date'], df_sales['sales'])
axes[0, 0].set_title('Daily Sales Trend')
axes[0, 0].set_xlabel('Date')
axes[0, 0].set_ylabel('Sales')

# Bar plot
axes[0, 1].bar(range(len(df_sales)), df_sales['sales'])
axes[0, 1].set_title('Sales by Day')
axes[0, 1].set_xlabel('Day')
axes[0, 1].set_ylabel('Sales')

# Histogram
axes[1, 0].hist(df_sales['sales'], bins=10, edgecolor='black')
axes[1, 0].set_title('Sales Distribution')
axes[1, 0].set_xlabel('Sales Amount')
axes[1, 0].set_ylabel('Frequency')

# Box plot
axes[1, 1].boxplot(df_sales['sales'])
axes[1, 1].set_title('Sales Box Plot')
axes[1, 1].set_ylabel('Sales')

plt.tight_layout()
plt.show()
```

## Apache Spark

### Understanding Spark Architecture

In our platform:
- **Spark Master**: Coordinates jobs (port 7077)
- **Spark Worker**: Executes tasks (1 worker, 2GB RAM)
- **Spark UI**: Monitor jobs (port 8082)

### Creating Spark Jobs

1. **Create Job File**
```bash
nano spark/jobs/word_count.py
```

2. **Simple Spark Job**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc

def main():
    # Create Spark session
    spark = SparkSession.builder \
        .appName("WordCount") \
        .getOrCreate()
    
    # Create sample data
    data = [
        "Hello world",
        "Hello Spark",
        "Data Engineering with Spark",
        "Apache Spark is powerful"
    ]
    
    # Create DataFrame
    df = spark.createDataFrame(data, "string").toDF("text")
    
    # Word count
    words = df.select(explode(split(col("text"), " ")).alias("word"))
    word_counts = words.groupBy("word").count().sort(desc("count"))
    
    # Show results
    word_counts.show()
    
    # Save results
    word_counts.write.mode("overwrite").parquet("/data/processed/word_counts")
    
    # Stop Spark
    spark.stop()

if __name__ == "__main__":
    main()
```

3. **Submit Spark Job**
```bash
# From Airflow or terminal
docker exec spark_master spark-submit \
    --master spark://spark-master:7077 \
    /opt/spark/jobs/word_count.py
```

### Spark with PostgreSQL

```python
from pyspark.sql import SparkSession

# Create session with PostgreSQL driver
spark = SparkSession.builder \
    .appName("PostgreSQLIntegration") \
    .config("spark.jars", "/opt/spark/jars/postgresql-42.6.0.jar") \
    .getOrCreate()

# Connection properties
jdbc_url = "jdbc:postgresql://postgres:5432/datawarehouse"
connection_properties = {
    "user": "postgres",
    "password": "SecurePass123!",
    "driver": "org.postgresql.Driver"
}

# Read from PostgreSQL
df = spark.read.jdbc(
    url=jdbc_url,
    table="marts.fct_sales",
    properties=connection_properties
)

# Process data
summary = df.groupBy("customer_key") \
    .agg(
        count("sale_key").alias("total_purchases"),
        sum("total_amount").alias("total_spent"),
        avg("total_amount").alias("avg_purchase")
    )

# Write back to PostgreSQL
summary.write.mode("overwrite").jdbc(
    url=jdbc_url,
    table="marts.customer_summary",
    properties=connection_properties
)
```

---

# 9. Creating Data Pipelines

## End-to-End Pipeline Example

Let's create a complete data pipeline that:
1. Extracts data from a source
2. Transforms it using Spark
3. Loads into PostgreSQL
4. Runs dbt transformations
5. Creates visualizations

### Step 1: Create the DAG

```python
# airflow/dags/sales_analytics_pipeline.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.spark.operators.spark_submit import SparkSubmitOperator

default_args = {
    'owner': 'analytics-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'sales_analytics_pipeline',
    default_args=default_args,
    description='End-to-end sales analytics pipeline',
    schedule_interval='0 2 * * *',  # Run at 2 AM daily
    catchup=False,
    tags=['production', 'sales']
)

# Task 1: Extract data
def extract_sales_data(**context):
    """Extract sales data from source"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Generate sample data (replace with actual extraction)
    execution_date = context['execution_date']
    
    # Create sample sales data
    n_records = 1000
    data = {
        'transaction_id': range(1, n_records + 1),
        'customer_id': np.random.choice(['C001', 'C002', 'C003', 'C004', 'C005'], n_records),
        'product_id': np.random.choice(['P001', 'P002', 'P003', 'P004'], n_records),
        'quantity': np.random.randint(1, 10, n_records),
        'unit_price': np.random.uniform(10, 100, n_records).round(2),
        'transaction_date': execution_date
    }
    
    df = pd.DataFrame(data)
    df['total_amount'] = df['quantity'] * df['unit_price']
    
    # Save to raw data
    output_path = f'/opt/airflow/data/raw/sales_{execution_date.strftime("%Y%m%d")}.csv'
    df.to_csv(output_path, index=False)
    
    return output_path

extract_task = PythonOperator(
    task_id='extract_sales_data',
    python_callable=extract_sales_data,
    provide_context=True,
    dag=dag
)

# Task 2: Load to staging
load_staging_task = PostgresOperator(
    task_id='load_to_staging',
    postgres_conn_id='postgres_default',
    sql="""
    -- Create staging table
    CREATE TABLE IF NOT EXISTS staging.sales_{{ ds_nodash }} (
        transaction_id INTEGER,
        customer_id VARCHAR(10),
        product_id VARCHAR(10),
        quantity INTEGER,
        unit_price DECIMAL(10,2),
        total_amount DECIMAL(10,2),
        transaction_date DATE
    );
    
    -- Load data
    COPY staging.sales_{{ ds_nodash }}
    FROM '/data/raw/sales_{{ ds }}.csv'
    WITH (FORMAT csv, HEADER true);
    
    -- Create indexes
    CREATE INDEX idx_sales_{{ ds_nodash }}_customer 
    ON staging.sales_{{ ds_nodash }}(customer_id);
    """,
    dag=dag
)

# Task 3: Spark processing
spark_transform_task = SparkSubmitOperator(
    task_id='spark_customer_metrics',
    application='/opt/spark/jobs/calculate_customer_metrics.py',
    conn_id='spark_default',
    total_executor_cores=2,
    executor_memory='1g',
    driver_memory='1g',
    name='customer_metrics_{{ ds }}',
    application_args=['{{ ds }}'],
    dag=dag
)

# Task 4: Run dbt models
dbt_run_task = BashOperator(
    task_id='run_dbt_models',
    bash_command="""
    cd /opt/dbt && \
    dbt run --models staging.* marts.* --vars '{"execution_date": "{{ ds }}"}'
    """,
    dag=dag
)

# Task 5: Data quality checks
quality_check_task = PostgresOperator(
    task_id='data_quality_checks',
    postgres_conn_id='postgres_default',
    sql="""
    -- Check for duplicates
    DO $$
    DECLARE
        duplicate_count INTEGER;
    BEGIN
        SELECT COUNT(*) INTO duplicate_count
        FROM (
            SELECT transaction_id, COUNT(*)
            FROM staging.sales_{{ ds_nodash }}
            GROUP BY transaction_id
            HAVING COUNT(*) > 1
        ) t;
        
        IF duplicate_count > 0 THEN
            RAISE EXCEPTION 'Found % duplicate transactions', duplicate_count;
        END IF;
    END $$;
    
    -- Check for null values
    DO $$
    DECLARE
        null_count INTEGER;
    BEGIN
        SELECT COUNT(*) INTO null_count
        FROM staging.sales_{{ ds_nodash }}
        WHERE customer_id IS NULL 
           OR product_id IS NULL
           OR total_amount IS NULL;
        
        IF null_count > 0 THEN
            RAISE EXCEPTION 'Found % records with null values', null_count;
        END IF;
    END $$;
    """,
    dag=dag
)

# Task 6: Create summary
create_summary_task = PostgresOperator(
    task_id='create_daily_summary',
    postgres_conn_id='postgres_default',
    sql="""
    INSERT INTO marts.daily_sales_summary (
        summary_date,
        total_transactions,
        unique_customers,
        total_revenue,
        avg_transaction_value
    )
    SELECT 
        '{{ ds }}'::DATE,
        COUNT(*),
        COUNT(DISTINCT customer_id),
        SUM(total_amount),
        AVG(total_amount)
    FROM staging.sales_{{ ds_nodash }};
    """,
    dag=dag
)

# Set task dependencies
extract_task >> load_staging_task >> spark_transform_task
spark_transform_task >> dbt_run_task >> quality_check_task >> create_summary_task
```

### Step 2: Create Spark Job

```python
# spark/jobs/calculate_customer_metrics.py
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from datetime import datetime

def main(execution_date):
    # Initialize Spark
    spark = SparkSession.builder \
        .appName(f"CustomerMetrics_{execution_date}") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()
    
    # Database connection
    jdbc_url = "jdbc:postgresql://postgres:5432/datawarehouse"
    connection_properties = {
        "user": "postgres",
        "password": "SecurePass123!",
        "driver": "org.postgresql.Driver"
    }
    
    # Read staging data
    staging_table = f"staging.sales_{execution_date.replace('-', '')}"
    df_sales = spark.read.jdbc(
        url=jdbc_url,
        table=staging_table,
        properties=connection_properties
    )
    
    # Calculate customer metrics
    customer_metrics = df_sales.groupBy("customer_id") \
        .agg(
            count("transaction_id").alias("transaction_count"),
            sum("total_amount").alias("total_spent"),
            avg("total_amount").alias("avg_transaction_amount"),
            max("total_amount").alias("max_transaction_amount"),
            min("total_amount").alias("min_transaction_amount"),
            countDistinct("product_id").alias("unique_products_purchased")
        )
    
    # Add calculated fields
    customer_metrics = customer_metrics.withColumn(
        "customer_segment",
        when(col("total_spent") > 5000, "VIP")
        .when(col("total_spent") > 2000, "Premium")
        .when(col("total_spent") > 500, "Regular")
        .otherwise("New")
    )
    
    # Add processing date
    customer_metrics = customer_metrics.withColumn(
        "processing_date", 
        lit(execution_date)
    )
    
    # Write results to PostgreSQL
    customer_metrics.write \
        .mode("overwrite") \
        .jdbc(
            url=jdbc_url,
            table=f"marts.customer_metrics_{execution_date.replace('-', '')}",
            properties=connection_properties
        )
    
    # Show summary
    print(f"Processed {customer_metrics.count()} customers")
    customer_metrics.groupBy("customer_segment").count().show()
    
    spark.stop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: spark-submit calculate_customer_metrics.py <execution_date>")
        sys.exit(1)
    
    execution_date = sys.argv[1]
    main(execution_date)
```

### Step 3: Create dbt Models

```sql
-- dbt/models/staging/stg_sales.sql
{{ config(
    materialized='view',
    schema='staging'
) }}

WITH source_data AS (
    SELECT 
        transaction_id,
        customer_id,
        product_id,
        quantity,
        unit_price,
        total_amount,
        transaction_date,
        CURRENT_TIMESTAMP as loaded_at
    FROM staging.sales_{{ var('execution_date').replace('-', '') }}
)

SELECT 
    {{ dbt_utils.surrogate_key(['transaction_id']) }} as sale_key,
    transaction_id,
    customer_id,
    product_id,
    quantity,
    unit_price,
    total_amount,
    transaction_date,
    loaded_at
FROM source_data
WHERE total_amount > 0
```

```sql
-- dbt/models/marts/fct_daily_sales.sql
{{ config(
    materialized='incremental',
    unique_key='sale_key',
    on_schema_change='fail'
) }}

WITH sales_data AS (
    SELECT 
        sale_key,
        transaction_id,
        customer_id,
        product_id,
        quantity,
        unit_price,
        total_amount,
        transaction_date,
        loaded_at
    FROM {{ ref('stg_sales') }}
)

SELECT 
    s.sale_key,
    s.transaction_id,
    TO_CHAR(s.transaction_date, 'YYYYMMDD')::INTEGER as date_key,
    c.customer_key,
    p.product_key,
    s.quantity,
    s.unit_price,
    s.total_amount,
    s.transaction_date,
    s.loaded_at
FROM sales_data s
LEFT JOIN {{ ref('dim_customer') }} c
    ON s.customer_id = c.customer_id
LEFT JOIN {{ ref('dim_product') }} p
    ON s.product_id = p.product_id

{% if is_incremental() %}
WHERE s.loaded_at > (SELECT MAX(loaded_at) FROM {{ this }})
{% endif %}
```

### Step 4: Create Monitoring Dashboard

```python
# notebooks/sales_dashboard.ipynb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Database connection
engine = create_engine('postgresql://postgres:SecurePass123!@postgres:5432/datawarehouse')

# Load data
query = """
SELECT 
    transaction_date,
    COUNT(*) as transaction_count,
    SUM(total_amount) as daily_revenue,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(total_amount) as avg_transaction_value
FROM marts.fct_daily_sales
WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY transaction_date
ORDER BY transaction_date
"""

df_daily = pd.read_sql(query, engine)

# Create dashboard
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Daily Revenue', 'Transaction Count', 
                    'Unique Customers', 'Average Transaction Value'),
    specs=[[{"type": "scatter"}, {"type": "bar"}],
           [{"type": "scatter"}, {"type": "scatter"}]]
)

# Daily Revenue
fig.add_trace(
    go.Scatter(x=df_daily['transaction_date'], 
               y=df_daily['daily_revenue'],
               mode='lines+markers',
               name='Revenue'),
    row=1, col=1
)

# Transaction Count
fig.add_trace(
    go.Bar(x=df_daily['transaction_date'], 
           y=df_daily['transaction_count'],
           name='Transactions'),
    row=1, col=2
)

# Unique Customers
fig.add_trace(
    go.Scatter(x=df_daily['transaction_date'], 
               y=df_daily['unique_customers'],
               mode='lines+markers',
               name='Customers'),
    row=2, col=1
)

# Average Transaction Value
fig.add_trace(
    go.Scatter(x=df_daily['transaction_date'], 
               y=df_daily['avg_transaction_value'],
               mode='lines+markers',
               name='Avg Value'),
    row=2, col=2
)

# Update layout
fig.update_layout(
    title_text="Sales Analytics Dashboard",
    showlegend=False,
    height=800
)

fig.show()

# Customer Segment Analysis
query_segments = """
SELECT 
    customer_segment,
    COUNT(*) as customer_count,
    AVG(total_spent) as avg_spend,
    SUM(total_spent) as total_revenue
FROM marts.customer_metrics_{{ execution_date }}
GROUP BY customer_segment
"""

df_segments = pd.read_sql(query_segments, engine)

# Pie chart for customer segments
fig_pie = px.pie(df_segments, 
                 values='customer_count', 
                 names='customer_segment',
                 title='Customer Distribution by Segment')
fig_pie.show()
```

---

# 10. Database Operations and Management

## Database Design Best Practices

### Schema Organization

```sql
-- Create logical schemas
CREATE SCHEMA IF NOT EXISTS raw AUTHORIZATION postgres;
COMMENT ON SCHEMA raw IS 'Raw data from source systems';

CREATE SCHEMA IF NOT EXISTS staging AUTHORIZATION postgres;
COMMENT ON SCHEMA staging IS 'Cleaned and standardized data';

CREATE SCHEMA IF NOT EXISTS marts AUTHORIZATION postgres;
COMMENT ON SCHEMA marts IS 'Business-ready data models';

CREATE SCHEMA IF NOT EXISTS ml AUTHORIZATION postgres;
COMMENT ON SCHEMA ml IS 'Machine learning features and predictions';

-- Grant appropriate permissions
GRANT USAGE ON SCHEMA raw TO airflow_user;
GRANT ALL ON SCHEMA staging TO airflow_user;
GRANT SELECT ON ALL TABLES IN SCHEMA marts TO analytics_user;
```

### Creating Optimized Tables

```sql
-- Partitioned fact table for large datasets
CREATE TABLE marts.fct_sales_partitioned (
    sale_key BIGSERIAL,
    date_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    store_key INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (date_key);

-- Create monthly partitions
CREATE TABLE marts.fct_sales_y2024m01 
PARTITION OF marts.fct_sales_partitioned
FOR VALUES FROM (20240101) TO (20240201);

CREATE TABLE marts.fct_sales_y2024m02 
PARTITION OF marts.fct_sales_partitioned
FOR VALUES FROM (20240201) TO (20240301);

-- Create indexes on partitions
CREATE INDEX idx_fct_sales_y2024m01_customer 
ON marts.fct_sales_y2024m01(customer_key);

CREATE INDEX idx_fct_sales_y2024m01_product 
ON marts.fct_sales_y2024m01(product_key);
```

### Performance Optimization

```sql
-- Materialized view for complex aggregations
CREATE MATERIALIZED VIEW marts.mv_daily_sales_summary AS
SELECT 
    d.date_actual,
    d.year,
    d.quarter,
    d.month,
    d.week_of_year,
    COUNT(DISTINCT f.customer_key) as unique_customers,
    COUNT(f.sale_key) as transaction_count,
    SUM(f.quantity) as units_sold,
    SUM(f.total_amount) as gross_revenue,
    SUM(f.discount_amount) as total_discount,
    SUM(f.total_amount - f.discount_amount) as net_revenue,
    AVG(f.total_amount) as avg_transaction_value,
    MAX(f.total_amount) as max_transaction_value
FROM marts.fct_sales_partitioned f
JOIN marts.dim_date d ON f.date_key = d.date_key
GROUP BY 1, 2, 3, 4, 5
WITH DATA;

-- Create indexes on materialized view
CREATE INDEX idx_mv_daily_sales_date 
ON marts.mv_daily_sales_summary(date_actual);

-- Refresh materialized view (schedule in Airflow)
REFRESH MATERIALIZED VIEW CONCURRENTLY marts.mv_daily_sales_summary;
```

### Database Maintenance

```sql
-- Vacuum and analyze tables
VACUUM (VERBOSE, ANALYZE) marts.fct_sales_partitioned;

-- Update table statistics
ANALYZE marts.fct_sales_partitioned;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
                   pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname IN ('raw', 'staging', 'marts')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- Monitor long-running queries
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
  AND state = 'active'
ORDER BY duration DESC;
```

### Backup and Recovery

```bash
# Create backup script
nano scripts/backup_database.sh
```

```bash
#!/bin/bash
# Database backup script

BACKUP_DIR="/opt/airflow/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="datawarehouse"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting backup of $DB_NAME..."

# Full backup with custom format
docker exec postgres_dw pg_dump \
    -U postgres \
    -d $DB_NAME \
    -F custom \
    -f /tmp/backup_$TIMESTAMP.dump

# Copy backup from container
docker cp postgres_dw:/tmp/backup_$TIMESTAMP.dump $BACKUP_DIR/

# Create schema-only backup
docker exec postgres_dw pg_dump \
    -U postgres \
    -d $DB_NAME \
    --schema-only \
    -f /tmp/schema_$TIMESTAMP.sql

docker cp postgres_dw:/tmp/schema_$TIMESTAMP.sql $BACKUP_DIR/

# Compress backups
gzip $BACKUP_DIR/backup_$TIMESTAMP.dump
gzip $BACKUP_DIR/schema_$TIMESTAMP.sql

echo "Backup completed: $BACKUP_DIR/backup_$TIMESTAMP.dump.gz"

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
```

### Restore Procedure

```bash
# Restore from backup
nano scripts/restore_database.sh
```

```bash
#!/bin/bash
# Database restore script

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE=$1
DB_NAME="datawarehouse"

echo "Restoring database from $BACKUP_FILE..."

# Copy backup to container
docker cp $BACKUP_FILE postgres_dw:/tmp/restore.dump.gz

# Decompress
docker exec postgres_dw gunzip /tmp/restore.dump.gz

# Drop and recreate database
docker exec postgres_dw psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker exec postgres_dw psql -U postgres -c "CREATE DATABASE $DB_NAME;"

# Restore
docker exec postgres_dw pg_restore \
    -U postgres \
    -d $DB_NAME \
    -v \
    /tmp/restore.dump

echo "Restore completed!"
```

---

# 11. Troubleshooting Guide

## Common Issues and Solutions

### Docker Issues

#### Issue: Docker daemon not running
**Symptoms**: 
- Error: "Cannot connect to the Docker daemon"
- Docker commands fail

**Solutions**:
```bash
# Windows
1. Check Docker Desktop is running (system tray)
2. Right-click whale icon → Restart
3. If persists:
   - Open Services (services.msc)
   - Find "Docker Desktop Service"
   - Right-click → Restart

# Mac
1. Check Docker in menu bar
2. Click Docker → Restart
3. If persists:
   - Applications → Docker → Force Quit
   - Reopen Docker
```

#### Issue: WSL2 integration not working (Windows)
**Symptoms**:
- Docker commands fail in Ubuntu
- "docker: command not found"

**Solutions**:
```bash
# In PowerShell as Admin
wsl --set-default Ubuntu
wsl --shutdown

# Restart Docker Desktop
# Settings → Resources → WSL Integration
# Enable Ubuntu integration
```

### Service-Specific Issues

#### Airflow not accessible
**Symptoms**:
- http://localhost:8080 doesn't load
- Connection refused error

**Solutions**:
```bash
# Check if service is running
docker-compose ps airflow-webserver

# Check logs
docker-compose logs --tail=100 airflow-webserver

# Common fixes:
# 1. Wait longer (2-3 minutes for first start)
# 2. Restart service
docker-compose restart airflow-webserver

# 3. Check port conflict
netstat -an | grep 8080  # Mac/Linux
netstat -an | findstr 8080  # Windows

# 4. Force recreate
docker-compose up -d --force-recreate airflow-webserver
```

#### PostgreSQL connection issues
**Symptoms**:
- "FATAL: password authentication failed"
- "could not connect to server"

**Solutions**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker exec -it postgres_dw psql -U postgres -d datawarehouse

# Reset password
docker exec -it postgres_dw psql -U postgres -c "ALTER USER postgres PASSWORD 'SecurePass123!';"

# Check environment variables
cat .env | grep POSTGRES
```

#### Jupyter kernel dying
**Symptoms**:
- Kernel restarts repeatedly
- "Dead kernel" message

**Solutions**:
```python
# Check memory usage
docker stats jupyter_pyspark

# Increase memory allocation
# Edit .env file:
JUPYTER_MEMORY=2G

# Restart Jupyter
docker-compose up -d jupyter

# Clear output in notebook
# Kernel → Restart & Clear Output
```

### Performance Issues

#### Slow query performance
**Symptoms**:
- Queries take minutes to complete
- Airflow tasks timeout

**Solutions**:
```sql
-- Check query plan
EXPLAIN (ANALYZE, BUFFERS) 
YOUR_SLOW_QUERY;

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_table_column 
ON schema.table(column);

-- Update statistics
ANALYZE schema.table;

-- Increase work memory
SET work_mem = '256MB';
```

#### Container using too much memory
**Symptoms**:
- System becomes slow
- Containers get killed

**Solutions**:
```bash
# Check resource usage
docker stats

# Limit container resources
# Edit docker-compose.yml:
services:
  postgres:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

# Apply changes
docker-compose up -d
```

### Data Issues

#### DAG not appearing in Airflow
**Symptoms**:
- New DAG file created but not visible
- Import errors

**Solutions**:
```python
# 1. Check for syntax errors
python airflow/dags/your_dag.py

# 2. Check Airflow logs
docker-compose logs airflow-scheduler | grep "ERROR"

# 3. Common issues:
# - Missing imports
# - Syntax errors
# - Incorrect file location
# - No DAG object in file

# 4. Force refresh
docker-compose restart airflow-scheduler
```

#### dbt model failures
**Symptoms**:
- "Compilation Error" in dbt
- "Database Error" messages

**Solutions**:
```bash
# Test dbt connection
docker exec -it airflow_webserver dbt debug

# Run specific model with verbose output
docker exec -it airflow_webserver dbt run --models your_model --debug

# Common issues:
# - Wrong schema references
# - Missing source tables
# - SQL syntax errors
# - Permission issues
```

### Recovery Procedures

#### Complete platform reset
```bash
# WARNING: This deletes all data!

# Stop everything
docker-compose down -v

# Remove all containers and images
docker system prune -a --volumes

# Remove data directories
rm -rf postgres_data pgadmin_data airflow/logs/*

# Recreate from scratch
./scripts/simple-setup.sh
```

#### Recover from backup
```bash
# List available backups
ls -la backups/

# Restore specific backup
./scripts/restore.sh backups/backup_20240115_020000.dump.gz
```

### PostgreSQL Connection Issues from pgAdmin

#### Issue: "Connection refused" or "server at X.X.X.X port 5432 failed"
**Symptoms**: 
- pgAdmin shows connection refused errors
- Can access PostgreSQL from host but not from other containers

**Root Cause**: PostgreSQL not listening on all network interfaces

**Solution**:
```bash
# 1. Check if PostgreSQL is listening on all interfaces
docker exec postgres_dw netstat -tlnp | grep 5432

# Should show: 0.0.0.0:5432 (correct)
# NOT: 127.0.0.1:5432 (wrong - only localhost)

# 2. If showing 127.0.0.1, fix the configuration
echo "listen_addresses = '*'" >> docker/postgres/postgresql.conf

# 3. Restart PostgreSQL
docker-compose restart postgres

# 4. Verify fix
docker exec postgres_dw netstat -tlnp | grep 5432

---

# 12. Best Practices and Tips

## Development Best Practices

### Version Control
```bash
# Initialize git repository
cd ~/projects/data-engineering-platform
git init
git add .
git commit -m "Initial platform setup"

# Create .gitignore entries
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "data/" >> .gitignore
echo "backups/" >> .gitignore
```

### Code Organization
- Keep DAGs simple and focused
- Use common utilities in plugins
- Separate concerns (extract, transform, load)
- Document complex logic

### Testing Strategy
```python
# tests/test_dag_validation.py
import unittest
from airflow.models import DagBag

class TestDagIntegrity(unittest.TestCase):
    
    def setUp(self):
        self.dagbag = DagBag(dag_folder='airflow/dags')
    
    def test_import_dags(self):
        """Test that all DAGs can be imported"""
        self.assertFalse(
            len(self.dagbag.import_errors),
            f"DAG import failures: {self.dagbag.import_errors}"
        )
    
    def test_dag_dependencies(self):
        """Test that all DAGs have proper dependencies"""
        for dag_id, dag in self.dagbag.dags.items():
            self.assertGreaterEqual(
                len(dag.tasks), 1,
                f"DAG {dag_id} has no tasks"
            )
```

## Performance Optimization

### PostgreSQL Tuning
- Use appropriate indexes
- Partition large tables
- Regular VACUUM and ANALYZE
- Monitor query performance
- Use connection pooling

### Airflow Optimization
- Use pools for resource management
- Set appropriate task concurrency
- Implement proper retry logic
- Use sensors instead of polling
- Minimize DAG parsing time

### Spark Optimization
- Partition data appropriately
- Use broadcast joins for small tables
- Cache frequently used DataFrames
- Monitor Spark UI for bottlenecks
- Tune executor memory and cores

## Security Best Practices

### Credential Management
```python
# Use Airflow Variables and Connections
from airflow.models import Variable

# Store secrets in Airflow
api_key = Variable.get("api_key", deserialize_json=False)

# Use connections for databases
from airflow.hooks.postgres_hook import PostgresHook
pg_hook = PostgresHook(postgres_conn_id='postgres_default')
```

### Access Control
- Change default passwords immediately
- Use strong passwords
- Implement role-based access
- Regular security updates
- Monitor access logs

## Monitoring and Alerting

### Health Checks
```bash
# Create health check script
nano scripts/health_check.sh
```

```bash
#!/bin/bash
# Platform health check

echo "Checking platform health..."

# Check services
services=("postgres" "airflow-webserver" "airflow-scheduler" "spark-master" "jupyter")

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
    fi
done

# Check disk space
echo -e "\nDisk usage:"
df -h | grep -E "/$|/var/lib/docker"

# Check memory
echo -e "\nMemory usage:"
free -h

# Check recent errors
echo -e "\nRecent errors:"
docker-compose logs --tail=20 | grep -i error || echo "No recent errors"
```

### Alerting Setup
```python
# airflow/dags/monitoring_dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'platform-admin',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['admin@company.com'],
    'email_on_failure': True,
    'retries': 0
}

dag = DAG(
    'platform_monitoring',
    default_args=default_args,
    schedule_interval='*/30 * * * *',  # Every 30 minutes
    catchup=False
)

health_check = BashOperator(
    task_id='health_check',
    bash_command='/opt/airflow/scripts/health_check.sh',
    dag=dag
)
```

---

# 13. Appendix: Complete Setup Scripts

## Complete Platform Setup Script

```bash
#!/bin/bash
# Complete Data Engineering Platform Setup Script
# This script creates ALL necessary files and configurations

set -e  # Exit on error

echo "🚀 Data Engineering Platform - Complete Setup"
echo "==========================================="
echo ""

# Create main directory structure
echo "📁 Creating directory structure..."
mkdir -p airflow/{dags,plugins,config,logs,tests}
mkdir -p spark/jobs
mkdir -p dbt/{models/{staging,marts},tests,macros,seeds,snapshots}
mkdir -p notebooks/{examples,analysis,ml}
mkdir -p data/{raw,processed,archive}
mkdir -p sql/{schemas,migrations,functions,views}
mkdir -p docker/{postgres,pgadmin}
mkdir -p backups
mkdir -p scripts
mkdir -p tests/{unit,integration}
mkdir -p logs
mkdir -p .vscode
mkdir -p .github/workflows
mkdir -p docs

# Create .gitkeep files to preserve empty directories
find . -type d -empty -exec touch {}/.gitkeep \;

# Create docker-compose.yml
echo "🐳 Creating docker-compose.yml..."
cat > docker-compose.yml << 'EOFDOCKER'
version: '3.8'

x-airflow-common: &airflow-common
  image: apache/airflow:2.8.1-python3.10
  environment: &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:${AIRFLOW_DB_PASSWORD}@postgres-airflow:5432/airflow
    AIRFLOW__CORE__FERNET_KEY: ${AIRFLOW_FERNET_KEY}
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    PYTHONPATH: '/opt/airflow/dags:/opt/dbt'
  volumes:
    - ./airflow/dags:/opt/airflow/dags
    - ./airflow/logs:/opt/airflow/logs
    - ./airflow/plugins:/opt/airflow/plugins
    - ./dbt:/opt/dbt
    - ./data:/data
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on:
    postgres-airflow:
      condition: service_healthy

services:
  postgres:
    image: postgres:15-alpine
    container_name: postgres_dw
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/postgresql.conf:/etc/postgresql/postgresql.conf
      - ./sql:/docker-entrypoint-initdb.d/
      - ./data:/data
    ports:
      - "5432:5432"
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      retries: 5
    networks:
      - data_network
    deploy:
      resources:
        limits:
          memory: ${POSTGRES_MEMORY:-2G}
          cpus: '${POSTGRES_CPUS:-1.0}'

  postgres-airflow:
    image: postgres:15-alpine
    container_name: postgres_airflow
    environment:
      POSTGRES_DB: airflow
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: ${AIRFLOW_DB_PASSWORD}
    volumes:
      - postgres_airflow_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U airflow -d airflow"]
      interval: 5s
      retries: 5
    networks:
      - data_network

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "8081:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
      - ./docker/pgadmin/servers.json:/pgadmin4/servers.json:ro
    depends_on:
      - postgres
    networks:
      - data_network

  airflow-webserver:
    <<: *airflow-common
    container_name: airflow_webserver
    command: webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    networks:
      - data_network
    deploy:
      resources:
        limits:
          memory: ${AIRFLOW_MEMORY:-2G}
          cpus: '${AIRFLOW_CPUS:-1.0}'

  airflow-scheduler:
    <<: *airflow-common
    container_name: airflow_scheduler
    command: scheduler
    healthcheck:
      test: ["CMD-SHELL", 'airflow jobs check --job-type SchedulerJob --hostname "$${HOSTNAME}"']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    networks:
      - data_network

  airflow-init:
    <<: *airflow-common
    container_name: airflow_init
    entrypoint: /bin/bash
    command:
      - -c
      - |
        mkdir -p /sources/logs /sources/dags /sources/plugins
        chown -R "${AIRFLOW_UID:-50000}:0" /sources/{logs,dags,plugins}
        exec /entrypoint airflow version
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_UPGRADE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-admin}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-admin}
    user: "0:0"
    networks:
      - data_network

  spark-master:
    image: bitnami/spark:3.5.1
    container_name: spark_master
    environment:
      - SPARK_MODE=master
      - SPARK_MASTER_HOST=spark-master
      - SPARK_MASTER_PORT=7077
    ports:
      - "8082:8080"
      - "7077:7077"
    volumes:
      - ./spark/jobs:/opt/spark/jobs:ro
      - ./data:/opt/spark/data
    networks:
      - data_network
    deploy:
      resources:
        limits:
          memory: ${SPARK_MEMORY:-2G}
          cpus: '${SPARK_CPUS:-1.0}'

  spark-worker:
    image: bitnami/spark:3.5.1
    container_name: spark_worker
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=${SPARK_WORKER_MEMORY:-2g}
      - SPARK_WORKER_CORES=${SPARK_WORKER_CORES:-2}
    ports:
      - "8083:8081"
    volumes:
      - ./spark/jobs:/opt/spark/jobs:ro
      - ./data:/opt/spark/data
    depends_on:
      - spark-master
    networks:
      - data_network

  jupyter:
    image: jupyter/pyspark-notebook:latest
    container_name: jupyter_pyspark
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - SPARK_MASTER=spark://spark-master:7077
      - JUPYTER_TOKEN=${JUPYTER_TOKEN:-development}
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work
      - ./data:/home/jovyan/data
    networks:
      - data_network
    depends_on:
      - spark-master
    deploy:
      resources:
        limits:
          memory: ${JUPYTER_MEMORY:-1G}
          cpus: '${JUPYTER_CPUS:-0.5}'

networks:
  data_network:
    driver: bridge

volumes:
  postgres_data:
  postgres_airflow_data:
  pgadmin_data:
EOFDOCKER

# Create .env.template
echo "📝 Creating .env.template..."
cat > .env.template << 'EOF'
# Resource Allocations
POSTGRES_MEMORY=2G
POSTGRES_CPUS=1.0
AIRFLOW_MEMORY=2G
AIRFLOW_CPUS=1.0
SPARK_MEMORY=2G
SPARK_CPUS=1.0
SPARK_WORKER_MEMORY=2g
SPARK_WORKER_CORES=2
JUPYTER_MEMORY=1G
JUPYTER_CPUS=0.5

# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=SecurePass123!
POSTGRES_DB=datawarehouse

# Airflow Configuration
AIRFLOW_UID=1000
AIRFLOW_DB_PASSWORD=SecurePass123!
AIRFLOW_FERNET_KEY=zUKvN7ksUjOgUNwHBBRjQBONZLWEOYpEMSvchBRD0Xo=
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=SecurePass123!

# Jupyter Configuration
JUPYTER_TOKEN=SecurePass123!
EOF

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Data directories
data/raw/*
data/processed/*
data/archive/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/archive/.gitkeep

# Backup files
backups/*.dump
backups/*.sql
backups/*.tar.gz
!backups/.gitkeep

# Environment files
.env
.env.local
.env.*.local
*.env

# Airflow
airflow/logs/*
airflow/airflow.db
airflow/airflow.cfg
airflow/unittests.cfg
airflow/webserver_config.py
airflow/__pycache__/
!airflow/logs/.gitkeep

# PostgreSQL
postgres_data/
postgres_airflow_data/
pgadmin_data/

# Jupyter
notebooks/.ipynb_checkpoints/
notebooks/*.html
notebooks/*.pdf

# dbt
dbt/target/
dbt/dbt_modules/
dbt/logs/
dbt/.user.yml

# Spark
spark/jobs/__pycache__/
spark/metastore_db/
spark/spark-warehouse/
*.pyc

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
.venv

# IDE
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
docker-compose.override.yml
.docker/

# Temporary files
*.tmp
*.temp
*.log
*.pid
*.lock

# Keep directory structure
!.gitkeep
EOF

# Create PostgreSQL configuration
echo "🐘 Creating PostgreSQL configuration..."
cat > docker/postgres/postgresql.conf << 'EOF'
# PostgreSQL Configuration for Analytics Workloads

# Network Configuration (CRITICAL: Allows connections from other containers)
listen_addresses = '*'

# Memory Configuration
shared_buffers = 2GB
work_mem = 256MB
maintenance_work_mem = 1GB
effective_cache_size = 6GB

# Connection Settings
max_connections = 100
max_parallel_workers = 8
max_parallel_workers_per_gather = 4

# Query Optimization
random_page_cost = 1.1
seq_page_cost = 1.0
cpu_tuple_cost = 0.01
effective_io_concurrency = 200

# WAL Configuration
wal_buffers = 64MB
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9

# Logging
log_statement = 'all'
log_min_duration_statement = 1000
log_temp_files = 0

# Extensions
shared_preload_libraries = 'pg_stat_statements'
EOF

# Create pgAdmin servers configuration
echo "🔧 Creating pgAdmin configuration..."
cat > docker/pgadmin/servers.json << 'EOF'
{
  "Servers": {
    "1": {
      "Name": "PostgreSQL Analytics",
      "Group": "Servers",
      "Host": "postgres",
      "Port": 5432,
      "MaintenanceDB": "postgres",
      "Username": "postgres",
      "SSLMode": "prefer"
    }
  }
}
EOF

# Create ALL helper scripts
echo "🛠️ Creating helper scripts..."

# simple-setup.sh
cat > scripts/simple-setup.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Simple Setup - Data Engineering Platform"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if .env exists
if [ -f .env ]; then
    echo "✅ Found existing .env file"
else
    echo "📝 Creating .env from template..."
    cp .env.template .env
    echo "✅ Generated configuration"
fi

echo ""
echo "🐳 Starting Docker services..."
echo "This may take 10-15 minutes on first run to download images..."
echo ""

# Pull images first
docker-compose pull

# Start services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
echo "   This may take 2-5 minutes..."
echo ""

# Wait a bit for services to start
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "🔍 Verifying PostgreSQL network configuration..."

# Wait a bit more for PostgreSQL to be fully ready
sleep 10

# Check if PostgreSQL is listening on all interfaces
POSTGRES_LISTENING=$(docker exec postgres_dw netstat -tlnp | grep "0.0.0.0:5432" || echo "FAILED")

if [[ $POSTGRES_LISTENING == *"0.0.0.0:5432"* ]]; then
    echo "✅ PostgreSQL is correctly listening on all network interfaces"
else
    echo "❌ WARNING: PostgreSQL may not be accessible from other containers"
    echo "   If pgAdmin connection fails, check PostgreSQL configuration"
fi

echo ""
echo "🔍 Testing container connectivity..."
if docker exec pgadmin4 nc -zv postgres 5432 >/dev/null 2>&1; then
    echo "✅ pgAdmin can reach PostgreSQL"
else
    echo "❌ WARNING: pgAdmin cannot reach PostgreSQL"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Access your services at:"
echo "  • Airflow: http://localhost:8080 (admin/SecurePass123!)"
echo "  • pgAdmin: http://localhost:8081 (admin@admin.com/admin)"
echo "  • Jupyter: http://localhost:8888 (token: SecurePass123!)"
echo "  • Spark UI: http://localhost:8082"
echo ""
echo "💡 Tips:"
echo "  • Check status: docker-compose ps"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo ""
echo "🎉 Happy Data Engineering!"
EOF
chmod +x scripts/simple-setup.sh

# start.sh
cat > scripts/start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Data Engineering Platform..."
docker-compose up -d
echo ""
echo "✅ Services starting..."
echo ""
echo "📊 Access URLs:"
echo "  • Airflow: http://localhost:8080"
echo "  • pgAdmin: http://localhost:8081"
echo "  • Jupyter: http://localhost:8888"
echo "  • Spark UI: http://localhost:8082"
echo ""
echo "Run 'docker-compose ps' to check status"
EOF
chmod +x scripts/start.sh

# stop.sh
cat > scripts/stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Data Engineering Platform..."
docker-compose down
echo "✅ All services stopped"
EOF
chmod +x scripts/stop.sh

# status.sh
cat > scripts/status.sh << 'EOF'
#!/bin/bash
echo "📊 Data Engineering Platform Status:"
echo "===================================="
docker-compose ps
echo ""
echo "📌 Service URLs:"
echo "  • Airflow: http://localhost:8080"
echo "  • pgAdmin: http://localhost:8081"
echo "  • Jupyter: http://localhost:8888"
echo "  • Spark UI: http://localhost:8082"
EOF
chmod +x scripts/status.sh

# logs.sh
cat > scripts/logs.sh << 'EOF'
#!/bin/bash
SERVICE=${1:-}
if [ -z "$SERVICE" ]; then
    echo "📋 Showing logs for all services (Ctrl+C to stop)..."
    docker-compose logs -f --tail=100
else
    echo "📋 Showing logs for $SERVICE (Ctrl+C to stop)..."
    docker-compose logs -f --tail=100 $SERVICE
fi
EOF
chmod +x scripts/logs.sh

# backup.sh
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="datawarehouse"

mkdir -p $BACKUP_DIR

echo "🔄 Starting backup of $DB_NAME..."

docker exec postgres_dw pg_dump \
    -U postgres \
    -d $DB_NAME \
    -F custom \
    -f /tmp/backup_$TIMESTAMP.dump

docker cp postgres_dw:/tmp/backup_$TIMESTAMP.dump $BACKUP_DIR/

gzip $BACKUP_DIR/backup_$TIMESTAMP.dump

echo "✅ Backup completed: $BACKUP_DIR/backup_$TIMESTAMP.dump.gz"

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
EOF
chmod +x scripts/backup.sh

# restore.sh
cat > scripts/restore.sh << 'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE=$1
DB_NAME="datawarehouse"

echo "🔄 Restoring database from $BACKUP_FILE..."

docker cp $BACKUP_FILE postgres_dw:/tmp/restore.dump.gz
docker exec postgres_dw gunzip /tmp/restore.dump.gz
docker exec postgres_dw pg_restore \
    -U postgres \
    -d $DB_NAME \
    -v \
    /tmp/restore.dump

echo "✅ Restore completed!"
EOF
chmod +x scripts/restore.sh

# Create VS Code settings
echo "💻 Creating VS Code configuration..."
cat > .vscode/settings.json << 'EOF'
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff",
  
  "files.associations": {
    "*.sql": "sql",
    "*.yml": "yaml",
    "*.yaml": "yaml",
    "Dockerfile*": "dockerfile",
    "*.env*": "dotenv"
  },
  
  "sqltools.connections": [
    {
      "name": "PostgreSQL Analytics",
      "driver": "PostgreSQL",
      "server": "localhost",
      "port": 5432,
      "database": "datawarehouse",
      "username": "postgres"
    }
  ],
  
  "docker.host": "unix:///var/run/docker.sock"
}
EOF

# Create VS Code extensions list
cat > .vscode/extensions.json << 'EOF'
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-toolsai.jupyter",
    "mtxr.sqltools",
    "ms-ossdata.vscode-postgresql",
    "charliermarsh.ruff",
    "innoverio.vscode-dbt-power-user",
    "redhat.vscode-yaml",
    "eamodio.gitlens",
    "ms-azuretools.vscode-docker",
    "ms-vscode-remote.remote-containers",
    "ms-vscode-remote.remote-wsl"
  ]
}
EOF

# Create dbt project configuration
echo "📊 Creating dbt configuration..."
cat > dbt/dbt_project.yml << 'EOF'
name: 'data_engineering_platform'
version: '1.0.0'
config-version: 2

profile: 'data_engineering_platform'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  data_engineering_platform:
    staging:
      +materialized: view
    marts:
      +materialized: table
EOF

cat > dbt/profiles.yml << 'EOF'
data_engineering_platform:
  outputs:
    dev:
      type: postgres
      threads: 4
      host: localhost
      port: 5432
      user: postgres
      pass: SecurePass123!
      dbname: datawarehouse
      schema: dbt
  target: dev
EOF

# Create example Airflow DAG
echo "✈️ Creating example Airflow DAG..."
cat > airflow/dags/example_pipeline.py << 'EOF'
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'data-team',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def print_hello():
    return 'Hello from Airflow!'

with DAG(
    'example_pipeline',
    default_args=default_args,
    description='A simple example DAG',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example']
) as dag:
    
    hello_task = PythonOperator(
        task_id='print_hello',
        python_callable=print_hello
    )
    
    create_table = PostgresOperator(
        task_id='create_example_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS example_data (
            id SERIAL PRIMARY KEY,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    
    hello_task >> create_table
EOF

# Create initial SQL setup
echo "🗄️ Creating SQL initialization script..."
cat > sql/init_database.sql << 'EOF'
-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create example dimension table
CREATE TABLE IF NOT EXISTS marts.dim_date (
    date_key INTEGER PRIMARY KEY,
    date_actual DATE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    week_of_year INTEGER,
    day_name VARCHAR(20),
    month_name VARCHAR(20)
);

-- Populate date dimension
INSERT INTO marts.dim_date (
    date_key, date_actual, year, quarter, month,
    day_of_month, day_of_week, week_of_year,
    day_name, month_name
)
SELECT 
    TO_CHAR(d, 'YYYYMMDD')::INTEGER as date_key,
    d as date_actual,
    EXTRACT(YEAR FROM d) as year,
    EXTRACT(QUARTER FROM d) as quarter,
    EXTRACT(MONTH FROM d) as month,
    EXTRACT(DAY FROM d) as day_of_month,
    EXTRACT(DOW FROM d) as day_of_week,
    EXTRACT(WEEK FROM d) as week_of_year,
    TO_CHAR(d, 'Day') as day_name,
    TO_CHAR(d, 'Month') as month_name
FROM generate_series('2020-01-01'::DATE, '2025-12-31'::DATE, '1 day'::INTERVAL) d;
EOF

# Create a sample notebook
echo "📓 Creating example Jupyter notebook..."
mkdir -p notebooks/examples
cat > notebooks/examples/getting_started.ipynb << 'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Getting Started with Data Engineering Platform\n",
    "\n",
    "This notebook demonstrates basic operations with the platform."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Import libraries\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "from sqlalchemy import create_engine\n",
    "\n",
    "# Connect to PostgreSQL\n",
    "engine = create_engine('postgresql://postgres:SecurePass123!@postgres:5432/datawarehouse')\n",
    "\n",
    "# Test connection\n",
    "df = pd.read_sql('SELECT version()', engine)\n",
    "print(df)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF

# Create README
echo "📚 Creating README.md..."
cat > README.md << 'EOF'
# Data Engineering Platform

A production-ready, dockerized data engineering platform with PostgreSQL, Airflow, Spark, Jupyter, and more.

## Quick Start

```bash
# 1. Make sure Docker is running

# 2. Run the simple setup
./scripts/simple-setup.sh

# 3. Access services:
# - Airflow: http://localhost:8080
# - pgAdmin: http://localhost:8081
# - Jupyter: http://localhost:8888
# - Spark: http://localhost:8082
```

## Daily Usage

```bash
# Start services
./scripts/start.sh

# Check status
./scripts/status.sh

# View logs
./scripts/logs.sh

# Stop services
./scripts/stop.sh
```

## Documentation

See the `docs/` directory for detailed guides.
EOF

# Create LICENSE
echo "📄 Creating LICENSE..."
cat > LICENSE << 'EOF'
Apache License
Version 2.0, January 2004

Copyright 2024 Data Engineering Platform Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
EOF

# Create documentation files
echo "📚 Creating documentation templates..."
touch docs/SETUP.md
touch docs/USAGE.md
touch docs/ARCHITECTURE.md
touch docs/TROUBLESHOOTING.md

echo ""
echo "✅ Platform setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Run: ./scripts/simple-setup.sh"
echo "   2. Wait for services to start (10-15 minutes first time)"
echo "   3. Access services at:"
echo "      - Airflow: http://localhost:8080"
echo "      - pgAdmin: http://localhost:8081"
echo "      - Jupyter: http://localhost:8888"
echo "      - Spark: http://localhost:8082"
echo ""
echo "📚 Documentation available in docs/ directory"
echo ""
echo "Happy Data Engineering! 🎉"
```

---

# End of Document

This comprehensive guide provides everything needed to set up, configure, and use a professional data engineering platform on your personal computer. The platform combines industry-standard tools in a production-ready architecture while remaining accessible for learning and development.

For questions, updates, or contributions, please refer to the project repository and documentation.

**Version**: 1.0  
**Last Updated**: January 2024  
**Total Pages**: 150+

---
