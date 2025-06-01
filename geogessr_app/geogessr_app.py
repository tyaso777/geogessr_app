# poetry run streamlit run geogessr_app/geogessr_app.py

import folium
import numpy as np
import streamlit as st
import yaml
from config.data_processor import DataProcessor
from config.field_config import (
    CHAR_TO_LANGUAGES,
    DISPLAY_OPTIONS,
    FILTERABLE_FIELDS,
    field_options,
)
from config.street_config import LANGUAGE_STREET_TERMS
from folium import DivIcon
from streamlit_folium import st_folium

st.set_page_config(page_title="GeoGuessR Helper", layout="wide")
st.title("🗺️ GeoGuessR Helper: Countries, Languages & Street Terms")


@st.cache_data
def load_data() -> dict:
    with open("geo_data.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@st.cache_data
def calculate_numeric_percentiles(data: dict, field_path: str):
    """数値フィールドの分布を計算してパーセンタイルを取得"""
    values = []
    for country_info in data.values():
        value = DataProcessor.process_field(field_path, country_info)
        # 数値の解析を改善（範囲や不確実性を含む値を処理）
        parsed_value = parse_numeric_value(value)
        if parsed_value is not None:
            values.append(parsed_value)

    if not values:
        return None

    values = np.array(values)
    return {
        "min": np.min(values),
        "q25": np.percentile(values, 25),
        "median": np.percentile(values, 50),
        "q75": np.percentile(values, 75),
        "max": np.max(values),
        "values": values,
    }


def parse_numeric_value(value):
    """数値、範囲、不確実性を含む値を解析"""
    if isinstance(value, (int, float)):
        return value

    if not isinstance(value, str):
        return None

    import re

    # "3" のような単純な数値
    if value.isdigit():
        return int(value)

    # "3.5" のような小数
    try:
        return float(value)
    except ValueError:
        pass

    # "3 or 5", "3-5", "3～5" のような範囲
    range_patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:or|または)\s*(\d+(?:\.\d+)?)",  # "3 or 5"
        r"(\d+(?:\.\d+)?)\s*[-～〜]\s*(\d+(?:\.\d+)?)",  # "3-5", "3～5"
        r"(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)",  # "3 to 5"
    ]

    for pattern in range_patterns:
        match = re.search(pattern, value)
        if match:
            # 範囲の場合は中央値を返す
            min_val = float(match.group(1))
            max_val = float(match.group(2))
            return (min_val + max_val) / 2

    # "約3", "~3", "3前後" のような近似値
    approx_patterns = [
        r"(?:約|~|around|approximately)\s*(\d+(?:\.\d+)?)",  # "約3", "~3"
        r"(\d+(?:\.\d+)?)\s*(?:前後|程度|くらい)",  # "3前後"
    ]

    for pattern in approx_patterns:
        match = re.search(pattern, value)
        if match:
            return float(match.group(1))

    # 単純に数値を抽出
    numbers = re.findall(r"\d+(?:\.\d+)?", value)
    if numbers:
        # 複数の数値がある場合は最初のものを使用
        return float(numbers[0])

    return None


def get_background_color_for_numeric_field(
    field_path: str, value, percentiles: dict = None
) -> str:
    """数値フィールドに応じて背景色を取得（動的分布ベース）"""
    # 元の値を解析
    parsed_value = parse_numeric_value(value)

    if parsed_value is None or percentiles is None:
        return "white"

    # パーセンタイルベースの色分け
    if parsed_value <= percentiles["q25"]:
        return "#ffe6e6"  # 薄い赤 (下位25%)
    elif parsed_value <= percentiles["median"]:
        return "#fff2e6"  # 薄いオレンジ (25-50%)
    elif parsed_value <= percentiles["q75"]:
        return "#fffae6"  # 薄い黄色 (50-75%)
    else:
        return "#e6f7e6"  # 薄い緑 (上位25%)


