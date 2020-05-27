import re
import numpy as np


def sqm_angles(sqm, threshold_percent, threshold_mag, opening, single):
    # Load and process the lowest cenit readings
    # Regex: get magnitudes of m20
    m20 = str(re.findall(r'm20 = \[(.*)\]', sqm)[0]).split(", ")
    for item in m20:
        item.replace(",", ".")
    m20 = np.array(m20, dtype=np.float32)

    # Get the difference between maximum and minimum
    # Regex: Get all contents between "[" and "]"
    magnitudes = re.findall(r'\[(.*)\]', sqm)
    total = []
    for item in magnitudes:
        for x in item.split(", "):
            total.append(str(x).replace(",", "."))
    total = np.asfarray(total, float)
    total_range = (total.max() - total.min()).round(2)
    print('magnitude range: (' + str(total.min()) + ',', str(total.max()) + ')')

    # Calculate the threshold
    if threshold_mag is not None:
        th = threshold_mag
    else:
        th = m20.min() + threshold_percent * total_range

    angle_min = []
    angle_max = []
    # if percentile threshold is set as 1, full angle range
    if threshold_percent == 1:
        angle_min.append(0)
        angle_max.append(359.99)
        return

    # If optional opening was set, just set the global, otherwise proceed to calculate them
    if opening is not None:
        angle_min.append(opening[0])
        angle_max.append(opening[1])
    else:
        # Angles at left and right position of the minimum value
        center_index = int(np.where(m20 == m20.min())[0])
        angle_left = float(((center_index - 1) % 12) * 30)
        angle_right = float(((center_index + 1) % 12) * 30)

        # Set default minimum angle opening
        # If both values at left and right are equal, the opening will be 60º, otherwise 30º
        if m20[int(angle_left / 30)] < m20[int(angle_right / 30)]:
            angle_min.append(angle_left)
            angle_max.append(float(center_index * 30))
        elif m20[int(angle_right / 30)] < m20[int(angle_left / 30)]:
            angle_min.append(float(center_index * 30))
            angle_max.append(angle_right)
        else:
            angle_min.append(angle_left)
            angle_max.append(angle_right)

        # If value at right of min is within percentile threshold and less than the angle_right, update
        # break loop if value surpass percentile threshold
        idx = int(np.where(m20 == m20.min())[0])
        for aux in range(int(idx + 1), int(idx + 13)):
            if m20[aux % 12] <= th:
                angle_max[0] = float((aux % 12) * 30)
            else:
                break

        # If value at left of min is within percentile threshold and less than the angle_left, update
        # break loop if value surpass percentile threshold
        for aux in range(idx - 1, idx - 12, -1):
            if m20[aux % 12] <= th:
                angle_min[0] = float((aux % 12) * 30)
            else:
                break

    if single is False:
        # Continue searching from the main maximum toward right, until main minimum
        # Set start and end indexes
        start = int(((angle_max[0] + 30) % 360) / 30)
        end = int((angle_min[0] % 360) / 30)
        if start == end:
            return
        elif start > end:
            end = end + 12
        # control angle pairs with position in list
        position = 1
        valley = False
        for index in range(start, end):
            # if in "valley"
            if m20[index % 12] <= th:
                # if first entry, new angle pairs
                if len(angle_min) < (position + 1):
                    valley = True
                    angle_min.append(float((index % 12) * 30))
                    angle_max.append(float((index % 12) * 30))
                # if still in valley
                else:
                    angle_max[position] = float((index % 12) * 30)
            # if exit the valley
            elif (m20[index % 12] > th) and (valley is True):
                position = position + 1
                valley = False

    return angle_min, angle_max