import traffic_simulator.cars as ts
import traffic_simulator.physics as ph
import traffic_simulator.geometry as geo
import numpy as np


car = ts.Cars(
    number_of_cars=10,
    v_initial=18,
    dt=0.1,
    name="Monaco",
)

for step in car.t:

    # Declaration
    cars_data = np.array([
        car.positions,
        car.velocities,
    ])

    sector_data = np.array([
        car.segment_positions,
        car.segment_lengths,
        car.segment_speeds
    ])

    sectors = geo.position(positions=car.positions, segment_positions=car.segment_positions)
    distances = geo.distance(positions=car.positions, length=car.length)
    minimum_gaps = car.minimum_distances()

    # Computing
    acc_sector = ph.sector_acceleration(
        cars=cars_data,
        sectors=sector_data,
        sector_positions=sectors,
        beta=car.segment_reactions,
    )
    acc_distance = ph.distance_acceleration(
        s_diff=distances,
        s_min=minimum_gaps,
        alpha=car.distance_reactions,
    )
    acc = ph.calculate_acceleration(
        acc_sect=acc_sector,
        acc_car=acc_distance,
    )


    # Calculate new velocities and positions then remembering them
    car.velocities = ph.ei_v(vel=car.velocities, acc=acc, dt=car.dt)
    car.positions = ph.ei_s(pos=car.positions, vel=car.velocities, acc=acc, dt=car.dt)
    car.add_position_history(car.positions)
    car.add_speed_history(car.velocities)


# Animation
car.animate_cars()
car.plot()
