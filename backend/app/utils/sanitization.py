import re
import unicodedata


def sanitize_column_name(name: str) -> str:
    name = str(name).strip()
    name = unicodedata.normalize("NFKD", name)
    name = name.lower()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")
    if not name or name[0].isdigit():
        name = "col_" + name
    pg_reserved = {
        "all", "analyse", "analyze", "and", "any", "array", "as", "asc",
        "asymmetric", "both", "case", "cast", "check", "collate", "column",
        "constraint", "create", "current_date", "current_role", "current_time",
        "current_timestamp", "current_user", "default", "deferrable", "desc",
        "distinct", "do", "else", "end", "except", "false", "fetch", "for",
        "foreign", "from", "grant", "group", "having", "in", "initially",
        "intersect", "into", "lateral", "leading", "limit", "localtime",
        "localtimestamp", "not", "null", "offset", "on", "only", "or", "order",
        "placing", "primary", "references", "returning", "select", "session_user",
        "some", "symmetric", "table", "then", "to", "trailing", "true", "union",
        "unique", "user", "using", "variadic", "when", "where", "window", "with",
    }
    if name in pg_reserved:
        name = name + "_col"
    return name


def sanitize_table_name(file_id_short: str, original_name: str) -> str:
    name = original_name.rsplit(".", 1)[0]  # remove extension
    name = sanitize_column_name(name)
    name = name[:50]  # limit length
    return f"wc_{file_id_short}_{name}"


def deduplicate_columns(columns: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    result = []
    for col in columns:
        if col in seen:
            seen[col] += 1
            result.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            result.append(col)
    return result
