import json

import xbmc
import xbmcaddon


class Monitor(xbmc.Monitor):

    _powermanagement_displaysoff = 0
    _disabled_powermanagement_displaysoff = False
    _windows_unlock = False

    def __init__(self) -> None:

        super().__init__()
        self._update()

    def _update(self) -> None:

        addon = xbmcaddon.Addon()

        self._windows_unlock = addon.getSettingBool("windows_unlock")
        self._powermanagement_displaysoff = addon.getSettingInt(
            "powermanagement_displaysoff")
        self.reset_powermanagement_displaysoff()

    def onSettingsChanged(self) -> None:

        self._update()

    def start(self) -> None:

        prev_windows_unlock = False

        while not self.abortRequested():

            if self._windows_unlock != prev_windows_unlock:
                prev_windows_unlock = self.set_windows_unlock(
                    self._windows_unlock)

            if self._powermanagement_displaysoff:
                self._prevent_powermanagement_displaysoff()

            if self.waitForAbort(10):
                break

    def set_windows_unlock(self, value: bool) -> bool:

        if xbmc.getCondVisibility("system.platform.windows"):
            import ctypes

            ctypes.windll.kernel32.SetThreadExecutionState(
                0x80000002 if value else 0x80000000
            )

        return value

    def _prevent_powermanagement_displaysoff(self) -> None:

        is_fullscreen = xbmc.getCondVisibility("System.IsFullscreen")
        if is_fullscreen and self._disabled_powermanagement_displaysoff:
            self.reset_powermanagement_displaysoff()

        elif not is_fullscreen and not self._disabled_powermanagement_displaysoff:
            self._disabled_powermanagement_displaysoff = True
            self.set_powermanagement_displaysoff(0)

    def reset_powermanagement_displaysoff(self) -> None:

        if self._powermanagement_displaysoff:
            self.set_powermanagement_displaysoff(
                self._powermanagement_displaysoff)
            self._disabled_powermanagement_displaysoff = False

    def set_powermanagement_displaysoff(self, value: int) -> None:

        _request = {
            "jsonrpc": "2.0",
            "method": "Settings.SetSettingValue",
            "params": {
                "setting": "powermanagement.displaysoff",
                "value": value
            },
            "id": 1
        }

        xbmc.executeJSONRPC(json.dumps(_request))


if __name__ == "__main__":

    monitor = Monitor()

    try:
        monitor.start()

    finally:
        monitor.reset_powermanagement_displaysoff()
        monitor.set_windows_unlock(False)
