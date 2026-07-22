import pytest
import numpy as np
from unittest.mock import patch

from traffic_sim.geometry import distance, position
from traffic_sim.physics import (
    sign,
    reactor,
    distance_acceleration,
    sector_acceleration,
    calculate_acceleration,
    ei_v,
    ei_s,
)
from traffic_sim.track import Track, RoadSegment
from traffic_sim.cars import Cars
from traffic_sim.animation import Animation
from traffic_sim.constants import PartIndex, CarConst


# ==============================================================================
# 1. Geometry Module Tests
# ==============================================================================
class TestGeometry:
    def test_distance_wrap_around(self):
        """Test circular track distance calculation between vehicles."""
        track_length = 100.0
        positions = np.array([10.0, 40.0, 90.0])
        
        # Expected distances: (40-10)=30, (90-40)=50, (10 + 100 - 90)=20
        expected = np.array([30.0, 50.0, 20.0])
        calculated = distance(positions, track_length)
        
        np.testing.assert_allclose(calculated, expected)

    def test_position_segment_mapping(self):
        """Test mapping car positions into road sector indexes."""
        segment_ends = np.array([100.0, 250.0, 500.0])
        car_positions = np.array([50.0, 150.0, 300.0])
        
        # 50.0 < 100 -> sector 0
        # 150.0 is in [100, 250) -> sector 1
        # 300.0 is in [250, 500) -> sector 2
        expected_sectors = np.array([0, 1, 2])
        calculated = position(car_positions, segment_ends)
        
        np.testing.assert_array_equal(calculated, expected_sectors)


# ==============================================================================
# 2. Physics Module Tests
# ==============================================================================
class TestPhysics:
    def test_sign_function(self):
        arr1 = np.array([5, 2, 3])
        arr2 = np.array([3, 2, 4])
        # 5 > 3 -> 1, 2 not > 2 -> -1, 3 not > 4 -> -1
        expected = np.array([1, -1, -1])
        np.testing.assert_array_equal(sign(arr1, arr2), expected)

    def test_reactor_function(self):
        arr1 = np.array([10.0, 20.0])
        arr2 = np.array([5.0, 30.0])
        res = reactor(arr1, arr2)
        
        assert res.shape == arr1.shape
        assert not np.isnan(res).any()
        assert not np.isinf(res).any()

    def test_distance_acceleration_beyond_sensitivity(self):
        """Cars beyond sensitivity distance should experience 0 car-following acceleration."""
        s_diff = np.array([100.0, 200.0])
        s_min = np.array([10.0, 10.0])
        alpha = np.array([1.0, 1.0])
        
        acc = distance_acceleration(s_diff, s_min, alpha, sensitivity=2.5)
        np.testing.assert_array_equal(acc, np.array([0.0, 0.0]))

    def test_calculate_acceleration_combination(self):
        acc_sect = np.array([0.5, -1.0])
        acc_car = np.array([-0.2, 0.5])
        
        total_acc = calculate_acceleration(acc_sect, acc_car)
        np.testing.assert_allclose(total_acc, np.array([0.3, -0.5]))

    def test_euler_integration(self):
        vel = np.array([10.0, 20.0])
        acc = np.array([2.0, -4.0])
        dt = 0.5
        
        # v1 = v0 + a*dt
        v_next = ei_v(vel, acc, dt)
        np.testing.assert_allclose(v_next, np.array([11.0, 18.0]))
        
        # s1 = s0 + v0*dt + 0.5*a*dt^2
        pos = np.array([0.0, 100.0])
        s_next = ei_s(pos, vel, acc, dt)
        expected_s = pos + vel * dt + 0.5 * acc * (dt ** 2)
        np.testing.assert_allclose(s_next, expected_s)


# ==============================================================================
# 3. Track & Road Segment Tests
# ==============================================================================
class TestTrack:
    def test_road_segment_properties(self):
        seg = RoadSegment(position=1, segment_type="highway")
        assert seg.segment_speed == 36
        assert seg.segment_length == 800
        assert seg.segment_icon == "🟩 "

    @patch("builtins.input", side_effect=["y"])
    def test_predetermined_track_initialization(self, mock_input):
        track = Track()
        
        assert track.number_of_segments > 0
        assert track.length > 0
        assert track.r == track.length / (2 * np.pi)
        assert track.segments.shape[0] == 3  # (LENGTH, ZONES, MAX_SPEEDS)

    @patch("builtins.input", side_effect=["y"])
    def test_change_speed_limit(self, mock_input):
        track = Track()
        initial_speed = track.segment_speeds[0]
        
        track.change_speed_limit(0, initial_speed + 5.0)
        assert track.segment_speeds[0] == initial_speed + 5.0

    @patch("builtins.input", side_effect=["y"])
    def test_invalid_speed_limit_change(self, mock_input):
        track = Track()
        
        with pytest.raises(ValueError):
            track.change_speed_limit(-1, 20.0)
            
        with pytest.raises(TypeError):
            track.change_speed_limit(0, "fast")


# ==============================================================================
# 4. Cars State Tests
# ==============================================================================
class TestCars:
    @patch("builtins.input", side_effect=["y"])
    def test_cars_initialization(self, mock_input):
        num_cars = 5
        v_initial = 12.0
        dt = 0.1
        
        cars = Cars(number_of_cars=num_cars, v_initial=v_initial, dt=dt, name="TestRun")
        
        assert len(cars.positions) == num_cars
        assert len(cars.velocities) == num_cars
        assert np.all(cars.velocities == v_initial)
        assert len(cars.distance_reactions) == num_cars

    @patch("builtins.input", side_effect=["y"])
    def test_invalid_car_count(self, mock_input):
        with pytest.raises(ValueError, match="positive integer"):
            Cars(number_of_cars=0, v_initial=10.0, dt=0.1, name="Invalid")

    @patch("builtins.input", side_effect=["y"])
    def test_positions_modulo_wrapping(self, mock_input):
        cars = Cars(number_of_cars=4, v_initial=10.0, dt=0.1, name="WrapTest")
        
        # Position exceeding track length should wrap cleanly via modulo
        overshoot_positions = np.array([cars.length + 10.0, cars.length + 50.0, 5.0, 12.0])
        cars.positions = overshoot_positions
        
        expected = overshoot_positions % cars.length
        np.testing.assert_allclose(cars.positions, expected)


# ==============================================================================
# 5. Animation Data Logging Tests
# ==============================================================================
class TestAnimation:
    @patch("builtins.input", side_effect=["y"])
    def test_history_logging(self, mock_input):
        anim = Animation(name="LogTest", numc=3, dt=0.1)
        
        p_frame = np.array([10.0, 20.0, 30.0])
        v_frame = np.array([5.0, 5.0, 5.0])
        c_frame = np.array([1.0, 0.8, 1.2])
        
        anim.add_position_history(p_frame)
        anim.add_speed_history(v_frame)
        anim.add_congestion_history(c_frame)
        
        assert len(anim.position_history) == 1
        assert len(anim.speed_history) == 1
        assert len(anim.congestion_history) == 1
        np.testing.assert_array_equal(anim.position_history[0], p_frame)
