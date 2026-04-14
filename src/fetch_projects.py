#!/usr/bin/env python3
"""
AI Agent 项目数据抓取脚本
从 GitHub API 获取 AI Agent 相关的热门和活跃项目
"""

import json
import os
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import time

# GitHub API 配置
GITHUB_API_URL = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "AI-Agent-Tracker/1.0"
}

# 如果有 GitHub Token，可以增加 API 限制
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# AI Agent 相关关键词
AI_AGENT_KEYWORDS = [
    "agent",
    "autonomous-agent",
    "ai-agent",
    "gpt-agent",
    "claude-agent",
    "langchain",
    "autogen",
    "crewai",
    "phi-data",
    "superagent",
    "flowise",
    "llama-index",
    "dspy",
    "microsoft-autogen",
    "openai-assistant",
    "babyagi",
    "multi-agent",
    "agentic",
    "agent-framework",
    "llm-agent"
]

# 热门编程语言
LANGUAGES = ["Python", "JavaScript", "TypeScript", "Go"]


def make_request(url, retries=3):
    """发送 API 请求，带重试机制"""
    headers = HEADERS.copy()
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    for attempt in range(retries):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            if e.code == 403 and "rate limit" in str(e.read()).lower():
                print("Rate limit hit, waiting 60 seconds...")
                time.sleep(60)
            elif e.code == 429:
                print("Too many requests, waiting 60 seconds...")
                time.sleep(60)
            else:
                print(f"HTTP Error {e.code}: {e.reason}")
                if attempt == retries - 1:
                    return None
        except URLError as e:
            print(f"URL Error: {e.reason}")
            if attempt < retries - 1:
                time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            if attempt == retries - 1:
                return None
        time.sleep(2)
    return None


def search_ai_agent_repos():
    """搜索 AI Agent 相关仓库"""
    repos = []
    
    # 搜索策略1: 按热门 AI Agent 关键词搜索
    for keyword in AI_AGENT_KEYWORDS:
        print(f"Searching for: {keyword}")
        url = f"{GITHUB_API_URL}/search/repositories?q={keyword}+in:name,description,readme&sort=stars&order=desc&per_page=15"
        result = make_request(url)
        
        if result and "items" in result:
            for item in result["items"]:
                if item["full_name"] not in [r["full_name"] for r in repos]:
                    repos.append(item)
        
        time.sleep(1)  # 避免触发 rate limit
    
    # 搜索策略2: 搜索最近活跃的仓库（按更新时间排序）
    print("Searching for recently active AI agent repos...")
    for keyword in ["agent", "autonomous", "llm-agent"]:
        url = f"{GITHUB_API_URL}/search/repositories?q={keyword}+language:python&sort=updated&order=desc&per_page=10"
        result = make_request(url)
        
        if result and "items" in result:
            for item in result["items"]:
                if item["full_name"] not in [r["full_name"] for r in repos]:
                    repos.append(item)
        
        time.sleep(1)
    
    return repos


def get_repo_details(full_name):
    """获取仓库详细信息，包括每日统计变化"""
    url = f"{GITHUB_API_URL}/repos/{full_name}"
    return make_request(url)


def calculate_trend(stars, forks, issues, updated, created):
    """计算项目活跃趋势 (简单算法)"""
    now = datetime.now()
    
    # 计算项目年龄（天数）
    try:
        created_date = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
        age_days = (now - created_date).days
        if age_days < 1:
            age_days = 1
    except:
        age_days = 365
    
    # 计算每天获得的 stars 平均值
    stars_per_day = stars / age_days
    
    # 最近更新时间加权
    try:
        updated_date = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%SZ")
        days_since_update = (now - updated_date).days
    except:
        days_since_update = 30
    
    # 活跃度得分
    activity_score = stars_per_day * 10 + (30 - min(days_since_update, 30)) * 0.5 + forks * 0.1
    
    # 趋势百分比（相对于平均）
    trend = (activity_score / max(stars_per_day, 0.1) - 1) * 100
    return max(-50, min(50, trend))  # 限制在 -50% 到 +50% 之间


def process_repos(repos):
    """处理仓库数据，提取需要的信息"""
    processed = []
    
    for repo in repos:
        full_name = repo["full_name"]
        
        # 获取更详细的信息
        details = get_repo_details(full_name)
        if not details:
            details = repo
        
        stars = details.get("stargazers_count", repo.get("stargazers_count", 0))
        forks = details.get("forks_count", repo.get("forks_count", 0))
        open_issues = details.get("open_issues_count", repo.get("open_issues_count", 0))
        description = details.get("description", repo.get("description", ""))
        language = details.get("language", repo.get("language", ""))
        updated = details.get("updated_at", repo.get("updated_at", ""))
        created = details.get("created_at", repo.get("created_at", ""))
        html_url = details.get("html_url", repo.get("html_url", ""))
        owner = details.get("owner", {}).get("login", "")
        name = details.get("name", repo.get("name", full_name))
        
        # 判断是否为新项目（7天内创建）
        try:
            created_date = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
            is_new = (datetime.now() - created_date).days <= 7
        except:
            is_new = False
        
        # 计算趋势
        trend = calculate_trend(stars, forks, open_issues, updated, created)
        
        processed.append({
            "name": name,
            "full_name": full_name,
            "description": description,
            "language": language,
            "stars": stars,
            "forks": forks,
            "issues": open_issues,
            "url": html_url,
            "owner": owner,
            "created": created,
            "updated": updated,
            "is_new": is_new,
            "trend": round(trend, 1)
        })
        
        time.sleep(0.5)  # 避免 API 请求过快
    
    return processed


def save_data(projects, output_path):
    """保存数据到 JSON 文件"""
    data = {
        "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "projects": sorted(projects, key=lambda x: x["stars"], reverse=True)
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Data saved to {output_path}")
    print(f"Total projects: {len(projects)}")


def main():
    """主函数"""
    print("=" * 50)
    print("AI Agent 项目追踪器 - 数据抓取")
    print("=" * 50)
    
    # 输出路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_path = os.path.join(project_root, "data", "projects.json")
    
    # 确保 data 目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 搜索仓库
    print("\n[1/3] 搜索 AI Agent 相关项目...")
    repos = search_ai_agent_repos()
    print(f"找到 {len(repos)} 个相关仓库")
    
    if not repos:
        print("未找到任何仓库，尝试使用备用关键词...")
        # 备用搜索
        url = f"{GITHUB_API_URL}/search/repositories?q=AI+agent+language:python&sort=stars&order=desc&per_page=30"
        result = make_request(url)
        if result and "items" in result:
            repos = result["items"]
    
    # 处理数据
    print("\n[2/3] 获取项目详细信息...")
    projects = process_repos(repos[:30])  # 限制处理数量
    
    # 保存数据
    print("\n[3/3] 保存数据...")
    save_data(projects, output_path)
    
    print("\n" + "=" * 50)
    print("抓取完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
