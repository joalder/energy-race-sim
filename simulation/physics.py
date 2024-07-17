def power_for_velocity(velocity):
    # calculate air resistance
    roh = 1.2041
    coefficient_of_drag = 0.23
    area = 1.433 * 1.850  # from model 3 width * height
    cw_a = coefficient_of_drag * area
    force_air = cw_a * velocity * velocity / 2 * roh

    # calculate roll resistance
    c_r = 0.012  # asphalt 0.011-0,015 according Wikipedia.
    force_roll_resistance = c_r * 1950 * 9.81  # model 3 incl driver = 1,95t*g=F

    # calculate power needed for specific velocity
    return (force_air + force_roll_resistance) * velocity


def power_for_velocity_change(delta_velocity):
    pass