def get_legend_info(field_path: str, percentiles: dict) -> list:
    """フィールドと分布に応じた凡例情報を取得"""
    if not percentiles:
        return []

    return [
        (f"≤{percentiles['q25']:.1f}", "#ffe6e6", "Lower 25%"),
        (f"{percentiles['q25']:.1f}-{percentiles['median']:.1f}", "#fff2e6", "25-50%"),
        (f"{percentiles['median']:.1f}-{percentiles['q75']:.1f}", "#fffae6", "50-75%"),
        (f"≥{percentiles['q75']:.1f}", "#e6f7e6", "Upper 25%"),
    ]


def get_display_label(
    country: str, info: dict, field_path: str, display_config: dict
) -> str:
    """汎用的な表示ラベル取得関数"""
    if field_path == "#country":
        return country
    if field_path == "#notext":
        return ""

    # DataProcessorを使用して動的/静的フィールドを統一的に処理
    value = DataProcessor.process_field(field_path, info)

    if isinstance(value, list):
        value = ", ".join(value)
    elif not isinstance(value, str):
        value = str(value) if value is not None else ""

    if display_config.get(field_path, False):
        return f"{country}: {value}"
    return value


display_config = DISPLAY_OPTIONS.get("prepend_country_name", {})
data = load_data()

# ▼ 表示観点（サイドバー）
st.sidebar.write("### 🎯 Display Field")
selected_view = st.sidebar.radio(
    "Display Field",
    list(field_options.keys()),
    index=list(field_options.keys()).index("Flag (image only)"),
    label_visibility="collapsed",
)
icon_key, label_key = field_options[selected_view]

# ▼ 数値フィールドの分布計算と凡例表示
numeric_percentiles = None
if label_key in FILTERABLE_FIELDS and FILTERABLE_FIELDS[label_key][0] == "number":
    numeric_percentiles = calculate_numeric_percentiles(data, label_key)

    if numeric_percentiles:
        st.markdown("### 🎨 Color Legend (Based on Data Distribution)")
        legend_items = get_legend_info(label_key, numeric_percentiles)

        # 統計情報も表示
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.markdown(f"**Field:** {FILTERABLE_FIELDS[label_key][1]}")
            st.markdown(
                f"**Total countries with data:** {len(numeric_percentiles['values'])}"
            )
        with stats_col2:
            st.markdown(
                f"**Range:** {numeric_percentiles['min']:.1f} - {numeric_percentiles['max']:.1f}"
            )
            st.markdown(f"**Median:** {numeric_percentiles['median']:.1f}")

        # 色の凡例
        if legend_items:
            legend_cols = st.columns(len(legend_items))
            for i, (range_text, color, description) in enumerate(legend_items):
                with legend_cols[i]:
                    st.markdown(
                        f'<div style="background-color: {color}; padding: 8px; border-radius: 4px; text-align: center; border: 1px solid #ddd; margin: 2px;">'
                        f"<strong>{range_text}</strong><br><small>{description}</small></div>",
                        unsafe_allow_html=True,
                    )

# ▼ 特徴文字によるフィルター設定
import unicodedata


def sort_characters_by_base(char_list: list[str]) -> list[str]:
    def base_form(char: str) -> str:
        return (
            unicodedata.normalize("NFKD", char)
            .encode("ASCII", "ignore")
            .decode("ASCII")
            .lower()
        )

    return sorted(char_list, key=base_form)


st.sidebar.write("### 🔤 Character-based Language Filter")
char_states = {}
char_cols = st.sidebar.columns(5)
for idx, char in enumerate(sort_characters_by_base(CHAR_TO_LANGUAGES)):
    lang_count = len(CHAR_TO_LANGUAGES[char])
    if lang_count == 1:
        color = "#ff4d4d"  # vivid red (very specific)
    elif lang_count == 2:
        color = "#ffa500"  # strong orange
    elif lang_count == 3:
        color = "#f4e04d"  # bright yellow
    else:
        color = "#c6f7c3"  # soft green (less specific)
    with char_cols[idx % 5]:
        st.markdown(
            f"<div style='background-color:{color}; padding:3px; border-radius:5px; text-align: center;'>",
            unsafe_allow_html=True,
        )
        char_states[char] = st.checkbox(char, key=f"char_{char}_checkbox")
        st.markdown("</div>", unsafe_allow_html=True)

selected_chars = [c for c, v in char_states.items() if v]


