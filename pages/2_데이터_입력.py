import streamlit as st
import pandas as pd
from datetime import date

try:
    from app.logic import (
        load_input_logs,
        append_manual_entry,
        normalize_uploaded_df,
        calculate_input_summary,
        calculate_input_quality,
        get_input_preview,
        get_today_date_str,
    )
except ModuleNotFoundError:
    from logic import (
        load_input_logs,
        append_manual_entry,
        normalize_uploaded_df,
        calculate_input_summary,
        calculate_input_quality,
        get_input_preview,
        get_today_date_str,
    )

st.set_page_config(
    page_title="데이터 입력",
    layout="wide"
)

EXPECTED_COLUMNS = [
    "date",
    "time_slot",
    "site",
    "zone",
    "task_type",
    "missed_ppe",
    "is_violated",
    "team",
    "note",
]


# =========================
# 유틸
# =========================
def summary_metrics(df: pd.DataFrame):
    total_count = len(df)
    violated_count = int((df["is_violated"] == 1).sum()) if not df.empty else 0
    normal_count = total_count - violated_count

    today_count = 0
    if not df.empty and "date" in df.columns:
        today_str = str(pd.Timestamp.today().date())
        today_count = int((df["date"].astype(str) == today_str).sum())

    return total_count, today_count, violated_count, normal_count


def make_manual_entry(
    date_value,
    time_slot,
    site,
    zone,
    task_type,
    missed_ppe,
    team,
    worker_id,
    note,
):
    missed_ppe = str(missed_ppe).strip()
    is_violated = 0 if missed_ppe == "" or missed_ppe == "정상 착용" else 1

    if missed_ppe == "정상 착용":
        missed_ppe = ""

    return {
        "date": str(date_value),
        "time_slot": time_slot,
        "site": site,
        "zone": zone,
        "task_type": task_type,
        "missed_ppe": missed_ppe,
        "ppe_type": missed_ppe,
        "is_violated": is_violated,
        "team": team,
        "worker_name": worker_id if worker_id.strip() else team,
        "note": note,
    }


def save_uploaded_rows_to_db(upload_df: pd.DataFrame):
    normalized_df = normalize_uploaded_df(upload_df)

    success_count = 0
    fail_count = 0
    errors = []

    for _, row in normalized_df.iterrows():
        entry = {
            "date": row.get("date", ""),
            "time_slot": row.get("time_slot", ""),
            "site": row.get("site", ""),
            "zone": row.get("zone", ""),
            "task_type": row.get("task_type", ""),
            "missed_ppe": row.get("missed_ppe", ""),
            "ppe_type": row.get("missed_ppe", ""),
            "is_violated": int(row.get("is_violated", 0)),
            "team": row.get("team", ""),
            "worker_name": row.get("team", "미지정 작업자"),
            "note": row.get("note", ""),
        }

        result = append_manual_entry(entry)

        if result.get("status") == "success":
            success_count += 1
        else:
            fail_count += 1
            errors.append(result.get("message", "알 수 없는 오류"))

    return normalized_df, success_count, fail_count, errors


