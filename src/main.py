import flet as ft
import asyncio
import pyautogui
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
from pynput import keyboard
from settings.settings import bind
app_page = None
handle_click_ptr = None



def on_press(key):
    try:
        if key.char.lower() in bind:
            pyautogui.press('playpause')
            if app_page and handle_click_ptr:
                app_page.run_threadsafe(handle_click_ptr)
    except AttributeError:
        pass


async def get_media_info():
    try:
        manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        session = manager.get_current_session()
        if not session:
            sessions = manager.get_sessions()
            session = sessions[0] if len(sessions) > 0 else None

        if session:
            props = await session.try_get_media_properties_async()
            return props.artist, props.title
    except Exception:
        pass
    return None, None


async def get_playback_status():
    try:
        manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        session = manager.get_current_session()
        if not session:
            sessions = manager.get_sessions()
            session = sessions[0] if len(sessions) > 0 else None

        if session:
            playback_info = session.get_playback_info()
            return playback_info.playback_status == 4  # 4 - играет, 5 - пауза
    except Exception:
        pass
    return None

async def main(page: ft.Page):
    global app_page, handle_click_ptr
    app_page = page
    
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.title = "Music Controller"
    page.window_width = 300
    page.window_height = 450

    class AppState:
        is_paused = True

    state = AppState()

    artist_text = ft.Text(size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, no_wrap=False)
    title_text = ft.Text(size=18, text_align=ft.TextAlign.CENTER, no_wrap=False)

    # Логика кнопок
    def next_track(e):
        pyautogui.press('nexttrack')

    def prev_track(e):
        pyautogui.press('prevtrack')

    def handle_click(e=None):
        if e is not None:
            pyautogui.press('playpause')
        state.is_paused = not state.is_paused
        play_pause_button.icon = ft.Icons.PAUSE_CIRCLE_FILLED if not state.is_paused else ft.Icons.PLAY_CIRCLE_FILLED
        page.update()

    handle_click_ptr = handle_click


    initial_playback_status = await get_playback_status()
    if initial_playback_status is not None:
        state.is_paused = not initial_playback_status
    
    play_pause_button = ft.IconButton(
        icon=ft.Icons.PAUSE_CIRCLE_FILLED if not state.is_paused else ft.Icons.PLAY_CIRCLE_FILLED,
        icon_size=60,
        on_click=handle_click
    )

    prev_button = ft.IconButton(
        icon=ft.Icons.SKIP_PREVIOUS_ROUNDED,
        icon_size=40,
        on_click=prev_track
    )

    next_button = ft.IconButton(
        icon=ft.Icons.SKIP_NEXT_ROUNDED,
        icon_size=40,
        on_click=next_track
    )


    def open_yandex_music_browser(e):
        import subprocess
        subprocess.Popen(["start", "chrome", "https://music.yandex.ru"], shell=True)

    def open_yandex_music_app(e):
        import subprocess
        subprocess.Popen(["start", "yandexmusic:"], shell=True)

    def open_spotify(e):
        import subprocess
        subprocess.Popen(["start", "spotify:"], shell=True)

    yandex_browser_button = ft.ElevatedButton(
        "Яндекс Музыка (Chrome)",
        on_click=open_yandex_music_browser,
        width=250
    )

    yandex_app_button = ft.ElevatedButton(
        "Яндекс Музыка (App)",
        on_click=open_yandex_music_app,
        width=250
    )

    spotify_button = ft.ElevatedButton(
        "Spotify",
        on_click=open_spotify,
        width=250
    )


    page.add(
        artist_text,
        title_text,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ft.Row(
            [prev_button, play_pause_button, next_button],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ft.Column(
            [
                yandex_browser_button,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                yandex_app_button,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                spotify_button
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while True:
        artist, title = await get_media_info()
        if artist_text.value != artist or title_text.value != title:
            artist_text.value = artist
            title_text.value = title
            page.update()
        
        playback_status = await get_playback_status()
        if playback_status is not None and state.is_paused == playback_status:
            state.is_paused = not playback_status
            play_pause_button.icon = ft.Icons.PAUSE_CIRCLE_FILLED if not state.is_paused else ft.Icons.PLAY_CIRCLE_FILLED
            page.update()
        
        await asyncio.sleep(0.2)

if __name__ == "__main__":
    ft.app(target=main)