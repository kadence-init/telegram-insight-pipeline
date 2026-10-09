"""
Модуль для визуализации данных (Load/Present).
Строит интерактивный дашборд на базе фреймворка Streamlit,
используя Pandas для манипуляции данными и Plotly для продвинутой графики.
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def create_dashboard(data: list):
    """
    Принимает на вход список словарей и генерирует на их основе веб-дашборд.

    Args:
        data: Список словарей с результатами AI-анализа.
    """
    if not data:
        st.error("Нет данных для отображения.")
        return

    # Конфигурация страницы для широкого макета
    st.set_page_config(layout="wide")
    st.title("Аналитический дашборд новостных постов")

    # Преобразование данных в DataFrame для удобного анализа
    df = pd.DataFrame(data)

    # --- Верхнеуровневые метрики (KPI) ---
    st.header("Общая Сводка")
    col1, col2, col3 = st.columns(3)
    col1.metric("Всего постов", len(df))
    col2.metric("Уникальных каналов", df["source_channel"].nunique())
    col3.metric("Преобладающая тональность", df["sentiment"].mode()[0])

    st.subheader("Проанализированные каналы:")
    unique_channels = df["source_channel"].unique()
    # Использование HTML для кастомного отображения элементов
    st.write(
        f"""
        <div style="display: flex; flex-wrap: wrap; gap: 5px;">
            {''.join([f'<span style="background-color: #f0f2f6; color: black; border-radius: 10px; padding: 5px 10px;">{channel}</span>' for channel in unique_channels])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --- Визуализация распределения тем ---
    # Нормализация данных: "взрываем" списки тем для агрегации
    all_topics = df.explode("topics")
    topic_counts = all_topics["topics"].value_counts()

    fig_col1, fig_col2 = st.columns(2)
    with fig_col1:
        st.header("Топ-5 тем")
        top_5_topics = topic_counts.head(5)
        # Использование Plotly для создания интерактивной круговой диаграммы
        fig = px.pie(
            values=top_5_topics.values,
            names=top_5_topics.index,
            title="Распределение 5 самых популярных тем",
        )
        st.plotly_chart(fig, width="stretch")

    with fig_col2:
        st.header("Все темы")
        # Стандартная гистограмма Streamlit для обзора всех тем
        st.bar_chart(topic_counts)

    st.divider()

    # --- Интерактивная таблица с возможностью фильтрации ---
    st.header("Детальный Анализ Постов")
    channels_list = ["Все каналы"] + df["source_channel"].unique().tolist()
    # Интерактивный виджет для фильтрации данных
    selected_channel = st.selectbox("Фильтр по каналу:", channels_list)

    if selected_channel == "Все каналы":
        filtered_df = df
    else:
        filtered_df = df[df["source_channel"] == selected_channel]

    st.dataframe(filtered_df)


if __name__ == "__main__":
    # Блок для автономной проверки работоспособности модуля
    print("--- ЗАПУСК dashboard_core.py В РЕЖИМЕ ПРОВЕРКИ ---")
    fake_analysis_data = [
        {
            "summary": "Сводка 1",
            "sentiment": "Negative",
            "topics": ["AI", "Бизнес"],
            "source_id": 1,
            "source_channel": "Канал 1",
        },
        {
            "summary": "Сводка 2",
            "sentiment": "Positive",
            "topics": ["Технологии", "Гаджеты"],
            "source_id": 2,
            "source_channel": "Канал 2",
        },
        {
            "summary": "Сводка 3",
            "sentiment": "Neutral",
            "topics": ["Финансы", "Политика", "AI"],
            "source_id": 3,
            "source_channel": "Канал 1",
        },
    ]
    create_dashboard(fake_analysis_data)
