import json

import folium
import streamlit as st
from config.field_config import CHAR_TO_LANGUAGES, FILTERABLE_FIELDS, field_options
from folium import DivIcon
from streamlit_folium import st_folium

st.set_page_config(page_title="Geo Map with Filters", layout="wide")
st.title("🗺️ Country Info Map with Dynamic Filters and Responsive Map")


@st.cache_data
def load_data() -> dict:
    with open("geo_data.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ネストキーの取得
def get_nested_value(obj: dict, dotted_key: str):
    try:
        for key in dotted_key.split("."):
            obj = obj[key]
        return obj
    except Exception:
        return None


def get_display_label(
    country: str, info: dict, field_path: str, display_config: dict
) -> str:
    if field_path == "#country":
        return country
    if field_path == "#notext":
        return ""
    value = get_nested_value(info, field_path)
    if isinstance(value, list):
        value = ", ".join(value)
    elif not isinstance(value, str):
        value = str(value)
    if display_config.get(field_path, False):
        return f"{country}: {value}"
    return value


data = load_data()
display_config = data.get("_display_options", {}).get("prepend_country_name", {})
data = {k: v for k, v in data.items() if not k.startswith("_")}

# ▼ 表示観点（サイドバー）
st.sidebar.write("### 🎯 Display Field")
selected_view = st.sidebar.radio(
    "",
    list(field_options.keys()),
    index=list(field_options.keys()).index("Flag (image only)"),
    label_visibility="collapsed",
)
icon_key, label_key = field_options[selected_view]

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
            f"<div style='background-color:{color}; padding:3px; border-radius:5px;'>",
            unsafe_allow_html=True,
        )
        char_states[char] = st.checkbox(char, key=f"char_{char}")
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
            f["value"] = st.text_input("Value", key=f"value_{i}", value=f["value"])
        with cols[3]:
            if st.button("❌", key=f"remove_{i}"):
                st.session_state.filters.pop(i)
                st.rerun()


# フィルター判定
def passes_all_filters(info: dict, filters: list[dict]) -> bool:
    for f in filters:
        value = get_nested_value(info, f["field"])
        if value is None:
            return False

        if isinstance(value, list):
            if f["match"] == "contains":
                if not any(f["value"].lower() in v.lower() for v in value):
                    return False
            elif f["match"] == "equals":
                if f["value"].lower() not in [v.lower() for v in value]:
                    return False
        else:
            if f["match"] == "contains":
                if f["value"].lower() not in str(value).lower():
                    return False
            elif f["match"] == "equals":
                if f["value"].lower() != str(value).lower():
                    return False
    return True


# 判定：ラベルを表示するか
def should_display_label(label_key: str) -> bool:
    return label_key != "#notext"


# ▼ チェックされた文字に対応する言語を表示
if selected_chars:
    st.markdown("### 🧠 Languages Matching Selected Characters")
    for char in selected_chars:
        langs = CHAR_TO_LANGUAGES.get(char, [])
        st.markdown(f"**{char}** → {', '.join(langs)}")

# 地図の作成
m = folium.Map(location=[0, 0], zoom_start=2)

for country, info in data.items():
    if selected_chars and not matches_selected_language(info, matching_langs):
        continue
    if not passes_all_filters(info, st.session_state.filters):
        continue

    icon_url = get_nested_value(info, icon_key) if icon_key != "#noimage" else None
    label = get_display_label(country, info, label_key, display_config)

    if icon_url:
        html = f"""
        <div style="text-align: center; font-size: 10px;">
            <img src="{icon_url}" style="width: 40px; height: auto; display: block; margin: 0 auto;" />
            {f'<div style="display: inline-block; background: white; padding: 1px 4px; border-radius: 4px;">{label}</div>' if label else ""}
        </div>
        """
    else:
        html = f"""
        <div style="text-align: center; font-size: 10px;">
            <div style="display: inline-block; background: white; padding: 1px 4px; border-radius: 4px;">
                {label}
            </div>
        </div>
        """

    div_icon = DivIcon(icon_size=(40, 40), icon_anchor=(20, 20), html=html)

    popup_html = f"""
    <div style="width: 200px; text-align: center;">
        <h4>{info['flag']['emoji']} {country}</h4>
        <img src="{info['flag']['image_url']}" width="80" /><br>
        <p><b>Flag:</b> {info['flag']['description']}</p>
        <p><b>Language:</b> {', '.join(info['language'])}</p>
        <p><b>Domain:</b> {info['tld']}</p>
    </div>
    """

    # ✅ wrap-around 表示（経度ずらし）
    for offset in [-360, 0, 360]:
        lon = info["latlng"][1] + offset
        lat = info["latlng"][0]
        folium.Marker(
            location=[lat, lon],
            icon=div_icon,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=country,
        ).add_to(m)

# ▼ 横幅をブラウザ幅にフィットさせる（最大1500px）
st_folium(m, width=1500, height=1000)
