#!/bin/bash

# Ralph Agent Loop Script
# 使用说明：将此脚本复制到项目根目录，确保有执行权限

# 配置
DEFAULT_ITERATIONS=10
DEFAULT_BRANCH_PREFIX="ralph/"
DEFAULT_PRD_DIR="tasks"
DEFAULT_PROGRESS_FILE="prd-progress.txt"
DEFAULT_PRD_FILE="prd.json"

# 命令行参数
ITERATIONS=${1:-$DEFAULT_ITERATIONS}
BRANCH_PREFIX=${2:-$DEFAULT_BRANCH_PREFIX}
PRD_DIR=${3:-$DEFAULT_PRD_DIR}
PROGRESS_FILE=${4:-$DEFAULT_PROGRESS_FILE}
PRD_FILE=${5:-$DEFAULT_PRD_FILE}

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 命令未找到，请先安装"
        exit 1
    fi
}

# 初始化 Git
init_git() {
    log_info "初始化 Git..."
    
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        git init
        log_success "Git 仓库初始化完成"
    else
        log_info "Git 仓库已存在"
    fi
    
    # 检查工作区是否干净
    if [ -n "$(git status --porcelain)" ]; then
        log_warning "工作区不干净，请先提交或暂存更改"
        log_info "当前状态："
        git status --short
        read -p "是否继续？(y/n) " -n 1 -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "已取消 Ralph 运行"
            exit 0
        fi
    fi
}

# 读取 PRD
read_prd() {
    log_info "读取 PRD 文件..."
    
    if [ -f "$PRD_DIR/$PRD_FILE" ]; then
        cat "$PRD_DIR/$PRD_FILE"
    elif [ -f "$PRD_FILE" ]; then
        cat "$PRD_FILE"
    else
        log_error "PRD 文件未找到：$PRD_DIR/$PRD_FILE 或 $PRD_FILE"
        exit 1
    fi
}

# 运行 Ralph 循环
run_ralph_loop() {
    local prd_file=$1
    local max_iterations=$2
    
    log_info "启动 Ralph 循环..."
    log_info "最大迭代次数：$max_iterations"
    
    # 创建进度文件
    if [ ! -f "$PROGRESS_FILE" ]; then
        touch "$PROGRESS_FILE"
        echo "# Ralph 进度日志" > "$PROGRESS_FILE"
        echo "# 开始时间：$(date)" >> "$PROGRESS_FILE"
    fi
    
    # 迭代计数器
    local iteration=0
    local completed=0
    local total=$(echo "$prd_file" | jq '.userStories | length')
    
    # 开始循环
    while [ $iteration -lt $max_iterations ]; do
        ((iteration++))
        
        log_info "开始迭代 $iteration/$max_iterations"
        echo "---" >> "$PROGRESS_FILE"
        echo "迭代 $iteration - $(date)" >> "$PROGRESS_FILE"
        
        # 检查是否还有未完成的用户故事
        local remaining=$(echo "$prd_file" | jq '.userStories[] | select(.passes == false) | length')
        
        if [ $remaining -eq 0 ]; then
            log_success "所有用户故事已完成！"
            break
        fi
        
        # 获取下一个用户故事
        local next_story=$(echo "$prd_file" | jq -r '.userStories[] | select(.passes == false) | .[0]')
        local story_id=$(echo "$next_story" | jq -r '.id')
        local story_title=$(echo "$next_story" | jq -r '.title')
        
        log_info "处理用户故事：$story_id - $story_title"
        echo "处理用户故事：$story_id - $story_title" >> "$PROGRESS_FILE"
        
        # 模拟故事实现（实际使用时，这里会调用 Claude Code 生成代码）
        # 这里只是示例，实际使用时会调用相应的技能
        
        # 更新故事状态
        # 实际使用时，这里会：
        # 1. 调用 ai-spec skill 生成技术规范
        # 2. 调用 code-debugger skill 生成代码
        # 3. 调用其他相关技能
        
        sleep 2  # 模拟代码生成时间
        
        # 标记故事为完成（模拟）
        ((completed++))
        
        log_info "用户故事 $story_id 已完成"
        echo "用户故事 $story_id 已完成，迭代 $iteration/$max_iterations" >> "$PROGRESS_FILE"
        
        # 更新完成度
        local progress=$((completed * 100 / total))
        log_success "完成度：$progress%（$completed/$total）"
        echo "完成度：$progress%（$completed/$total）" >> "$PROGRESS_FILE"
        
        # 提交更改（模拟）
        echo "提交更改到 Git..." >> "$PROGRESS_FILE"
    done
    
    log_info "Ralph 循环完成"
    echo "---" >> "$PROGRESS_FILE"
    echo "完成时间：$(date)" >> "$PROGRESS_FILE"
}

# 创建功能分支
create_feature_branch() {
    local feature_name=$1
    local branch_name="$BRANCH_PREFIX$feature_name"
    
    log_info "创建功能分支：$branch_name"
    
    # 检查分支是否已存在
    if git show-ref --verify --quiet "$branch_name"; then
        log_warning "分支 $branch_name 已存在，将切换到该分支"
        git checkout "$branch_name"
    else
        git checkout -b "$branch_name"
        log_success "分支 $branch_name 创建成功"
    fi
}

# 提交代码
commit_changes() {
    local message=$1
    
    log_info "提交代码：$message"
    git add .
    git commit -m "$message"
}

# 主函数
main() {
    # 打印欢迎信息
    echo "======================================"
    echo "       Ralph Agent Loop System"
    echo "======================================"
    echo ""
    
    # 检查依赖
    check_command git
    check_command jq
    
    # 初始化 Git
    init_git
    
    # 读取 PRD
    local prd_content=$(read_prd)
    
    # 解析功能名称（从第一个用户故事）
    local feature_name=$(echo "$prd_content" | jq -r '.featureName // .featureSlug // .featureName')
    
    if [ -z "$feature_name" ]; then
        log_error "无法从 PRD 中提取功能名称"
        exit 1
    fi
    
    # 创建功能分支
    create_feature_branch "$feature_name"
    
    # 运行 Ralph 循环
    run_ralph_loop "$prd_content" "$ITERATIONS"
    
    # 完成信息
    echo ""
    log_success "Ralph 执行完成！"
    echo "查看详情："
    echo "  - PRD 状态：cat $PRD_FILE | jq '.userStories[] | {id, title, passes}'"
    echo "  - 进度日志：cat $PROGRESS_FILE"
    echo "  - Git 历史：git log --oneline -10"
}

# 执行主函数
main "$@"
