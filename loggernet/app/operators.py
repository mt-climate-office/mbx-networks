class V:
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self):
        return self.name

class S:
    def __init__(self, content: str):
        self.content = content
    
    def __str__(self):
        return f'"{self.content}"'

class F:
    """_summary_
    """
    def __init__(self, name: str, *args: list[str, int, float]):
        self.name = name
        self.args = args

    def __str__(self):
        return f"{self.name}({','.join(str(x) for x in self.args)})"

class If:
    
    def __init__(self, *args: str | int | float | V, logic: str):

        self.initial_condition = self._join_if_logic(*args)
        self.else_ifs = []
        self.else_logic = None
        self.logic = logic

    @staticmethod
    def _join_if_logic(*args: str | int | float | V | S, is_initial: bool=True):
        args = []
        if is_initial:
            return f"If {' '.join(str(x) for x in args)} Then"
        return f"ElseIf {' '.join(str(x) for x in args)} Then"
    
    def ElseIf(self, *args: str | int | float, logic: str):
        self.else_ifs.append(
            f"{self._join_if_logic(*args, is_initial=False)}\n    {logic}"
        )
        return self
    
    def Else(self, logic):
        self.else_logic = f"Else\n    {logic}"
        return self
    
    def __str__(self):

        code = [self.initial_condition]
        code.append(f"    {self.logic}")

        for elseif in self.else_ifs:
            code.append(elseif)

        if self.else_logic:
            code.append(self.else_logic)

        code.append("EndIf")
        return "\n".join(code)

class For:

    def __init__(self,logic: str, v: V, start: int | V, end: int | V, step: int | None = None):
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