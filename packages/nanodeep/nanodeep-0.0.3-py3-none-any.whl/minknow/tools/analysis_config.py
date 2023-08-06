def _replace_old_channel_state_pattern(pattern, classifications):
    """
    Replace a pattern like strandstrand so the classifications
    are surrounded b pointy braces: <strand><strand>

    :param pattern: The pattern input to fix.
    :param classifications: A sorted list of classifications, in order to be
                            replaced (normally longest to shortest).
    :return: The fixed pattern
    """
    for n in classifications:
        position = 0
        while position < len(pattern):
            # If the pattern isnt found were done with this read class
            found = pattern.find(n, position)
            if found == -1:
                break

            skip_this_find = False
            next_position = found + len(n)
            for i in range(found, -1, -1):
                # If were inside a tag, dont replace
                if pattern[i] == "<":
                    # wer inside a tag - ignore it.
                    skip_this_find = True
                    break
                # Otherwise were outside a tag, replace
                if pattern[i] == ">":
                    break

            if skip_this_find:
                position = next_position
                continue

            start = pattern[0:found]
            end = pattern[found + len(n) :]
            pattern = "{}<{}>{}".format(start, n, end)
            position = next_position + 2  # 2 for extra new characters
    return pattern


def fix_old_channel_state_patterns(config):
    """
    Replace old style analysic config channel state patterns with new style braces patterns
    :param config: The analysis config to mutate and make compliant with new format.
    """
    # Find names from the analysis config read classifications
    names = [
        x.split(" ")[0]
        for x in config["read_classification"]["parameters"]["rules_in_execution_order"]
    ]
    names.extend(["transition", "unclassed", "mux_uncertain"])
    # replace strings in order of reverse length
    names.sort(key=lambda x: len(x))

    # Fix patterns in channel states with tagged names
    states = config["channel_states"]
    for state in states:
        logic = states[state]["logic"]
        if "pattern" in logic:
            pattern = logic["pattern"]
            pattern = _replace_old_channel_state_pattern(pattern, names)
            logic["pattern"] = pattern
