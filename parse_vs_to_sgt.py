# parse_vs_to_sgt.py : Parse a .vs file from plotrefa to the .sgt format preferred by pygimli
# (c) 2024 Sean G. Polun

import os
import sys
import math


def parse_vs_to_sgt(vs_file, sgt_file, first_shot, last_shot, first_geophone, last_geophone, shot_spacing):
    """
    parse_vs_to_sgt.py:
    Parse a .vs file with pick information from Geometrics to the .sgt format preferred by pygimli.
    Does not support .vs files with layer information from plotrefa.
    (c) 2024 Sean G. Polun

    Args:
        vs_file: Path to the .vs file
        sgt_file: Path to the .sgt file
        first_shot: First shot location (float)
        last_shot: Last shot location (float)
        first_geophone: First geophone location (float)
        last_geophone: Last geophone location (float)
        shot_spacing: Shot spacing (float)

    Returns:

    """
    linenum = 0
    sgt_obs = []
    shot = 0

    with open(vs_file, 'r') as vs:
        line1 = vs.readline()
        line2 = vs.readline()
        line1 = line1.split()
        line2 = line2.split()
        num_shots = int(line2[1])
        phone_spacing = float(line2[2])
        linenum = 2
        for line in vs:
            linenum += 1
            line_split = line.split()
            if len(line_split) != 3:
                if int(float(line_split[0])) == 0 and int(float(line_split[1])) == 0:
                    print("Encountered end of observations at line {0}".format(linenum))
                    break
                else:
                    raise ValueError('Invalid line format')
            if int(float(line_split[2])) == 0:
                shot_loc = float(line_split[0])
                if ((shot_loc - first_shot) / shot_spacing) != shot:
                    raise ValueError('Shot number does not match expected shot number')
                shot += 1
                continue
            if int(line_split[2]) == 1:
                geophone_loc = float(line_split[0])
                geophone_num = int((geophone_loc - first_geophone) / phone_spacing)
                time_ms = float(line_split[1])
                time_s = time_ms / 1000
                if geophone_loc < first_geophone or geophone_loc > last_geophone:
                    raise ValueError('Geophone location out of range')
                line = "{0} {1} {2:.6f}\n".format(shot, geophone_num, time_s)
                sgt_obs.append(line)

    num_geophones = int((last_geophone - first_geophone) / phone_spacing) + 1
    num_obs = len(sgt_obs)
    station_lines = []
    # Calculate stations
    # Lead shots
    lead_shots = int(math.ceil((first_geophone - first_shot) / shot_spacing))
    trail_shots = int(math.ceil((last_shot - last_geophone) / shot_spacing))
    num_stations = num_geophones + lead_shots + trail_shots
    station_lines.append("{0} # shot/geophone points\n".format(num_stations))
    station_lines.append("x y\n")
    x = 0.0
    y = 0.0
    trl = trail_shots - 1
    for sta in range(num_stations + 1):
        if sta < lead_shots:
            x = sta * shot_spacing + first_shot
            station_lines.append("{0:.2f} {1:.2f}\n".format(x, y))
            continue
        if sta < lead_shots + num_geophones:
            x = (sta - lead_shots) * phone_spacing + first_geophone
            station_lines.append("{0:.2f} {1:.2f}\n".format(x, y))
            continue
        if sta > lead_shots + num_geophones:
            x = last_shot - (trl * shot_spacing)
            trl -= 1
            # x = (sta - lead_shots - num_geophones) * shot_spacing + last_geophone
            station_lines.append("{0:.2f} {1:.2f}\n".format(x, y))
            continue
    print("Writing to file")
    output = station_lines
    output.append("{0} # measurements\n".format(num_obs))
    output.append("# s g t\n")
    output.extend(sgt_obs)
    with open(sgt_file, 'w') as sgt:
        sgt.writelines(output)
    print("Wrote {0} observations to {1}".format(num_obs, sgt_file))


if __name__ == "__main__":
    if len(sys.argv) < 7:
        print(parse_vs_to_sgt.__doc__)
        sys.exit(1)
    vs_file = sys.argv[1]
    sgt_file = sys.argv[2]
    first_shot = float(sys.argv[3])
    last_shot = float(sys.argv[4])
    first_geophone = float(sys.argv[5])
    last_geophone = float(sys.argv[6])
    shot_spacing = float(sys.argv[7])
    parse_vs_to_sgt(vs_file, sgt_file, first_shot, last_shot, first_geophone, last_geophone, shot_spacing)



