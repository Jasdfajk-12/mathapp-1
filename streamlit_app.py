import streamlit as st
import numpy as np
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import math

# 페이지 설정
st.set_page_config(page_title="구구단 숫자판 게임", layout="centered")
st.title("🔢 구구단 숫자판 게임")
st.write("숫자판에 일의 자리 규칙 경로를 그려보세요!")

# ========== 함수 정의 ==========

# 일의 자리 규칙 계산 함수
def get_digit_sequence(table):
    """곱셈 단의 일의 자리 규칙 경로 계산"""
    sequence = []
    for i in range(1, 10):
        sequence.append((table * i) % 10)
    return sequence

# 원형 숫자판 좌표 계산
def get_circle_positions(center_x, center_y, radius, num_points=10):
    """원 위에 숫자 0-9를 배치하는 좌표 계산"""
    positions = {}
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    # 12시 방향부터 시작하도록 각도 조정
    angles = angles - np.pi / 2
    
    for i, angle in enumerate(angles):
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        positions[i] = (x, y)
    
    return positions

# 캔버스 생성 함수
def create_canvas_image():
    """원형 숫자판이 있는 캔버스 생성"""
    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), color="white")
    draw = ImageDraw.Draw(img)
    
    # 원 그리기
    circle_margin = 20
    draw.ellipse(
        [CENTER - RADIUS - circle_margin, CENTER - RADIUS - circle_margin,
         CENTER + RADIUS + circle_margin, CENTER + RADIUS + circle_margin],
        outline="lightgray",
        width=2
    )
    
    # 숫자 배치
    dot_radius = 8
    for num, (x, y) in CIRCLE_POSITIONS.items():
        # 점 그리기
        draw.ellipse(
            [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
            fill="lightblue",
            outline="darkblue",
            width=2
        )
        # 숫자 텍스트 추가
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
            text = str(num)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text(
                (x - text_width // 2, y - text_height // 2),
                text,
                fill="darkblue",
                font=font
            )
        except:
            pass
    
    return img

# 그려진 선 분석 함수
def analyze_drawn_lines(black_pixels, positions, threshold=30):
    """그려진 선이 연결하는 숫자 찾기"""
    segments = set()
    
    # 각 숫자 위치 근처에서 그려진 픽셀 찾기
    point_touches = {}
    for num, (x, y) in positions.items():
        nearby_pixels = (
            (black_pixels[0] > y - threshold) &
            (black_pixels[0] < y + threshold) &
            (black_pixels[1] > x - threshold) &
            (black_pixels[1] < x + threshold)
        )
        if np.any(nearby_pixels):
            point_touches[num] = True
    
    # 터치된 숫자들 정렬
    touched_numbers = sorted(point_touches.keys())
    
    # 연속된 숫자들 사이의 선분 생성
    for i in range(len(touched_numbers) - 1):
        num1 = touched_numbers[i]
        num2 = touched_numbers[i + 1]
        segment = tuple(sorted([num1, num2]))
        segments.add(segment)
    
    return segments

# 정답 경로 세그먼트 생성
def get_correct_segments(sequence, positions):
    """일의 자리 규칙 경로의 모든 세그먼트 반환"""
    segments = set()
    for i in range(len(sequence) - 1):
        num1 = sequence[i]
        num2 = sequence[i + 1]
        segment = tuple(sorted([num1, num2]))
        segments.add(segment)
    return segments

# 결과 이미지 생성
def create_result_image(base_img, correct_segments, drawn_segments, positions):
    """정답(초록색)과 오답(빨간색)을 표시한 이미지 생성"""
    result_img = base_img.copy()
    draw = ImageDraw.Draw(result_img)
    
    line_width = 3
    
    # 정답 세그먼트 그리기 (초록색)
    for segment in correct_segments:
        num1, num2 = segment
        x1, y1 = positions[num1]
        x2, y2 = positions[num2]
        draw.line([(x1, y1), (x2, y2)], fill="green", width=line_width)
    
    # 그려진 세그먼트 중 오답 표시 (빨간색)
    for segment in drawn_segments:
        if segment not in correct_segments:
            num1, num2 = segment
            x1, y1 = positions[num1]
            x2, y2 = positions[num2]
            draw.line([(x1, y1), (x2, y2)], fill="red", width=line_width)
    
    return result_img

# ========== 상수 및 기본 설정 ==========

# 세션 상태 초기화
if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

CANVAS_SIZE = 500
CENTER = CANVAS_SIZE / 2
RADIUS = 150
CIRCLE_POSITIONS = get_circle_positions(CENTER, CENTER, RADIUS)

# ========== 메인 UI ==========

# 슬라이더로 곱셈 단 선택
col1, col2 = st.columns([1, 2])
with col1:
    st.write("**곱셈 단 선택:**")
with col2:
    multiplication_table = st.slider(
        "곱할 수를 선택하세요",
        min_value=1,
        max_value=9,
        value=6,
        label_visibility="collapsed"
    )

# 정답 경로 생성
digit_sequence = get_digit_sequence(multiplication_table)
st.write(f"**{multiplication_table}단의 일의 자리 규칙:** {' → '.join(map(str, digit_sequence))}")

# 캔버스 표시
st.write("**숫자판 위에 경로를 그려주세요:**")

# 드로잉 캔버스
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=3,
    stroke_color="black",
    background_image=create_canvas_image(),
    height=CANVAS_SIZE,
    width=CANVAS_SIZE,
    drawing_mode="freedraw",
    key=f"canvas_{st.session_state.canvas_key}",
)

# 채점 및 리셋 버튼
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("📝 채점하기"):
        if canvas_result.image_data is not None:
            # 그려진 선 분석
            drawn_image = canvas_result.image_data
            # 검은색 픽셀 찾기 (그려진 선)
            black_pixels = np.where(
                (drawn_image[:, :, 0] < 100) &
                (drawn_image[:, :, 1] < 100) &
                (drawn_image[:, :, 2] < 100)
            )
            
            if len(black_pixels[0]) > 0:
                # 그려진 선 분석
                drawn_segments = analyze_drawn_lines(black_pixels, CIRCLE_POSITIONS)
                
                # 정답 경로와 비교
                correct_segments = get_correct_segments(digit_sequence, CIRCLE_POSITIONS)
                
                # 결과 이미지 생성
                result_img = create_result_image(
                    create_canvas_image(),
                    correct_segments,
                    drawn_segments,
                    CIRCLE_POSITIONS
                )
                
                st.image(result_img, use_column_width=True)
                
                # 점수 계산
                correct_count = 0
                for segment in drawn_segments:
                    if segment in correct_segments:
                        correct_count += 1
                
                st.write(f"**결과:** {correct_count}/{len(correct_segments)} 경로 정답")
            else:
                st.warning("그려진 선이 없습니다. 다시 그려주세요.")

with col2:
    if st.button("🔄 초기화"):
        st.session_state.canvas_key += 1
        st.rerun()

with col3:
    st.write("")

# 정보 표시
st.markdown("---")
st.info("""
**게임 설명:**
- 곱셈 단을 선택하면 일의 자리 규칙이 표시됩니다
- 숫자판 위에 자신이 생각하는 경로를 그려보세요
- "채점하기" 버튼을 누르면 정답 여부가 나타납니다
  - 🟢 초록색: 정답 경로
  - 🔴 빨간색: 오답 경로
""")
