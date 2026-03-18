"""Series and Seasons related commands."""

from __future__ import annotations

import click
from rich.table import Table

from .. import payloads
from . import common


@click.group()
def series():
    """管理合集与系列。"""
    pass


@series.command(name="list")
@click.argument("mid", type=int)
@common.structured_output_options
def series_list_cmd(mid: int, as_json: bool, as_yaml: bool):
    """列出 UP 主的所有系列和合集。"""
    from .. import client

    output_format = common.resolve_output_format(as_json=as_json, as_yaml=as_yaml)
    data = common.run_or_exit(client.get_series_list(mid), "获取系列列表失败")

    structured = payloads.normalize_series_list(data)
    if common.emit_structured(structured, output_format):
        return

    series_list = structured.get("series", [])
    seasons_list = structured.get("seasons", [])

    if not series_list and not seasons_list:
        common.console.print(f"[yellow]用户 {mid} 暂无合集或系列[/yellow]")
        return

    if series_list:
        table = Table(title=f"📂 系列列表 (UID: {mid})", border_style="blue")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("名称", width=30)
        table.add_column("视频数", width=10, justify="right")
        
        for s in series_list:
            table.add_row(s["id"], s["name"], str(s["total"]))
        
        common.console.print(table)

    if seasons_list:
        if series_list:
            common.console.print()
        table = Table(title=f"📂 合集列表 (UID: {mid})", border_style="blue")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("名称", width=30)
        table.add_column("视频数", width=10, justify="right")
        
        for s in seasons_list:
            table.add_row(s["id"], s["name"], str(s["total"]))
        
        common.console.print(table)

    common.console.print(f"\n[dim]使用 [bold]bili series archives <ID> --mid {mid}[/bold] 查看系列视频[/dim]")
    common.console.print(f"[dim]使用 [bold]bili series season <ID> --mid {mid}[/bold] 查看合集视频[/dim]")


@series.command()
@click.argument("series_id", type=int)
@click.option("--mid", type=int, required=True, help="UP 主 UID")
@click.option("--page", "-p", default=1, type=click.IntRange(1), help="页码")
@click.option("--page-size", "-ps", default=10, type=click.IntRange(1, 50), help="每页数量 (默认 10)")
@common.structured_output_options
def archives(series_id: int, mid: int, page: int, page_size: int, as_json: bool, as_yaml: bool):
    """获取系列内的视频列表。"""
    from .. import client

    output_format = common.resolve_output_format(as_json=as_json, as_yaml=as_yaml)
    data = common.run_or_exit(
        client.get_series_archives(mid, series_id, pn=page, ps=page_size),
        "获取系列内容失败",
    )

    vlist = data.get("archives") or []
    if common.emit_structured(
        [payloads.normalize_video_summary(v) for v in vlist], 
        output_format
    ):
        return

    if not vlist:
        common.console.print("[yellow]该系列为空或不存在[/yellow]")
        return

    table = Table(title=f"📂 系列 #{series_id} (页码: {page})", border_style="blue")
    table.add_column("#", style="dim", width=4)
    table.add_column("BV号", style="cyan", width=14)
    table.add_column("标题", max_width=40)
    table.add_column("时长", width=8)
    
    for i, v in enumerate(vlist, 1 + (page - 1) * page_size):
        table.add_row(
            str(i),
            v.get("bvid", ""),
            v.get("title", "")[:40],
            common.format_duration(v.get("duration", 0)),
        )

    common.console.print(table)
    common.console.print(f"\n[dim]页码: {page} | 每页显示 {page_size} 条[/dim]")
    common.console.print(f"[dim]查看下一页: [bold]bili series archives {series_id} --mid {mid} -p {page + 1}[/bold][/dim]")


@series.command()
@click.argument("season_id", type=int)
@click.option("--mid", type=int, required=True, help="UP 主 UID")
@click.option("--page", "-p", default=1, type=click.IntRange(1), help="页码")
@click.option("--page-size", "-ps", default=10, type=click.IntRange(1, 50), help="每页数量 (默认 10)")
@common.structured_output_options
def season(season_id: int, mid: int, page: int, page_size: int, as_json: bool, as_yaml: bool):
    """获取合集内的视频列表。"""
    from .. import client

    output_format = common.resolve_output_format(as_json=as_json, as_yaml=as_yaml)
    data = common.run_or_exit(
        client.get_season_archives(mid, season_id, pn=page, ps=page_size),
        "获取合集内容失败",
    )

    # 合集列表 API 返回的字段略有不同，需要从 data 中提取总数或列表
    # 假设返回结构与用户提供的 API 示例一致
    vlist = data.get("archives") or []
    if common.emit_structured(
        [payloads.normalize_video_summary(v) for v in vlist], 
        output_format
    ):
        return

    if not vlist:
        common.console.print("[yellow]该合集为空或不存在[/yellow]")
        return

    table = Table(title=f"📂 合集 #{season_id} (页码: {page})", border_style="blue")
    table.add_column("#", style="dim", width=4)
    table.add_column("BV号", style="cyan", width=14)
    table.add_column("标题", max_width=40)
    table.add_column("时长", width=8)
    
    for i, v in enumerate(vlist, 1 + (page - 1) * page_size):
        table.add_row(
            str(i),
            v.get("bvid", ""),
            v.get("title", "")[:40],
            common.format_duration(v.get("duration", 0)),
        )

    common.console.print(table)
    common.console.print(f"\n[dim]页码: {page} | 每页显示 {page_size} 条[/dim]")
    common.console.print(f"[dim]查看下一页: [bold]bili series season {season_id} --mid {mid} -p {page + 1}[/bold][/dim]")
