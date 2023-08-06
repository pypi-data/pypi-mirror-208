def serialize_json(obj) -> str:
    if type(obj) == tuple:
        serialized = []
        for i in obj:
            serialized.append(f"{serialize_json(i)}")
        ans = ", ".join(serialized)
        return f"[{ans}]"
    else:
        return f"\"{str(obj)}\""


def deserialize_json(obj: str):
    if obj == '[]':
        return tuple()
    elif obj[0] == '[':
        obj = obj[1:len(obj) - 1]
        parsed = []
        depth = 0
        quote = False
        substr = ""
        for i in obj:
            if i == '[':
                depth += 1
            elif i == ']':
                depth -= 1
            elif i == '\"':
                quote = not quote
            elif i == ',' and not quote and depth == 0:
                parsed.append(deserialize_json(substr))
                substr = ""
                continue
            elif i == ' ' and not quote:
                continue

            substr += i

        parsed.append(deserialize_json(substr))
        return tuple(parsed)
    else:
        return obj[1:len(obj) - 1]
