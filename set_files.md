# Modular Data Engineering Platform Setup

## Directory Structure
```
setup-platform/
├── setup.sh                    # Main orchestrator
├── config/
│   └── platform.yaml          # Configuration
├── lib/
│   └── common.sh              # Shared functions
├── modules/
│   ├── 01_core.sh
│   ├── 02_docker.sh
│   ├── 03_database.sh
│   ├── 04_airflow.sh
│   ├── 05_spark.sh
│   ├── 06_jupyter.sh
│   ├── 07_dbt.sh
│   ├── 08_monitoring.sh
│   ├── 09_utilities.sh
│   └── 10_development.sh
└── templates/
    ├── docker-compose.yml.tmpl
    ├── postgresql.conf.tmpl
    ├── env.tmpl
    └── gitignore.tmpl
```

## File Contents

### 📁 **setup.sh** (Main Orchestrator)
```bash
#!/bin/bash
# Data Engineering Platform - Modular Setup Orchestrator
# Version: 2.0.0

set -e  # Exit on error

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(pwd)"

# Source common functions
source "$SCRIPT_DIR/lib/common.sh"

# Parse command line arguments
SKIP_MODULES=""
ONLY_MODULES=""
INTERACTIVE=false
VERBOSE=false

function show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -v, --verbose           Enable verbose output
    -i, --interactive       Interactive mode - choose components
    --skip <modules>        Skip specific modules (comma-separated)
    --only <modules>        Only run specific modules (comma-separated)
    --list-modules          List all available modules
    --config <file>         Use custom configuration file
    --dry-run              Show what would be done without executing

Examples:
    $0                      # Run all modules
    $0 --skip jupyter,dbt   # Skip Jupyter and dbt setup
    $0 --only core,docker   # Only setup core and docker
    $0 --interactive        # Choose components interactively

EOF
    exit 0
}

function list_modules() {
    echo "Available modules:"
    echo ""
    for module in "$SCRIPT_DIR"/modules/*.sh; do
        basename "$module" .sh | sed 's/^[0-9]*_/  - /'
    done
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -i|--interactive)
            INTERACTIVE=true
            shift
            ;;
        --skip)
            SKIP_MODULES="$2"
            shift 2
            ;;
        --only)
            ONLY_MODULES="$2"
            shift 2
            ;;
        --list-modules)
            list_modules
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            ;;
    esac
done

# Welcome message
print_banner() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║     🚀 Data Engineering Platform - Modular Setup v2.0      ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

# Interactive mode
interactive_setup() {
    echo "🎯 Interactive Setup Mode"
    echo "========================="
    echo ""
    
    local modules=()
    for module in "$SCRIPT_DIR"/modules/*.sh; do
        local name=$(basename "$module" .sh | sed 's/^[0-9]*_//')
        echo -n "Install $name? [Y/n]: "
        read -r response
        if [[ ! "$response" =~ ^[Nn]$ ]]; then
            modules+=("$module")
        fi
    done
    
    echo ""
    log_info "Selected modules: ${#modules[@]}"
    
    for module in "${modules[@]}"; do
        run_module "$module"
    done
}

# Run a specific module
run_module() {
    local module_path="$1"
    local module_name=$(basename "$module_path" .sh)
    
    # Check module dependencies
    case "$module_name" in
        "08_monitoring")
            if [[ ! -f ".env" ]]; then
                log_error "Module 08_monitoring requires .env file (run 02_docker first)"
                return 1
            fi
            ;;
        "04_airflow"|"05_spark"|"06_jupyter")
            if [[ ! -f "docker-compose.yml" ]]; then
                log_error "Module $module_name requires docker-compose.yml (run 02_docker first)"
                return 1
            fi
            ;;
    esac
    
    # Check if module should be skipped
    if [[ -n "$SKIP_MODULES" ]] && [[ "$SKIP_MODULES" == *"${module_name#*_}"* ]]; then
        log_warning "Skipping module: $module_name"
        return 0
    fi
    
    # Check if only specific modules should run
    if [[ -n "$ONLY_MODULES" ]] && [[ "$ONLY_MODULES" != *"${module_name#*_}"* ]]; then
        return 0
    fi
    
    log_section "Running module: $module_name"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would execute: $module_path"
        return 0
    fi
    
    # Execute module
    if [[ -f "$module_path" ]]; then
        (
            cd "$PROJECT_ROOT"
            source "$module_path"
        )
        check_status "Module $module_name completed"
    else
        log_error "Module not found: $module_path"
        return 1
    fi
}

# Main execution
main() {
    print_banner
    
    # Check prerequisites
    log_section "Checking Prerequisites"
    check_prerequisites
    
    # Check ports
    log_section "Checking Port Availability"
    check_ports || exit 1
    
    # Load configuration
    log_section "Loading Configuration"
    load_configuration "${CONFIG_FILE:-$SCRIPT_DIR/config/platform.yaml}"
    
    if [[ "$INTERACTIVE" == "true" ]]; then
        interactive_setup
    else
        # Run all modules in order
        for module in "$SCRIPT_DIR"/modules/*.sh; do
            run_module "$module"
        done
    fi
    
    # Final summary
    print_summary
}

# Print final summary
print_summary() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║            ✅ Platform Setup Complete!                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 Access your services at:"
    echo "  • Airflow:   http://localhost:8080"
    echo "  • pgAdmin:   http://localhost:8081"
    echo "  • Jupyter:   http://localhost:8888"
    echo "  • Spark UI:  http://localhost:8082"
    echo ""
    echo "📚 Quick Start Commands:"
    echo "  • Start services:  ./scripts/start.sh"
    echo "  • Stop services:   ./scripts/stop.sh"
    echo "  • Check status:    ./scripts/status.sh"
    echo "  • View logs:       ./scripts/logs.sh"
    echo ""
    echo "🎉 Happy Data Engineering!"
}

# Run main function
main "$@"
```

### 📁 **lib/common.sh** (Shared Functions)
```bash
#!/bin/bash
# Common functions and variables for all modules

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Global variables
PLATFORM_NAME="data-engineering-platform"
PLATFORM_VERSION="2.0.0"
CONFIG_FILE=""
DRY_RUN=false

# Logging functions
log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    return 1
}

log_section() {
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}▶ $1${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════${NC}"
}

# Check command status
check_status() {
    if [ $? -eq 0 ]; then
        log_success "$1"
    else
        log_error "$1 failed"
        exit 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    local missing_deps=()
    
    # Required commands
    local required_commands=("docker" "python3" "git")
    
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            missing_deps+=("$cmd")
        fi
    done
    
    # Check docker-compose or docker compose
    if ! command_exists "docker-compose" && ! docker compose version >/dev/null 2>&1; then
        missing_deps+=("docker-compose")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies and try again."
        exit 1
    fi
    
    # Check Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check Docker Compose version
    if command_exists "docker-compose"; then
        compose_version=$(docker-compose version --short 2>/dev/null || echo "0.0.0")
    else
        compose_version=$(docker compose version --short 2>/dev/null || echo "0.0.0")
    fi
    
    # Check minimum Docker resources
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - check Docker Desktop resources
        docker_mem=$(docker system info --format '{{.MemTotal}}' 2>/dev/null || echo 0)
        docker_mem_gb=$((docker_mem / 1073741824))
        if [[ $docker_mem_gb -lt 8 ]]; then
            log_warning "Docker Desktop memory should be at least 8GB (currently ${docker_mem_gb}GB)"
            log_info "Adjust in Docker Desktop > Settings > Resources"
        fi
    fi
    
    log_success "All prerequisites met"
}

# Docker Compose wrapper to handle v1/v2
docker_compose() {
    if command_exists "docker-compose"; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

export -f docker_compose

# Check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

# Check all required ports
check_ports() {
    local ports=("5432" "8080" "8081" "8082" "8083" "8888" "7077")
    local used_ports=()
    
    for port in "${ports[@]}"; do
        if ! check_port "$port"; then
            used_ports+=("$port")
        fi
    done
    
    if [ ${#used_ports[@]} -gt 0 ]; then
        log_error "The following ports are already in use: ${used_ports[*]}"
        echo "Please free these ports or modify the port configuration."
        return 1
    fi
    
    log_success "All required ports are available"
    return 0
}

# Load configuration from YAML
load_configuration() {
    local config_file="$1"
    
    if [[ ! -f "$config_file" ]]; then
        log_warning "Configuration file not found: $config_file"
        log_info "Using default configuration"
        return 0
    fi
    
    # Check if PyYAML is available
    if ! python3 -c "import yaml" 2>/dev/null; then
        log_warning "PyYAML not installed. Installing..."
        pip3 install pyyaml 2>/dev/null || {
            log_warning "Could not install PyYAML. Using defaults."
            return 0
        }
    fi
    
    # Export configuration as environment variables
    export CONFIG_FILE="$config_file"
    log_success "Configuration loaded from: $config_file"
}

# Read configuration value
get_config() {
    local key="$1"
    local default="$2"
    
    if [[ -f "$CONFIG_FILE" ]]; then
        # Use Python to parse YAML if available
        if command_exists python3; then
            value=$(python3 -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    keys = '$key'.split('.')
    value = config
    for k in keys:
        value = value.get(k, '$default')
    print(value)
except:
    print('$default')
" 2>/dev/null)
            echo "${value:-$default}"
        else
            echo "$default"
        fi
    else
        echo "$default"
    fi
}

# Create directory with logging
create_directory() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    fi
}

# Create file from template
create_from_template() {
    local template="$1"
    local output="$2"
    local template_file="$SCRIPT_DIR/templates/$template"
    
    if [[ -f "$template_file" ]]; then
        envsubst < "$template_file" > "$output"
        log_success "Created $output from template"
    else
        log_warning "Template not found: $template_file"
    fi
}

# Generate secure password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Check if password file exists, otherwise generate new passwords
load_or_generate_passwords() {
    local password_file=".platform_passwords"
    
    if [[ -f "$password_file" ]]; then
        source "$password_file"
    else
        export POSTGRES_PASSWORD=$(generate_password)
        export AIRFLOW_DB_PASSWORD=$(generate_password)
        export AIRFLOW_ADMIN_PASSWORD=$(generate_password)
        export JUPYTER_TOKEN=$(generate_password)
        export PGADMIN_PASSWORD=$(generate_password)
        
        cat > "$password_file" << EOF
export POSTGRES_PASSWORD='$POSTGRES_PASSWORD'
export AIRFLOW_DB_PASSWORD='$AIRFLOW_DB_PASSWORD'
export AIRFLOW_ADMIN_PASSWORD='$AIRFLOW_ADMIN_PASSWORD'
export JUPYTER_TOKEN='$JUPYTER_TOKEN'
export PGADMIN_PASSWORD='$PGADMIN_PASSWORD'
EOF
        chmod 600 "$password_file"
    fi
}

# Generate Fernet key for Airflow
generate_fernet_key() {
    python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || generate_password
}

# Download file with progress
download_file() {
    local url="$1"
    local output="$2"
    
    if [[ -f "$output" ]]; then
        log_info "File already exists: $output"
        return 0
    fi
    
    log_info "Downloading: $url"
    if command_exists wget; then
        wget -q --show-progress "$url" -O "$output"
    elif command_exists curl; then
        curl -L --progress-bar "$url" -o "$output"
    else
        log_error "Neither wget nor curl is available"
        return 1
    fi
    check_status "Download completed: $output"
}

# Wait for service to be ready
wait_for_service() {
    local service_name="$1"
    local url="$2"
    local max_attempts="${3:-30}"
    local attempt=1
    
    echo -n "Waiting for $service_name"
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|302"; then
            echo ""
            log_success "$service_name is ready"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    echo ""
    log_warning "$service_name is not responding (but may still be starting)"
    return 1
}

# Export functions for use in modules
export -f log_info log_success log_warning log_error log_section
export -f check_status command_exists create_directory
export -f generate_password generate_fernet_key
export -f download_file wait_for_service get_config
```

