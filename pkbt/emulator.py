from pathlib import Path
import subprocess

class EmulatorProc:

    def __init__(self, exe: Path, rom: Path, scripts: list[Path] | None = None) -> None:
        self.exe = exe
        self.rom = rom
        self.scripts = scripts

    def start(self) -> None:
        """Starts the emulator with (optionally) the given scripts."""
        scripting_args = []
        for s in self.scripts or []:
            scripting_args.extend(["--script", str(s)])

        p = subprocess.Popen([
            str(self.exe),
            *scripting_args,
            str(self.rom)
        ])

        if p is None:
            raise Exception("Failed to start emulator")
        else:
            self.process = p

    def stop(self) -> None:
        """Stops the emulator."""
        self.process.terminate()


"""For testing purposes, we can run the module directly to start and stop the emulator."""

if __name__ == "__main__":

    import time
    from pkbt.config import MGBA_DEV, POKEMON_RED_ROM, INPUT_DISPLAY_SCRIPT, SERVER_SCRIPT

    e = EmulatorProc(
        MGBA_DEV,
        POKEMON_RED_ROM,
        [INPUT_DISPLAY_SCRIPT, SERVER_SCRIPT]
    )

    print("Starting emulator...")
    e.start()

    print(f"Emulator started successfully with PID {e.process.pid}. Stopping in 3 seconds...")
    time.sleep(3)

    print(f"Stopping emulator with PID {e.process.pid}...")
    e.stop()