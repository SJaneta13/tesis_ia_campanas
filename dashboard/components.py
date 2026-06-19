# dashboard/components.py
import html
import streamlit as st


def safe_text(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def topbar(title: str, subtitle: str, pill_text: str | None = None):
    title = safe_text(title)
    subtitle = safe_text(subtitle)

    pill_html = ""

    if pill_text:
        pill_html = (
            '<div class="topbar-pill">'
            f'<div class="small-pill"><span class="dot-green"></span>{safe_text(pill_text)}</div>'
            '</div>'
        )

    st.markdown(
        f'''
<div class="topbar">
    {pill_html}
    <div class="topbar-title">{title}</div>
    <div class="topbar-subtitle">{subtitle}</div>
</div>
''',
        unsafe_allow_html=True
    )


def kpi_card(label: str, value: str, help_text: str = "", variant: str = "blue"):
    st.markdown(
        f'''
<div class="kpi-card kpi-card-{variant}">
    <div class="kpi-label">{safe_text(label)}</div>
    <div class="kpi-value">{safe_text(value)}</div>
    <div class="kpi-help">{safe_text(help_text)}</div>
</div>
''',
        unsafe_allow_html=True
    )


def hypothesis_card(text: str):
    st.markdown(
        f'''
<div class="custom-card">
    <div class="card-title">Hipótesis del Estudio</div>
    <div class="hypothesis-box">
        {safe_text(text)}
    </div>
</div>
''',
        unsafe_allow_html=True
    )


def method_card(title: str, text: str):
    st.markdown(
        f'''
<div class="method-card">
    <div class="method-title">{safe_text(title)}</div>
    <div class="method-text">{safe_text(text)}</div>
</div>
''',
        unsafe_allow_html=True
    )


def section_card_header(title: str, subtitle: str | None = None):
    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<div class="card-subtitle">{safe_text(subtitle)}</div>'

    st.markdown(
        f'''
<div class="section-card-header">
    <div class="card-title">{safe_text(title)}</div>
    {subtitle_html}
</div>
''',
        unsafe_allow_html=True
    )


def warning_box(text: str):
    st.markdown(
        f'''
<div class="alert-warning">
    {safe_text(text)}
</div>
''',
        unsafe_allow_html=True
    )


def danger_box(text: str):
    st.markdown(
        f'''
<div class="alert-danger">
    {safe_text(text)}
</div>
''',
        unsafe_allow_html=True
    )