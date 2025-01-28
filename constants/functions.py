from containers import ButtonSettings


def make_slider(state: str, len_slider: range) -> tuple[ButtonSettings, ...]:
    return tuple((ButtonSettings(f'interaction.{state}/save{value}', str(value)) for value in len_slider))


def replace_constant_text(constant: str, value: str | int) -> str:
    pass
