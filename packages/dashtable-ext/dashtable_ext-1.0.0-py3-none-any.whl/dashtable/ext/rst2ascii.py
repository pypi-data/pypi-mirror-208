from .presetstyle import PresetStyle


def rst2ascii(table, preset: PresetStyle = PresetStyle.thin_thick_rounded):
    map = preset
    tlist = table.split("\n")
    rlist = [list(row) for row in tlist]
    head = "header_" if rlist[2][1] == "=" else ""

    rlist[0][0] = map[head + "top_left_corner"]
    rlist[0][-1] = map[head + "top_right_corner"]
    rlist[-1][0] = map["bottom_left_corner"]
    rlist[-1][-1] = map["bottom_right_corner"]

    for _ in rlist[0]:
        if _ == "-":
            rlist[0][rlist[0].index(_)] = map[head + "top_horizontal"]
        elif _ == "+":
            rlist[0][rlist[0].index(_)] = map[head + "top_cross"]
    rlist[1] = [map[head + "vertical"] if _ == "|" else _ for _ in rlist[1]]

    for row in rlist[0:]:
        for i, char in enumerate(row):
            if char == "|":
                row[i] = map["vertical"]
            if char == "+":
                if (row[i - 1] == " " or i == 0) and rlist[rlist.index(row) - 1][
                    i
                ] == map["vertical"]:
                    # left " " & up "│"
                    if i + 1 < len(row) and row[i + 1] == " ":
                        # left " " & up "│" & right " "
                        if (
                            rlist.index(row) + 1 < len(rlist)
                            and rlist[rlist.index(row) + 1][i] != "|"
                        ):
                            # left " " & up "│" & right " " & down " "
                            pass  # not possible
                        if rlist.index(row) + 1 < len(rlist) and (
                            rlist[rlist.index(row) + 1][i] == "|"
                            or rlist[rlist.index(row) + 1][i] == "│"
                        ):
                            # left " " & up "│" & right " " & down "│"
                            pass  # no cross
                        if rlist.index(row) == len(rlist) - 1:
                            # left " " & up "│" & right " " & no down
                            pass  # not possible
                    if i + 1 < len(row) and (row[i + 1] == "-" or row[i + 1] == "="):
                        # left " " & up "│" & right "-" or "="
                        if (
                            rlist.index(row) + 1 < len(rlist)
                            and rlist[rlist.index(row) + 1][i] != "|"
                        ):
                            # left " " & up "│" & right "-" & down " "
                            row[i] = map[head + "up_right"]
                        if rlist.index(row) + 1 < len(rlist) and (
                            rlist[rlist.index(row) + 1][i] == "|"
                            or rlist[rlist.index(row) + 1][i] == "│"
                        ):
                            # left " " & up "│" & right "-" or "=" & down "│"
                            row[i] = map[head + "up_right_down"]
                        if rlist.index(row) == len(rlist) - 1:
                            # left " " & up "│" & right "-" or "=" & no down
                            row[i] = map[head + "up_right"]
                    if i == len(row) - 1:
                        # left " " & up "│" & no right
                        if (
                            rlist.index(row) + 1 < len(rlist)
                            and rlist[rlist.index(row) + 1][i] != "|"
                        ):
                            # left " " & up "│" & no right & down " "
                            pass  # not possible
                        if rlist.index(row) + 1 < len(rlist) and (
                            rlist[rlist.index(row) + 1][i] == "|"
                            or rlist[rlist.index(row) + 1][i] == "│"
                        ):
                            # left " " & up "│" & no right & down "│"
                            pass  # no cross
                        if rlist.index(row) == len(rlist) - 1:
                            # left " " & up "│" & no right & no down
                            pass  # not possible

                if row[i - 1] == "-" and rlist[rlist.index(row) - 1][i] != "│":
                    # left "-" & up " "
                    if i + 1 < len(row) and row[i + 1] == " ":
                        # left "-" & up " " & right " "
                        if (
                            rlist.index(row) + 1 < len(rlist)
                            and rlist[rlist.index(row) + 1][i] != "|"
                        ):
                            # left "-" & up " " & right " " & down " "
                            pass  # not possible
                        if rlist.index(row) + 1 < len(rlist) and (
                            rlist[rlist.index(row) + 1][i] == "|"
                            or rlist[rlist.index(row) + 1][i] == "│"
                        ):
                            # left "-" & up " " & right " " & down "│"
                            row[i] = map["left_down"]
                        if rlist.index(row) == len(rlist) - 1:
                            # left "-" & up " " & right " " & no down
                            pass  # not possible
                    if i + 1 < len(row) and row[i + 1] == "-":
                        # left "-" & up " " & right "-"
                        if (
                            rlist.index(row) + 1 < len(rlist)
                            and rlist[rlist.index(row) + 1][i] != "|"
                        ):
                            # left "-" & up " " & right "-" & down " "
                            pass  # not possible
                        if rlist.index(row) + 1 < len(rlist) and (
                            rlist[rlist.index(row) + 1][i] == "|"
                            or rlist[rlist.index(row) + 1][i] == "│"
                        ):
                            # left "-" & up " " & right "-" & down "│"
                            row[i] = map["left_right_down"]
                        if rlist.index(row) == len(rlist) - 1:
                            # left "-" & up " " & right "-" & no down
                            pass  # not possible
                    if i == len(row) - 1:
                        # left "-" & up " " & no right
                        if (
                            rlist.index(row) + 1 < len(rlist)
                            and rlist[rlist.index(row) + 1][i] != "|"
                        ):
                            # left "-" & up " " & no right & down " "
                            pass  # not possible
                        if rlist.index(row) + 1 < len(rlist) and (
                            rlist[rlist.index(row) + 1][i] == "|"
                            or rlist[rlist.index(row) + 1][i] == "│"
                        ):
                            # left "-" & up " " & no right & down "│"
                            row[i] = map["left_down"]
                        if rlist.index(row) == len(rlist) - 1:
                            # left "-" & up " " & no right & no down
                            pass  # not possible

                if (row[i - 1] == "-" or row[i - 1] == "=") and rlist[
                    rlist.index(row) - 1
                ][i] == map["vertical"]:
                    # left "-" & up "│"
                    if i + 1 < len(row) and row[i + 1] == " ":
                        # left "-" & up "│" & right " "
                        if (
                            rlist.index(row) + 1 < len(rlist)
                            and rlist[rlist.index(row) + 1][i] != "|"
                        ):
                            # left "-" & up "│" & right " " & down " "
                            row[i] = map["left_up"]
                        if rlist.index(row) + 1 < len(rlist) and (
                            rlist[rlist.index(row) + 1][i] == "|"
                            or rlist[rlist.index(row) + 1][i] == "│"
                        ):
                            # left "-" & up "│" & right " " & down "│"
                            row[i] = map["left_up_down"]
                        if rlist.index(row) == len(rlist) - 1:
                            # left "-" & up "│" & right " " & no down
                            row[i] = map["left_up"]
                    if i + 1 < len(row) and row[i + 1] == "-":
                        # left "-" & up "│" & right "-"
                        if (
                            rlist.index(row) + 1 < len(rlist)
                            and rlist[rlist.index(row) + 1][i] != "|"
                        ):
                            # left "-" & up "│" & right "-" & down " "
                            row[i] = map["left_up_right"]
                        if rlist.index(row) + 1 < len(rlist) and (
                            rlist[rlist.index(row) + 1][i] == "|"
                            or rlist[rlist.index(row) + 1][i] == "│"
                        ):
                            # left "-" & up " & right "-" & down "│"

                            row[i] = map["cross"]
                        if rlist.index(row) == len(rlist) - 1:
                            # left "-" & up "│" & right "-" & no down
                            row[i] = map["left_up_right"]
                    if i == len(row) - 1:
                        # left "-" & up "│" & no right
                        if (
                            rlist.index(row) + 1 < len(rlist)
                            and rlist[rlist.index(row) + 1][i] != "|"
                        ):
                            # left "-" & up "│" & no right & down " "
                            row[i] = map["left_up"]
                        if rlist.index(row) + 1 < len(rlist) and (
                            rlist[rlist.index(row) + 1][i] == "|"
                            or rlist[rlist.index(row) + 1][i] == "│"
                        ):
                            # left "-" & up "│" & no right & down "│"
                            row[i] = map["left_up_down"]
                        if rlist.index(row) == len(rlist) - 1:
                            # left "-" & up "│" & no right & no down
                            row[i] = map["left_up"]
            if char == "|" and row[i - 1] == "-" and row[i + 1] == " ":
                row[i] = map["left_up_down"]
        for j, char in enumerate(row):
            if char == "-":
                row[j] = map["horizontal"]
            if char == "=":
                row[j] = map["header_horizontal"]

    tlist = ["".join(row) for row in rlist]
    return "\n".join(tlist)
