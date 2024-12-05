import os
import cv2
import pygame
import time
import threading
from tkinter import Tk, Button, Label, filedialog, StringVar, OptionMenu, Entry
from tkinter import messagebox
from PIL import Image
from screeninfo import get_monitors
import json
import numpy as np  # Missing import for numpy

# Biến toàn cục để kiểm soát trạng thái trình chiếu
slideshow_running = False
slideshow_thread = None  # Lưu trữ luồng trình chiếu

# Tải file cấu hình đã chọn
def load_config():
    config_file = filedialog.askopenfilename(
        title="Chọn file cấu hình",
        filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
    )
    if config_file and os.path.exists(config_file):
        with open(config_file, "r") as f:
            settings = json.load(f)
            
            # Đặt giá trị folder
            folder_path.set(settings.get("folder", ""))
            
            # Đặt giá trị thời gian hiển thị ảnh
            image_duration_var.set(settings.get("duration", "5"))
        
        messagebox.showinfo("Đã tải cấu hình")
    else:
        messagebox.showwarning("Tải cấu hình thất bại ")


# Hàm lọc các tệp ảnh và video trong thư mục
def get_media_files(folder_path):
    valid_image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
    valid_video_extensions = (".mp4", ".avi", ".mov", ".mkv")
    media_files = []

    for file in os.listdir(folder_path):
        if file.lower().endswith(valid_image_extensions + valid_video_extensions):
            media_files.append(os.path.join(folder_path, file))
    return media_files