### 📁 **config/platform.yaml** (Configuration)
```yaml
# Data Engineering Platform Configuration
# Version: 2.0.0

platform:
  name: "data-engineering-platform"
  version: "2.0.0"
  environment: "development"

# Service versions
versions:
  postgresql: "16.1-alpine"
  airflow: "2.9.3-python3.11"
  spark: "3.5.1"
  jupyter: "spark-3.5.1"
  pgadmin: "8.11"
  python: "3.11"
  dbt: "1.8.3"
  postgresql_jdbc: "42.7.3"

# Resource allocations
resources:
  postgres:
    memory: "2G"
    cpus: 1.0
  postgres_airflow:
    memory: "1G"
    cpus: 0.5
  airflow:
    webserver:
      memory: "2G"
      cpus: 1.0
    scheduler:
      memory: "2G"
      cpus: 1.0
  spark:
    master:
      memory: "2G"
      cpus: 1.0
    worker:
      memory: "4G"
      cpus: 2.0
  jupyter:
    memory: "2G"
    cpus: 1.0
  pgadmin:
    memory: "512M"
    cpus: 0.5

# Network configuration
network:
  name: "data_network"
  driver: "bridge"

# Port mappings
ports:
  postgres: 5432
  airflow_webserver: 8080
  pgadmin: 8081
  jupyter: 8888
  spark_master_web: 8082
  spark_master: 7077
  spark_worker_web: 8083

# Security
security:
  postgres_password: "SecurePass123!"
  airflow_db_password: "SecurePass123!"
  airflow_admin_user: "admin"
  airflow_admin_password: "SecurePass123!"
  jupyter_token: "SecurePass123!"
  pgadmin_email: "admin@admin.com"
  pgadmin_password: "admin"

# Database configuration
database:
  name: "datawarehouse"
  user: "postgres"
  schemas:
    - "raw"
    - "staging"
    - "marts"
    - "ml"

# Feature flags
features:
  enable_example_dags: true
  enable_spark_history: false
  enable_jupyter_extensions: true
  hot_reload_dags: true
  debug_mode: false
```

### 📁 **modules/01_core.sh** (Core Setup)
```bash
#!/bin/bash
# Module: Core Setup - Directory structure and basic files
# PRODUCTION FIXED VERSION

source "$SCRIPT_DIR/lib/common.sh"

log_section "Core Setup Module"

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."
    
    # ============================================
    # CRITICAL FIX #1: Docker Volume Pre-Creation
    # MUST BE FIRST - These directories are required for bind mounts
    # ============================================
    log_info "Creating Docker volume directories (CRITICAL for bind mounts)..."
    
    # Create volume directories with proper permissions
    mkdir -p docker/volumes/postgres_data
    mkdir -p docker/volumes/postgres_airflow_data
    mkdir -p docker/volumes/pgadmin_data
    mkdir -p docker/volumes/spark_logs
    
    # Set base permissions
    chmod 755 docker/volumes
    
    # FIX: pgAdmin specific permissions (runs as user 5050)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux: Try to set proper ownership, fallback to 777
        sudo chown -R 5050:5050 docker/volumes/pgadmin_data 2>/dev/null || {
            log_warning "Could not set pgAdmin ownership, using permissive mode"
            chmod 777 docker/volumes/pgadmin_data
        }
    else
        # macOS/Windows: Use permissive permissions
        chmod 777 docker/volumes/pgadmin_data
    fi
    
    # PostgreSQL volumes need proper permissions
    chmod 700 docker/volumes/postgres_data docker/volumes/postgres_airflow_data
    
    log_success "Docker volumes created with proper permissions"
    
    # ============================================
    # Standard Directory Structure
    # ============================================
    local directories=(
        "airflow/dags"
        "airflow/plugins"
        "airflow/config"
        "airflow/logs"
        "airflow/tests"
        "spark/jobs"
        "spark/jars"
        "spark/conf"
        "spark/logs"
        "dbt/models/staging"
        "dbt/models/marts"
        "dbt/tests"
        "dbt/macros"
        "dbt/seeds"
        "dbt/snapshots"
        "notebooks/examples"
        "notebooks/analysis"
        "notebooks/ml"
        "data/raw"
        "data/processed"
        "data/archive"
        "sql/schemas"
        "sql/migrations"
        "sql/functions"
        "sql/views"
        "docker/postgres"
        "docker/pgadmin"
        "docker/airflow"
        "backups/daily"
        "backups/weekly"
        "backups/monthly"
        "scripts"
        "tests/unit"
        "tests/integration"
        "logs"
        ".vscode"
        ".github/workflows"
        "docs"
    )
    
    for dir in "${directories[@]}"; do
        create_directory "$dir"
    done
    
    # Create .gitkeep files for empty directories
    find . -type d -empty -exec touch {}/.gitkeep \; 2>/dev/null
    
    log_success "Directory structure created"
}

# Create production-ready .gitignore
create_gitignore() {
    log_info "Creating .gitignore..."
    
    cat > .gitignore << 'EOF'
# Data directories
data/raw/*
data/processed/*
data/archive/*
!data/**/.gitkeep

# Backup files
backups/**/*.dump
backups/**/*.sql
backups/**/*.tar.gz
backups/**/*.gz
!backups/**/.gitkeep

# Environment files
.env
.env.*
.platform_passwords
*.env
!.env.example

# Docker volumes - NEVER commit these
docker/volumes/postgres_data/*
docker/volumes/postgres_airflow_data/*
docker/volumes/pgadmin_data/*
docker/volumes/spark_logs/*
!docker/volumes/**/.gitkeep

# Airflow
airflow/logs/*
airflow/airflow.db
airflow/*.cfg
airflow/__pycache__/
airflow/webserver_config.py
!airflow/logs/.gitkeep

# Jupyter
notebooks/.ipynb_checkpoints/
notebooks/*.html
notebooks/*.pdf
notebooks/*-checkpoint.ipynb

# dbt
dbt/target/
dbt/dbt_modules/
dbt/logs/
dbt/.user.yml
dbt/profiles.yml

# Spark
spark/logs/*
spark/metastore_db/
spark/spark-warehouse/
spark/derby.log
*.pyc
!spark/logs/.gitkeep

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
!.vscode/extensions.json
!.vscode/launch.json
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
*.log
*.pid
*.lock
*.out

# Docker
docker-compose.override.yml
.docker/

# Security - NEVER commit secrets
*.pem
*.key
*.crt
*.p12
*_rsa
*_dsa
*_ecdsa
*_ed25519

# Keep directory structure
!.gitkeep
EOF
    
    log_success ".gitignore created"
}

# Create .env.example for documentation
create_env_example() {
    log_info "Creating .env.example..."
    
    cat > .env.example << 'EOF'
# Example environment file - Copy to .env and update values
# NEVER commit .env file with real passwords!

# Platform
PLATFORM_NAME=data-engineering-platform
PLATFORM_VERSION=2.0.0
PLATFORM_ENV=development

# PostgreSQL - CHANGE THESE IN PRODUCTION!
POSTGRES_USER=postgres
POSTGRES_PASSWORD=ChangeThisPassword123!
POSTGRES_DB=datawarehouse

# Airflow - CHANGE THESE IN PRODUCTION!
AIRFLOW_DB_PASSWORD=ChangeThisPassword123!
AIRFLOW_ADMIN_PASSWORD=ChangeThisPassword123!

# Jupyter - CHANGE THIS IN PRODUCTION!
JUPYTER_TOKEN=ChangeThisToken123!

# pgAdmin - CHANGE THESE IN PRODUCTION!
PGADMIN_DEFAULT_EMAIL=admin@yourdomain.com
PGADMIN_DEFAULT_PASSWORD=ChangeThisPassword123!

# Resource Limits (adjust based on your system)
POSTGRES_MEMORY=2G
AIRFLOW_WEBSERVER_MEMORY=2G
SPARK_WORKER_MEMORY=4G
EOF
    
    log_success ".env.example created"
}

# Initialize git repository with production practices
init_git() {
    if [[ ! -d .git ]]; then
        log_info "Initializing git repository..."
        git init
        
        # Configure git
        git config core.autocrlf input
        git config core.eol lf
        
        # Initial commit
        git add .gitignore .env.example
        git commit -m "Initial commit: Data Engineering Platform v2.0 - Production Ready" 2>/dev/null || true
        
        log_success "Git repository initialized"
    else
        log_info "Git repository already exists"
    fi
}

# Validate core setup
validate_core_setup() {
    log_info "Validating core setup..."
    
    local errors=0
    
    # Check critical directories
    local critical_dirs=(
        "docker/volumes/postgres_data"
        "docker/volumes/postgres_airflow_data"
        "docker/volumes/pgadmin_data"
        "docker/volumes/spark_logs"
        "airflow/dags"
        "spark/jars"
    )
    
    for dir in "${critical_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_error "Critical directory missing: $dir"
            ((errors++))
        fi
    done
    
    # Check permissions
    if [[ ! -w "docker/volumes" ]]; then
        log_error "Docker volumes directory not writable"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        log_success "Core setup validation passed"
        return 0
    else
        log_error "Core setup validation failed with $errors errors"
        return 1
    fi
}

# Main execution
main() {
    create_directories
    create_gitignore
    create_env_example
    init_git
    validate_core_setup
}

main
```