# =========================
# 스타일
# =========================
st.markdown("""
<style>
.block-container {
    padding-top: 2.4rem;
    padding-bottom: 2rem;
    max-width: 1480px;
}

.main-title {
    font-size: 2.05rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
}

.sub-title {
    color: #64748b;
    font-size: 1rem;
    margin-bottom: 1rem;
}

.section-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    margin-bottom: 1rem;
}

.section-title {
    font-size: 1.12rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 0.5rem;
}

.help-box {
    border: 1px dashed #cbd5e1;
    background: #f8fafc;
    border-radius: 16px;
    padding: 16px;
    color: #475569;
    font-size: 0.9rem;
    line-height: 1.6;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 18px 18px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    margin-bottom: 0.8rem;
}

.metric-label {
    color: #64748b;
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.metric-value {
    color: #0f172a;
    font-size: 1.9rem;
    font-weight: 800;
    line-height: 1;
}

.stButton > button {
    border-radius: 14px;
    font-weight: 800;
    min-height: 44px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# 데이터 로드
# =========================
df = load_input_logs()
total_count, today_count, violated_count, normal_count = summary_metrics(df)
today_str = get_today_date_str()
summary = calculate_input_summary(df, today_str)
quality = calculate_input_quality(df)


# =========================
# 헤더
# =========================
st.markdown('<div class="main-title">데이터 입력</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">CSV 업로드 또는 수기 입력으로 PPE 점검 데이터를 PostgreSQL에 저장합니다</div>',
    unsafe_allow_html=True
)

left, right = st.columns([2.2, 1])


# =========================
# 좌측: 업로드 + 입력
# =========================
with left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">CSV 파일 업로드</div>', unsafe_allow_html=True)
    st.caption("업로드한 CSV 데이터는 파일이 아니라 PostgreSQL inspections 테이블에 저장됩니다.")

    uploaded_file = st.file_uploader(
        "CSV 파일 선택",
        type=["csv"],
        label_visibility="collapsed"
    )

    st.markdown(
        """
        <div class="help-box">
            <b>예시 컬럼 구조</b><br>
            date,time_slot,site,zone,task_type,missed_ppe,is_violated,team,note
            <br><br>
            <b>예시 값</b><br>
            2026-05-30,오후,현장1,고소작업구역,고소작업,랜야드,1,A팀,업로드 테스트
        </div>
        """,
        unsafe_allow_html=True
    )

    if uploaded_file is not None:
        try:
            upload_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
        except Exception:
            uploaded_file.seek(0)
            upload_df = pd.read_csv(uploaded_file)

        normalized_df = normalize_uploaded_df(upload_df)

        st.write("업로드 미리보기")
        st.dataframe(
            normalized_df.head(10).astype(str).astype(object),
            use_container_width=True
        )

        if st.button("업로드 데이터 DB 저장", use_container_width=True):
            normalized_df, success_count, fail_count, errors = save_uploaded_rows_to_db(upload_df)

            if success_count > 0:
                st.success(f"PostgreSQL 저장 완료: {success_count}건")

            if fail_count > 0:
                st.error(f"저장 실패: {fail_count}건")
                with st.expander("오류 상세"):
                    for err in errors[:10]:
                        st.write(err)

            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">수기 데이터 입력</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    c5, c6 = st.columns(2)
    c7, c8 = st.columns(2)

    with c1:
        manual_date = st.date_input("날짜", value=date.today())
    with c2:
        manual_time_slot = st.selectbox("시간대", ["오전", "점심직후", "오후"])

    with c3:
        manual_site = st.selectbox("현장", ["현장1", "현장2", "현장3"])
    with c4:
        manual_zone = st.selectbox(
            "작업구역",
            ["고소작업구역", "절단작업구역", "자재운반구역", "설비점검구역"]
        )

    with c5:
        manual_team = st.selectbox("팀", ["A팀", "B팀", "C팀", "D팀"])
    with c6:
        manual_worker_id = st.text_input("작업자 ID", placeholder="예 : W-1234")

    with c7:
        manual_task_type = st.selectbox(
            "작업유형",
            ["고소작업", "절단작업", "자재운반", "설비점검"]
        )
    with c8:
        manual_missed_ppe = st.selectbox(
            "누락 PPE",
            ["정상 착용", "장갑", "안전모", "랜야드"]
        )

    manual_note = st.text_input("비고", placeholder="추가 메모 입력")

    if st.button("수기 입력 DB 저장", use_container_width=True):
        entry = make_manual_entry(
            date_value=manual_date,
            time_slot=manual_time_slot,
            site=manual_site,
            zone=manual_zone,
            task_type=manual_task_type,
            missed_ppe=manual_missed_ppe,
            team=manual_team,
            worker_id=manual_worker_id,
            note=manual_note,
        )

        result = append_manual_entry(entry)

        if result.get("status") == "success":
            st.success(result["message"])
            st.rerun()
        else:
            st.error(result.get("message", "DB 저장 실패"))

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">데이터 미리보기</div>', unsafe_allow_html=True)
    st.caption("PostgreSQL inspections 테이블 최근 20건 기준입니다.")

    preview_df = df.tail(20).iloc[::-1] if not df.empty else df
    st.dataframe(
        preview_df.astype(str).astype(object),
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# 우측: 요약
# =========================
with right:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">데이터 상태 요약</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">총 데이터 건수</div>
            <div class="metric-value">{total_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">오늘 데이터</div>
            <div class="metric-value">{today_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">위험 데이터</div>
            <div class="metric-value">{violated_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">정상 데이터</div>
            <div class="metric-value">{normal_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">완성도</div>
            <div class="metric-value">{quality.get("completeness_rate", 0)}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)