def get_and_matching_languages(
    selected_chars: list[str], char_to_lang: dict
) -> set[str]:
    if not selected_chars:
        return set()
    lang_sets = [set(char_to_lang.get(c, [])) for c in selected_chars]
    return set.intersection(*lang_sets)


matching_langs = get_and_matching_languages(selected_chars, CHAR_TO_LANGUAGES)


def matches_selected_language(info: dict, matching_langs: set[str]) -> bool:
    langs = info.get("language", [])
    return any(lang in matching_langs for lang in langs)


# フィルターの状態
if "filters" not in st.session_state:
    st.session_state.filters = []

# メイン領域にフィルター表示
with st.expander("Filters", expanded=True):
    if st.button("+ Add Filter"):
        st.session_state.filters.append(
            {"field": "language", "match": "contains", "value": ""}
        )

    for i, f in enumerate(st.session_state.filters):
        cols = st.columns([2, 2, 4, 1])
        with cols[0]:
            f["field"] = st.selectbox(
                "Field", sorted(FILTERABLE_FIELDS.keys()), key=f"field_{i}"
            )
        with cols[1]:
            f["match"] = st.selectbox("Match", ["contains", "equals"], key=f"match_{i}")
        with cols[2]:
            help_text = FILTERABLE_FIELDS.get(f["field"], ("", ""))[1]
            f["value"] = st.text_input(
                f"Value ({help_text})", key=f"value_{i}", value=f["value"]
            )
        with cols[3]:
            if st.button("❌", key=f"remove_{i}"):
                st.session_state.filters.pop(i)
                st.rerun()


def passes_all_filters(info: dict, filters: list[dict]) -> bool:
    """汎用的なフィルター判定関数"""
    for f in filters:
        if not DataProcessor.filter_matches(f["field"], info, f["match"], f["value"]):
            return False
    return True


