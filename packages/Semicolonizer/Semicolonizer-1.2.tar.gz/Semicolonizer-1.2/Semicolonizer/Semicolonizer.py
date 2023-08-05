import os
import re
import sys
from tkinter.simpledialog import askstring
from win10toast import ToastNotifier
from pynput import keyboard


class Semicolonizer:
    def process(self, text: str):
        for line in text.splitlines():
            if line:
                if not (line[-1] == ";"):
                    if re.match(r"\s*[a-zA-Z]+\s.*\w+\(.*\)$", line):
                        yield f"{line}\n"
                        continue
                    elif re.match(r"(.+\{)|(^\{$)", line):
                        yield f"{line}\n"
                        continue
                    elif line in ("<?php", "?>"):
                        yield f"{line}\n"
                        continue
                else:
                    yield f"{line}\n"
                    continue
            else:
                yield line
                continue

            yield f"{line};\n"

    def semicolonize(self, file_name: str, new_file_name: str):
        with open(new_file_name, "w") as f:
            for line in self.process(open(file_name).read()):
                f.write(line)


class Listener:
    KEY = keyboard.Key.f5

    def __init__(self):
        self.mainloop_running = True
        self.is_enabled = False
        self.notifier = ToastNotifier()
        self.file_name = "index.php"
        self.semicolonizer = Semicolonizer()

    def show_toast(self, msg):
        try:
            self.notifier.show_toast(title="Notification",
                                     msg=msg,
                                     threaded=True,
                                     duration=2)
        except Exception as e:
            pass

    def semicolonize(self, key):
        if self.is_enabled:
            if type(key) == keyboard.Key and key == keyboard.Key.f4:
                name, ext = os.path.splitext(self.file_name)
                self.semicolonizer.semicolonize(self.file_name, new_file_name := f"{name}_semicolonized{ext}")
                self.show_toast(f"Semicolonized!\n{new_file_name}")

    def mainloop(self):
        def on_pressed(key):
            if self.mainloop_running:
                try:
                    if key == Listener.KEY:
                        self.is_enabled = not self.is_enabled
                        self.show_toast("enabled!" if self.is_enabled else "disabled!")
                        if self.file_name:
                            self.semicolonize(key)
                        else:
                            self.semicolonize(key)
                    elif key == keyboard.Key.f2:
                        self.file_name = askstring(title="file name",
                                                   prompt="give me the file name[default: index.php]") or "index.php"
                    elif key == keyboard.Key.f6:
                        self.show_toast("Exit Semicolonizer")
                        sys.exit(0)
                    self.semicolonize(key)

                except Exception as e:
                    print(e, file=sys.stderr)
            else:
                return

        with keyboard.Listener(on_press=on_pressed) as listener:
            listener.join()


def main():
    lst = Listener()
    if len(sys.argv) > 1:
        lst.file_name = sys.argv[1]
    file_name = lst.file_name
    print(f"{file_name = }")
    print("f5 to enable/disable the Semicolonizer")
    print("f4 to Semicolonize the php file")
    print("f2 to change default file_name")
    print("f6 to quit")
    lst.mainloop()


if __name__ == "__main__":
    main()
