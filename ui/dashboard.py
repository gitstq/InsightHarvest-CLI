"""TUI交互式仪表盘 - 使用curses构建终端界面"""

import sys
import curses


class Dashboard:
    """
    TUI交互式仪表盘，使用curses库

    功能:
    - 显示采集数据列表
    - 键盘导航
    - 详情查看
    - 来源过滤
    """

    KEY_ESCAPE = 27
    KEY_ENTER = 10
    KEY_SPACE = 32

    def __init__(self, items=None, analysis=None, keywords=None, logger=None):
        self.items = items or []
        self.analysis = analysis
        self.keywords = keywords or []
        self.logger = logger
        self.selected_index = 0
        self.scroll_offset = 0
        self.current_view = "list"  # list, stats, keywords, help
        self.filter_source = "all"
        self.running = True

    def run(self):
        """启动TUI仪表盘"""
        try:
            curses.wrapper(self._main_loop)
        except curses.error as e:
            sys.stderr.write("TUI错误: {}\n".format(str(e)))
            sys.stderr.write("提示: 请确保终端支持curses\n")
        except KeyboardInterrupt:
            pass

    def _main_loop(self, stdscr):
        """主循环"""
        # 初始化curses
        self._init_curses(stdscr)

        while self.running:
            self._draw(stdscr)
            self._handle_input(stdscr)

        # 清理
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def _init_curses(self, stdscr):
        """初始化curses设置"""
        curses.curs_set(0)  # 隐藏光标
        stdscr.nodelay(True)  # 非阻塞输入
        stdscr.keypad(True)  # 启用特殊键
        curses.noecho()  # 不回显输入

        # 颜色
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    # 标题
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # 高亮
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # 选中
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # 信息
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 普通
            curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # 标签
            curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)    # 错误

    def _draw(self, stdscr):
        """绘制界面"""
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()

        # 标题栏
        self._draw_header(stdscr, max_x)

        # 根据当前视图绘制内容
        if self.current_view == "list":
            self._draw_list(stdscr, max_y, max_x)
        elif self.current_view == "stats":
            self._draw_stats(stdscr, max_y, max_x)
        elif self.current_view == "keywords":
            self._draw_keywords(stdscr, max_y, max_x)
        elif self.current_view == "detail":
            self._draw_detail(stdscr, max_y, max_x)
        elif self.current_view == "help":
            self._draw_help(stdscr, max_y, max_x)

        # 底部状态栏
        self._draw_footer(stdscr, max_y, max_x)

        stdscr.refresh()

    def _draw_header(self, stdscr, max_x):
        """绘制标题栏"""
        title = " InsightHarvest-CLI Dashboard "
        if curses.has_colors():
            stdscr.attron(curses.color_pair(1))
        try:
            stdscr.addstr(0, 0, title.center(max_x)[:max_x - 1])
        except curses.error:
            pass
        if curses.has_colors():
            stdscr.attroff(curses.color_pair(1))

        # 视图标签
        views = ["[1]List", "[2]Stats", "[3]Keywords", "[4]Detail", "[5]Help"]
        view_str = "  ".join(views)
        try:
            stdscr.addstr(1, 0, view_str[:max_x - 1])
        except curses.error:
            pass

    def _draw_list(self, stdscr, max_y, max_x):
        """绘制数据列表"""
        filtered = self._get_filtered_items()

        if not filtered:
            msg = "No items to display. Press [q] to quit."
            try:
                stdscr.addstr(max_y // 2, (max_x - len(msg)) // 2, msg)
            except curses.error:
                pass
            return

        # 列表区域
        list_start = 3
        list_end = max_y - 3
        visible_lines = list_end - list_start

        # 调整滚动
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_lines:
            self.scroll_offset = self.selected_index - visible_lines + 1

        for i in range(visible_lines):
            idx = self.scroll_offset + i
            if idx >= len(filtered):
                break

            item = filtered[idx]
            y = list_start + i

            # 选中高亮
            if idx == self.selected_index:
                if curses.has_colors():
                    stdscr.attron(curses.color_pair(3))

            # 格式化行
            source = item.get("source", "?")[:8]
            title = item.get("title", "No title")
            score = item.get("score", 0)

            # 截断标题
            max_title_len = max_x - 22
            if len(title) > max_title_len:
                title = title[:max_title_len - 3] + "..."

            line = " {:>8s} | {:<5d} | {}".format(source, score, title)

            try:
                stdscr.addstr(y, 0, line[:max_x - 1])
            except curses.error:
                pass

            if idx == self.selected_index:
                if curses.has_colors():
                    stdscr.attroff(curses.color_pair(3))

    def _draw_stats(self, stdscr, max_y, max_x):
        """绘制统计视图"""
        y = 3
        if not self.analysis:
            try:
                stdscr.addstr(y, 2, "No analysis data available.")
            except curses.error:
                pass
            return

        if curses.has_colors():
            stdscr.attron(curses.color_pair(4))

        try:
            stdscr.addstr(y, 2, "=== Trend Analysis ===")
        except curses.error:
            pass
        y += 2

        if curses.has_colors():
            stdscr.attroff(curses.color_pair(4))

        stats = self.analysis.get("statistics", {})
        stat_lines = [
            "Total Items: {}".format(self.analysis.get("total_items", 0)),
            "Total Score: {}".format(stats.get("total_score", 0)),
            "Avg Score:   {}".format(stats.get("avg_score", 0)),
            "Max Score:   {}".format(stats.get("max_score", 0)),
            "Median Score: {}".format(stats.get("median_score", "N/A")),
            "",
            "=== Source Distribution ===",
        ]

        for line in stat_lines:
            try:
                stdscr.addstr(y, 4, line[:max_x - 5])
            except curses.error:
                pass
            y += 1

        source_dist = self.analysis.get("source_distribution", {})
        for source, count in sorted(source_dist.items(), key=lambda x: x[1], reverse=True):
            bar_len = min(count * 2, max_x - 30)
            bar = "#" * bar_len
            line = "  {:>15s} | {} ({})".format(source, bar, count)
            try:
                stdscr.addstr(y, 4, line[:max_x - 5])
            except curses.error:
                pass
            y += 1

    def _draw_keywords(self, stdscr, max_y, max_x):
        """绘制关键词视图"""
        y = 3

        if not self.keywords:
            try:
                stdscr.addstr(y, 2, "No keywords extracted.")
            except curses.error:
                pass
            return

        if curses.has_colors():
            stdscr.attron(curses.color_pair(6))

        try:
            stdscr.addstr(y, 2, "=== Top Keywords ===")
        except curses.error:
            pass
        y += 2

        if curses.has_colors():
            stdscr.attroff(curses.color_pair(6))

        for kw in self.keywords[:min(len(self.keywords), max_y - 6)]:
            keyword = kw.get("keyword", "")
            freq = kw.get("frequency", 0)
            score = kw.get("tfidf_score", 0)

            bar_len = min(int(freq * 3), max_x - 40)
            bar = "*" * bar_len

            line = "  {:>20s} | {:>5d} | {:.4f} {}".format(
                keyword, freq, score, bar
            )
            try:
                stdscr.addstr(y, 2, line[:max_x - 3])
            except curses.error:
                pass
            y += 1

    def _draw_detail(self, stdscr, max_y, max_x):
        """绘制详情视图"""
        filtered = self._get_filtered_items()
        if not filtered or self.selected_index >= len(filtered):
            return

        item = filtered[self.selected_index]
        y = 3

        fields = [
            ("Title", item.get("title", "N/A")),
            ("Source", item.get("source", "N/A")),
            ("URL", item.get("url", "N/A")),
            ("Author", item.get("author", "N/A")),
            ("Score", str(item.get("score", 0))),
            ("Tags", ", ".join(item.get("tags", [])) or "N/A"),
            ("", ""),
            ("Description", item.get("description", "N/A")),
        ]

        for label, value in fields:
            if not label and not value:
                y += 1
                continue

            if curses.has_colors():
                stdscr.attron(curses.color_pair(4))

            try:
                stdscr.addstr(y, 2, "{}: ".format(label))
            except curses.error:
                pass

            if curses.has_colors():
                stdscr.attroff(curses.color_pair(4))

            # 描述可能很长，需要换行
            if label == "Description":
                desc = value
                max_line_len = max_x - 4
                while desc and y < max_y - 4:
                    line = desc[:max_line_len]
                    desc = desc[max_line_len:]
                    try:
                        stdscr.addstr(y, 4, line[:max_x - 5])
                    except curses.error:
                        pass
                    y += 1
            else:
                # 截断长行
                val = value[:max_x - len(label) - 6]
                try:
                    stdscr.addstr(y, 4 + len(label), val[:max_x - 5 - len(label)])
                except curses.error:
                    pass
                y += 1

    def _draw_help(self, stdscr, max_y, max_x):
        """绘制帮助视图"""
        y = 3
        help_lines = [
            "=== Keyboard Shortcuts ===",
            "",
            "  Up/Down    - Navigate items",
            "  PgUp/PgDn  - Scroll page",
            "  Home/End   - Jump to first/last",
            "  1          - List view",
            "  2          - Statistics view",
            "  3          - Keywords view",
            "  4          - Detail view",
            "  5          - Help view",
            "  f          - Filter by source",
            "  a          - Show all sources",
            "  q/Esc      - Quit",
            "",
            "=== About ===",
            "",
            "  InsightHarvest-CLI v1.0.0",
            "  Lightweight Terminal AI Multi-Source",
            "  Intelligence Harvesting & Synthesis Engine",
        ]

        for line in help_lines:
            try:
                stdscr.addstr(y, 4, line[:max_x - 5])
            except curses.error:
                pass
            y += 1

    def _draw_footer(self, stdscr, max_y, max_x):
        """绘制底部状态栏"""
        y = max_y - 2
        filtered = self._get_filtered_items()

        status = " Items: {} | Selected: {}/{} | Filter: {} | View: {} ".format(
            len(filtered),
            self.selected_index + 1,
            len(filtered),
            self.filter_source,
            self.current_view.upper(),
        )

        if curses.has_colors():
            stdscr.attron(curses.color_pair(1))

        try:
            stdscr.addstr(y, 0, status[:max_x - 1])
        except curses.error:
            pass

        if curses.has_colors():
            stdscr.attroff(curses.color_pair(1))

    def _get_filtered_items(self):
        """获取过滤后的数据"""
        if self.filter_source == "all":
            return self.items
        return [item for item in self.items if item.get("source") == self.filter_source]

    def _handle_input(self, stdscr):
        """处理键盘输入"""
        try:
            key = stdscr.getch()
        except Exception:
            key = -1

        if key == -1:
            return

        filtered = self._get_filtered_items()

        if key == ord('q') or key == self.KEY_ESCAPE:
            self.running = False

        elif key == ord('1'):
            self.current_view = "list"
        elif key == ord('2'):
            self.current_view = "stats"
        elif key == ord('3'):
            self.current_view = "keywords"
        elif key == ord('4'):
            self.current_view = "detail"
        elif key == ord('5'):
            self.current_view = "help"

        elif key == curses.KEY_UP:
            if self.selected_index > 0:
                self.selected_index -= 1
        elif key == curses.KEY_DOWN:
            if self.selected_index < len(filtered) - 1:
                self.selected_index += 1
        elif key == curses.KEY_PPAGE:
            self.selected_index = max(0, self.selected_index - 10)
        elif key == curses.KEY_NPAGE:
            self.selected_index = min(len(filtered) - 1, self.selected_index + 10)
        elif key == curses.KEY_HOME:
            self.selected_index = 0
            self.scroll_offset = 0
        elif key == curses.KEY_END:
            self.selected_index = len(filtered) - 1

        elif key == ord('f'):
            # 切换来源过滤
            sources = list(set(item.get("source", "") for item in self.items))
            sources = ["all"] + sorted(sources)
            current_idx = sources.index(self.filter_source) if self.filter_source in sources else 0
            next_idx = (current_idx + 1) % len(sources)
            self.filter_source = sources[next_idx]
            self.selected_index = 0
            self.scroll_offset = 0

        elif key == ord('a'):
            self.filter_source = "all"
            self.selected_index = 0
            self.scroll_offset = 0