### 📁 **modules/02_docker.sh** (Docker Setup)
```bash
#!/bin/bash
# Module: Docker Setup - Docker Compose and environment configuration
# PRODUCTION FIXED VERSION

source "$SCRIPT_DIR/lib/common.sh"

log_section "Docker Setup Module"

# ============================================
# CRITICAL FIX: Verify Docker volumes exist
# ============================================
verify_docker_volumes() {
    log_info "Verifying Docker volume directories..."
    
    local volume_dirs=(
        "docker/volumes/postgres_data"
        "docker/volumes/postgres_airflow_data"
        "docker/volumes/pgadmin_data"
        "docker/volumes/spark_logs"
    )
    
    local missing=0
    for dir in "${volume_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_warning "Creating missing volume directory: $dir"
            mkdir -p "$dir"
            ((missing++))
        fi
    done
    
    # Fix pgAdmin permissions
    if [[ -d "docker/volumes/pgadmin_data" ]]; then
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo chown -R 5050:5050 docker/volumes/pgadmin_data 2>/dev/null || chmod 777 docker/volumes/pgadmin_data
        else
            chmod 777 docker/volumes/pgadmin_data
        fi
    fi
    
    if [[ $missing -gt 0 ]]; then
        log_warning "Created $missing missing volume directories"
    else
        log_success "All Docker volume directories verified"
    fi
}

# Generate production-ready .env file
generate_env_file() {
    log_info "Generating .env file..."
    
    # Load or generate secure passwords
    load_or_generate_passwords
    
    # Get values from configuration or use generated passwords
    local postgres_password="${POSTGRES_PASSWORD}"
    local airflow_db_password="${AIRFLOW_DB_PASSWORD}"
    local airflow_admin_user=$(get_config "security.airflow_admin_user" "admin")
    local airflow_admin_password="${AIRFLOW_ADMIN_PASSWORD}"
    local jupyter_token="${JUPYTER_TOKEN}"
    local pgadmin_email=$(get_config "security.pgadmin_email" "admin@admin.com")
    local pgadmin_password="${PGADMIN_PASSWORD}"
    
    # Generate cryptographic keys
    local fernet_key=$(generate_fernet_key)
    local secret_key=$(openssl rand -hex 32)
    
    # CRITICAL: Get current user UID for Airflow
    local current_uid=$(id -u)
    
    cat > .env << EOF
# Generated by Data Engineering Platform Setup
# Date: $(date)
# WARNING: NEVER commit this file to version control!

# Platform
PLATFORM_NAME=$(get_config "platform.name" "data-engineering-platform")
PLATFORM_VERSION=$(get_config "platform.version" "2.0.0")
PLATFORM_ENV=$(get_config "platform.environment" "development")

# Versions
POSTGRES_VERSION=$(get_config "versions.postgresql" "16.1-alpine")
AIRFLOW_VERSION=$(get_config "versions.airflow" "2.9.3-python3.11")
SPARK_VERSION=$(get_config "versions.spark" "3.5.1")
JUPYTER_VERSION=$(get_config "versions.jupyter" "spark-3.5.1")
PGADMIN_VERSION=$(get_config "versions.pgadmin" "8.11")

# PostgreSQL
POSTGRES_USER=$(get_config "database.user" "postgres")
POSTGRES_PASSWORD=${postgres_password}
POSTGRES_DB=$(get_config "database.name" "datawarehouse")

# Airflow - CRITICAL: UID must match current user
AIRFLOW_UID=${current_uid}
AIRFLOW_GID=0
AIRFLOW_DB_PASSWORD=${airflow_db_password}
AIRFLOW_FERNET_KEY=${fernet_key}
AIRFLOW_SECRET_KEY=${secret_key}
_AIRFLOW_WWW_USER_USERNAME=${airflow_admin_user}
_AIRFLOW_WWW_USER_PASSWORD=${airflow_admin_password}

# Jupyter
JUPYTER_TOKEN=${jupyter_token}

# pgAdmin
PGADMIN_DEFAULT_EMAIL=${pgadmin_email}
PGADMIN_DEFAULT_PASSWORD=${pgadmin_password}

# Ports
PORT_POSTGRES=$(get_config "ports.postgres" "5432")
PORT_AIRFLOW=$(get_config "ports.airflow_webserver" "8080")
PORT_PGADMIN=$(get_config "ports.pgadmin" "8081")
PORT_JUPYTER=$(get_config "ports.jupyter" "8888")
PORT_SPARK_MASTER_WEB=$(get_config "ports.spark_master_web" "8082")
PORT_SPARK_MASTER=$(get_config "ports.spark_master" "7077")
PORT_SPARK_WORKER_WEB=$(get_config "ports.spark_worker_web" "8083")

# Resource Limits - Production Optimized
POSTGRES_MEMORY=$(get_config "resources.postgres.memory" "2G")
POSTGRES_CPUS=$(get_config "resources.postgres.cpus" "1.0")
POSTGRES_AIRFLOW_MEMORY=$(get_config "resources.postgres_airflow.memory" "1G")
POSTGRES_AIRFLOW_CPUS=$(get_config "resources.postgres_airflow.cpus" "0.5")
AIRFLOW_WEBSERVER_MEMORY=$(get_config "resources.airflow.webserver.memory" "2G")
AIRFLOW_WEBSERVER_CPUS=$(get_config "resources.airflow.webserver.cpus" "1.0")
AIRFLOW_SCHEDULER_MEMORY=$(get_config "resources.airflow.scheduler.memory" "2G")
AIRFLOW_SCHEDULER_CPUS=$(get_config "resources.airflow.scheduler.cpus" "1.0")
SPARK_MASTER_MEMORY=$(get_config "resources.spark.master.memory" "2G")
SPARK_MASTER_CPUS=$(get_config "resources.spark.master.cpus" "1.0")
SPARK_WORKER_MEMORY=$(get_config "resources.spark.worker.memory" "4G")
SPARK_WORKER_CORES=2
SPARK_EXECUTOR_MEMORY=3G
JUPYTER_MEMORY=$(get_config "resources.jupyter.memory" "2G")
JUPYTER_CPUS=$(get_config "resources.jupyter.cpus" "1.0")
PGADMIN_MEMORY=$(get_config "resources.pgadmin.memory" "512M")
PGADMIN_CPUS=$(get_config "resources.pgadmin.cpus" "0.5")

# Features
ENABLE_EXAMPLE_DAGS=$(get_config "features.enable_example_dags" "false")
AIRFLOW_LOAD_EXAMPLES=false

# System paths (for bind mounts)
PROJECT_ROOT=${PWD}
EOF
    
    # Set restrictive permissions on .env
    chmod 600 .env
    
    log_success ".env file generated with secure permissions"
}

# Create production-ready docker-compose.yml
create_docker_compose() {
    log_info "Creating production-ready docker-compose.yml..."
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

# ============================================
# PRODUCTION-READY DOCKER COMPOSE
# ============================================

x-airflow-common: &airflow-common
  image: apache/airflow:${AIRFLOW_VERSION:-2.9.3-python3.11}
  environment: &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:${AIRFLOW_DB_PASSWORD}@postgres-airflow:5432/airflow
    AIRFLOW__CORE__FERNET_KEY: ${AIRFLOW_FERNET_KEY}
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: '${ENABLE_EXAMPLE_DAGS:-false}'
    AIRFLOW__WEBSERVER__RBAC: 'true'
    AIRFLOW__WEBSERVER__SECRET_KEY: ${AIRFLOW_SECRET_KEY}
    # Database pool configuration
    AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_ENABLED: 'true'
    AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_SIZE: 5
    AIRFLOW__DATABASE__SQL_ALCHEMY_MAX_OVERFLOW: 10
    AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_RECYCLE: 1800
    AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_PRE_PING: 'true'
    # Performance
    AIRFLOW__CORE__PARALLELISM: 16
    AIRFLOW__CORE__DAG_CONCURRENCY: 8
    AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG: 4
    # Python path
    PYTHONPATH: '/opt/airflow/dags:/opt/dbt'
    # PostgreSQL connection details
    POSTGRES_HOST: postgres
    POSTGRES_PORT: 5432
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: ${POSTGRES_DB}
  volumes:
    - ./airflow/dags:/opt/airflow/dags
    - ./airflow/logs:/opt/airflow/logs
    - ./airflow/plugins:/opt/airflow/plugins
    - ./dbt:/opt/dbt
    - ./data:/data
    - ./spark/jobs:/opt/spark/jobs:ro
  user: "${AIRFLOW_UID:-50000}:${AIRFLOW_GID:-0}"
  depends_on: &airflow-common-depends-on
    postgres-airflow:
      condition: service_healthy
    postgres:
      condition: service_healthy
  networks:
    - data_network

services:
  # ============================================
  # DATABASE SERVICES
  # ============================================
  
  postgres:
    image: postgres:${POSTGRES_VERSION:-16.1-alpine}
    container_name: postgres_dw
    hostname: postgres
    domainname: data.local
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-datawarehouse}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--auth-host=scram-sha-256 --auth-local=scram-sha-256"
      # Performance tuning
      POSTGRES_SHARED_BUFFERS: "512MB"
      POSTGRES_WORK_MEM: "32MB"
      POSTGRES_MAINTENANCE_WORK_MEM: "256MB"
      POSTGRES_EFFECTIVE_CACHE_SIZE: "1GB"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/postgresql.conf:/etc/postgresql/postgresql.conf:ro
      - ./docker/postgres/init:/docker-entrypoint-initdb.d:ro
      - ./sql:/sql:ro
      - ./data:/data
      - ./backups:/backups
    ports:
      - "${PORT_POSTGRES:-5432}:5432"
    command: 
      - postgres
      - -c
      - config_file=/etc/postgresql/postgresql.conf
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      data_network:
        aliases:
          - postgres.data.local
          - datawarehouse.local
    deploy:
      resources:
        limits:
          memory: ${POSTGRES_MEMORY:-2G}
          cpus: '${POSTGRES_CPUS:-1.0}'
        reservations:
          memory: 1G
          cpus: '0.5'
    mem_limit: ${POSTGRES_MEMORY:-2G}
    memswap_limit: ${POSTGRES_MEMORY:-2G}
    mem_reservation: 1G
    shm_size: 256M
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
        compress: "true"

  postgres-airflow:
    image: postgres:${POSTGRES_VERSION:-16.1-alpine}
    container_name: postgres_airflow
    hostname: postgres-airflow
    domainname: data.local
    environment:
      POSTGRES_DB: airflow
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: ${AIRFLOW_DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "--auth-host=scram-sha-256 --auth-local=scram-sha-256"
    volumes:
      - postgres_airflow_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U airflow -d airflow"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      data_network:
        aliases:
          - postgres-airflow.data.local
    deploy:
      resources:
        limits:
          memory: ${POSTGRES_AIRFLOW_MEMORY:-1G}
          cpus: '${POSTGRES_AIRFLOW_CPUS:-0.5}'
        reservations:
          memory: 512M
          cpus: '0.25'
    mem_limit: ${POSTGRES_AIRFLOW_MEMORY:-1G}
    memswap_limit: ${POSTGRES_AIRFLOW_MEMORY:-1G}
    mem_reservation: 512M
    shm_size: 128M
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
        compress: "true"

  # ============================================
  # AIRFLOW SERVICES
  # ============================================
  
  # CRITICAL FIX: Enhanced airflow-init with retry logic
  airflow-init:
    <<: *airflow-common
    container_name: airflow_init
    entrypoint: /bin/bash
    command:
      - -c
      - |
        # Enhanced initialization with proper error handling
        set -e
        
        # Wait for database to be REALLY ready
        echo "Waiting for Airflow database to be ready..."
        for i in {1..30}; do
          if PGPASSWORD=${AIRFLOW_DB_PASSWORD} psql -h postgres-airflow -U airflow -d airflow -c "SELECT 1" >/dev/null 2>&1; then
            echo "✅ Database is ready!"
            break
          fi
          echo "⏳ Waiting for database... attempt $$i/30"
          sleep 2
          if [ $$i -eq 30 ]; then
            echo "❌ Database not ready after 30 attempts"
            exit 1
          fi
        done
        
        # Version check
        function ver() {
          printf "%04d%04d%04d%04d" $${1//./ }
        }
        airflow_version=$$(AIRFLOW__LOGGING__LOGGING_LEVEL=ERROR airflow version)
        airflow_version_comparable=$$(ver $${airflow_version})
        min_airflow_version=2.2.0
        min_airflow_version_comparable=$$(ver $${min_airflow_version})
        if (( airflow_version_comparable < min_airflow_version_comparable )); then
          echo "❌ ERROR: Airflow version $${airflow_version} is less than $${min_airflow_version}"
          exit 1
        fi
        
        # Check UID
        if [[ -z "${AIRFLOW_UID}" ]]; then
          echo "❌ ERROR: AIRFLOW_UID not set"
          exit 1
        fi
        
        # Create directories with proper permissions
        echo "Creating Airflow directories..."
        mkdir -p /sources/logs /sources/dags /sources/plugins
        chown -R "${AIRFLOW_UID}:0" /sources/{logs,dags,plugins}
        
        # Initialize database with retry logic
        echo "Initializing Airflow database..."
        for i in {1..3}; do
          if airflow db init; then
            echo "✅ Database initialized successfully"
            break
          else
            echo "⚠️  Database init failed, retry $$i/3"
            sleep 5
            if [ $$i -eq 3 ]; then
              echo "❌ Failed to initialize database after 3 attempts"
              exit 1
            fi
          fi
        done
        
        # Create admin user (will skip if exists)
        echo "Creating admin user..."
        airflow users create \
          --username ${_AIRFLOW_WWW_USER_USERNAME:-admin} \
          --password ${_AIRFLOW_WWW_USER_PASSWORD:-admin} \
          --firstname Admin \
          --lastname User \
          --role Admin \
          --email admin@example.com 2>/dev/null || echo "ℹ️  Admin user already exists"
        
        echo "✅ Airflow initialization complete!"
        exec /entrypoint airflow version
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_MIGRATE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-admin}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-admin}
      PGPASSWORD: ${AIRFLOW_DB_PASSWORD}
    user: "0:0"
    volumes:
      - ./airflow:/sources
    depends_on:
      postgres-airflow:
        condition: service_healthy
    networks:
      - data_network

  airflow-webserver:
    <<: *airflow-common
    container_name: airflow_webserver
    hostname: airflow-webserver
    command: webserver
    ports:
      - "${PORT_AIRFLOW:-8080}:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    deploy:
      resources:
        limits:
          memory: ${AIRFLOW_WEBSERVER_MEMORY:-2G}
          cpus: '${AIRFLOW_WEBSERVER_CPUS:-1.0}'
        reservations:
          memory: 1G
          cpus: '0.5'
    mem_limit: ${AIRFLOW_WEBSERVER_MEMORY:-2G}
    memswap_limit: ${AIRFLOW_WEBSERVER_MEMORY:-2G}
    mem_reservation: 1G
    restart: always
    depends_on:
      airflow-init:
        condition: service_completed_successfully
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
        compress: "true"

  airflow-scheduler:
    <<: *airflow-common
    container_name: airflow_scheduler
    hostname: airflow-scheduler
    command: scheduler
    healthcheck:
      test: ["CMD-SHELL", 'airflow jobs check --job-type SchedulerJob --hostname "$${HOSTNAME}"']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    deploy:
      resources:
        limits:
          memory: ${AIRFLOW_SCHEDULER_MEMORY:-2G}
          cpus: '${AIRFLOW_SCHEDULER_CPUS:-1.0}'
        reservations:
          memory: 1G
          cpus: '0.5'
    mem_limit: ${AIRFLOW_SCHEDULER_MEMORY:-2G}
    memswap_limit: ${AIRFLOW_SCHEDULER_MEMORY:-2G}
    mem_reservation: 1G
    restart: always
    depends_on:
      airflow-init:
        condition: service_completed_successfully
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
        compress: "true"

  # ============================================
  # SPARK SERVICES
  # ============================================
  
  spark-master:
    image: bitnami/spark:${SPARK_VERSION:-3.5.1}
    container_name: spark_master
    hostname: spark-master
    domainname: data.local
    environment:
      - SPARK_MODE=master
      - SPARK_MASTER_HOST=spark-master
      - SPARK_MASTER_PORT=7077
      - SPARK_MASTER_WEBUI_PORT=8080
      - SPARK_DAEMON_MEMORY=1g
      - SPARK_MASTER_OPTS=-Xmx1g -XX:MaxPermSize=256m
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    ports:
      - "${PORT_SPARK_MASTER_WEB:-8082}:8080"
      - "${PORT_SPARK_MASTER:-7077}:7077"
    volumes:
      - ./spark/jobs:/opt/spark/jobs:ro
      - ./spark/jars:/opt/spark/jars:ro
      - ./spark/conf:/opt/spark/conf:ro
      - ./data:/opt/spark/data
      - spark_logs:/opt/spark/logs
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 45s
    networks:
      data_network:
        aliases:
          - spark-master.data.local
    deploy:
      resources:
        limits:
          memory: ${SPARK_MASTER_MEMORY:-2G}
          cpus: '${SPARK_MASTER_CPUS:-1.0}'
        reservations:
          memory: 1G
          cpus: '0.5'
    mem_limit: ${SPARK_MASTER_MEMORY:-2G}
    memswap_limit: ${SPARK_MASTER_MEMORY:-2G}
    mem_reservation: 1G
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
        compress: "true"

  spark-worker:
    image: bitnami/spark:${SPARK_VERSION:-3.5.1}
    container_name: spark_worker
    hostname: spark-worker
    domainname: data.local
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=${SPARK_EXECUTOR_MEMORY:-3g}
      - SPARK_WORKER_CORES=${SPARK_WORKER_CORES:-2}
      - SPARK_DAEMON_MEMORY=512m
      - SPARK_WORKER_OPTS=-Xmx3g -XX:MaxPermSize=512m
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    ports:
      - "${PORT_SPARK_WORKER_WEB:-8083}:8081"
    volumes:
      - ./spark/jobs:/opt/spark/jobs:ro
      - ./spark/jars:/opt/spark/jars:ro
      - ./spark/conf:/opt/spark/conf:ro
      - ./data:/opt/spark/data
      - spark_logs:/opt/spark/logs
    depends_on:
      spark-master:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 45s
    networks:
      data_network:
        aliases:
          - spark-worker.data.local
    deploy:
      resources:
        limits:
          memory: ${SPARK_WORKER_MEMORY:-4G}
          cpus: '${SPARK_WORKER_CPUS:-2.0}'
        reservations:
          memory: 2G
          cpus: '1.0'
    mem_limit: ${SPARK_WORKER_MEMORY:-4G}
    memswap_limit: ${SPARK_WORKER_MEMORY:-4G}
    mem_reservation: 2G
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
        compress: "true"

  # ============================================
  # ANALYTICS SERVICES
  # ============================================
  
  jupyter:
    image: jupyter/pyspark-notebook:${JUPYTER_VERSION:-spark-3.5.1}
    container_name: jupyter_pyspark
    hostname: jupyter
    domainname: data.local
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - SPARK_MASTER=spark://spark-master:7077
      - JUPYTER_TOKEN=${JUPYTER_TOKEN:-development}
      - GRANT_SUDO=yes
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    ports:
      - "${PORT_JUPYTER:-8888}:8888"
    volumes:
      - ./notebooks:/home/jovyan/work
      - ./data:/home/jovyan/data:rw
      - ./spark/jars:/home/jovyan/spark/jars:ro
    networks:
      data_network:
        aliases:
          - jupyter.data.local
    depends_on:
      - spark-master
      - postgres
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8888/api"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: ${JUPYTER_MEMORY:-2G}
          cpus: '${JUPYTER_CPUS:-1.0}'
        reservations:
          memory: 1G
          cpus: '0.5'
    mem_limit: ${JUPYTER_MEMORY:-2G}
    memswap_limit: ${JUPYTER_MEMORY:-2G}
    mem_reservation: 1G
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
        compress: "true"

  # ============================================
  # ADMIN SERVICES
  # ============================================
  
  pgadmin:
    image: dpage/pgadmin4:${PGADMIN_VERSION:-8.11}
    container_name: pgadmin4
    hostname: pgadmin
    domainname: data.local
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_DEFAULT_EMAIL:-admin@admin.com}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_DEFAULT_PASSWORD:-admin}
      PGADMIN_CONFIG_SERVER_MODE: 'False'
      PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED: 'False'
    ports:
      - "${PORT_PGADMIN:-8081}:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
      - ./docker/pgadmin/servers.json:/pgadmin4/servers.json:ro
    depends_on:
      - postgres
      - postgres-airflow
    healthcheck:
      test: ["CMD", "wget", "-O", "-", "http://localhost:80/misc/ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    networks:
      data_network:
        aliases:
          - pgadmin.data.local
    deploy:
      resources:
        limits:
          memory: ${PGADMIN_MEMORY:-512M}
          cpus: '${PGADMIN_CPUS:-0.5}'
        reservations:
          memory: 256M
          cpus: '0.25'
    mem_limit: ${PGADMIN_MEMORY:-512M}
    memswap_limit: ${PGADMIN_MEMORY:-512M}
    mem_reservation: 256M
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
        compress: "true"

# ============================================
# NETWORKS - Enhanced configuration
# ============================================

networks:
  data_network:
    name: data_platform_network
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1
    driver_opts:
      com.docker.network.bridge.name: br-data-platform
      com.docker.network.bridge.enable_ip_masquerade: "true"
      com.docker.network.bridge.enable_icc: "true"
      com.docker.network.bridge.host_binding_ipv4: "0.0.0.0"
      com.docker.network.driver.mtu: "1450"

# ============================================
# VOLUMES - Fixed bind mounts
# ============================================

volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      device: ${PROJECT_ROOT}/docker/volumes/postgres_data
      o: bind
  postgres_airflow_data:
    driver: local
    driver_opts:
      type: none
      device: ${PROJECT_ROOT}/docker/volumes/postgres_airflow_data
      o: bind
  pgadmin_data:
    driver: local
    driver_opts:
      type: none
      device: ${PROJECT_ROOT}/docker/volumes/pgadmin_data
      o: bind
  spark_logs:
    driver: local
    driver_opts:
      type: none
      device: ${PROJECT_ROOT}/docker/volumes/spark_logs
      o: bind
EOF
    
    log_success "Production-ready docker-compose.yml created"
}

# Validate Docker setup
validate_docker_setup() {
    log_info "Validating Docker setup..."
    
    local errors=0
    
    # Check docker-compose.yml syntax
    if docker_compose config >/dev/null 2>&1; then
        log_success "docker-compose.yml syntax valid"
    else
        log_error "docker-compose.yml has syntax errors"
        docker_compose config
        ((errors++))
    fi
    
    # Check .env file
    if [[ ! -f ".env" ]]; then
        log_error ".env file not found"
        ((errors++))
    else
        # Check for required variables
        source .env
        if [[ -z "$AIRFLOW_UID" ]]; then
            log_error "AIRFLOW_UID not set in .env"
            ((errors++))
        fi
        if [[ -z "$POSTGRES_PASSWORD" ]]; then
            log_error "POSTGRES_PASSWORD not set in .env"
            ((errors++))
        fi
    fi
    
    # Check volume directories
    local volumes=("postgres_data" "postgres_airflow_data" "pgadmin_data" "spark_logs")
    for vol in "${volumes[@]}"; do
        if [[ ! -d "docker/volumes/$vol" ]]; then
            log_error "Volume directory missing: docker/volumes/$vol"
            ((errors++))
        fi
    done
    
    if [[ $errors -eq 0 ]]; then
        log_success "Docker setup validation passed"
        return 0
    else
        log_error "Docker setup validation failed with $errors errors"
        return 1
    fi
}

# Main execution
main() {
    verify_docker_volumes
    generate_env_file
    create_docker_compose
    validate_docker_setup
}

main
```

