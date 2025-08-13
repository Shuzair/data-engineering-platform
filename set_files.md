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

source "$SCRIPT_DIR/lib/common.sh"

log_section "Core Setup Module"

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."
    
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
        "backups"
        "scripts"
        "tests/unit"
        "tests/integration"
        "logs"
        ".vscode"
        ".github/workflows"
        "docs"
        "docker/volumes/postgres_data"
        "docker/volumes/postgres_airflow_data"
        "docker/volumes/pgadmin_data"
        "docker/volumes/spark_logs"
    )
    
    for dir in "${directories[@]}"; do
        create_directory "$dir"
    done
    
    # Create .gitkeep files
    find . -type d -empty -exec touch {}/.gitkeep \; 2>/dev/null
    
    log_success "Directory structure created"
}

# Create .gitignore
create_gitignore() {
    log_info "Creating .gitignore..."
    
    cat > .gitignore << 'EOF'
# Data directories
data/raw/*
data/processed/*
data/archive/*
!data/**/.gitkeep

# Backup files
backups/*.dump
backups/*.sql
backups/*.tar.gz
!backups/.gitkeep

# Environment files
.env
.env.local
.platform_passwords
*.env

# Airflow
airflow/logs/*
airflow/airflow.db
airflow/*.cfg
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
spark/logs/*
spark/metastore_db/
spark/spark-warehouse/
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
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
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
    
    log_success ".gitignore created"
}

# Initialize git repository
init_git() {
    if [[ ! -d .git ]]; then
        log_info "Initializing git repository..."
        git init
        git add .gitignore
        git commit -m "Initial commit: Data Engineering Platform v2.0" 2>/dev/null || true
        log_success "Git repository initialized"
    else
        log_info "Git repository already exists"
    fi
}

# Main execution
main() {
    create_directories
    create_gitignore
    init_git
}

main
```

### 📁 **modules/02_docker.sh** (Docker Setup)
```bash
#!/bin/bash
# Module: Docker Setup - Docker Compose and environment configuration

source "$SCRIPT_DIR/lib/common.sh"

log_section "Docker Setup Module"

# Generate .env file
generate_env_file() {
    log_info "Generating .env file..."
    
	# Load or generate passwords
    load_or_generate_passwords
    
    # Get values from configuration or use generated passwords
    local postgres_password="${POSTGRES_PASSWORD}"
    local airflow_db_password="${AIRFLOW_DB_PASSWORD}"
    local airflow_admin_user=$(get_config "security.airflow_admin_user" "admin")
    local airflow_admin_password="${AIRFLOW_ADMIN_PASSWORD}"
    local jupyter_token="${JUPYTER_TOKEN}"
    local pgadmin_email=$(get_config "security.pgadmin_email" "admin@admin.com")
    local pgadmin_password="${PGADMIN_PASSWORD}"
    
    # Generate keys
    local fernet_key=$(generate_fernet_key)
    local secret_key=$(openssl rand -hex 32)
    
    cat > .env << EOF
# Generated by Data Engineering Platform Setup
# Date: $(date)

# Platform
PLATFORM_NAME=$(get_config "platform.name" "data-engineering-platform")
PLATFORM_VERSION=$(get_config "platform.version" "2.0.0")
PLATFORM_ENV=$(get_config "platform.environment" "development")

# Versions
POSTGRES_VERSION=$(get_config "versions.postgresql" "15.4-alpine")
AIRFLOW_VERSION=$(get_config "versions.airflow" "2.8.1-python3.10")
SPARK_VERSION=$(get_config "versions.spark" "3.5.1")
JUPYTER_VERSION=$(get_config "versions.jupyter" "spark-3.5.1")
PGADMIN_VERSION=$(get_config "versions.pgadmin" "8.2")

# PostgreSQL
POSTGRES_USER=$(get_config "database.user" "postgres")
POSTGRES_PASSWORD=${postgres_password}
POSTGRES_DB=$(get_config "database.name" "datawarehouse")

# Airflow
AIRFLOW_UID=$(id -u)
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

# Resource Limits
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
JUPYTER_MEMORY=$(get_config "resources.jupyter.memory" "2G")
JUPYTER_CPUS=$(get_config "resources.jupyter.cpus" "1.0")
PGADMIN_MEMORY=$(get_config "resources.pgadmin.memory" "512M")
PGADMIN_CPUS=$(get_config "resources.pgadmin.cpus" "0.5")

# Features
ENABLE_EXAMPLE_DAGS=$(get_config "features.enable_example_dags" "true")
EOF
    
    log_success ".env file generated"
}

# Create docker-compose.yml
create_docker_compose() {
    log_info "Creating docker-compose.yml..."
    
    cat > docker-compose.yml << 'EOF'
version: '2.4'

x-airflow-common: &airflow-common
  image: apache/airflow:${AIRFLOW_VERSION:-2.8.1-python3.10}
  environment: &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:${AIRFLOW_DB_PASSWORD}@postgres-airflow:5432/airflow
    AIRFLOW__CORE__FERNET_KEY: ${AIRFLOW_FERNET_KEY}
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: '${ENABLE_EXAMPLE_DAGS:-false}'
    AIRFLOW__WEBSERVER__RBAC: 'true'
    PYTHONPATH: '/opt/airflow/dags:/opt/dbt'
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
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on:
    postgres-airflow:
      condition: service_healthy
    postgres:
      condition: service_healthy
  networks:
    - data_network

services:
  postgres:
    image: postgres:${POSTGRES_VERSION:-15.4-alpine}
    container_name: postgres_dw
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-datawarehouse}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/postgresql.conf:/etc/postgresql/postgresql.conf:ro
      - ./docker/postgres/init:/docker-entrypoint-initdb.d:ro
      - ./sql:/sql:ro
      - ./data:/data
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
    networks:
      - data_network
    mem_limit: ${POSTGRES_MEMORY:-2G}
    cpus: ${POSTGRES_CPUS:-1.0}
    restart: unless-stopped

  postgres-airflow:
    image: postgres:${POSTGRES_VERSION:-15.4-alpine}
    container_name: postgres_airflow
    environment:
      POSTGRES_DB: airflow
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: ${AIRFLOW_DB_PASSWORD}
    volumes:
      - postgres_airflow_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U airflow -d airflow"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - data_network
    mem_limit: ${POSTGRES_AIRFLOW_MEMORY:-1G}
    cpus: ${POSTGRES_AIRFLOW_CPUS:-0.5}
    restart: unless-stopped

  pgadmin:
    image: dpage/pgadmin4:${PGADMIN_VERSION:-8.2}
    container_name: pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_DEFAULT_EMAIL:-admin@admin.com}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_DEFAULT_PASSWORD:-admin}
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    ports:
      - "${PORT_PGADMIN:-8081}:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
      - ./docker/pgadmin/servers.json:/pgadmin4/servers.json:ro
    depends_on:
      - postgres
    networks:
      - data_network
    deploy:
      resources:
        limits:
          memory: ${PGADMIN_MEMORY:-512M}
          cpus: '${PGADMIN_CPUS:-0.5}'
    restart: unless-stopped

  airflow-webserver:
    <<: *airflow-common
    container_name: airflow_webserver
    command: webserver
    ports:
      - "${PORT_AIRFLOW:-8080}:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: always
    deploy:
      resources:
        limits:
          memory: ${AIRFLOW_WEBSERVER_MEMORY:-2G}
          cpus: '${AIRFLOW_WEBSERVER_CPUS:-1.0}'

  airflow-scheduler:
    <<: *airflow-common
    container_name: airflow_scheduler
    command: scheduler
    healthcheck:
      test: ["CMD-SHELL", 'airflow jobs check --job-type SchedulerJob --hostname "$${HOSTNAME}"']
      interval: 30s
      timeout: 10s
      retries: 5
    restart: always
    deploy:
      resources:
        limits:
          memory: ${AIRFLOW_SCHEDULER_MEMORY:-2G}
          cpus: '${AIRFLOW_SCHEDULER_CPUS:-1.0}'

  airflow-init:
    <<: *airflow-common
    container_name: airflow_init
    entrypoint: /bin/bash
    command:
      - -c
      - |
        function ver() {
          printf "%04d%04d%04d%04d" $${1//./ }
        }
        airflow_version=$$(AIRFLOW__LOGGING__LOGGING_LEVEL=ERROR airflow version)
        airflow_version_comparable=$$(ver $${airflow_version})
        min_airflow_version=2.2.0
        min_airflow_version_comparable=$$(ver $${min_airflow_version})
        if (( airflow_version_comparable < min_airflow_version_comparable )); then
          echo "ERROR: Airflow version $${airflow_version} is less than $${min_airflow_version}"
          exit 1
        fi
        if [[ -z "${AIRFLOW_UID}" ]]; then
          echo "ERROR: AIRFLOW_UID not set"
          exit 1
        fi
        one_meg=1048576
        mem_available=$$(($$(getconf _PHYS_PAGES) * $$(getconf PAGE_SIZE) / one_meg))
        cpus_available=$$(grep -cE 'cpu[0-9]+' /proc/stat)
        disk_available=$$(df / | tail -1 | awk '{print $$4}')
        warning_resources="false"
        if (( mem_available < 4000 )) ; then
          echo "WARNING: Docker memory should be at least 4GB, currently $${mem_available}MB"
          warning_resources="true"
        fi
        if (( cpus_available < 2 )); then
          echo "WARNING: Docker CPUs should be at least 2, currently $${cpus_available}"
          warning_resources="true"
        fi
        if (( disk_available < one_meg * 10 )); then
          echo "WARNING: Docker disk should be at least 10GB free"
          warning_resources="true"
        fi
        if [[ $${warning_resources} == "true" ]]; then
          echo "WARNING: You have low resources"
        fi
        mkdir -p /sources/logs /sources/dags /sources/plugins
        chown -R "${AIRFLOW_UID}:0" /sources/{logs,dags,plugins}
        exec /entrypoint airflow version
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_UPGRADE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-admin}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-admin}
      _PIP_ADDITIONAL_REQUIREMENTS: ''
    user: "0:0"
    volumes:
      - ./airflow:/sources
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_UPGRADE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-admin}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-admin}
    user: "0:0"
    restart: "no"

  spark-master:
    image: bitnami/spark:${SPARK_VERSION:-3.5.1}
    container_name: spark_master
    environment:
      - SPARK_MODE=master
      - SPARK_MASTER_HOST=spark-master
      - SPARK_MASTER_PORT=7077
      - SPARK_MASTER_WEBUI_PORT=8080
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
      test: ["CMD", "curl", "-f", "http://localhost:8080"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - data_network
    deploy:
      resources:
        limits:
          memory: ${SPARK_MASTER_MEMORY:-2G}
          cpus: '${SPARK_MASTER_CPUS:-1.0}'
    restart: unless-stopped

  spark-worker:
    image: bitnami/spark:${SPARK_VERSION:-3.5.1}
    container_name: spark_worker
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=${SPARK_WORKER_MEMORY:-4g}
      - SPARK_WORKER_CORES=${SPARK_WORKER_CORES:-2}
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
      - spark-master
    networks:
      - data_network
    deploy:
      resources:
        limits:
          memory: ${SPARK_WORKER_MEMORY:-4G}
          cpus: '${SPARK_WORKER_CPUS:-2.0}'
    restart: unless-stopped

  jupyter:
    image: jupyter/pyspark-notebook:${JUPYTER_VERSION:-spark-3.5.1}
    container_name: jupyter_pyspark
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - SPARK_MASTER=spark://spark-master:7077
      - JUPYTER_TOKEN=${JUPYTER_TOKEN:-development}
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
      - data_network
    depends_on:
      - spark-master
      - postgres
    deploy:
      resources:
        limits:
          memory: ${JUPYTER_MEMORY:-2G}
          cpus: '${JUPYTER_CPUS:-1.0}'
    restart: unless-stopped

networks:
  data_network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.20.0.0/16
    driver_opts:
      com.docker.network.bridge.name: data_platform_bridge
      com.docker.network.bridge.enable_ip_masquerade: "true"
      com.docker.network.bridge.enable_icc: "true"
      com.docker.network.bridge.host_binding_ipv4: "0.0.0.0"

volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      device: ${PWD}/docker/volumes/postgres_data
      o: bind
  postgres_airflow_data:
    driver: local
    driver_opts:
      type: none
      device: ${PWD}/docker/volumes/postgres_airflow_data
      o: bind
  pgadmin_data:
    driver: local
    driver_opts:
      type: none
      device: ${PWD}/docker/volumes/pgadmin_data
      o: bind
  spark_logs:
    driver: local
    driver_opts:
      type: none
      device: ${PWD}/docker/volumes/spark_logs
      o: bind
  airflow_logs:
    driver: local
    driver_opts:
      type: none
      device: ${PWD}/airflow/logs
      o: bind
EOF
    
    log_success "docker-compose.yml created"
}

# Main execution
main() {
    generate_env_file
    create_docker_compose
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

# Connections
max_connections = 100

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

source "$SCRIPT_DIR/lib/common.sh"

log_section "Airflow Setup Module"

# Create example DAG
create_example_dag() {
    log_info "Creating example Airflow DAG..."
    
    cat > airflow/dags/example_pipeline.py << 'EOF'
"""
Example data pipeline demonstrating platform capabilities
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def check_database_connection(**context):
    """Test database connectivity"""
    hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()[0]
    print(f"Connected to: {db_version}")
    return "Database connection successful"

def generate_sample_data(**context):
    """Generate sample data for testing"""
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    data = {
        'date': dates,
        'sales': np.random.randint(1000, 5000, size=100),
        'customers': np.random.randint(50, 200, size=100),
        'region': np.random.choice(['North', 'South', 'East', 'West'], size=100)
    }
    df = pd.DataFrame(data)
    df.to_csv('/data/raw/sample_sales.csv', index=False)
    print(f"Generated {len(df)} records")
    return "Sample data generated"

with DAG(
    'example_pipeline',
    default_args=default_args,
    description='Example data pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'tutorial']
) as dag:
    
    check_db = PythonOperator(
        task_id='check_database',
        python_callable=check_database_connection
    )
    
    create_tables = PostgresOperator(
        task_id='create_tables',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE SCHEMA IF NOT EXISTS example;
        
        CREATE TABLE IF NOT EXISTS example.sales_data (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            sales INTEGER,
            customers INTEGER,
            region VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    
    generate_data = PythonOperator(
        task_id='generate_sample_data',
        python_callable=generate_sample_data
    )
    
    check_db >> create_tables >> generate_data
EOF
    
    log_success "Example DAG created"
}

# Create Airflow connections initialization script
create_connections_script() {
    log_info "Creating Airflow connections script..."
    
    cat > scripts/init-airflow-connections.sh << 'EOF'
#!/bin/bash
# Initialize Airflow connections

echo "🔗 Setting up Airflow connections..."

# Wait for Airflow to be ready
sleep 30

# Load environment variables
source .env

# Create PostgreSQL connection
docker exec airflow_webserver airflow connections add \
    'postgres_default' \
    --conn-type 'postgres' \
    --conn-host 'postgres' \
    --conn-schema "$POSTGRES_DB" \
    --conn-login "$POSTGRES_USER" \
    --conn-password "$POSTGRES_PASSWORD" \
    --conn-port 5432 \
    2>/dev/null || echo "Connection postgres_default already exists"

echo "✅ Airflow connections configured"
EOF
    
    chmod +x scripts/init-airflow-connections.sh
    log_success "Airflow connections script created"
}

# Set Airflow permissions
set_airflow_permissions() {
    log_info "Setting Airflow directory permissions..."
    
    # Get current user ID
    local current_uid=$(id -u)
    
    # Update .env with correct UID if needed
    if grep -q "AIRFLOW_UID=50000" .env 2>/dev/null; then
        sed -i.bak "s/AIRFLOW_UID=50000/AIRFLOW_UID=$current_uid/" .env
        log_info "Updated AIRFLOW_UID to $current_uid"
    fi
    
    # Ensure directories are writable
    chmod -R 775 airflow/ 2>/dev/null || true
}

# Main execution
main() {
    create_example_dag
    create_connections_script
    set_airflow_permissions
}

main
```

### 📁 **modules/05_spark.sh** (Spark Setup)
```bash
#!/bin/bash
# Module: Spark Setup - Configuration and example jobs

source "$SCRIPT_DIR/lib/common.sh"

log_section "Spark Setup Module"

# Download JDBC driver
download_jdbc_driver() {
    log_info "Downloading PostgreSQL JDBC driver..."
    
    local jdbc_version=$(get_config "versions.postgresql_jdbc" "42.6.0")
    local jdbc_file="spark/jars/postgresql-${jdbc_version}.jar"
    local jdbc_url="https://jdbc.postgresql.org/download/postgresql-${jdbc_version}.jar"
    
    download_file "$jdbc_url" "$jdbc_file"
}

# Create Spark configuration
create_spark_config() {
    log_info "Creating Spark configuration..."
    
    cat > spark/conf/spark-defaults.conf << 'EOF'
# Spark Configuration

spark.app.name              DataEngineeringPlatform
spark.master                spark://spark-master:7077

# Memory
spark.driver.memory         2g
spark.executor.memory       2g
spark.driver.maxResultSize  1g

# Parallelism
spark.default.parallelism   8
spark.sql.shuffle.partitions 8

# SQL
spark.sql.adaptive.enabled  true
spark.sql.adaptive.coalescePartitions.enabled true

# Serialization
spark.serializer            org.apache.spark.serializer.KryoSerializer
spark.kryoserializer.buffer.max 256m

# Network
spark.network.timeout       600s

# PostgreSQL
spark.jars                  /opt/spark/jars/postgresql-42.6.0.jar
EOF
    
    log_success "Spark configuration created"
}

# Create example Spark job
create_spark_job() {
    log_info "Creating example Spark job..."
    
    cat > spark/jobs/example_spark_job.py << 'EOF'
"""
Example Spark job demonstrating PySpark capabilities
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, count
import sys
import os

def main():
    # Create Spark session
    spark = SparkSession.builder \
        .appName("ExampleSparkJob") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("INFO")
    
    # PostgreSQL connection
    jdbc_url = f"jdbc:postgresql://postgres:5432/{os.getenv('POSTGRES_DB', 'datawarehouse')}"
    connection_properties = {
        "user": os.getenv('POSTGRES_USER', 'postgres'),
        "password": os.getenv('POSTGRES_PASSWORD', 'SecurePass123!'),
        "driver": "org.postgresql.Driver"
    }
    
    try:
        # Read from PostgreSQL
        df = spark.read.jdbc(
            url=jdbc_url,
            table="marts.dim_date",
            properties=connection_properties
        )
        
        print(f"Loaded {df.count()} records")
        df.printSchema()
        
        # Perform aggregations
        summary = df.filter(col("year") == 2024) \
            .groupBy("month") \
            .agg(count("*").alias("days_count")) \
            .orderBy("month")
        
        summary.show()
        
        print("Job completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
EOF
    
    log_success "Example Spark job created"
}

# Main execution
main() {
    download_jdbc_driver
    create_spark_config
    create_spark_job
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

# Check services
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

# Main execution
main() {
    create_pgadmin_config
    create_health_check
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
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="datawarehouse"

mkdir -p $BACKUP_DIR

echo "🔄 Starting backup..."

# Database backup
docker exec postgres_dw pg_dump \
    -U postgres \
    -d $DB_NAME \
    -F custom \
    -f /tmp/backup_$TIMESTAMP.dump

docker cp postgres_dw:/tmp/backup_$TIMESTAMP.dump $BACKUP_DIR/
docker exec postgres_dw rm /tmp/backup_$TIMESTAMP.dump

gzip $BACKUP_DIR/backup_$TIMESTAMP.dump

echo "✅ Backup completed: $BACKUP_DIR/backup_$TIMESTAMP.dump.gz"
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
