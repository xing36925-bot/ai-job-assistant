import streamlit as st
from analyzer import DEMO_JD, DEMO_RESUME, SKILLS, analyze, report

st.set_page_config(page_title="AI 求职助手", page_icon="📄", layout="wide")
st.title("📄 AI 求职助手 · 规则演示版")
st.caption("本地规则分析 · 无付费 API · 无大模型调用")

st.warning(
    "请仅使用下方虚构示例或自行匿名化的模拟文本，"
    "不要输入真实姓名、电话、邮箱或其他个人信息。"
    "文本仅在当前运行实例内存中处理；本应用不写入文件、不上传至第三方。"
)
st.info(
    "评分只表示已支持关键词的覆盖率，不验证实际能力，也不代表录用概率。"
    "否定表达（如“不熟悉 Python”）也可能被计入，请人工核对。"
)

with st.expander("查看评分规则和支持的能力词"):
    st.write(
        "JD 中识别到的能力组等权计分，"
        "分数 = 简历覆盖组数 ÷ JD 识别组数 × 100。"
        "重复词不额外加分；没有支持的词时不评分。"
        "学历、年限、要求优先级和其他未支持词不计分。"
    )
    st.json({key: list(value) for key, value in SKILLS.items()})

if "resume" not in st.session_state:
    st.session_state.resume = DEMO_RESUME
    st.session_state.jd = DEMO_JD

if st.button("恢复内置模拟数据"):
    st.session_state.resume = DEMO_RESUME
    st.session_state.jd = DEMO_JD

left, right = st.columns(2)

with left:
    resume = st.text_area(
        "个人简历文本（仅使用模拟数据）",
        key="resume",
        height=260,
        max_chars=20000,
    )

with right:
    jd = st.text_area(
        "岗位 JD",
        key="jd",
        height=260,
        max_chars=20000,
    )

if st.button("开始分析", type="primary"):
    try:
        result = analyze(resume, jd)
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.metric(
            "关键词覆盖参考评分",
            f'{result["score"]}/100'
            if result["score"] is not None
            else "无法评分",
        )

        if result["score"] is None:
            st.warning("JD 中未找到支持的能力词，请人工阅读完整岗位要求。")

        st.subheader("匹配依据")
        if result["evidence"]:
            st.table(result["evidence"])
        else:
            st.write("暂未找到匹配项。")

        st.subheader("简历中未体现的能力")
        st.write(
            "、".join(result["missing"])
            or "未发现缺失关键词，仍需人工核实实际要求。"
        )

        st.subheader("不编造经历的优化建议")
        for suggestion in result["suggestions"]:
            st.write("• " + suggestion)

        st.download_button(
            "下载分析报告（Markdown）",
            report(result),
            "求职匹配报告.md",
            "text/markdown",
            on_click="ignore",
        )

st.caption(
    "输入修改后请重新点击“开始分析”。"
    "报告只包含能力词及建议，不附带完整简历或 JD。"
)