from pyecharts import options as opts
from pyecharts.charts import Pie, Bar, Tab
from pyecharts.commons.utils import JsCode

from pyecharts.globals import CurrentConfig
CurrentConfig.ONLINE_HOST = "../resource/pyechart/" # 导向本地js资源

def generate_analysis(sample_data, html_name="样本分析报告.html"):
    """
    封装函数：传入样本数据生成饼图和柱状图
    :param sample_data: 格式为 [("类别A", 10), ("类别B", 20), ...]
    :param html_name: 输出的 HTML 文件名
    """

    # --- 1. 超大号高辨识度配色方案 (共 50 种颜色) ---
    # 即使类别非常多，也会按顺序循环，且颜色对比度高，适合大场面展示
    COLOR_LIST = [
        '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc',
        '#d48265', '#91c7ae', '#749f83', '#ca8622', '#bda29a', '#6e7074', '#546570', '#c4ccd3', '#f05b72',
        '#ef5b9c', '#f47920', '#905a3d', '#fab27b', '#2a5caa', '#444693', '#726930', '#102b42', '#152132',
        '#223e36', '#475164', '#003366', '#006699', '#4cabce', '#e5323e', '#bf444c', '#525288', '#20a162',
        '#da1d23', '#228fbd', '#c1cad1', '#7e884f', '#a1afc9', '#2d589e', '#50a1ba', '#f4a351', '#73b061'
    ]

    # --- 2. 饼状图配置 (大小统一的标准饼图) ---
    def create_pie() -> Pie:
        c = (
            Pie(init_opts=opts.InitOpts(width="1200px", height="700px"))
            .add(
                "",
                sample_data,
                radius=["0%", "65%"],  # 设置起始半径为0%，即标准的实心饼图
                rosetype=None,  # 关闭玫瑰图模式，确保所有切片半径一致
                center=["45%", "50%"],  # 略微偏左，给右侧滚动图例留出空间
            )
            .set_colors(COLOR_LIST)  # 应用自定义配色
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="样本数量占比分析",
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(font_size=28, font_weight="bold")
                ),
                # 滚动图例：支持超多类别切换
                legend_opts=opts.LegendOpts(
                    type_="scroll",
                    pos_left="88%",
                    orient="vertical",
                    textstyle_opts=opts.TextStyleOpts(font_size=14)
                ),
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(
                    formatter="{b}: {c}\n({d}%)",  # 显示类别、数量和百分比
                    font_size=16,
                    font_weight="bold"
                )
            )
        )
        return c

    # --- 3. 柱状图配置 (支持横向滚动缩放) ---
    def create_bar() -> Bar:
        x_data = [item[0] for item in sample_data]
        y_data = [item[1] for item in sample_data]

        c = (
            Bar(init_opts=opts.InitOpts(width="1200px", height="700px"))
            .add_xaxis(x_data)
            .add_yaxis("样本数量", y_data, category_gap="30%")
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="样本数量柱状分布图",
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(font_size=28, font_weight="bold")
                ),
                # 为处理超多类别，增加缩放组件
                datazoom_opts=[
                    opts.DataZoomOpts(is_show=True, type_="slider", range_start=0, range_end=50),
                    opts.DataZoomOpts(type_="inside")
                ],
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=30, font_size=14, font_weight="bold"),
                    name="类别",
                    name_textstyle_opts=opts.TextStyleOpts(font_size=16)
                ),
                yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(font_size=14),
                    name="数量",
                    name_textstyle_opts=opts.TextStyleOpts(font_size=16)
                ),
                legend_opts=opts.LegendOpts(is_show=False)
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(is_show=True, position="top", font_size=16, font_weight="bold"),
                # 每一个柱子分配不同颜色
                itemstyle_opts={
                    "normal": {
                        "color": JsCode("""
                            function(params) {
                                var colorList = """ + str(COLOR_LIST) + """;
                                return colorList[params.dataIndex % colorList.length];
                            }
                        """)
                    }
                }
            )
        )
        return c

    # --- 4. 封装到 Tab 并保存 ---
    tab = Tab()
    tab.add(create_pie(), "饼状图分析")
    tab.add(create_bar(), "柱状图分析")
    tab.render(html_name)