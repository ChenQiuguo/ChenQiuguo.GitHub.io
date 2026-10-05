#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""index.html 行号锁定工具: 保证总行数 1314, 且两个"小巧思"停在 520 / 1314 行。

背景
----
文件里有两处彩蛋注释:
    第  520 行:  <!--I LOVE U-->
    第 1314 行:  <!--她真的好可爱呀，我从来没有如此喜欢过一个人-->
文件总行数必须恰好 1314 行。第 521 至 1313 行是一大片填充空行, 用作缓冲:
正文区增减了多少行, 就从缓冲空行里删/补多少行, 使总数始终锁定 1314。

关键点: 缓冲空行只能吸收"总行数"的涨落, 不能修正标记的位置。
若新增内容插在彩蛋之前, 标记会整体下移; 因此 fix 会先把标记搬回 520/1314,
再用缓冲空行补齐总行数。

命令
----
  check   只校验, 不改文件
  fix     自动修复: 复位标记位置 + 用缓冲空行锁定总行数
  report  打印当前布局概览(彩色蛋、正文区、缓冲区各占多少行)

用法
----
  python lock_layout.py check  [path]
  python lock_layout.py fix    [path]
  python lock_layout.py report [path]
"""
import sys

# Windows 控制台常为 GBK, 强制 UTF-8 输出避免彩蛋中文导致 UnicodeEncodeError
for _stream in ("stdout", "stderr"):
    _s = getattr(sys, _stream, None)
    if _s is not None and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

TOTAL_LINES = 1314
LINE_A = 520
LINE_B = 1314
MARK_A = "I LOVE U"
MARK_B = "她真的好可爱呀"
NEWLINE = "\r\n"          # 文件全程使用 CRLF

# 第 1 至 519 行里允许顶格出现的结构行(与原始基线一致, 1基行号)。
# 注意: </body> / </html> 的位置会随正文增减而浮动, 因此不在这里硬编码,
# 而是由 _is_struct_tag() 按标签名动态放行。
HEAD_STRUCT_LINES = {1, 2, 3}

# 结构标签: 顶格出现属于文档骨架, 不算正文入侵
STRUCT_TAGS = (
    "<!doctype", "<html", "</html", "<head", "</head", "<body", "</body",
    "<style", "</style", "<meta", "<title", "</title", "<script", "</script",
)


def _is_struct_tag(line):
    s = line.strip().lower()
    return s.startswith(STRUCT_TAGS)


def head_intrusion(lines):
    """检查正文是否侵入第 1 至 519 行。返回可疑行列表 [(行号, 内容)]。

    只标记"实质正文内容"(如卡片、条目、链接)出现在彩蛋上方的情况;
    缩进行、文档骨架标签、彩蛋注释本身都不算。
    """
    bad = []
    for i in range(min(LINE_A - 1, len(lines))):
        line = lines[i]
        if is_blank(line):
            continue
        lineno = i + 1
        if lineno in HEAD_STRUCT_LINES or _is_struct_tag(line):
            continue
        # 允许缩进行(样式表内部与卡片结构)
        if line.startswith((" ", "\t")):
            continue
        # 彩蛋注释本身不算入侵
        if line.strip().startswith("<!--"):
            continue
        bad.append((lineno, line))
    return bad


# ---------------------------------------------------------------- 读写

def read_lines(path):
    """返回 (lines, nl)。lines 不含换行符; 末尾换行不产生额外空项。"""
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8")
    crlf, lf = text.count("\r\n"), text.count("\n")
    nl = "\r\n" if crlf >= lf - crlf else "\n"
    body = text[:-len(nl)] if text.endswith(nl) else text
    return body.split(nl), nl


def write_lines(path, lines, nl):
    with open(path, "wb") as fh:
        fh.write((nl.join(lines) + nl).encode("utf-8"))


# ---------------------------------------------------------------- 定位

def find_mark(lines, mark):
    """返回彩蛋所在的行下标(0基), 找不到返回 None。"""
    for i, line in enumerate(lines):
        if mark in line and line.strip().startswith("<!--"):
            return i
    return None


def is_blank(line):
    return line.strip() == ""


# ---------------------------------------------------------------- 校验

def evaluate(lines):
    """返回 (ok, [(标签, 是否通过, 详情)])。"""
    msgs = []
    total = len(lines)
    ia = find_mark(lines, MARK_A)
    ib = find_mark(lines, MARK_B)

    msgs.append(("总行数 == 1314", total == TOTAL_LINES, f"实际 {total}"))
    msgs.append((
        f"第 {LINE_A} 行是彩蛋 A",
        ia is not None and ia == LINE_A - 1,
        f"实际在第 {ia + 1} 行" if ia is not None else "找不到 <!--I LOVE U-->",
    ))
    msgs.append((
        f"第 {LINE_B} 行是彩蛋 B",
        ib is not None and ib == LINE_B - 1,
        f"实际在第 {ib + 1} 行" if ib is not None else "找不到中文彩蛋注释",
    ))
    return all(m[1] for m in msgs), msgs


def print_msgs(msgs):
    print("-" * 60)
    for label, passed, detail in msgs:
        print(f"[{'PASS' if passed else 'FAIL'}] {label}: {detail}")
    print("-" * 60)


# ---------------------------------------------------------------- 命令

def cmd_check(path):
    lines, _ = read_lines(path)
    ok, msgs = evaluate(lines)
    print(f"文件: {path}  (共 {len(lines)} 行)")
    print_msgs(msgs)
    print("结论:", "全部通过" if ok else "存在违反")
    return 0 if ok else 1


def cmd_report(path):
    lines, nl = read_lines(path)
    ia = find_mark(lines, MARK_A)
    ib = find_mark(lines, MARK_B)
    total = len(lines)
    print(f"文件: {path}")
    print(f"总行数   : {total}   换行: {'CRLF' if nl == NEWLINE else 'LF'}")
    print(f"彩蛋 A   : 第 {ia + 1 if ia is not None else '?'} 行")
    print(f"彩蛋 B   : 第 {ib + 1 if ib is not None else '?'} 行")
    if ia is not None and ib is not None:
        gap = lines[ia + 1:ib]
        blanks = sum(1 for l in gap if is_blank(l))
        print(f"缓冲空行 : {blanks} 行 (第 {ia + 2} 至 {ib} 行), 可吸收 ±{blanks} 行涨落")
    ok, msgs = evaluate(lines)
    print_msgs(msgs)
    print("结论:", "全部通过" if ok else "存在违反")
    return 0 if ok else 1


def cmd_fix(path):
    lines, nl = read_lines(path)
    print(f"文件: {path}")

    ia = find_mark(lines, MARK_A)
    ib = find_mark(lines, MARK_B)
    if ia is None or ib is None:
        print("错误: 找不到彩蛋注释, 无法自动修复。")
        return 2

    bad = head_intrusion(lines)
    if bad:
        print("错误: 检测到正文内容侵入第 1 至 519 行, 彩蛋位置已被顶掉且无法靠空行复位。")
        print(f"      发现 {len(bad)} 行可疑内容, 前几行:")
        for lineno, content in bad[:5]:
            print(f"        第 {lineno} 行: {content.strip()[:70]}")
        print("      请先把这些行移回第 520 行以下, 再运行 fix。")
        return 4

    # 彩蛋 A 必须精确落在第 520 行。
    # 删了正文行时它会向上浮, 插了正文行时它会向下沉, 两种情况都要复位。
    if ia > LINE_A - 1:
        moved = lines[LINE_A - 1:ia]
        lines = lines[:LINE_A - 1] + [lines[ia]] + moved + lines[ia + 1:]
        print(f"已把彩蛋 A 之前多出的 {len(moved)} 行内容移到其后方。")
    elif ia < LINE_A - 1:
        deficit = (LINE_A - 1) - ia
        avail = sum(1 for l in lines[ia + 1:] if is_blank(l))
        if avail < deficit:
            print(f"错误: 彩蛋 A 在第 {ia + 1} 行, 需下移 {deficit} 行, "
                  f"但彩蛋之后只有 {avail} 行空行可拆。")
            print("      说明正文被删得太多, 请先补回内容。")
            return 5
        # 在彩蛋 A 前插入空行, 把它推到第 520 行
        lines = lines[:ia] + [""] * deficit + lines[ia:]
        print(f"已在彩蛋 A 之前补 {deficit} 个空行, 使其回到第 {LINE_A} 行。")
    ia = LINE_A - 1
    ib = find_mark(lines, MARK_B)

    # 再把彩蛋 B 拖动到文件最后一行
    if ib != len(lines) - 1:
        tail = lines[ib]
        lines = lines[:ib] + lines[ib + 1:] + [tail]
        print("已把彩蛋 B 移动到文件末尾(最后一行)。")
        ib = len(lines) - 1

    # 最后用缓冲空行锁定总行数
    delta = len(lines) - TOTAL_LINES
    blank_idx = [i for i in range(ia + 1, ib) if is_blank(lines[i])]
    print(f"当前总行数: {len(lines)}   目标: {TOTAL_LINES}   差值: {delta:+d}")
    print(f"缓冲空行: {len(blank_idx)} 行 (第 {ia + 2} 至 {ib} 行)")

    if delta > 0:
        if len(blank_idx) < delta:
            print(f"错误: 缓冲空行不足, 需删 {delta} 行但只有 {len(blank_idx)} 行空行。")
            print("      说明新增内容过多, 请先精简正文。")
            return 3
        victims = set(blank_idx[-delta:])
        lines = [l for i, l in enumerate(lines) if i not in victims]
        print(f"已删减 {delta} 个缓冲空行。")
    elif delta < 0:
        need = -delta
        at = blank_idx[-1] + 1 if blank_idx else ib
        lines = lines[:at] + [""] * need + lines[at:]
        print(f"已补足 {need} 个缓冲空行。")

    write_lines(path, lines, nl)
    lines2, _ = read_lines(path)
    ok, msgs = evaluate(lines2)
    print_msgs(msgs)
    if ok:
        print("结论: 已修复, 全部通过")
        return 0
    print("结论: 修复后仍不合规")
    return 1


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("check", "fix", "report"):
        print(__doc__)
        return 64
    mode = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) > 2 else "index.html"
    return {"check": cmd_check, "fix": cmd_fix, "report": cmd_report}[mode](path)


if __name__ == "__main__":
    sys.exit(main())