# Hàm hiển thị ảnh với hiệu ứng fade in và fade out
def display_image(screen, file_path, fade_duration=2):
    img = Image.open(file_path)
    img = img.convert("RGB")
    img_width, img_height = img.size

    screen_width, screen_height = screen.get_size()
    img_ratio = img_width / img_height
    screen_ratio = screen_width / screen_height

    if img_ratio > screen_ratio:  # Ảnh rộng hơn
        new_width = screen_width
        new_height = int(screen_width / img_ratio)
    else:  # Ảnh cao hơn
        new_height = screen_height
        new_width = int(screen_height * img_ratio)

    img = img.resize((new_width, new_height))
    img_surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode)

    x_offset = (screen_width - new_width) // 2
    y_offset = (screen_height - new_height) // 2

    # Fade-in effect
    for alpha in range(0, 255, 255 // (fade_duration * 30)):
        screen.fill((0, 0, 0))
        img_surface.set_alpha(alpha)
        screen.blit(img_surface, (x_offset, y_offset))
        pygame.display.flip()
        pygame.time.delay(30)

    # Giữ ảnh hiện lên trong một thời gian ngắn
    display_time = pygame.time.get_ticks()  # Thời gian hiện tại
    while pygame.time.get_ticks() - display_time < 1000 * 1:  # 1 giây hiển thị ảnh
        pygame.event.get()  # Quản lý sự kiện
        pygame.time.delay(10)

    # Fade-out effect
    for alpha in range(255, 0, -255 // (fade_duration * 30)):
        screen.fill((0, 0, 0))
        img_surface.set_alpha(alpha)
        screen.blit(img_surface, (x_offset, y_offset))
        pygame.display.flip()
        pygame.time.delay(30)

# Hàm phát video với hiệu ứng fade in và fade out
def play_video(screen, file_path, fade_duration=2):
    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps)

    screen_width, screen_height = screen.get_size()

    # Fade-in effect
    alpha = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or not slideshow_running:
            break

        frame_height, frame_width, _ = frame.shape
        video_ratio = frame_width / frame_height
        screen_ratio = screen_width / screen_height

        if video_ratio > screen_ratio:
            new_width = screen_width
            new_height = int(screen_width / video_ratio)
        else:
            new_height = screen_height
            new_width = int(screen_height * video_ratio)

        frame = cv2.resize(frame, (new_width, new_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame)

        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2
        screen.fill((0, 0, 0))
        screen.blit(frame_surface, (x_offset, y_offset))
        pygame.display.flip()

        # Increase alpha for fade in effect
        alpha += 255 // (fade_duration * 30)
        if alpha > 255:
            alpha = 255
        pygame.time.delay(delay)

    # Phát video
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or not slideshow_running:
            break
        frame_height, frame_width, _ = frame.shape
        video_ratio = frame_width / frame_height
        screen_ratio = screen_width / screen_height

        if video_ratio > screen_ratio:
            new_width = screen_width
            new_height = int(screen_width / video_ratio)
        else:
            new_height = screen_height
            new_width = int(screen_height * video_ratio)

        frame = cv2.resize(frame, (new_width, new_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame)

        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2
        screen.fill((0, 0, 0))
        screen.blit(frame_surface, (x_offset, y_offset))
        pygame.display.flip()

        pygame.time.delay(delay)

    # Fade-out effect
    alpha = 255
    while alpha > 0:
        ret, frame = cap.read()
        if not ret or not slideshow_running:
            break
        frame_height, frame_width, _ = frame.shape
        video_ratio = frame_width / frame_height
        screen_ratio = screen_width / screen_height

        if video_ratio > screen_ratio:
            new_width = screen_width
            new_height = int(screen_width / video_ratio)
        else:
            new_height = screen_height
            new_width = int(screen_height * video_ratio)

        frame = cv2.resize(frame, (new_width, new_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.array(frame)

        # Apply fade out effect
        frame = cv2.addWeighted(frame, alpha / 255.0, frame, 0, 0)
        frame_surface = pygame.surfarray.make_surface(frame)

        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2
        screen.fill((0, 0, 0))
        screen.blit(frame_surface, (x_offset, y_offset))
        pygame.display.flip()

        alpha -= 255 // (fade_duration * 30)
        pygame.time.delay(delay)

    cap.release()

# Hàm chạy trình chiếu trên màn hình được chọn
# Hàm chạy trình chiếu trên màn hình được chọn
def slideshow_task(folder_path, display_index, image_duration):
    global slideshow_running
    slideshow_running = True

    media_files = get_media_files(folder_path)
    if not media_files:
        messagebox.showerror("Lỗi", "Thư mục không chứa tệp ảnh hoặc video hợp lệ!")
        return

    pygame.init()
    monitors = get_monitors()
    if display_index >= len(monitors):
        messagebox.showerror("Lỗi", "Màn hình không tồn tại!")
        return

    monitor = monitors[display_index]
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{monitor.x},{monitor.y}"

    screen = pygame.display.set_mode((monitor.width, monitor.height))  # Không sử dụng pygame.FULLSCREEN
    pygame.display.set_caption("Trình chiếu ảnh và video")

    while slideshow_running:
        for media_file in media_files:
            if not slideshow_running:  # Kiểm tra lại trạng thái
                break

            if media_file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
                display_image(screen, media_file, fade_duration=2)
                for _ in range(image_duration * 10):
                    if not slideshow_running:
                        break
                    pygame.event.get()  # Quản lý sự kiện
                    pygame.time.delay(10)
            elif media_file.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                play_video(screen, media_file)

    pygame.quit()


# Dừng trình chiếu
def stop_slideshow(event=None):
    global slideshow_running
    slideshow_running = False
    print("Trình chiếu đã dừng.")

# Hàm hiển thị thông tin tác giả
def show_author_info():
    author_info = """ 
    Tên phần mềm: Pictures Slideshow
    Phiên bản: Beta
    Tác giả: Nguyễn Thiên Quân
    Email: ngthzuan@gmail.com
    Mô tả: Phần mềm này cho phép trình chiếu ảnh và video với các hiệu ứng chuyển cảnh.
    ! Được đăng ký bản quyền kĩ thuật số.
    """
    messagebox.showinfo("Thông tin tác giả", author_info)

# GUI
def select_folder():
    folder = filedialog.askdirectory(title="Chọn thư mục chứa ảnh và video")
    folder_path.set(folder)
    save_settings(folder, selected_display.get(), image_duration_var.get())  # Lưu cài đặt khi chọn thư mục

def start():
    folder = folder_path.get()
    try:
        image_duration = int(image_duration_var.get())
        if image_duration <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Lỗi", "Thời gian hiển thị ảnh phải là một số dương!")
        return

    # Lấy màn hình được chọn
    monitor_index = monitor_options.index(selected_display.get())

    global slideshow_thread
    slideshow_thread = threading.Thread(target=slideshow_task, args=(folder, monitor_index, image_duration))
    slideshow_thread.start()

# Lưu các cài đặt vào file
def save_settings(folder, monitor, duration):
    settings = {
        "folder": folder,
        "monitor": monitor,
        "duration": duration
    }
    with open("settings.json", "w") as f:
        json.dump(settings, f)

# Đọc các cài đặt từ file
def load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings = json.load(f)
            return settings
    return None

# Tạo giao diện người dùng
root = Tk()
root.title("Trình chiếu ảnh và video")

folder_path = StringVar()
image_duration_var = StringVar(value="5")

# Lấy thông tin các màn hình
monitors = get_monitors()
monitor_options = [f"Màn hình {i+1} ({monitor.width}x{monitor.height})" for i, monitor in enumerate(monitors)]
selected_display = StringVar(value=monitor_options[0])

# Đọc cài đặt từ file (nếu có)
settings = load_settings()
if settings:
    folder_path.set(settings["folder"])
    selected_display.set(settings["monitor"])
    image_duration_var.set(settings["duration"])

# Nút để duyệt và tải file cấu hình
Button(root, text="Tải cấu hình", command=load_config).pack()

Label(root, text="Vui lòng chọn các thư mục chứa các video cần trình chiếu!").pack()
Button(root, text="Chọn thư mục", command=select_folder).pack()

Label(root, text="Hiệu ứng chuyển cảnh kéo dài trong (giây):").pack()
Entry(root, textvariable=image_duration_var).pack()

Label(root, text="Chọn màn hình để chiếu:").pack()
OptionMenu(root, selected_display, *monitor_options).pack()

Button(root, text="Bắt đầu", command=start).pack()
Button(root, text="Ngưng trình chiếu", command=stop_slideshow).pack()

# Thêm nút để hiển thị thông tin tác giả
Button(root, text="Thông tin tác giả", command=show_author_info).pack()

root.mainloop()
