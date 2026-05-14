import pandas as pd
import streamlit as st
import textwrap



from dashboard.components import topbar


def empty_state(message: str):
    st.markdown(
        f"""
        <div class="empty-state">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )



def html_block(content: str):
    compact_html = " ".join(
        line.strip()
        for line in textwrap.dedent(content).strip().splitlines()
        if line.strip()
    )

    st.markdown(compact_html, unsafe_allow_html=True)    

def render_metric_table():
    rows = [
        {
            "modelo": "Regresión logística ordinal",
            "exactitud": "0.351 ± 0.016",
            "f1": "0.306 ± 0.015",
            "qwk": "0.168 ± 0.039",
            "mae": "0.914 ± 0.033",
            "auc": "0.562 ± 0.009",
            "tiempo": "76.8 ± 4.6s",
            "interp": '<span class="mp-pill green">Alta</span>',
            "selected": "",
        },
        {
            "modelo": "Random Forest",
            "exactitud": "0.461 ± 0.017",
            "f1": "0.453 ± 0.017",
            "qwk": "0.219 ± 0.045",
            "mae": "0.799 ± 0.044",
            "auc": "0.683 ± 0.019",
            "tiempo": "402.2 ± 114.4s",
            "interp": '<span class="mp-pill yellow">Media</span>',
            "selected": '<span class="mp-pill green">Seleccionado</span>',
        },
        {
            "modelo": "SVM-RBF",
            "exactitud": "0.432 ± 0.038",
            "f1": "0.422 ± 0.034",
            "qwk": "0.212 ± 0.059",
            "mae": "0.834 ± 0.063",
            "auc": "0.666 ± 0.028",
            "tiempo": "86.8 ± 8.5s",
            "interp": '<span class="mp-pill red">Baja</span>',
            "selected": "",
        },
    ]

    html_rows = ""

    for row in rows:
        selected_class = "selected" if row["modelo"] == "Random Forest" else ""

        html_rows += f"""
        <tr class="{selected_class}">
            <td>{row["modelo"]}</td>
            <td>{row["exactitud"]}</td>
            <td>{row["f1"]}</td>
            <td>{row["qwk"]}</td>
            <td>{row["mae"]}</td>
            <td>{row["auc"]}</td>
            <td>{row["tiempo"]}</td>
            <td>{row["interp"]}</td>
            <td>{row["selected"]}</td>
        </tr>
        """

    html_block(
        f"""
        <table class="mp-table">
            <thead>
                <tr>
                    <th>Modelo</th>
                    <th>Exactitud</th>
                    <th>F1-w</th>
                    <th>QWK</th>
                    <th>MAE ordinal</th>
                    <th>AUC OvR</th>
                    <th>Tiempo</th>
                    <th>Interpretabilidad</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {html_rows}
            </tbody>
        </table>
        """

    )


def render_importance_bars():
    variables = [
        ("IA mejora transparencia electoral", 0.0360),
        ("Deepfakes generan desconfianza", 0.0294),
        ("IA mejora comunicación política", 0.0239),
        ("Bots reducen confianza informativa", 0.0235),
        ("Demanda de regulación legal", 0.0232),
        ("Riesgo de manipulación personalizada", 0.0222),
        ("Exposición a contenido político digital", 0.0180),
        ("Participación digital durante campaña", 0.0167),
        ("Percepción de automatización", 0.0165),
        ("Voto segunda vuelta", 0.0164),
    ]

    max_value = max(value for _, value in variables)

    html = ""

    for label, value in variables:
        width = value / max_value * 100

        html += f"""
        <div class="mp-bar-row">
            <div class="mp-bar-head">
                <span>{label}</span>
                <span>{value:.4f}</span>
            </div>
            <div class="mp-track">
                <div class="mp-fill" style="width:{width:.1f}%;"></div>
            </div>
        </div>
        """

    html_block(html)


def render_seed_stability():
    seeds = [
        {"seed": 0, "acc": 0.439, "auc": 0.694, "f1": 0.433, "qwk": 0.222},
        {"seed": 7, "acc": 0.474, "auc": 0.696, "f1": 0.471, "qwk": 0.201},
        {"seed": 13, "acc": 0.462, "auc": 0.659, "f1": 0.450, "qwk": 0.203},
        {"seed": 21, "acc": 0.486, "auc": 0.706, "f1": 0.474, "qwk": 0.302},
        {"seed": 42, "acc": 0.445, "auc": 0.662, "f1": 0.437, "qwk": 0.169},
    ]

    html = ""

    for item in seeds:
        acc_width = item["acc"] * 100
        auc_width = item["auc"] * 100

        html += f"""
        <div class="mp-seed">
            <div class="mp-seed-title">Seed {item["seed"]}</div>

            <div class="mp-seed-line">
                <span>Accuracy</span>
                <div class="mp-mini-track">
                    <div class="mp-mini-fill acc" style="width:{acc_width:.1f}%;"></div>
                </div>
                <strong>{acc_width:.1f}%</strong>
            </div>

            <div class="mp-seed-line">
                <span>AUC</span>
                <div class="mp-mini-track">
                    <div class="mp-mini-fill auc" style="width:{auc_width:.1f}%;"></div>
                </div>
                <strong>{item["auc"]:.3f}</strong>
            </div>
        </div>
        """

    html_block(html)


def render_class_distribution():
    clases = [
        {"clase": "Clase 1", "n": 37, "pct": 6.4},
        {"clase": "Clase 2", "n": 206, "pct": 35.8},
        {"clase": "Clase 3", "n": 165, "pct": 28.7},
        {"clase": "Clase 4", "n": 152, "pct": 26.4},
        {"clase": "Clase 5", "n": 15, "pct": 2.6},
    ]

    max_pct = max(item["pct"] for item in clases)

    html = ""

    for item in clases:
        width = item["pct"] / max_pct * 100

        html += f"""
        <div class="mp-bar-row">
            <div class="mp-bar-head">
                <span>{item["clase"]}</span>
                <span>{item["n"]} casos · {item["pct"]:.1f}%</span>
            </div>
            <div class="mp-track">
                <div class="mp-fill" style="width:{width:.1f}%;"></div>
            </div>
        </div>
        """

    html_block(html)


def render_modelos_predictivos(survey_df: pd.DataFrame):
    n_total = 575

    topbar(
        title="Modelos Predictivos",
        subtitle=(
            "Evaluación comparativa de modelos supervisados para predecir el nivel de confianza electoral "
            "a partir de variables sociodemográficas, exposición digital y percepciones sobre IA en campañas políticas digitales."
        ),
        pill_text=f"n = {n_total:,} participantes",
    )

    html_block(
        """
        <div class="mp-kpi-grid">
            <div class="mp-kpi teal">
                <div class="mp-kpi-label">Modelo seleccionado</div>
                <div class="mp-selected">Random<br>Forest</div>
                <div class="mp-kpi-help">Mejor desempeño global y permite importancia de variables</div>
            </div>

            <div class="mp-kpi blue">
                <div class="mp-kpi-label">Exactitud promedio (RF)</div>
                <div class="mp-kpi-value">46.1%</div>
                <div class="mp-kpi-help">Promedio sobre 5 semillas con split 70/30</div>
            </div>

            <div class="mp-kpi green">
                <div class="mp-kpi-label">AUC OvR (RF)</div>
                <div class="mp-kpi-value">0.683</div>
                <div class="mp-kpi-help">Capacidad discriminativa multiclase</div>
            </div>

            <div class="mp-kpi yellow">
                <div class="mp-kpi-label">QWK (RF)</div>
                <div class="mp-kpi-value">0.219</div>
                <div class="mp-kpi-help">Métrica ordinal para escala Likert de 5 niveles</div>
            </div>
        </div>
        """
    )

    with st.container(border=True, key="card_mp_metricas"):
        html_block(
            """
            <div class="section-title-card">Comparación de modelos predictivos</div>
            <div class="section-subtitle-card">
                Resultados promedio ± desviación estándar sobre 5 semillas. Target principal:
                confianza_idx_round, escala ordinal de 5 clases.
            </div>
            """
        )

        render_metric_table()

        html_block(
            """
            <div class="mp-note-green">
                <strong>Justificación de selección: Random Forest.</strong><br>
                Random Forest fue seleccionado como modelo principal porque obtuvo el mejor desempeño global:
                mayor exactitud promedio, mejor F1 ponderado, mayor QWK, menor MAE ordinal y mayor AUC OvR.
                Además, permite estimar importancia de variables, lo que facilita la interpretación sustantiva
                de los factores asociados a la confianza electoral.
            </div>
            """
        )

    st.markdown('<div class="mp-section-gap"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True, key="card_mp_importancia"):
            st.markdown(
                """
                <div class="section-title-card">Importancia de variables (Random Forest)</div>
                <div class="section-subtitle-card">
                    Variables con mayor contribución al modelo predictivo seleccionado.
                </div>
                """,
                unsafe_allow_html=True,
            )

            render_importance_bars()

            st.markdown(
                """
                <div class="mp-note-blue">
                    Las variables con mayor peso pertenecen principalmente al bloque de percepción ciudadana
                    sobre IA: transparencia, deepfakes, comunicación política, bots, regulación y manipulación personalizada.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        with st.container(border=True, key="card_mp_estabilidad"):
            st.markdown(
                """
                <div class="section-title-card">Estabilidad por semilla (Random Forest)</div>
                <div class="section-subtitle-card">
                    Desempeño del modelo principal en cinco particiones 70/30 estratificadas.
                </div>
                """,
                unsafe_allow_html=True,
            )

            render_seed_stability()

    st.markdown('<div class="mp-section-gap"></div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="large")

    with col3:
        with st.container(border=True, key="card_mp_clases"):
            st.markdown(
                """
                <div class="section-title-card">Distribución de clases</div>
                <div class="section-subtitle-card">
                    Distribución del target confianza_idx_round en cinco niveles ordinales.
                </div>
                """,
                unsafe_allow_html=True,
            )

            render_class_distribution()

            st.markdown(
                """
                <div class="mp-note-blue">
                    La variable objetivo presenta desbalance en las clases extremas, especialmente en los niveles 1 y 5.
                    Por ello, el modelo tiende a clasificar mejor las categorías intermedias de confianza electoral.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col4:
        with st.container(border=True, key="card_mp_justificacion"):
            st.markdown(
                """
                <div class="section-title-card">Justificación técnica de los modelos</div>
                <div class="section-subtitle-card">
                    Comparación conceptual de los tres algoritmos evaluados.
                </div>
                """,
                unsafe_allow_html=True,
            )

            html_block(
                """
                <div class="mp-model-grid" style="grid-template-columns: 1fr;">
                    <div class="mp-model-card blue">
                        <div class="mp-model-title">Regresión logística ordinal</div>
                        <div class="mp-model-text">
                            Modelo interpretable y coherente con la naturaleza ordinal de la escala Likert.
                            Su desempeño fue menor, pero aporta lectura mediante odds ratios e intervalos de confianza.
                        </div>
                        <div class="mp-badge-row">
                            <span class="mp-badge">Acc: 35.1%</span>
                            <span class="mp-badge">AUC: 0.562</span>
                            <span class="mp-badge">QWK: 0.168</span>
                        </div>
                    </div>

                    <div class="mp-model-card green">
                        <div class="mp-model-title">Random Forest seleccionado</div>
                        <div class="mp-model-text">
                            Captura relaciones no lineales e interacciones entre variables.
                            Presentó el mejor rendimiento global y permite ranking de importancia de variables.
                        </div>
                        <div class="mp-badge-row">
                            <span class="mp-badge">Acc: 46.1%</span>
                            <span class="mp-badge">AUC: 0.683</span>
                            <span class="mp-badge">QWK: 0.219</span>
                        </div>
                    </div>

                    <div class="mp-model-card yellow">
                        <div class="mp-model-title">SVM-RBF</div>
                        <div class="mp-model-text">
                            Modelo no lineal con buen desempeño, pero menor interpretabilidad sustantiva.
                            Quedó por debajo de Random Forest en exactitud, F1, QWK, MAE y AUC.
                        </div>
                        <div class="mp-badge-row">
                            <span class="mp-badge">Acc: 43.2%</span>
                            <span class="mp-badge">AUC: 0.666</span>
                            <span class="mp-badge">QWK: 0.212</span>
                        </div>
                    </div>
                </div>
                """

            )

    st.markdown('<div class="mp-section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_mp_interpretacion"):
        st.markdown(
            """
            <div class="section-title-card">Lectura interpretativa</div>
            <div class="section-subtitle-card">
                El modelado predictivo permite estimar qué factores se asocian con el nivel de confianza electoral
                frente al uso de inteligencia artificial en campañas políticas digitales.
            </div>
            """,
            unsafe_allow_html=True,
        )

        html_block(
            """
            <div class="interpretation-grid">
                <div class="interpretation-box green">
                    <div class="interpretation-value">RF</div>
                    <div class="interpretation-label">
                        fue el modelo con mejor desempeño global y mayor utilidad interpretativa para el análisis.
                    </div>
                </div>

                <div class="interpretation-box blue">
                    <div class="interpretation-value">46.1%</div>
                    <div class="interpretation-label">
                        de exactitud promedio evidencia capacidad predictiva moderada en una variable perceptual compleja.
                    </div>
                </div>

                <div class="interpretation-box yellow">
                    <div class="interpretation-value">0.683</div>
                    <div class="interpretation-label">
                        de AUC OvR indica una capacidad discriminativa superior a los modelos alternativos evaluados.
                    </div>
                </div>

                <div class="interpretation-box red">
                    <div class="interpretation-value">5</div>
                    <div class="interpretation-label">
                        niveles ordinales de confianza generan mayor dificultad para clasificar las clases extremas.
                    </div>
                </div>
            </div>

            <div class="mp-note-green">
                Los resultados sugieren que la confianza electoral está más asociada con percepciones sobre el ecosistema
                digital —transparencia, deepfakes, bots, regulación y manipulación personalizada— que con variables
                sociodemográficas aisladas. La capacidad predictiva es moderada, lo cual es metodológicamente esperable
                al tratarse de una variable perceptual, ordinal y políticamente contextual.
            </div>
            """

        )

    st.caption(
        "Nota metodológica: los modelos fueron evaluados con partición estratificada 70/30 y cinco semillas "
        "(0, 7, 13, 21, 42). El target principal fue confianza_idx_round, compuesto por cinco clases ordinales. "
        "Se reportan métricas clásicas y ordinales: Exactitud, F1 ponderado, QWK, MAE ordinal y AUC OvR."
    )