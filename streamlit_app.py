import streamlit as st
import math
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="직접 그리는 곱셈 일의 자리 규칙", layout="wide")

st.title("✏️ 곱셈 일의 자리 규칙을 직접 그려보세요!")

# -----------------------------
# 1. 단 입력
# -----------------------------
dan = st.slider("단(1~9)을 선택하세요", 1, 9, 6)

# -----------------------------
# 2. 숫자 0~9 원형 좌표 계산
# -----------------------------
def generate_positions(radius=200, center=(250, 250)):
    pos = {}
    for i in range(10):
        angle = math.radians(90 - i * 36)
        x = center[0] + radius * math.cos(angle)
        y = center[1] - radius * math.sin(angle)
        pos[i] = (x, y)
    return pos

positions = generate_positions()

# -----------------------------
# 3. 정답 경로 계산
# -----------------------------
correct_path = []
current = 0
while True:
    next_num = (current + dan) % 10
    correct_path.append((current, next_num))
    current = next_num
    if next_num == 0:
        break

st.markdown(f"### 🔁 {dan}단의 일의 자리 규칙 경로 (정답): **{[a for a,b in correct_path]}** → 0")


# -----------------------------
# 4. 바탕 이미지 (숫자판) 만들기
# -----------------------------
base = Image.new("RGB", (500, 500), "white")
draw = ImageDraw.Draw(base)

draw.ellipse((50, 50, 450, 450), outline="black", width=3)

# 숫자 표시
for num, (x, y) in positions.items():
    draw.text((x - 5, y - 5), str(num), fill="black")

st.image(base, caption="원판")

# -----------------------------
# 5. 캔버스 제공
# -----------------------------
st.markdown("## 🎨 직접 선을 그어보세요")

canvas_result = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=4,
    stroke_color="blue",
    background_image=base,
    height=500,
    width=500,
    drawing_mode="freedraw",
    key="drawing",
)

# -----------------------------
# 6. 채점하기 버튼
# -----------------------------
if st.button("채점하기"):
    if canvas_result.json_data is None:
        st.warning("선을 먼저 그려주세요!")
    else:
        # 사용자가 그린 선의 좌표 모음
        user_lines = canvas_result.json_data["objects"]

        # 정답 판정 이미지 생성
        result_img = base.copy()
        rdraw = ImageDraw.Draw(result_img)

        # 정답 선(초록색) 그리기
        for a, b in correct_path:
            x1, y1 = positions[a]
            x2, y2 = positions[b]
            rdraw.line((x1, y1, x2, y2), fill="green", width=4)

        # 사용자가 그린 선을 검사
        for line in user_lines:
            if line["type"] != "path":
                continue

            # 사용자가 그린 좌표 중 시작점과 끝점만 사용
            points = line["path"]

            # path 형식이 [["M", x, y], ["L", x, y], ...] 형태라서 정리 필요
            coords = [(p[1], p[2]) for p in points if p[0] in ["M", "L"]]

            if len(coords) < 2:
                continue

            ux, uy = coords[0]
            vx, vy = coords[-1]

            # 사용자 선이 어떤 두 숫자를 연결했는지 확인
            start_num = min(positions, key=lambda k: (positions[k][0]-ux)**2 + (positions[k][1]-uy)**2)
            end_num = min(positions, key=lambda k: (positions[k][0]-vx)**2 + (positions[k][1]-vy)**2)

            # 정답인지 확인
            if (start_num, end_num) in correct_path:
                # 정답 선 (초록색)
                rdraw.line((positions[start_num], positions[end_num]), fill="green", width=6)
            else:
                # 오답 선 (빨간색)
                rdraw.line((positions[start_num], positions[end_num]), fill="red", width=6)

        st.image(result_img, caption="채점 결과")