### 📁 **modules/03_database.sh** (Database Setup)
```bash
#!/bin/bash
# Module: Database Setup - PostgreSQL configuration and initialization

source "$SCRIPT_DIR/lib/common.sh"

log_section "Database Setup Module"

# Create PostgreSQL configuration
create_postgres_config() {
    log_info "Creating PostgreSQL configuration..."
    
    cat > docker/postgres/postgresql.conf << 'EOF'
# PostgreSQL Configuration for Analytics Workloads
# Optimized for Data Warehouse operations

# Network
listen_addresses = '*'
port = 5432

# Memory
shared_buffers = 512MB
work_mem = 256MB
maintenance_work_mem = 512MB
effective_cache_size = 2GB

# Write Ahead Log
wal_buffers = 64MB
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9
max_wal_size = 2GB
min_wal_size = 1GB

# Query Planner
random_page_cost = 1.1
effective_io_concurrency = 200

# Parallel Query
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

# Connections and Pooling
max_connections = 200
superuser_reserved_connections = 3
max_prepared_transactions = 100

# Connection pooling settings (for pgBouncer compatibility)
tcp_keepalives_idle = 60
tcp_keepalives_interval = 10
tcp_keepalives_count = 6

# Logging
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# Statistics
track_activities = on
track_counts = on
track_io_timing = on

# Autovacuum
autovacuum = on
autovacuum_max_workers = 4

# Extensions
shared_preload_libraries = 'pg_stat_statements'

# Security
password_encryption = scram-sha-256
EOF
    
    log_success "PostgreSQL configuration created"
}

# Create initialization SQL
create_init_sql() {
    log_info "Creating database initialization script..."
    
    mkdir -p docker/postgres/init
    
    cat > docker/postgres/init/01_init_database.sql << 'EOF'
-- Initialize Data Warehouse Database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS ml;

-- Create roles
CREATE ROLE readonly;
GRANT CONNECT ON DATABASE datawarehouse TO readonly;
GRANT USAGE ON SCHEMA raw, staging, marts TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA raw, staging, marts TO readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw, staging, marts GRANT SELECT ON TABLES TO readonly;

CREATE ROLE etl_user;
GRANT CONNECT ON DATABASE datawarehouse TO etl_user;
GRANT ALL ON SCHEMA raw, staging, marts TO etl_user;
GRANT ALL ON ALL TABLES IN SCHEMA raw, staging, marts TO etl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw, staging, marts GRANT ALL ON TABLES TO etl_user;

-- Create date dimension table
CREATE TABLE IF NOT EXISTS marts.dim_date (
    date_key INTEGER PRIMARY KEY,
    date_actual DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    week INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE
);

-- Populate date dimension (2020-2030)
INSERT INTO marts.dim_date (
    date_key, date_actual, year, quarter, month, week,
    day_of_month, day_of_week, day_of_year,
    day_name, month_name, is_weekend
)
SELECT 
    TO_CHAR(d, 'YYYYMMDD')::INTEGER as date_key,
    d as date_actual,
    EXTRACT(YEAR FROM d)::INTEGER as year,
    EXTRACT(QUARTER FROM d)::INTEGER as quarter,
    EXTRACT(MONTH FROM d)::INTEGER as month,
    EXTRACT(WEEK FROM d)::INTEGER as week,
    EXTRACT(DAY FROM d)::INTEGER as day_of_month,
    EXTRACT(DOW FROM d)::INTEGER as day_of_week,
    EXTRACT(DOY FROM d)::INTEGER as day_of_year,
    TRIM(TO_CHAR(d, 'Day')) as day_name,
    TRIM(TO_CHAR(d, 'Month')) as month_name,
    EXTRACT(DOW FROM d) IN (0, 6) as is_weekend
FROM generate_series('2020-01-01'::DATE, '2030-12-31'::DATE, '1 day'::INTERVAL) d
ON CONFLICT (date_key) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_dim_date_actual ON marts.dim_date(date_actual);
CREATE INDEX IF NOT EXISTS idx_dim_date_year_month ON marts.dim_date(year, month);

-- Grant permissions
GRANT SELECT ON marts.dim_date TO readonly;
GRANT ALL ON marts.dim_date TO etl_user;
EOF
    
    log_success "Database initialization script created"
}

# Main execution
main() {
    create_postgres_config
    create_init_sql
}

main
```

