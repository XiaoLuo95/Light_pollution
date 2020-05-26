import pandas as pd


def tas_angles(tas, threshold_percent, threshold_mag, opening, m10, single):
    # get useful information: T_IR, T_Sens, Mag, Azi of m10, and max & min value in Mag
    mag_max = float(tas[0].split()[5])
    mag_min = float(tas[0].split()[5])
    for line in tas:
        sp = line.split()
        if sp[7] == '10.0':
            cloudiness = 100 - 3 * (float(sp[4]) - float(sp[3]))
            m10 = m10.append({'Mag': sp[5], 'Azi': sp[8], 'Cloudiness': cloudiness}, ignore_index=True)
        if float(sp[5]) > mag_max:
            mag_max = float(sp[5])
        elif float(sp[5]) < mag_min:
            mag_min = float(sp[5])
    m10 = m10.astype({'Mag': float, 'Azi': float, 'Cloudiness': float})
    m10 = m10.round({'Mag': 2, 'Azi': 2, 'Cloudiness': 2})
    mag_range = mag_max - mag_min

    # Calculate threshold
    if threshold_mag is not None:
        th = threshold_mag
    else:
        th = mag_min + threshold_percent * mag_range

    angle_min = []
    angle_max = []
    if threshold_percent == 1:
        angle_min.append(0)
        angle_max.append(359.99)
        return

    # If optional opening was set, just set the global, otherwise proceed to calculate them
    if opening is not None:
        angle_min.append(opening[0])
        angle_max.append(opening[1])
    else:
        # position of the minimum and its angle
        center_index = m10['Mag'].argmin()
        angle_center = m10.loc[[center_index]]['Azi'].item()
        # magnitudes and angles of adjacents from minimum
        mag_left = m10.loc[[(center_index - 1) % len(m10)]]['Mag'].item()
        mag_right = m10.loc[[(center_index + 1) % len(m10)]]['Mag'].item()
        angle_left = m10.loc[[(center_index - 1) % len(m10)]]['Azi'].item()
        angle_right = m10.loc[[(center_index + 1) % len(m10)]]['Azi'].item()

        # Set default minimum angle opening
        # If both values at left and right are equal, the opening will be 22º, otherwise 11º
        if mag_left < mag_right:
            angle_min.append(angle_left)
            angle_max.append(angle_center)
        elif mag_right < mag_left:
            angle_min.append(angle_center)
            angle_max.append(angle_right)
        else:
            angle_min.append(angle_left)
            angle_max.append(angle_right)

        max_index = center_index
        min_index = center_index
        # If value at right of min is within threshold and less than the angle_right, update
        # break loop if value surpass threshold
        for aux in range(center_index + 1, center_index + len(m10)):
            val_max = m10.loc[[aux % len(m10)]]['Mag'].item()
            if val_max <= th:
                angle_max[0] = m10.loc[[aux % len(m10)]]['Azi'].item()
                max_index = aux % len(m10)
            else:
                break

        # If value at left of min is within threshold and less than the angle_left, update
        # break loop if value surpass threshold
        for aux in range(center_index - 1, center_index - len(m10), -1):
            val_min = m10.loc[[aux % len(m10)]]['Mag'].item()
            if val_min <= th:
                angle_min[0] = m10.loc[[aux % len(m10)]]['Azi'].item()
                min_index = aux % len(m10)
            else:
                break

    if single is False:
        # Continue searching from the main maximum toward right, until main minimum
        # Set start and end indexes
        start = (max_index + 1) % len(m10)
        end = min_index
        if start == end:
            return
        elif start > end:
            end = end + len(m10)
        # control of angle pairs with position of angle in the list
        position = 1
        valley = False
        for index in range(start, end):
            # if enter the "valley"
            if m10.loc[[index % len(m10)]]['Mag'].item() <= th:
                # if first entry, new pair of angles
                if len(angle_min) < (position + 1):
                    valley = True
                    angle_min.append(m10.loc[[index % len(m10)]]['Azi'].item())
                    angle_max.append(m10.loc[[index % len(m10)]]['Azi'].item())
                # if still in valley
                else:
                    angle_max[position] = m10.loc[[index % len(m10)]]['Azi'].item()
            # if exit the "valley"
            elif (m10.loc[[index % len(m10)]]['Mag'].item() > th) and (valley is True):
                position = position + 1
                valley = False

    return angle_min, angle_max, m10