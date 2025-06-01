# poetry run streamlit run geogessr_app/geogessr_app.py

import folium
import numpy as np
import streamlit as st
import yaml
from config.char_config import CHAR_TO_LANGUAGES
from config.data_processor import DataProcessor
from config.field_config import (
    DISPLAY_OPTIONS,
    FILTERABLE_FIELDS,
    field_options,
    icon_options,
)
from config.number_plate_config import has_number_plate_config
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
    """数値フィールドに応じて背景色を取得（パーセンタイル順位ベース）"""
    # 元の値を解析
    parsed_value = parse_numeric_value(value)

    if parsed_value is None or percentiles is None:
        return "white"

    # パーセンタイル順位を計算（0-100の範囲）
    values = percentiles["values"]
    percentile_rank = (np.sum(values < parsed_value) / len(values)) * 100

    # パーセンタイル順位を0-1に正規化
    normalized = percentile_rank / 100

    # グラデーション色を計算（赤→黄→緑）
    if normalized < 0.5:
        # 赤から黄色へのグラデーション
        ratio = normalized * 2  # 0-1に変換
        red = 255
        green = int(255 * ratio)
        blue = 0
    else:
        # 黄色から緑へのグラデーション
        ratio = (normalized - 0.5) * 2  # 0-1に変換
        red = int(255 * (1 - ratio))
        green = 255
        blue = 0

    # 透明度を調整して見やすくする
    alpha = 0.4
    return f"rgba({red}, {green}, {blue}, {alpha})"


def get_legend_info(field_path: str, percentiles: dict) -> list:
    """フィールドと分布に応じた凡例情報を取得（パーセンタイル順位ベース）"""
    if not percentiles:
        return []

    # パーセンタイル順位ベースの凡例
    return [
        ("0-20%", "rgba(255, 0, 0, 0.4)", "Bottom quintile"),
        ("20-40%", "rgba(255, 128, 0, 0.4)", "Second quintile"),
        ("40-60%", "rgba(255, 255, 0, 0.4)", "Middle quintile"),
        ("60-80%", "rgba(128, 255, 0, 0.4)", "Fourth quintile"),
        ("80-100%", "rgba(0, 255, 0, 0.4)", "Top quintile"),
    ]


def get_display_content(country: str, info: dict, field_path: str) -> str:
    """表示用コンテンツを取得"""
    # 国名情報をinfoに追加（DataProcessorで使用）
    info_with_country = {**info, "_country_name": country}

    # DataProcessorを使用して動的/静的フィールドを統一的に処理
    value = DataProcessor.process_field(field_path, info_with_country)

    if isinstance(value, list):
        formatted_value = ", ".join(str(v) for v in value)
    elif not isinstance(value, str):
        formatted_value = str(value) if value is not None else ""
    else:
        formatted_value = value

    return formatted_value


def create_display_html(
    country: str,
    info: dict,
    content_field: str,
    show_flag: bool,
    show_country_name: bool,
    bg_color: str = "white",
) -> str:
    """表示用HTMLを生成"""

    # 特別な表示処理が必要なフィールドかチェック
    if DataProcessor.is_special_field(content_field):
        special_html = DataProcessor.create_special_html(
            country, info, content_field, show_flag, show_country_name, bg_color
        )
        if special_html:
            return special_html
        else:
            # 特別処理に失敗した場合はフォールバック
            content = "No config available"
    else:
        content = get_display_content(country, info, content_field)

    # 通常のテキスト表示処理
    # フラグアイコンの準備
    flag_html = ""
    if show_flag:
        flag_url = info.get("flag", {}).get("image_url", "")
        if flag_url:
            flag_html = f'<img src="{flag_url}" style="width: 40px; height: auto; display: block; margin: 0 auto;" />'

    # 国名プレフィックスの準備
    prefix_text = ""
    if show_country_name:
        prefix_text = f"{country}: "

    # 最終的な表示テキスト
    display_text = f"{prefix_text}{content}" if content else ""

    if flag_html:
        # フラグアイコン付きの場合
        html = f"""
        <div style="text-align: center; font-size: 10px;">
            {flag_html}
            {f'<div style="display: inline-block; background: {bg_color}; padding: 1px 4px; border-radius: 4px; max-width: 200px; word-wrap: break-word; border: 1px solid #666; color: #000;">{display_text}</div>' if display_text else ""}
        </div>
        """
    else:
        # テキストのみの場合
        html = f"""
        <div style="text-align: center; font-size: 10px;">
            <div style="display: inline-block; background: {bg_color}; padding: 2px 6px; border-radius: 4px; max-width: 200px; word-wrap: break-word; line-height: 1.2; border: 1px solid #666; color: #000;">
                {display_text}
            </div>
        </div>
        """

    return html


display_config = DISPLAY_OPTIONS.get("prepend_country_name", {})
data = load_data()

# ▼ 表示観点（サイドバー）
st.sidebar.write("### 🎯 Display Field")
selected_field = st.sidebar.selectbox(
    "Content Field",
    list(field_options.keys()),
    index=0,
)
content_field = field_options[selected_field]

st.sidebar.write("### 🖼️ Display Options")
show_flag = st.sidebar.checkbox("Show Flag Icon", value=True)
show_country_name = st.sidebar.checkbox("Show Country Name", value=True)