### 📁 **modules/04_airflow.sh** (Airflow Setup)
```bash
#!/bin/bash
# Module: Airflow Setup - DAGs and configurations
# PRODUCTION FIXED VERSION

source "$SCRIPT_DIR/lib/common.sh"

log_section "Airflow Setup Module"

# CRITICAL FIX: Set Airflow permissions FIRST
set_airflow_permissions() {
    log_info "Setting Airflow directory permissions..."
    
    # Get current user ID
    local current_uid=$(id -u)
    local current_gid=$(id -g)
    
    # Update .env with correct UID if needed
    if [[ -f .env ]]; then
        if grep -q "AIRFLOW_UID=" .env 2>/dev/null; then
            # Update existing UID
            sed -i.bak "s/AIRFLOW_UID=.*/AIRFLOW_UID=$current_uid/" .env
            log_info "Updated AIRFLOW_UID to $current_uid"
        else
            # Add UID if missing
            echo "AIRFLOW_UID=$current_uid" >> .env
            log_info "Added AIRFLOW_UID=$current_uid to .env"
        fi
        
        # Also ensure GID is set
        if ! grep -q "AIRFLOW_GID=" .env 2>/dev/null; then
            echo "AIRFLOW_GID=0" >> .env
        fi
    else
        log_error ".env file not found - run Docker setup first"
        exit 1
    fi
    
    # Create Airflow directories with correct ownership
    local airflow_dirs=(
        "airflow/logs"
        "airflow/dags"
        "airflow/plugins"
        "airflow/config"
    )
    
    for dir in "${airflow_dirs[@]}"; do
        mkdir -p "$dir"
        
        # Set permissions based on OS
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux: try to set ownership
            sudo chown -R $current_uid:0 "$dir" 2>/dev/null || {
                log_warning "Could not set ownership for $dir, using chmod instead"
                chmod -R 775 "$dir"
            }
        else
            # macOS/Windows: ensure write permissions
            chmod -R 775 "$dir"
        fi
    done
    
    # Create .airflowignore to exclude test files
    cat > airflow/dags/.airflowignore << 'EOF'
# Ignore test files
test_*.py
*_test.py
__pycache__/
*.pyc
.pytest_cache/
EOF
    
    log_success "Airflow permissions configured"
}

# Create production-ready example DAG
create_example_dag() {
    log_info "Creating example Airflow DAG..."
    
    cat > airflow/dags/example_pipeline.py << 'EOF'
"""
Example data pipeline demonstrating platform capabilities
Production-ready with error handling and best practices
"""
from datetime import datetime, timedelta
import logging
from typing import Any, Dict

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowException
from airflow.models import Variable

# Configure logging
logger = logging.getLogger(__name__)

# Default arguments with production settings
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

def check_database_connection(**context) -> Dict[str, Any]:
    """
    Test database connectivity with proper error handling
    Returns connection details for downstream tasks
    """
    try:
        hook = PostgresHook(postgres_conn_id='postgres_default')
        conn = hook.get_conn()
        cursor = conn.cursor()
        
        # Test connection and get stats
        cursor.execute("""
            SELECT 
                version() as version,
                current_database() as database,
                current_user as user,
                pg_database_size(current_database()) as db_size
        """)
        result = cursor.fetchone()
        
        connection_info = {
            'version': result[0],
            'database': result[1],
            'user': result[2],
            'db_size_mb': result[3] / (1024 * 1024)
        }
        
        logger.info(f"Database connection successful: {connection_info['database']}")
        logger.info(f"PostgreSQL version: {connection_info['version']}")
        logger.info(f"Database size: {connection_info['db_size_mb']:.2f} MB")
        
        cursor.close()
        conn.close()
        
        # Push to XCom for downstream tasks
        context['task_instance'].xcom_push(key='db_info', value=connection_info)
        
        return connection_info
        
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise AirflowException(f"Cannot connect to database: {str(e)}")

def generate_sample_data(**context) -> str:
    """
    Generate sample data with error handling
    Uses XCom to get database info from upstream task
    """
    import pandas as pd
    import numpy as np
    from pathlib import Path
    
    try:
        # Get database info from upstream task
        db_info = context['task_instance'].xcom_pull(
            task_ids='check_database',
            key='db_info'
        )
        logger.info(f"Generating data for database: {db_info['database']}")
        
        # Create data directory if not exists
        data_dir = Path('/data/raw')
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate sample data
        np.random.seed(42)  # For reproducibility
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        
        data = {
            'date': dates,
            'sales': np.random.randint(1000, 5000, size=100),
            'customers': np.random.randint(50, 200, size=100),
            'region': np.random.choice(['North', 'South', 'East', 'West'], size=100),
            'product_category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], size=100),
            'revenue': np.round(np.random.uniform(10000, 50000, size=100), 2)
        }
        
        df = pd.DataFrame(data)
        
        # Add calculated fields
        df['avg_order_value'] = np.round(df['revenue'] / df['customers'], 2)
        df['is_weekend'] = df['date'].dt.dayofweek.isin([5, 6])
        
        # Save to CSV
        output_file = data_dir / f"sample_sales_{context['ds']}.csv"
        df.to_csv(output_file, index=False)
        
        logger.info(f"Generated {len(df)} records")
        logger.info(f"Data saved to: {output_file}")
        
        # Push file path to XCom
        context['task_instance'].xcom_push(key='data_file', value=str(output_file))
        
        return str(output_file)
        
    except Exception as e:
        logger.error(f"Data generation failed: {str(e)}")
        raise AirflowException(f"Failed to generate sample data: {str(e)}")

def validate_data(**context) -> bool:
    """
    Validate generated data quality
    """
    import pandas as pd
    from pathlib import Path
    
    try:
        # Get file path from upstream task
        data_file = context['task_instance'].xcom_pull(
            task_ids='generate_sample_data',
            key='data_file'
        )
        
        if not data_file or not Path(data_file).exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        # Load and validate data
        df = pd.read_csv(data_file)
        
        validation_results = {
            'row_count': len(df),
            'null_count': df.isnull().sum().sum(),
            'duplicate_count': df.duplicated().sum(),
            'date_range_valid': True,
            'numeric_ranges_valid': True
        }
        
        # Check for nulls
        if validation_results['null_count'] > 0:
            logger.warning(f"Found {validation_results['null_count']} null values")
        
        # Check for duplicates
        if validation_results['duplicate_count'] > 0:
            logger.warning(f"Found {validation_results['duplicate_count']} duplicate rows")
        
        # Validate numeric ranges
        if (df['sales'] < 0).any() or (df['customers'] < 0).any():
            validation_results['numeric_ranges_valid'] = False
            raise ValueError("Negative values found in sales or customers")
        
        # Validate date range
        df['date'] = pd.to_datetime(df['date'])
        if df['date'].min() < pd.Timestamp('2020-01-01'):
            validation_results['date_range_valid'] = False
            logger.warning("Dates outside expected range")
        
        logger.info(f"Validation completed: {validation_results}")
        
        # Push validation results to XCom
        context['task_instance'].xcom_push(key='validation_results', value=validation_results)
        
        return all([
            validation_results['row_count'] > 0,
            validation_results['null_count'] == 0,
            validation_results['numeric_ranges_valid'],
            validation_results['date_range_valid']
        ])
        
    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}")
        raise AirflowException(f"Data validation failed: {str(e)}")

# Create DAG
with DAG(
    'example_pipeline',
    default_args=default_args,
    description='Production-ready example data pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['example', 'production', 'tutorial'],
    doc_md="""
    # Example Data Pipeline
    
    This DAG demonstrates production-ready patterns:
    - Database connectivity checks
    - Data generation and validation
    - Error handling and retries
    - XCom for task communication
    - Logging best practices
    
    ## Tasks
    1. **check_database**: Verify database connectivity
    2. **create_tables**: Create necessary database tables
    3. **generate_sample_data**: Generate sample sales data
    4. **validate_data**: Validate data quality
    5. **load_to_staging**: Load data to staging tables
    """
) as dag:
    
    # Task 1: Check database connection
    check_db = PythonOperator(
        task_id='check_database',
        python_callable=check_database_connection,
        doc_md="Verify database connectivity and get connection info"
    )
    
    # Task 2: Create tables
    create_tables = PostgresOperator(
        task_id='create_tables',
        postgres_conn_id='postgres_default',
        sql="""
        -- Create schema if not exists
        CREATE SCHEMA IF NOT EXISTS staging;
        
        -- Create staging table with proper indexes
        CREATE TABLE IF NOT EXISTS staging.sales_data (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            sales INTEGER CHECK (sales >= 0),
            customers INTEGER CHECK (customers >= 0),
            region VARCHAR(50),
            product_category VARCHAR(100),
            revenue DECIMAL(12, 2),
            avg_order_value DECIMAL(10, 2),
            is_weekend BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_sales_date ON staging.sales_data(date);
        CREATE INDEX IF NOT EXISTS idx_sales_region ON staging.sales_data(region);
        CREATE INDEX IF NOT EXISTS idx_sales_category ON staging.sales_data(product_category);
        
        -- Create data quality table
        CREATE TABLE IF NOT EXISTS staging.data_quality_checks (
            id SERIAL PRIMARY KEY,
            check_date DATE NOT NULL,
            table_name VARCHAR(100),
            check_type VARCHAR(50),
            check_result BOOLEAN,
            details JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        doc_md="Create staging tables with proper schema and indexes"
    )
    
    # Task 3: Generate sample data
    generate_data = PythonOperator(
        task_id='generate_sample_data',
        python_callable=generate_sample_data,
        doc_md="Generate sample sales data for testing"
    )
    
    # Task 4: Validate data
    validate = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
        doc_md="Validate data quality before loading"
    )
    
    # Task 5: Load to staging
    load_to_staging = PostgresOperator(
        task_id='load_to_staging',
        postgres_conn_id='postgres_default',
        sql="""
        -- This would normally use COPY or bulk insert
        -- For demo purposes, we're inserting sample data
        INSERT INTO staging.sales_data (date, sales, customers, region, product_category, revenue)
        SELECT 
            CURRENT_DATE - (random() * 30)::int,
            (random() * 4000 + 1000)::int,
            (random() * 150 + 50)::int,
            (ARRAY['North', 'South', 'East', 'West'])[floor(random() * 4 + 1)],
            (ARRAY['Electronics', 'Clothing', 'Food', 'Books'])[floor(random() * 4 + 1)],
            (random() * 40000 + 10000)::decimal(12,2)
        FROM generate_series(1, 10);
        
        -- Log data quality check
        INSERT INTO staging.data_quality_checks (check_date, table_name, check_type, check_result)
        VALUES (CURRENT_DATE, 'staging.sales_data', 'row_count', true);
        """,
        doc_md="Load validated data to staging tables"
    )
    
    # Define task dependencies
    check_db >> create_tables >> generate_data >> validate >> load_to_staging
EOF
    
    log_success "Production-ready example DAG created"
}

# Create Airflow connections initialization script
create_connections_script() {
    log_info "Creating Airflow connections script..."
    
    cat > scripts/init-airflow-connections.sh << 'EOF'
#!/bin/bash
# Initialize Airflow connections with error handling

set -euo pipefail

echo "🔗 Setting up Airflow connections..."

# Wait for Airflow webserver to be ready
echo "Waiting for Airflow webserver..."
for i in {1..30}; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health | grep -q "200"; then
        echo "✅ Airflow is ready!"
        break
    fi
    echo "⏳ Waiting for Airflow... attempt $i/30"
    sleep 5
    if [ $i -eq 30 ]; then
        echo "❌ Airflow not ready after 30 attempts"
        exit 1
    fi
done

# Load environment variables
if [[ -f .env ]]; then
    source .env
else
    echo "❌ .env file not found"
    exit 1
fi

# Create PostgreSQL connection for main data warehouse
echo "Creating postgres_default connection..."
docker exec airflow_webserver airflow connections add \
    'postgres_default' \
    --conn-type 'postgres' \
    --conn-host 'postgres' \
    --conn-schema "${POSTGRES_DB}" \
    --conn-login "${POSTGRES_USER}" \
    --conn-password "${POSTGRES_PASSWORD}" \
    --conn-port 5432 \
    2>/dev/null || echo "ℹ️  Connection postgres_default already exists"

# Create Spark connection
echo "Creating spark_default connection..."
docker exec airflow_webserver airflow connections add \
    'spark_default' \
    --conn-type 'spark' \
    --conn-host 'spark://spark-master' \
    --conn-port 7077 \
    2>/dev/null || echo "ℹ️  Connection spark_default already exists"

# Create file system connection for data directory
echo "Creating fs_default connection..."
docker exec airflow_webserver airflow connections add \
    'fs_default' \
    --conn-type 'fs' \
    --conn-extra '{"path": "/data"}' \
    2>/dev/null || echo "ℹ️  Connection fs_default already exists"

# Verify connections
echo ""
echo "📋 Verifying connections..."
docker exec airflow_webserver airflow connections list 2>/dev/null | grep -E "postgres_default|spark_default|fs_default" || true

echo ""
echo "✅ Airflow connections configured successfully!"
echo ""
echo "📝 Available connections:"
echo "  - postgres_default: PostgreSQL data warehouse"
echo "  - spark_default: Spark cluster"
echo "  - fs_default: File system (/data)"
EOF
    
    chmod +x scripts/init-airflow-connections.sh
    log_success "Airflow connections script created"
}

# Create Airflow configuration file
create_airflow_config() {
    log_info "Creating Airflow configuration..."
    
    cat > airflow/config/airflow.cfg.template << 'EOF'
# Airflow Production Configuration Template
# Copy to airflow.cfg and customize as needed

[core]
# Executor
executor = LocalExecutor

# Parallelism
parallelism = 16
dag_concurrency = 8
max_active_runs_per_dag = 4
max_active_tasks_per_dag = 16

# DAG Processing
min_file_process_interval = 30
dag_dir_list_interval = 60
dagbag_import_timeout = 120

# Task Processing
task_runner = StandardTaskRunner
killed_task_cleanup_time = 60

[database]
# Connection pooling
sql_alchemy_pool_enabled = True
sql_alchemy_pool_size = 5
sql_alchemy_max_overflow = 10
sql_alchemy_pool_recycle = 1800
sql_alchemy_pool_pre_ping = True

[scheduler]
# Performance
min_file_process_interval = 30
dag_dir_list_interval = 60
scheduler_heartbeat_sec = 5
parsing_processes = 2
max_dagruns_to_create_per_loop = 10
max_tis_per_query = 512

# Health check
scheduler_health_check_threshold = 30
scheduler_zombie_task_threshold = 300
zombie_detection_interval = 300

[webserver]
# Server settings
web_server_host = 0.0.0.0
web_server_port = 8080
web_server_worker_timeout = 120
worker_refresh_interval = 30
worker_refresh_batch_size = 1
worker_class = sync

# UI settings
default_ui_timezone = UTC
expose_config = False
expose_hostname = False
expose_stacktrace = False
page_size = 100

[logging]
# Logging configuration
base_log_folder = /opt/airflow/logs
logging_level = INFO
fab_logging_level = WARNING
colored_console_log = False

# Remote logging (optional)
remote_logging = False

[metrics]
# StatsD metrics (optional)
statsd_on = False
statsd_host = localhost
statsd_port = 8125
statsd_prefix = airflow
EOF
    
    log_success "Airflow configuration template created"
}

# Validate Airflow setup
validate_airflow_setup() {
    log_info "Validating Airflow setup..."
    
    local errors=0
    
    # Check if DAGs directory is writable
    if [[ ! -w "airflow/dags" ]]; then
        log_error "Airflow DAGs directory not writable"
        ((errors++))
    fi
    
    # Check if example DAG exists
    if [[ ! -f "airflow/dags/example_pipeline.py" ]]; then
        log_error "Example DAG not found"
        ((errors++))
    fi
    
    # Check Python syntax of DAG
    if command_exists python3; then
        python3 -m py_compile airflow/dags/example_pipeline.py 2>/dev/null || {
            log_error "Example DAG has Python syntax errors"
            ((errors++))
        }
    fi
    
    # Check if connections script exists and is executable
    if [[ ! -x "scripts/init-airflow-connections.sh" ]]; then
        log_error "Airflow connections script not executable"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        log_success "Airflow setup validation passed"
        return 0
    else
        log_error "Airflow setup validation failed with $errors errors"
        return 1
    fi
}

# Main execution
main() {
    set_airflow_permissions
    create_example_dag
    create_connections_script
    create_airflow_config
    validate_airflow_setup
}

main
```

