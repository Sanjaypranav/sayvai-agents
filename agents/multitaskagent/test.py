from rich import print as rprint

speed_: float = 3.8  # m/s


def calculate_energy(mass: float, speed: float) -> float:
    return 0.5 * mass * speed ** 2


mass_: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
energy_: list[float] = [calculate_energy(mass=m, speed=speed_) for m in mass_]

rprint(f"[bold yellow]{energy_}[/bold yellow]")