# ▼ 数値フィールドの分布計算と凡例表示
numeric_percentiles = None
if (
    content_field in FILTERABLE_FIELDS
    and FILTERABLE_FIELDS[content_field][0] == "number"
):
    numeric_percentiles = calculate_numeric_percentiles(data, content_field)

    if numeric_percentiles:
        st.markdown("### 🎨 Color Legend (Based on Data Distribution)")
        legend_items = get_legend_info(content_field, numeric_percentiles)

        # 統計情報も表示
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.markdown(f"**Field:** {FILTERABLE_FIELDS[content_field][1]}")
            st.markdown(
                f"**Total countries with data:** {len(numeric_percentiles['values'])}"
            )
        with stats_col2:
            st.markdown(
                f"**Range:** {numeric_percentiles['min']:.0f} - {numeric_percentiles['max']:.0f}"
            )
            st.markdown(f"**Median:** {numeric_percentiles['median']:.0f}")

        # 色の凡例（パーセンタイル順位ベース）
        if legend_items:
            st.markdown("#### Color Scale (Percentile Ranking)")
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
if "filter_counter" not in st.session_state:
    st.session_state.filter_counter = 0

# メイン領域にフィルター表示
with st.expander("Filters", expanded=True):
    if st.button("+ Add Filter"):
        # 現在選択されているContent Fieldを正確に判定
        if content_field in FILTERABLE_FIELDS:
            default_field = content_field
        else:
            # フィルター不可能な場合はlanguageをデフォルトに
            default_field = "language"

        st.session_state.filter_counter += 1
        st.session_state.filters.append(
            {
                "field": default_field,
                "match": "contains",
                "value": "",
                "id": st.session_state.filter_counter,
            }
        )

    for i, f in enumerate(st.session_state.filters):
        cols = st.columns([2, 2, 4, 1])
        with cols[0]:
            # フィルターIDを使ってユニークなkeyを生成
            filter_id = f.get("id", i)
            f["field"] = st.selectbox(
                "Field",
                sorted(FILTERABLE_FIELDS.keys()),
                index=(
                    sorted(FILTERABLE_FIELDS.keys()).index(f["field"])
                    if f["field"] in FILTERABLE_FIELDS
                    else 0
                ),
                key=f"field_{filter_id}",
            )
        with cols[1]:
            f["match"] = st.selectbox(
                "Match", ["contains", "equals"], key=f"match_{filter_id}"
            )
        with cols[2]:
            help_text = FILTERABLE_FIELDS.get(f["field"], ("", ""))[1]
            f["value"] = st.text_input(
                f"Value ({help_text})", key=f"value_{filter_id}", value=f["value"]
            )
        with cols[3]:
            if st.button("❌", key=f"remove_{filter_id}"):
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

    # 選択された文字すべてを使用する言語を取得（AND演算）
    matching_langs = get_and_matching_languages(selected_chars, CHAR_TO_LANGUAGES)

    st.markdown(f"**Selected characters:** {' '.join(selected_chars)}")
    if matching_langs:
        st.markdown(
            f"**Matching languages (uses ALL selected characters):** {', '.join(sorted(matching_langs))}"
        )
    else:
        st.markdown("**No languages use ALL of the selected characters together**")

    # 街路表記モードの場合は対応する街路表記をテーブル形式で表示
    if content_field == "#dynamic_street_terms" and matching_langs:
        st.markdown("#### 🛣️ Street Terms for Selected Languages")

        # テーブル形式で見やすく表示
        street_data = []
        for lang in matching_langs:
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

# デバッグ情報を表示
if content_field == "#number_plate_visual":
    debug_info = []
    for country, info in data.items():
        if has_number_plate_config(info):
            debug_info.append(country)

    st.write(f"Countries with number plate config: {', '.join(debug_info)}")
    st.write(f"Total countries with config: {len(debug_info)}")

filtered_count = 0
for country, info in data.items():
    if selected_chars and not matches_selected_language(info, matching_langs):
        continue
    if not passes_all_filters(info, st.session_state.filters):
        continue

    content = get_display_content(country, info, content_field)

    # 有効な値がない場合（空文字、None、"No ... available"など）はスキップ
    def has_valid_content(content_text, field_key):
        # 特別フィールドの場合はDataProcessorで判定
        if DataProcessor.is_special_field(field_key):
            if field_key == "#number_plate_visual":
                return has_number_plate_config(info)
            # 他の特別フィールドもここで処理
            return False

        if not content_text or content_text.strip() == "":
            return False
        if (
            "No " in content_text and "available" in content_text
        ):  # "No street terms available"など
            return False
        return True

    if not has_valid_content(content, content_field):
        continue

    # ここまで来た場合のみカウント
    filtered_count += 1

    # 数値フィールドの場合は背景色を取得
    raw_value = DataProcessor.process_field(content_field, info)
    bg_color = get_background_color_for_numeric_field(
        content_field, raw_value, numeric_percentiles
    )

    # 表示用HTMLを生成
    html = create_display_html(
        country, info, content_field, show_flag, show_country_name, bg_color
    )
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
            "gdp_per_capita": "GDP per capita",
            "number_plate": "Number Plate",
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
    <div style="width: 300px; text-align: left; max-height: 400px; overflow-y: auto; background: #fff; color: #000; border: 1px solid #666;">
        <div style="text-align: center; margin-bottom: 10px; padding: 10px; background: #f8f9fa; border-bottom: 1px solid #ddd;">
            <h4 style="margin: 0 0 8px 0; color: #000;">{info['flag']['emoji']} {country}</h4>
            <img src="{info['flag']['image_url']}" width="80" />
        </div>
        <div style="font-size: 12px; line-height: 1.4; padding: 10px; color: #000;">
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