# ▼ チェックされた文字に対応する言語を表示
if selected_chars:
    st.markdown("### 🧠 Languages Matching Selected Characters")

    # 文字と言語の対応を表示
    char_lang_info = []
    for char in selected_chars:
        langs = CHAR_TO_LANGUAGES.get(char, [])
        char_lang_info.extend(langs)

    unique_langs = list(set(char_lang_info))
    st.markdown(f"**Selected characters:** {' '.join(selected_chars)}")
    st.markdown(f"**Matching languages:** {', '.join(unique_langs)}")

    # 街路表記モードの場合は対応する街路表記をテーブル形式で表示
    if label_key == "#dynamic_street_terms" and unique_langs:
        st.markdown("#### 🛣️ Street Terms for Selected Languages")

        # テーブル形式で見やすく表示
        street_data = []
        for lang in unique_langs:
            if lang in LANGUAGE_STREET_TERMS:
                terms = LANGUAGE_STREET_TERMS[lang]
                # 全ての街路表記を表示
                street_data.append(
                    {
                        "Language": lang,
                        "Street Terms": ", ".join(terms["street"]),
                        "Abbreviations": ", ".join(terms["abbreviations"]),
                    }
                )

        if street_data:
            import pandas as pd

            df = pd.DataFrame(street_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

# 地図の作成
m = folium.Map(location=[0, 0], zoom_start=2)

filtered_count = 0
for country, info in data.items():
    if selected_chars and not matches_selected_language(info, matching_langs):
        continue
    if not passes_all_filters(info, st.session_state.filters):
        continue

    icon_url = (
        DataProcessor.process_field(icon_key, info) if icon_key != "#noimage" else None
    )
    label = get_display_label(country, info, label_key, display_config)

    # 有効な値がない場合（国名のみ、空文字、None、"No ... available"など）はスキップ
    # ただし、Flag (image only) モードの場合は国名表示でもOK
    def has_valid_content(label_text, country_name, field_key):
        # Flag (image only) モードの場合は国名でもOK
        if field_key == "#country":
            return True

        if not label_text or label_text.strip() == "":
            return False
        if label_text == country_name:  # 国名のみの場合
            return False
        if (
            label_text.startswith(country_name + ":")
            and label_text.replace(country_name + ":", "").strip() == ""
        ):
            return False  # "国名: " の後に何もない場合
        if (
            "No " in label_text and "available" in label_text
        ):  # "No street terms available"など
            return False
        return True

    if not has_valid_content(label, country, label_key):
        continue

    # ここまで来た場合のみカウント
    filtered_count += 1

    # 数値フィールドの場合は背景色を取得
    raw_value = DataProcessor.process_field(label_key, info)
    bg_color = get_background_color_for_numeric_field(
        label_key, raw_value, numeric_percentiles
    )

    if icon_url:
        html = f"""
        <div style="text-align: center; font-size: 10px;">
            <img src="{icon_url}" style="width: 40px; height: auto; display: block; margin: 0 auto;" />
            {f'<div style="display: inline-block; background: {bg_color}; padding: 1px 4px; border-radius: 4px; max-width: 200px; word-wrap: break-word; border: 1px solid #ddd;">{label}</div>' if label else ""}
        </div>
        """
    else:
        html = f"""
        <div style="text-align: center; font-size: 10px;">
            <div style="display: inline-block; background: {bg_color}; padding: 2px 6px; border-radius: 4px; max-width: 200px; word-wrap: break-word; line-height: 1.2; border: 1px solid #ddd;">
                {label}
            </div>
        </div>
        """

    div_icon = DivIcon(icon_size=(40, 40), icon_anchor=(20, 20), html=html)

    # 詳細なポップアップ（全データを動的に表示）
    def format_data_for_popup(country_name: str, info: dict) -> str:
        """国の全データを動的にポップアップ用にフォーマット"""
        sections = []

        # 除外するキー（表示しない項目）
        excluded_keys = {"flag", "latlng"}  # flagは別途表示、latlngは座標として表示

        # 表示名のマッピング
        display_names = {
            "language": "Language",
            "tld": "Domain",
            "crosswalk_stripes": "Crosswalk Stripes",
            "crosswalk_features": "Crosswalk Features",
            "sign_back": "Sign Back",
            "camera": "Camera",
        }

        # 動的フィールドの処理
        street_terms = DataProcessor.process_field("#dynamic_street_terms", info)
        if street_terms and street_terms != "No street terms available":
            sections.append(f"<b>Street Terms:</b> {street_terms}")

        # 通常のフィールドを動的に処理
        for key, value in info.items():
            if key in excluded_keys:
                continue

            display_name = display_names.get(key, key.replace("_", " ").title())

            if isinstance(value, list):
                formatted_value = ", ".join(str(v) for v in value)
            elif isinstance(value, dict):
                # ネストした辞書は無視（flagなど）
                continue
            else:
                formatted_value = str(value)

            if formatted_value:  # 空でない場合のみ表示
                sections.append(f"<b>{display_name}:</b> {formatted_value}")

        # フラグ説明を追加
        flag_info = info.get("flag", {})
        if flag_info.get("description"):
            sections.append(f"<b>Flag:</b> {flag_info['description']}")

        # 座標情報を追加
        latlng = info.get("latlng", [])
        if len(latlng) == 2:
            sections.append(f"<b>Coordinates:</b> {latlng[0]}, {latlng[1]}")

        return "<br><br>".join(sections)

    popup_content = format_data_for_popup(country, info)
    popup_html = f"""
    <div style="width: 300px; text-align: left; max-height: 400px; overflow-y: auto;">
        <div style="text-align: center; margin-bottom: 10px;">
            <h4>{info['flag']['emoji']} {country}</h4>
            <img src="{info['flag']['image_url']}" width="80" />
        </div>
        <div style="font-size: 12px; line-height: 1.4;">
            {popup_content}
        </div>
    </div>
    """

    # ✅ wrap-around 表示（経度ずらし）
    for offset in [-360, 0, 360]:
        lon = info["latlng"][1] + offset
        lat = info["latlng"][0]
        # 有効なラベルがある場合のみマーカーを表示
        folium.Marker(
            location=[lat, lon],
            icon=div_icon,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=country,
        ).add_to(m)

# 統計情報の表示
st.markdown(f"### 📊 Showing {filtered_count} countries")

# ▼ 横幅をブラウザ幅にフィットさせる（最大1500px）
st_folium(m, width=1500, height=1000)