### 📁 **modules/05_spark.sh** (Spark Setup)
```bash
#!/bin/bash
# Module: Spark Setup - Configuration and example jobs
# PRODUCTION FIXED VERSION

source "$SCRIPT_DIR/lib/common.sh"

log_section "Spark Setup Module"

# CRITICAL FIX: Download and validate JDBC driver
download_jdbc_driver() {
    log_info "Downloading PostgreSQL JDBC driver (CRITICAL for Spark-PostgreSQL connectivity)..."
    
    local jdbc_version=$(get_config "versions.postgresql_jdbc" "42.7.3")
    local jdbc_file="spark/jars/postgresql-${jdbc_version}.jar"
    local jdbc_url="https://jdbc.postgresql.org/download/postgresql-${jdbc_version}.jar"
    
    # Create jars directory
    mkdir -p spark/jars
    
    # Check if file already exists and is valid
    if [[ -f "$jdbc_file" ]]; then
        # Validate file size (should be > 1MB)
        local file_size=$(stat -f%z "$jdbc_file" 2>/dev/null || stat -c%s "$jdbc_file" 2>/dev/null || echo "0")
        if [[ $file_size -gt 1000000 ]]; then
            log_success "JDBC driver already exists and is valid"
            return 0
        else
            log_warning "JDBC driver exists but appears corrupted, re-downloading..."
            rm -f "$jdbc_file"
        fi
    fi
    
    # Download with retry logic
    local max_attempts=3
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Download attempt $attempt/$max_attempts..."
        
        if command_exists wget; then
            wget -q --show-progress --timeout=30 --tries=2 "$jdbc_url" -O "$jdbc_file" && break
        elif command_exists curl; then
            curl -L --progress-bar --max-time 30 --retry 2 "$jdbc_url" -o "$jdbc_file" && break
        else
            log_error "Neither wget nor curl is available"
            return 1
        fi
        
        ((attempt++))
        if [[ $attempt -le $max_attempts ]]; then
            log_warning "Download failed, retrying..."
            sleep 2
        fi
    done
    
    # Validate downloaded file
    if [[ ! -f "$jdbc_file" ]]; then
        log_error "JDBC driver download failed after $max_attempts attempts"
        log_error "This is CRITICAL - Spark will not be able to connect to PostgreSQL!"
        log_info "You can manually download from: $jdbc_url"
        log_info "And place it in: $jdbc_file"
        return 1
    fi
    
    # Validate file size
    local file_size=$(stat -f%z "$jdbc_file" 2>/dev/null || stat -c%s "$jdbc_file" 2>/dev/null || echo "0")
    if [[ $file_size -lt 1000000 ]]; then
        log_error "Downloaded JDBC driver appears corrupted (size: $file_size bytes)"
        rm -f "$jdbc_file"
        return 1
    fi
    
    # Set proper permissions
    chmod 644 "$jdbc_file"
    
    # Create copies for different Spark contexts (master, worker, jupyter)
    log_info "Creating JDBC driver copies for all Spark contexts..."
    cp "$jdbc_file" "spark/jars/postgresql.jar" 2>/dev/null || true
    
    log_success "JDBC driver ready: $(ls -lh $jdbc_file | awk '{print $5}')"
    return 0
}

# Create Spark configuration with production settings
create_spark_config() {
    log_info "Creating Spark configuration..."
    
    cat > spark/conf/spark-defaults.conf << 'EOF'
# Spark Production Configuration
# Optimized for data engineering workloads

# Application Settings
spark.app.name              DataEngineeringPlatform
spark.master                spark://spark-master:7077

# Memory Configuration
spark.driver.memory         2g
spark.driver.maxResultSize  1g
spark.executor.memory       3g
spark.executor.memoryOverhead 512m

# Java Options for Better Memory Management
spark.driver.extraJavaOptions  -XX:+UseG1GC -XX:+UnlockDiagnosticVMOptions -XX:+G1SummarizeConcMark
spark.executor.extraJavaOptions -XX:+UseG1GC -XX:InitiatingHeapOccupancyPercent=35

# Parallelism and Partitioning
spark.default.parallelism   8
spark.sql.shuffle.partitions 8
spark.sql.files.maxPartitionBytes 134217728
spark.sql.files.openCostInBytes 4194304

# Adaptive Query Execution (Spark 3.0+)
spark.sql.adaptive.enabled true
spark.sql.adaptive.coalescePartitions.enabled true
spark.sql.adaptive.coalescePartitions.minPartitionNum 1
spark.sql.adaptive.coalescePartitions.initialPartitionNum 200
spark.sql.adaptive.advisoryPartitionSizeInBytes 134217728
spark.sql.adaptive.skewJoin.enabled true
spark.sql.adaptive.localShuffleReader.enabled true

# Serialization
spark.serializer            org.apache.spark.serializer.KryoSerializer
spark.kryoserializer.buffer.max 256m
spark.kryoserializer.buffer 64k

# Network and Timeout
spark.network.timeout       600s
spark.rpc.askTimeout        600s
spark.storage.blockManagerSlaveTimeoutMs 600000
spark.shuffle.registration.timeout 600000
spark.shuffle.io.connectionTimeout 600s

# Shuffle Performance
spark.shuffle.compress      true
spark.shuffle.spill.compress true
spark.io.compression.codec  lz4

# SQL Performance
spark.sql.autoBroadcastJoinThreshold 20971520
spark.sql.broadcastTimeout 600
spark.sql.crossJoin.enabled true
spark.sql.cbo.enabled      true
spark.sql.cbo.joinReorder.enabled true

# PostgreSQL JDBC Configuration
spark.jars                  /opt/spark/jars/postgresql-42.7.3.jar,/opt/spark/jars/postgresql.jar
spark.driver.extraClassPath /opt/spark/jars/postgresql-42.7.3.jar
spark.executor.extraClassPath /opt/spark/jars/postgresql-42.7.3.jar

# Monitoring
spark.eventLog.enabled      false
spark.eventLog.dir          /opt/spark/logs
spark.ui.retainedJobs      100
spark.ui.retainedStages    100
spark.ui.retainedTasks     500
spark.worker.ui.retainedExecutors 50
spark.worker.ui.retainedDrivers 50
spark.sql.ui.retainedExecutions 50

# Dynamic Allocation (disabled by default in standalone mode)
spark.dynamicAllocation.enabled false

# Speculation (helps with stragglers)
spark.speculation          false
spark.speculation.interval 100ms
spark.speculation.multiplier 1.5
spark.speculation.quantile 0.75
EOF
    
    log_success "Spark configuration created"
}

# Create example Spark job with production patterns
create_spark_job() {
    log_info "Creating example Spark job..."
    
    cat > spark/jobs/example_spark_job.py << 'EOF'
"""
Production-ready Spark job demonstrating best practices
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sum, avg, count, max, min,
    when, isnan, isnull, 
    date_format, year, month, dayofweek
)
from pyspark.sql.types import *
import sys
import os
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkJobConfig:
    """Configuration for Spark job"""
    def __init__(self):
        self.app_name = "ExampleSparkJob"
        self.jdbc_url = f"jdbc:postgresql://postgres:5432/{os.getenv('POSTGRES_DB', 'datawarehouse')}"
        self.connection_properties = {
            "user": os.getenv('POSTGRES_USER', 'postgres'),
            "password": os.getenv('POSTGRES_PASSWORD', 'SecurePass123!'),
            "driver": "org.postgresql.Driver",
            "fetchsize": "1000",
            "batchsize": "1000",
            "rewriteBatchedStatements": "true",
            "stringtype": "unspecified"
        }
        self.spark_config = {
            "spark.sql.execution.arrow.pyspark.enabled": "true",
            "spark.sql.execution.arrow.maxRecordsPerBatch": "10000",
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true"
        }

def create_spark_session(config: SparkJobConfig) -> SparkSession:
    """Create Spark session with proper configuration"""
    try:
        builder = SparkSession.builder.appName(config.app_name)
        
        # Add JDBC driver
        builder = builder.config("spark.jars", "/opt/spark/jars/postgresql-42.7.3.jar")
        
        # Add performance configurations
        for key, value in config.spark_config.items():
            builder = builder.config(key, value)
        
        spark = builder.getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        
        logger.info(f"Spark session created: {spark.version}")
        logger.info(f"Application ID: {spark.sparkContext.applicationId}")
        
        return spark
    except Exception as e:
        logger.error(f"Failed to create Spark session: {str(e)}")
        raise

def test_jdbc_connection(spark: SparkSession, config: SparkJobConfig) -> bool:
    """Test JDBC connection to PostgreSQL"""
    try:
        # Test with a simple query
        test_query = "(SELECT 1 as test) as t"
        df = spark.read.jdbc(
            url=config.jdbc_url,
            table=test_query,
            properties=config.connection_properties
        )
        result = df.collect()[0]['test']
        logger.info(f"JDBC connection test successful: {result}")
        return True
    except Exception as e:
        logger.error(f"JDBC connection test failed: {str(e)}")
        return False

def read_postgresql_table(spark: SparkSession, config: SparkJobConfig, table_name: str):
    """Read table from PostgreSQL with partitioning for better performance"""
    try:
        # First, get row count for partitioning
        count_query = f"(SELECT COUNT(*) as cnt FROM {table_name}) as count_table"
        count_df = spark.read.jdbc(
            url=config.jdbc_url,
            table=count_query,
            properties=config.connection_properties
        )
        row_count = count_df.collect()[0]['cnt']
        logger.info(f"Table {table_name} has {row_count} rows")
        
        # Read with partitioning if table is large
        if row_count > 10000:
            # Use partitioned read for better performance
            df = spark.read.jdbc(
                url=config.jdbc_url,
                table=table_name,
                numPartitions=4,
                properties=config.connection_properties
            )
        else:
            # Simple read for small tables
            df = spark.read.jdbc(
                url=config.jdbc_url,
                table=table_name,
                properties=config.connection_properties
            )
        
        # Cache if needed for multiple operations
        df.cache()
        
        logger.info(f"Successfully read {table_name}")
        logger.info(f"Schema: {df.schema}")
        
        return df
    except Exception as e:
        logger.error(f"Failed to read table {table_name}: {str(e)}")
        raise

def perform_data_analysis(df):
    """Perform sample data analysis"""
    try:
        # Basic statistics
        logger.info("Calculating basic statistics...")
        
        # Row count
        total_rows = df.count()
        logger.info(f"Total rows: {total_rows}")
        
        # Schema analysis
        logger.info(f"Columns: {df.columns}")
        logger.info(f"Data types: {df.dtypes}")
        
        # Null value analysis
        null_counts = df.select([
            count(when(col(c).isNull(), c)).alias(c) 
            for c in df.columns
        ]).collect()[0]
        
        logger.info("Null value counts:")
        for col_name in df.columns:
            null_count = null_counts[col_name]
            if null_count > 0:
                logger.info(f"  {col_name}: {null_count} ({100*null_count/total_rows:.2f}%)")
        
        # If date columns exist, analyze date range
        date_columns = [f.name for f in df.schema.fields if isinstance(f.dataType, DateType)]
        for date_col in date_columns:
            date_stats = df.select(
                min(col(date_col)).alias('min_date'),
                max(col(date_col)).alias('max_date')
            ).collect()[0]
            logger.info(f"Date range for {date_col}: {date_stats['min_date']} to {date_stats['max_date']}")
        
        return {
            'total_rows': total_rows,
            'columns': df.columns,
            'null_counts': null_counts.asDict() if null_counts else {}
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

def write_results_to_postgresql(df, config: SparkJobConfig, table_name: str, mode: str = "append"):
    """Write DataFrame back to PostgreSQL"""
    try:
        logger.info(f"Writing results to {table_name} with mode={mode}")
        
        df.write.jdbc(
            url=config.jdbc_url,
            table=table_name,
            mode=mode,
            properties=config.connection_properties
        )
        
        logger.info(f"Successfully wrote {df.count()} rows to {table_name}")
        
    except Exception as e:
        logger.error(f"Failed to write to {table_name}: {str(e)}")
        raise

def main():
    """Main execution function"""
    start_time = datetime.now()
    logger.info(f"Starting Spark job at {start_time}")
    
    # Initialize configuration
    config = SparkJobConfig()
    
    # Create Spark session
    spark = create_spark_session(config)
    
    try:
        # Test JDBC connection
        if not test_jdbc_connection(spark, config):
            raise Exception("Cannot connect to PostgreSQL")
        
        # Read from PostgreSQL
        df = read_postgresql_table(spark, config, "marts.dim_date")
        
        # Perform analysis
        analysis_results = perform_data_analysis(df)
        
        # Example transformation: Create monthly summary
        if 'year' in df.columns and 'month' in df.columns:
            monthly_summary = df.groupBy('year', 'month').agg(
                count('*').alias('days_count'),
                sum(when(col('is_weekend') == True, 1).otherwise(0)).alias('weekend_days'),
                sum(when(col('is_weekend') == False, 1).otherwise(0)).alias('weekdays')
            ).orderBy('year', 'month')
            
            logger.info("Monthly summary:")
            monthly_summary.show(10)
            
            # Write results back (commented out to avoid creating tables in example)
            # write_results_to_postgresql(monthly_summary, config, "marts.monthly_summary", "overwrite")
        
        # Success metrics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("="*50)
        logger.info(f"Job completed successfully!")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Rows processed: {analysis_results['total_rows']}")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"Job failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        spark.stop()
        logger.info("Spark session closed")

if __name__ == "__main__":
    main()
EOF
    
    log_success "Example Spark job created"
}

# Create Spark submit script
create_spark_submit_script() {
    log_info "Creating Spark submit script..."
    
    cat > scripts/run-spark-job.sh << 'EOF'
#!/bin/bash
# Submit Spark job to cluster

set -euo pipefail

# Default job
JOB_FILE=${1:-"spark/jobs/example_spark_job.py"}

if [[ ! -f "$JOB_FILE" ]]; then
    echo "❌ Job file not found: $JOB_FILE"
    echo "Usage: $0 [job_file.py]"
    exit 1
fi

echo "🚀 Submitting Spark job: $JOB_FILE"

# Load environment
source .env

# Check if Spark master is running
if ! docker ps | grep -q spark_master; then
    echo "❌ Spark master is not running"
    echo "Start it with: docker-compose up -d spark-master spark-worker"
    exit 1
fi

# Submit job
docker exec spark_master spark-submit \
    --master spark://spark-master:7077 \
    --deploy-mode client \
    --driver-memory 1g \
    --executor-memory 2g \
    --executor-cores 2 \
    --num-executors 1 \
    --conf spark.sql.execution.arrow.pyspark.enabled=true \
    --conf spark.sql.adaptive.enabled=true \
    --jars /opt/spark/jars/postgresql-42.7.3.jar \
    "/opt/$(basename $JOB_FILE)"

echo "✅ Spark job completed"
EOF
    
    chmod +x scripts/run-spark-job.sh
    log_success "Spark submit script created"
}

# Validate Spark setup
validate_spark_setup() {
    log_info "Validating Spark setup..."
    
    local errors=0
    local warnings=0
    
    # CRITICAL: Check JDBC driver
    local jdbc_file="spark/jars/postgresql-42.7.3.jar"
    if [[ ! -f "$jdbc_file" ]]; then
        log_error "CRITICAL: PostgreSQL JDBC driver not found at $jdbc_file"
        log_error "Spark will NOT be able to connect to PostgreSQL!"
        ((errors++))
    else
        local file_size=$(stat -f%z "$jdbc_file" 2>/dev/null || stat -c%s "$jdbc_file" 2>/dev/null || echo "0")
        if [[ $file_size -lt 1000000 ]]; then
            log_error "JDBC driver appears corrupted (size: $file_size bytes)"
            ((errors++))
        else
            log_success "JDBC driver present and valid ($(ls -lh $jdbc_file | awk '{print $5}'))"
        fi
    fi
    
    # Check Spark configuration
    if [[ ! -f "spark/conf/spark-defaults.conf" ]]; then
        log_warning "Spark configuration not found"
        ((warnings++))
    fi
    
    # Check example job
    if [[ ! -f "spark/jobs/example_spark_job.py" ]]; then
        log_warning "Example Spark job not found"
        ((warnings++))
    else
        # Validate Python syntax
        if command_exists python3; then
            python3 -m py_compile spark/jobs/example_spark_job.py 2>/dev/null || {
                log_error "Example Spark job has Python syntax errors"
                ((errors++))
            }
        fi
    fi
    
    # Check submit script
    if [[ ! -x "scripts/run-spark-job.sh" ]]; then
        log_warning "Spark submit script not executable"
        ((warnings++))
    fi
    
    # Final verdict
    if [[ $errors -eq 0 ]]; then
        if [[ $warnings -eq 0 ]]; then
            log_success "Spark setup validation passed perfectly"
        else
            log_success "Spark setup validation passed with $warnings warnings"
        fi
        return 0
    else
        log_error "Spark setup validation FAILED with $errors critical errors"
        log_error "Fix these issues or Spark jobs will fail!"
        return 1
    fi
}

# Main execution
main() {
    # CRITICAL: Download JDBC driver first
    if ! download_jdbc_driver; then
        log_error "Failed to download JDBC driver - this is critical!"
        log_error "Continuing setup but Spark WILL NOT work properly"
        # Don't exit, let user fix manually
    fi
    
    create_spark_config
    create_spark_job
    create_spark_submit_script
    validate_spark_setup
}

main
```

