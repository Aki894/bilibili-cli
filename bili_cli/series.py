#!/usr/bin/env python3
"""
Bilibili Series & Seasons Commands
合集与系列管理功能
"""

import click
import requests
import json

# API 端点
API_SERIES_LIST = "https://api.bilibili.com/x/polymer/web-space/seasons_series_list"
API_SERIES_ARCHIVES = "https://api.bilibili.com/x/series/archives"
API_SEASON_ARCHIVES = "https://api.bilibili.com/x/polymer/web-space/seasons_archives"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com",
}

@click.group()
def series():
    """系列/合集管理命令"""
    pass

@series.command()
@click.argument('mid', type=int)
@click.option('--format', 'output_format', type=click.Choice(['json', 'yaml']), default='yaml', help='输出格式')
@click.option('--page-size', type=int, default=20, help='每页数量')
def list(mid: int, output_format: str, page_size: int):
    """列出 UP 主的所有系列/合集
    
    MID: UP 主的 UID
    """
    params = {"mid": mid, "page_size": page_size, "page_num": 1}
    resp = requests.get(API_SERIES_LIST, params=params, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    
    if data.get("code") != 0:
        raise click.ClickException(f"API 错误：{data.get('message')}")
    
    result = data.get("data", {})
    
    if output_format == 'json':
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        items_lists = result.get('items_lists', {})
        series_list = items_lists.get('series_list', [])
        seasons_list = items_lists.get('seasons_list', [])
        
        # series_list 和 seasons_list 直接包含视频，需要提取元数据
        if series_list:
            click.echo(f"series: {len(series_list)} 个系列")
            for i, s in enumerate(series_list, 1):
                archives = s.get('archives', [])
                click.echo(f"  [{i}] 视频数：{len(archives)}")
                if archives:
                    click.echo(f"      最新：{archives[0].get('title', 'N/A')}")
        
        if seasons_list:
            click.echo(f"\nseasons: {len(seasons_list)} 个合集")
            for i, s in enumerate(seasons_list, 1):
                archives = s.get('archives', [])
                click.echo(f"  [{i}] 视频数：{len(archives)}")
                if archives:
                    click.echo(f"      最新：{archives[0].get('title', 'N/A')}")

@series.command()
@click.argument('series_id', type=int)
@click.option('--mid', type=int, required=True, help='UP 主 UID')
@click.option('--format', 'output_format', type=click.Choice(['json', 'yaml']), default='yaml', help='输出格式')
@click.option('--page', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='每页数量')
def archives(series_id: int, mid: int, output_format: str, page: int, page_size: int):
    """获取系列内的视频列表
    
    SERIES_ID: 系列 ID
    --mid: UP 主 UID（必需）
    """
    params = {"mid": mid, "series_id": series_id, "pn": page, "ps": page_size}
    resp = requests.get(API_SERIES_ARCHIVES, params=params, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    
    if data.get("code") != 0:
        raise click.ClickException(f"API 错误：{data.get('message')}")
    
    archives = data.get("data", {}).get("archives", [])
    
    if output_format == 'json':
        click.echo(json.dumps(archives, ensure_ascii=False, indent=2))
    else:
        for vid in archives:
            click.echo(f"- title: {vid.get('title')}")
            click.echo(f"  bvid: {vid.get('bvid')}")
            click.echo(f"  aid: {vid.get('aid')}")
            click.echo(f"  duration: {vid.get('duration')}")
            click.echo(f"  pubdate: {vid.get('pubdate')}")

@series.command()
@click.argument('season_id', type=int)
@click.option('--mid', type=int, required=True, help='UP 主 UID')
@click.option('--format', 'output_format', type=click.Choice(['json', 'yaml']), default='yaml', help='输出格式')
@click.option('--page', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='每页数量')
def season(season_id: int, mid: int, output_format: str, page: int, page_size: int):
    """获取合集内的视频列表
    
    SEASON_ID: 合集 ID
    --mid: UP 主 UID（必需）
    """
    params = {"mid": mid, "season_id": season_id, "pn": page, "ps": page_size}
    resp = requests.get(API_SEASON_ARCHIVES, params=params, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    
    if data.get("code") != 0:
        raise click.ClickException(f"API 错误：{data.get('message')}")
    
    archives = data.get("data", {}).get("archives", [])
    
    if output_format == 'json':
        click.echo(json.dumps(archives, ensure_ascii=False, indent=2))
    else:
        for vid in archives:
            click.echo(f"- title: {vid.get('title')}")
            click.echo(f"  bvid: {vid.get('bvid')}")
            click.echo(f"  aid: {vid.get('aid')}")
            click.echo(f"  duration: {vid.get('duration')}")
            click.echo(f"  pubdate: {vid.get('pubdate')}")
