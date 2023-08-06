def remove_prefix_suffix(s, pre, suff):
    return s[
        len(pre) * s.startswith(pre) : len(s) - len(suff) * s.endswith(suff)
    ]
