"""Regex Engine — Thompson NFA construction + simulation."""
class State:
    def __init__(self, char=None):
        self.char = char; self.out = []; self.is_match = False

def compile_regex(pattern):
    def parse(i):
        frags = []
        while i < len(pattern):
            c = pattern[i]
            if c == ')': return frags, i
            if c == '(':
                sub, i = parse(i + 1)
                frag = concat_frags(sub)
                frags.append(frag)
            elif c == '|':
                left = concat_frags(frags); frags = []
                right_frags, i = [left], i  # simplified
                i += 1; continue
            elif c == '*':
                if frags: frags[-1] = star(frags[-1])
            elif c == '+':
                if frags: frags[-1] = plus(frags[-1])
            elif c == '?':
                if frags: frags[-1] = optional(frags[-1])
            elif c == '.':
                frags.append((State('.'), []))
            else:
                frags.append((State(c), []))
            i += 1
        return frags, i
    def concat_frags(frags):
        if not frags: return (State(), [])
        start, dangling = frags[0]
        for s, d in frags[1:]:
            for state in (dangling if dangling else [start]):
                state.out.append(s)
            dangling = d if d else [s]
        return (start, dangling)
    def star(frag):
        s, d = frag
        loop = State()
        loop.out.append(s)
        for state in (d if d else [s]):
            state.out.append(loop)
        return (loop, [loop])
    def plus(frag):
        s, d = frag
        for state in (d if d else [s]):
            state.out.append(s)
        return (s, d if d else [s])
    def optional(frag):
        s, d = frag
        return (s, (d if d else []) + [s])
    frags, _ = parse(0)
    start, dangling = concat_frags(frags)
    match_state = State(); match_state.is_match = True
    for state in (dangling if dangling else [start]):
        state.out.append(match_state)
    return start

def match(start, text):
    def step(states):
        next_s = set()
        for s in states:
            if s.char is None and not s.is_match:
                for o in s.out: next_s.add(o)
            else: next_s.add(s)
        return next_s
    current = step({start})
    for c in text:
        next_states = set()
        for s in current:
            if s.is_match: continue
            if s.char == c or s.char == '.':
                for o in s.out: next_states.add(o)
        current = step(next_states)
        if not current: return False
    return any(s.is_match for s in current)

if __name__ == "__main__":
    tests = [("ab", "ab", True), ("a.b", "acb", True), ("a*b", "aaab", True),
             ("a*b", "b", True), ("a+b", "b", False), ("a+b", "ab", True)]
    for pat, txt, expected in tests:
        nfa = compile_regex(pat)
        result = match(nfa, txt)
        ok = "✅" if result == expected else "❌"
        print(f"{ok} /{pat}/ ~ '{txt}' = {result}")
        assert result == expected
    print("All tests passed!")
