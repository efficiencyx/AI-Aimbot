import platform
from typing import Optional


if platform.system() == "Windows":
    import win32api
    import win32con

    def quit_requested(key: str) -> bool:
        return win32api.GetAsyncKeyState(ord(key.upper())) != 0

    def activation_enabled() -> bool:
        return win32api.GetKeyState(win32con.VK_CAPITAL) != 0

    def move_mouse(x_delta: float, y_delta: float) -> None:
        win32api.mouse_event(
            win32con.MOUSEEVENTF_MOVE, int(x_delta), int(y_delta), 0, 0
        )

else:
    from pynput import keyboard, mouse

    _pressed_caps: bool = False
    _listener_started: bool = False
    _mouse_controller: Optional[mouse.Controller] = None
    _pressed_keys = set()


    def _ensure_listener_started() -> None:
        global _listener_started, _mouse_controller, _pressed_caps
        if _listener_started:
            return

        _mouse_controller = mouse.Controller()

        def _on_press(key):
            global _pressed_caps
            if key == keyboard.Key.caps_lock:
                _pressed_caps = not _pressed_caps
            elif isinstance(key, keyboard.KeyCode) and key.char:
                _pressed_keys.add(key.char.upper())

        def _on_release(key):
            if isinstance(key, keyboard.KeyCode) and key.char:
                _pressed_keys.discard(key.char.upper())

        listener = keyboard.Listener(on_press=_on_press, on_release=_on_release)
        listener.daemon = True
        listener.start()
        _listener_started = True


    def quit_requested(key: str) -> bool:
        _ensure_listener_started()
        return key.upper() in _pressed_keys


    def activation_enabled() -> bool:
        _ensure_listener_started()
        return _pressed_caps


    def move_mouse(x_delta: float, y_delta: float) -> None:
        _ensure_listener_started()
        _mouse_controller.move(int(x_delta), int(y_delta))