### 📁 **modules/06_jupyter.sh** (Jupyter Setup)
```bash
#!/bin/bash
# Module: Jupyter Setup - Notebooks and examples

source "$SCRIPT_DIR/lib/common.sh"

log_section "Jupyter Setup Module"

# Create example notebook
create_example_notebook() {
    log_info "Creating example Jupyter notebook..."
    
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
    "import matplotlib.pyplot as plt\n",
    "import os\n",
    "\n",
    "# Database connection\n",
    "db_user = os.getenv('POSTGRES_USER', 'postgres')\n",
    "db_password = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')\n",
    "db_host = os.getenv('POSTGRES_HOST', 'postgres')\n",
    "db_port = os.getenv('POSTGRES_PORT', '5432')\n",
    "db_name = os.getenv('POSTGRES_DB', 'datawarehouse')\n",
    "\n",
    "engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')\n",
    "\n",
    "# Test connection\n",
    "with engine.connect() as conn:\n",
    "    result = conn.execute(\"SELECT version()\")\n",
    "    print(\"PostgreSQL version:\")\n",
    "    print(result.fetchone()[0])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Query data\n",
    "query = \"\"\"\n",
    "SELECT \n",
    "    date_actual,\n",
    "    year,\n",
    "    month,\n",
    "    day_name,\n",
    "    is_weekend\n",
    "FROM marts.dim_date\n",
    "WHERE year = 2024\n",
    "LIMIT 10\n",
    "\"\"\"\n",
    "\n",
    "df = pd.read_sql(query, engine)\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# PySpark integration\n",
    "from pyspark.sql import SparkSession\n",
    "\n",
    "spark = SparkSession.builder \\\n",
    "    .appName(\"JupyterNotebook\") \\\n",
    "    .config(\"spark.master\", \"spark://spark-master:7077\") \\\n",
    "    .getOrCreate()\n",
    "\n",
    "print(f\"Spark version: {spark.version}\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.10.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF
    
    log_success "Example notebook created"
}

# Main execution
main() {
    create_example_notebook
}

main
```

### 📁 **modules/07_dbt.sh** (dbt Setup)
```bash
#!/bin/bash
# Module: dbt Setup - Project structure and configuration

source "$SCRIPT_DIR/lib/common.sh"

log_section "dbt Setup Module"

# Create dbt project configuration
create_dbt_project() {
    log_info "Creating dbt project configuration..."
    
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
      +schema: staging
    marts:
      +materialized: table
      +schema: marts
EOF
    
    log_success "dbt project configuration created"
}

# Create dbt profiles
create_dbt_profiles() {
    log_info "Creating dbt profiles..."
    
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
    
    log_success "dbt profiles created"
}

# Main execution
main() {
    create_dbt_project
    create_dbt_profiles
}

main
```

### 📁 **modules/08_monitoring.sh** (Monitoring Setup)
```bash
#!/bin/bash
# Module: Monitoring Setup - pgAdmin and monitoring tools

source "$SCRIPT_DIR/lib/common.sh"

log_section "Monitoring Setup Module"

# Create pgAdmin configuration
create_pgadmin_config() {
    log_info "Creating pgAdmin configuration..."
    
    # Load environment variables
    source .env
    
    cat > docker/pgadmin/servers.json << EOF
{
  "Servers": {
    "1": {
      "Name": "PostgreSQL Analytics",
      "Group": "Data Warehouse",
      "Host": "postgres",
      "Port": 5432,
      "MaintenanceDB": "${POSTGRES_DB}",
      "Username": "${POSTGRES_USER}",
      "SSLMode": "prefer"
    },
    "2": {
      "Name": "Airflow Metadata",
      "Group": "Platform Services",
      "Host": "postgres-airflow",
      "Port": 5432,
      "MaintenanceDB": "airflow",
      "Username": "airflow",
      "SSLMode": "prefer"
    }
  }
}
EOF
    
    # Create pgpass for auto-login
    cat > docker/pgadmin/pgpass << EOF
postgres:5432:*:${POSTGRES_USER}:${POSTGRES_PASSWORD}
postgres-airflow:5432:*:airflow:${AIRFLOW_DB_PASSWORD}
EOF
    chmod 600 docker/pgadmin/pgpass
    
    log_success "pgAdmin configuration created"
}

# Create health check script
create_health_check() {
    log_info "Creating health check script..."
    
    cat > scripts/health-check.sh << 'EOF'
#!/bin/bash
# Platform health check

echo "🏥 Data Engineering Platform Health Check"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Docker
echo "🐳 Docker Status:"
if docker info > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Docker is running${NC}"
else
    echo -e "  ${RED}❌ Docker is not running${NC}"
    exit 1
fi

# Docker Compose wrapper function
docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

# Check services
echo ""
echo "📦 Service Status:"
services=("postgres" "postgres-airflow" "airflow-webserver" "airflow-scheduler" "spark-master" "spark-worker" "jupyter" "pgadmin")

for service in "${services[@]}"; do
    if docker_compose ps | grep -q "$service.*Up"; then
        echo -e "  ${GREEN}✅ $service is running${NC}"
    else
        echo -e "  ${RED}❌ $service is not running${NC}"
    fi
done

# Check connections
echo ""
echo "🔌 Connection Tests:"

if docker exec postgres_dw pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ PostgreSQL is accepting connections${NC}"
else
    echo -e "  ${RED}❌ PostgreSQL is not accepting connections${NC}"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health | grep -q "200"; then
    echo -e "  ${GREEN}✅ Airflow is healthy${NC}"
else
    echo -e "  ${YELLOW}⚠️  Airflow is not responding${NC}"
fi

echo ""
echo "✅ Health check complete"
EOF
    
    chmod +x scripts/health-check.sh
    log_success "Health check script created"
}

# Create production health check script
create_production_health_check() {
    log_info "Creating production health check script..."
    
    cat > scripts/production-health-check.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🏥 Production Health Check"
echo "=========================="

WARNINGS=0
ERRORS=0

# Check disk space
DISK_USAGE=$(df /var/lib/docker 2>/dev/null | tail -1 | awk '{print $5}' | sed 's/%//' || echo "0")
if [ "$DISK_USAGE" -gt 80 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Disk usage is ${DISK_USAGE}%${NC}"
    ((WARNINGS++))
elif [ "$DISK_USAGE" -gt 90 ]; then
    echo -e "${RED}❌ CRITICAL: Disk usage is ${DISK_USAGE}%${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✅ Disk usage: ${DISK_USAGE}%${NC}"
fi

# Check memory
MEM_AVAILABLE=$(free -m 2>/dev/null | grep "^Mem" | awk '{print $7}' || echo "999999")
if [ "$MEM_AVAILABLE" -lt 500 ]; then
    echo -e "${RED}❌ CRITICAL: Only ${MEM_AVAILABLE}MB memory available${NC}"
    ((ERRORS++))
elif [ "$MEM_AVAILABLE" -lt 1000 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Only ${MEM_AVAILABLE}MB memory available${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✅ Memory available: ${MEM_AVAILABLE}MB${NC}"
fi

# Check container health
echo ""
echo "Container Health Status:"
for container in $(docker ps --format "{{.Names}}"); do
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "none")
    STATUS=$(docker inspect --format='{{.State.Status}}' $container 2>/dev/null || echo "unknown")
    
    if [ "$HEALTH" = "unhealthy" ]; then
        echo -e "  ${RED}❌ $container is unhealthy${NC}"
        ((ERRORS++))
    elif [ "$STATUS" != "running" ]; then
        echo -e "  ${RED}❌ $container is not running (status: $STATUS)${NC}"
        ((ERRORS++))
    elif [ "$HEALTH" = "healthy" ]; then
        echo -e "  ${GREEN}✅ $container is healthy${NC}"
    else
        echo -e "  ${GREEN}✅ $container is running${NC}"
    fi
done

# Check database connections
echo ""
echo "Database Connection Pool:"
if docker exec postgres_dw psql -U postgres -t -c "SELECT 1;" &>/dev/null; then
    CONN_COUNT=$(docker exec postgres_dw psql -U postgres -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | tr -d ' ')
    MAX_CONN=$(docker exec postgres_dw psql -U postgres -t -c "SHOW max_connections;" 2>/dev/null | tr -d ' ')
    CONN_PERCENT=$((CONN_COUNT * 100 / MAX_CONN))
    
    if [ "$CONN_PERCENT" -gt 80 ]; then
        echo -e "  ${YELLOW}⚠️  WARNING: Database connections at ${CONN_PERCENT}% (${CONN_COUNT}/${MAX_CONN})${NC}"
        ((WARNINGS++))
    else
        echo -e "  ${GREEN}✅ Database connections: ${CONN_COUNT}/${MAX_CONN} (${CONN_PERCENT}%)${NC}"
    fi
else
    echo -e "  ${RED}❌ Cannot connect to database${NC}"
    ((ERRORS++))
fi

# Check Airflow DAG status
echo ""
echo "Airflow Status:"
if docker exec airflow_scheduler airflow dags list &>/dev/null; then
    FAILED_DAGS=$(docker exec airflow_scheduler airflow dags list-runs -d failed 2>/dev/null | grep -c "failed" || echo "0")
    if [ "$FAILED_DAGS" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠️  WARNING: ${FAILED_DAGS} failed DAG runs${NC}"
        ((WARNINGS++))
    else
        echo -e "  ${GREEN}✅ No failed DAG runs${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  Airflow scheduler not accessible${NC}"
fi

# Summary
echo ""
echo "Summary:"
echo "========"
if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}❌ CRITICAL: ${ERRORS} error(s) found${NC}"
    exit 2
elif [ "$WARNINGS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: ${WARNINGS} warning(s) found${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All systems operational${NC}"
    exit 0
fi
EOF
    
    chmod +x scripts/production-health-check.sh
    log_success "Production health check script created"
}

# Main execution
main() {
    create_pgadmin_config
    create_health_check
    create_production_health_check
}

main
```

