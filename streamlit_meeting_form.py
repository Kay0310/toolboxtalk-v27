import streamlit as st
from datetime import datetime
import pytz

# 페이지 설정
st.set_page_config(layout="wide")
kst = pytz.timezone("Asia/Seoul")

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.room_code = ""
    st.session_state.rooms = {}

# 로그인 페이지
if not st.session_state.logged_in:
    st.title("📋 Toolbox Talk 회의록 로그인")
    name = st.text_input("이름")
    role = st.radio("역할", ["관리자", "팀원"])
    room_code = st.text_input("회의 코드")

    if role == "관리자":
        members = st.text_area("팀원 명단 (쉼표로 구분)", "김작업,박엔지,이안전")
        if st.button("회의 시작"):
            st.session_state.rooms[room_code] = {
                "admin": name,
                "members": [m.strip() for m in members.split(",")],
                "attendees": [],
                "confirmations": [],
                "discussion": [],
                "tasks": [],
                "info": {},
                "notes": ""
            }
            st.session_state.username = name
            st.session_state.role = role
            st.session_state.room_code = room_code
            st.session_state.logged_in = True
            st.experimental_rerun()
    else:
        if st.button("입장"):
            if room_code in st.session_state.rooms and name in st.session_state.rooms[room_code]["members"]:
                st.session_state.username = name
                st.session_state.role = role
                st.session_state.room_code = room_code
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("등록되지 않은 이름이거나 잘못된 회의 코드입니다.")
    st.stop()

# 회의방
code = st.session_state.room_code
room = st.session_state.rooms[code]
user = st.session_state.username
is_admin = st.session_state.role == "관리자"
now = datetime.now(kst)

if user not in room["attendees"]:
    room["attendees"].append(user)

st.title(f"📋 Toolbox Talk 회의록 - [{code}]")

# 1. 회의 정보
st.header("1️⃣ 회의 정보")
if is_admin:
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", now.date())
        place = st.text_input("장소", "현장 A")
    with col2:
        time = st.text_input("시간", now.strftime("%H:%M"))
        task = st.text_input("작업 내용", "고소작업")
    room["info"] = {"date": str(date), "place": place, "time": time, "task": task}
else:
    info = room.get("info", {})
    st.markdown(f"- 📅 날짜: {info.get('date')} ⏰ 시간: {info.get('time')}")
    st.markdown(f"- 📍 장소: {info.get('place')} 🛠 작업: {info.get('task')}")

# 2. 참석자
st.header("2️⃣ 참석자 명단")
st.markdown(", ".join(room["attendees"]))

# 3. 논의 내용
st.header("3️⃣ 논의 내용")
if is_admin:
    risk = st.text_input("위험요소")
    measure = st.text_input("안전대책")
    if st.button("➕ 논의 내용 추가") and risk and measure:
        room["discussion"].append((risk, measure))
else:
    for idx, (r, m) in enumerate(room["discussion"], 1):
        st.markdown(f"{idx}. **{r}** → {m}")

# 4. 추가 논의 사항
st.header("4️⃣ 추가 논의 사항")
if is_admin:
    room["notes"] = st.text_area("기타 사항 입력", value=room.get("notes", ""))
else:
    st.markdown(room.get("notes", ""))

# 5. 결정사항 및 조치
st.header("5️⃣ 결정사항 및 조치")
if is_admin:
    col1, col2, col3 = st.columns(3)
    person = col1.text_input("담당자")
    duty = col2.text_input("업무/역할")
    deadline = col3.date_input("완료예정일", now.date())
    if st.button("➕ 조치 추가") and person and duty:
        room["tasks"].append((person, duty, deadline))
else:
    for p, d, due in room["tasks"]:
        st.markdown(f"- {p}: {d} (예정일: {due})")

# 6. 회의록 확인 및 서명
st.header("6️⃣ 회의록 확인 및 서명")
if user not in room["confirmations"]:
    if st.button("✅ 회의 내용 확인"):
        room["confirmations"].append(user)
        st.success("확인되었습니다.")
else:
    st.info("이미 확인하셨습니다.")

# 관리자용 서명 현황
if is_admin:
    st.markdown(f"✔ 확인 완료: {len(room['confirmations'])} / {len(room['members'])}")
    for name in room["members"]:
        status = "✅" if name in room["confirmations"] else "❌"
        st.markdown(f"- {name} {status}")

# 인쇄용 미리보기
with st.expander("🖨 인쇄용 미리보기"):
    html = f"""
    <div style='font-family:sans-serif; font-size:14px; line-height:1.6; padding:20px;'>
        <h2 style='text-align:center;'>Toolbox Talk 회의록 - {code}</h2>
        <p style='text-align:center;'>리더: {room['admin']}</p>
        <p><b>날짜:</b> {room['info'].get('date')} ⏰ <b>시간:</b> {room['info'].get('time')}</p>
        <p><b>장소:</b> {room['info'].get('place')} 🛠 <b>작업:</b> {room['info'].get('task')}</p>
        <h4>참석자</h4>
        <ul>{"".join(f"<li>{a}</li>" for a in room['attendees'])}</ul>
        <h4>논의 내용</h4>
        <ul>{"".join(f"<li>{r} → {m}</li>" for r, m in room['discussion'])}</ul>
        <h4>추가 논의 사항</h4>
        <p>{room['notes']}</p>
        <h4>결정사항 및 조치</h4>
        <ul>{"".join(f"<li>{p}: {d} (예정일: {due})</li>" for p, d, due in room['tasks'])}</ul>
        <h4>서명</h4>
        <ul>{"".join(f"<li>{n} (확인 완료)</li>" for n in room['confirmations'])}</ul>
        <hr><p style='text-align:right; font-size:12px;'>App. support by HealSE Co., Ltd.</p>
    </div>
    """
    st.components.v1.html(html, height=1600, scrolling=True)