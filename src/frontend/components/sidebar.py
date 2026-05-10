"""Componente de sidebar (menu lateral). Reutilizável em todas as páginas."""

import streamlit as st

from src.backend.repository import EquipamentoRepository


def render_sidebar() -> None:
    repo = EquipamentoRepository()
    total = len(repo.listar())

    with st.sidebar:
        st.markdown("## ⚙️ Gestão de Ativos")
        st.caption("Sprint 1 — Cadastro Técnico")
        st.markdown("---")

        st.markdown("### Navegação")

        if st.button(
            "🏠 Consulta de Equipamentos",
            use_container_width=True,
            type="primary" if st.session_state.page == "consulta" else "secondary",
        ):
            st.session_state.page = "consulta"
            st.session_state.selected_equipment_id = None
            st.rerun()

        if st.button(
            "📝 Novo Cadastro",
            use_container_width=True,
            type="primary" if (
                st.session_state.page == "cadastro"
                and st.session_state.selected_equipment_id is None
            ) else "secondary",
        ):
            st.session_state.page = "cadastro"
            st.session_state.selected_equipment_id = None
            st.rerun()

        if st.button(
            "📊 Dados Brutos dos Sensores",
            use_container_width=True,
            type="primary" if st.session_state.page == "dados_brutos" else "secondary",
        ):
            st.session_state.page = "dados_brutos"
            st.rerun()

        st.markdown("---")
        st.metric("Equipamentos cadastrados", total)

        st.markdown("---")
        with st.expander("🔮 Próximos sprints", expanded=False):
            st.caption(
                "• **Sprint 2**: integração com modelo preditivo  \n"
                "• **Sprint 3**: detecção de anomalias e alertas  \n"
                "• **Sprint 4**: dashboard analítico & RUL  \n"
                "• **Sprint 5**: integração com sensores reais"
            )

        st.caption("FIAP Challenge • 2025")