### 📁 **modules/09_utilities.sh** (Utility Scripts)
```bash
#!/bin/bash
# Module: Utilities - Management scripts

source "$SCRIPT_DIR/lib/common.sh"

log_section "Utilities Module"

# Create start script
create_start_script() {
    cat > scripts/start.sh << 'EOF'
#!/bin/bash

# Docker Compose wrapper function
docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

echo "🚀 Starting Data Engineering Platform..."
docker_compose up -d
echo "✅ Services starting..."
echo ""
echo "📊 Access URLs:"
echo "  • Airflow: http://localhost:8080"
echo "  • pgAdmin: http://localhost:8081"
echo "  • Jupyter: http://localhost:8888"
echo "  • Spark UI: http://localhost:8082"
EOF
    chmod +x scripts/start.sh
}

# Create stop script
create_stop_script() {
    cat > scripts/stop.sh << 'EOF'
#!/bin/bash

# Docker Compose wrapper function
docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

echo "🛑 Stopping Data Engineering Platform..."
docker_compose down
echo "✅ All services stopped"
EOF
    chmod +x scripts/stop.sh
}

# Create status script
create_status_script() {
    cat > scripts/status.sh << 'EOF'
#!/bin/bash

# Docker Compose wrapper function
docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

echo "📊 Data Engineering Platform Status:"
echo "===================================="
docker_compose ps
EOF
    chmod +x scripts/status.sh
}

# Create logs script
create_logs_script() {
    cat > scripts/logs.sh << 'EOF'
#!/bin/bash

# Docker Compose wrapper function
docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

SERVICE=${1:-}
if [ -z "$SERVICE" ]; then
    echo "📋 Available services:"
    docker_compose ps --services
    echo ""
    echo "Usage: ./scripts/logs.sh [service_name]"
else
    echo "📋 Showing logs for $SERVICE..."
    docker_compose logs -f --tail=100 $SERVICE
fi
EOF
    chmod +x scripts/logs.sh
}

# Create backup script
create_backup_script() {
    cat > scripts/backup.sh << 'EOF'
#!/bin/bash
set -euo pipefail  # Exit on error, undefined variables, pipe failures

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="${POSTGRES_DB:-datawarehouse}"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "🔄 Starting backup..."

# Create backup with error handling
if docker exec postgres_dw pg_dump \
    -U postgres \
    -d $DB_NAME \
    -F custom \
    -f /tmp/backup_$TIMESTAMP.dump 2>/dev/null; then
    
    # Copy from container
    if docker cp postgres_dw:/tmp/backup_$TIMESTAMP.dump $BACKUP_DIR/; then
        # Clean up container temp file
        docker exec postgres_dw rm /tmp/backup_$TIMESTAMP.dump
        
        # Compress with keep original flag
        if gzip -k $BACKUP_DIR/backup_$TIMESTAMP.dump 2>/dev/null; then
            # Remove uncompressed only after successful compression
            rm $BACKUP_DIR/backup_$TIMESTAMP.dump
            echo "✅ Backup completed: $BACKUP_DIR/backup_$TIMESTAMP.dump.gz"
            
            # Verify backup file
            if [[ -f "$BACKUP_DIR/backup_$TIMESTAMP.dump.gz" ]]; then
                SIZE=$(ls -lh "$BACKUP_DIR/backup_$TIMESTAMP.dump.gz" | awk '{print $5}')
                echo "📦 Backup size: $SIZE"
            fi
        else
            echo "⚠️  Compression failed, keeping uncompressed backup"
            echo "✅ Backup completed: $BACKUP_DIR/backup_$TIMESTAMP.dump"
        fi
    else
        echo "❌ Failed to copy backup from container"
        exit 1
    fi
else
    echo "❌ Database backup failed"
    echo "Debug: Check if postgres_dw container is running"
    docker ps | grep postgres_dw
    exit 1
fi

# Cleanup old backups (keep last 7)
echo "🧹 Cleaning old backups..."
cd $BACKUP_DIR && ls -t backup_*.dump.gz 2>/dev/null | tail -n +8 | xargs -r rm
cd - > /dev/null
echo "✅ Backup maintenance complete"
EOF
    chmod +x scripts/backup.sh
}

# Create volume backup script
create_volume_backup_script() {
    cat > scripts/backup-volumes.sh << 'EOF'
#!/bin/bash
# Backup all Docker volumes

BACKUP_DIR="./backups/volumes"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "🔄 Starting volume backup..."

# Function to use docker_compose
docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

# Stop services
echo "Stopping services..."
docker_compose down

# Backup volumes
for volume in postgres_data postgres_airflow_data pgadmin_data spark_logs; do
    echo "Backing up volume: $volume"
    docker run --rm \
        -v ${PWD}/docker/volumes/${volume}:/source:ro \
        -v ${PWD}/${BACKUP_DIR}:/backup \
        alpine tar czf /backup/${volume}_${TIMESTAMP}.tar.gz -C /source .
done

echo "✅ Volume backup completed: $BACKUP_DIR/*_${TIMESTAMP}.tar.gz"
echo "Starting services..."
docker_compose up -d
EOF
    chmod +x scripts/backup-volumes.sh
}

# Create volume restore script
create_volume_restore_script() {
    cat > scripts/restore-volumes.sh << 'EOF'
#!/bin/bash
# Restore Docker volumes from backup

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_timestamp>"
    echo "Available backups:"
    ls -la backups/volumes/*.tar.gz 2>/dev/null | awk '{print $9}' | sed 's/.*_\([0-9]*\)\.tar\.gz/\1/' | sort -u
    exit 1
fi

TIMESTAMP=$1
BACKUP_DIR="./backups/volumes"

# Function to use docker_compose
docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

echo "🔄 Restoring volumes from timestamp: $TIMESTAMP"

# Stop services
docker_compose down

# Restore volumes
for volume in postgres_data postgres_airflow_data pgadmin_data spark_logs; do
    if [ -f "${BACKUP_DIR}/${volume}_${TIMESTAMP}.tar.gz" ]; then
        echo "Restoring volume: $volume"
        # Clear existing data
        rm -rf ${PWD}/docker/volumes/${volume}/*
        # Extract backup
        docker run --rm \
            -v ${PWD}/docker/volumes/${volume}:/target \
            -v ${PWD}/${BACKUP_DIR}:/backup:ro \
            alpine tar xzf /backup/${volume}_${TIMESTAMP}.tar.gz -C /target
    fi
done

echo "✅ Volume restore completed"
echo "Starting services..."
docker_compose up -d
EOF
    chmod +x scripts/restore-volumes.sh
}

# Main execution
main() {
    log_info "Creating utility scripts..."
    create_start_script
    create_stop_script
    create_status_script
    create_logs_script
    create_backup_script
    create_volume_backup_script
    create_volume_restore_script
    log_success "All utility scripts created"
}

main
```

### 📁 **modules/10_development.sh** (Development Setup)
```bash
#!/bin/bash
# Module: Development Setup - VS Code, documentation, README

source "$SCRIPT_DIR/lib/common.sh"

log_section "Development Setup Module"

# Create VS Code settings
create_vscode_settings() {
    log_info "Creating VS Code configuration..."
    
    cat > .vscode/settings.json << 'EOF'
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  
  "files.associations": {
    "*.sql": "sql",
    "*.yml": "yaml",
    "*.yaml": "yaml",
    "Dockerfile*": "dockerfile"
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
  ]
}
EOF
    
    cat > .vscode/extensions.json << 'EOF'
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-toolsai.jupyter",
    "mtxr.sqltools",
    "ms-azuretools.vscode-docker",
    "redhat.vscode-yaml"
  ]
}
EOF
    
    log_success "VS Code configuration created"
}

# Create README
create_readme() {
    log_info "Creating README.md..."
    
    cat > README.md << 'EOF'
# Data Engineering Platform v2.0

A production-ready, modular data engineering platform.

## 🚀 Quick Start

```bash
# Run setup
./setup.sh

# Start services
./scripts/start.sh

# Check status
./scripts/status.sh
```

## 📊 Services

- **PostgreSQL**: Data warehouse (port 5432)
- **Airflow**: Workflow orchestration (port 8080)
- **Spark**: Distributed computing (port 8082)
- **Jupyter**: Interactive notebooks (port 8888)
- **pgAdmin**: Database management (port 8081)

## 📁 Project Structure

```
├── setup.sh            # Main setup script
├── config/            # Configuration files
├── lib/               # Shared functions
├── modules/           # Setup modules
├── airflow/           # Airflow DAGs
├── spark/             # Spark jobs
├── notebooks/         # Jupyter notebooks
├── dbt/              # dbt models
├── scripts/          # Management scripts
└── data/             # Data storage
```

## 🛠️ Management

```bash
# Start/stop services
./scripts/start.sh
./scripts/stop.sh

# View logs
./scripts/logs.sh [service]

# Health check
./scripts/health-check.sh

# Backup
./scripts/backup.sh
```

## 🔐 Default Credentials

- **Airflow**: admin/SecurePass123!
- **pgAdmin**: admin@admin.com/admin
- **Jupyter**: token = SecurePass123!
- **PostgreSQL**: postgres/SecurePass123!

## 📚 Documentation

See the `docs/` directory for detailed documentation.
EOF
    
    log_success "README.md created"
}

# Main execution
main() {
    create_vscode_settings
    create_readme
}

main
```

## 📝 Usage Instructions

1. **Save all files** in the structure shown above
2. **Make the main script executable**: `chmod +x setup.sh`
3. **Run the setup**: `./setup.sh`
4. **Optional: Interactive mode**: `./setup.sh --interactive`
5. **Optional: Skip modules**: `./setup.sh --skip jupyter,dbt`
6. **Optional: Only specific modules**: `./setup.sh --only core,docker`

The modular approach allows you to:
- Maintain and update individual components easily
- Debug specific modules independently
- Customize the installation process
- Share modules across projects
- Version control individual components

Each module is self-contained and can be run independently if needed.
