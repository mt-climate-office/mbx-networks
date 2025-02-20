from app.functions import Variable


class If:
    def __init__(self, *args: str | int | float | Variable, logic: str | list[str]):
        self.initial_condition = self._join_if_logic(*args, is_initial=True)
        self.else_ifs = []
        self.else_logic = None
        self.logic = logic

    @staticmethod
    def _join_if_logic(*args: str | int | float | Variable, is_initial: bool = True):
        if is_initial:
            return f"If {' '.join(str(x) for x in args)} Then"
        return f"ElseIf {' '.join(str(x) for x in args)} Then"

    def ElseIf(self, *args: str | int | float, logic: str | list[str]):
        if isinstance(logic, str):
            logic = [logic]
        self.else_ifs.append(
            f"{self._join_if_logic(*args, is_initial=False)}\n{'\n    '.join(x for x in logic)}"
        )
        return self

    def Else(self, logic: str | list[str]):
        if isinstance(logic, str):
            logic = [logic]
        logic = "\n    ".join(x for x in logic)
        self.else_logic = f"Else\n    {logic}"
        return self

    def __str__(self):
        code = [self.initial_condition]
        if isinstance(self.logic, str):
            self.logic = [self.logic]
        elif isinstance(self.logic, If):
            self.logic = str(self.logic)

        code.append(f"    {'\n    '.join(x for x in self.logic)}")

        for elseif in self.else_ifs:
            code.append(elseif)

        if self.else_logic:
            code.append(self.else_logic)

        code.append("EndIf")
        return "\n".join(code)

    def __eq__(self, other: "If") -> bool:
        return self.initial_condition == other.initial_condition

    def __add__(self, other: "If") -> "If":
        assert self == other, (
            "The two If objects are not equal. They must have identical If conditions."
        )
        self.logic = f"{self.logic}\n    {other.logic}"
        return self


class For:
    def __init__(
        self,
        logic: str,
        v: Variable,
        start: int | Variable,
        end: int | Variable,
        step: int | None = None,
    ):
        self.logic = logic
        self.v = v
        self.start = start
        self.end = end
        self.step = step

    def __str__(self):
        formatted_logic = "\n".join(f"    {line}" for line in self.logic.splitlines())
        first_line = f"For {self.v}={self.start} To {self.end}"
        if self.step:
            first_line += f" Step {self.step}"
        return f"{first_line}\n{formatted_logic}\nNext {self.v}"
