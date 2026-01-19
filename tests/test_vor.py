import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vor_mod.parse_airports import get_airports, Airport
from vor_mod.parse_earth_nav import get_vors, Waypoint
from vor_mod.vor import Path, PathPoint


class TestVORNavigation(unittest.TestCase):

    def test_get_airports(self):
        """Test that airport data can be loaded"""
        airports = get_airports()
        self.assertIsInstance(airports, list)
        self.assertGreater(len(airports), 0)

        # Check that first airport has required attributes
        airport = airports[0]
        self.assertIsInstance(airport, Airport)
        self.assertTrue(hasattr(airport, 'icao'))
        self.assertTrue(hasattr(airport, 'lat'))
        self.assertTrue(hasattr(airport, 'lng'))

    def test_get_vors(self):
        """Test that VOR data can be loaded"""
        vors = get_vors()
        self.assertIsInstance(vors, list)
        self.assertGreater(len(vors), 0)

        # Check that first VOR has required attributes
        vor = vors[0]
        self.assertIsInstance(vor, Waypoint)
        self.assertEqual(vor.type, "VOR")
        self.assertTrue(hasattr(vor, 'ident'))
        self.assertTrue(hasattr(vor, 'lat'))
        self.assertTrue(hasattr(vor, 'lng'))
        self.assertTrue(hasattr(vor, 'freq'))

    def test_path_creation(self):
        """Test basic Path class functionality"""
        airports = get_airports()
        if len(airports) < 2:
            self.skipTest("Need at least 2 airports for path test")

        start_airport = airports[0]
        end_airport = airports[1]

        start_point = PathPoint(start_airport)
        end_point = PathPoint(end_airport)

        path = Path(start_point, end_point, 10000)

        self.assertEqual(path.start_point.object, start_airport)
        self.assertEqual(path.end_point.object, end_airport)
        self.assertEqual(path.cruise_altitude, 10000)
        self.assertEqual(len(path.path), 1)  # Should start with just the start point

    def test_path_point_creation(self):
        """Test PathPoint creation for airports and waypoints"""
        airports = get_airports()
        vors = get_vors()

        if len(airports) > 0:
            airport = airports[0]
            path_point = PathPoint(airport)
            self.assertEqual(path_point.object, airport)
            self.assertEqual(path_point.type, "airport")
            self.assertEqual(path_point.shortname, airport.icao)

        if len(vors) > 0:
            vor = vors[0]
            path_point = PathPoint(vor)
            self.assertEqual(path_point.object, vor)
            self.assertEqual(path_point.type, "waypoint")
            self.assertEqual(path_point.shortname, vor.ident)


if __name__ == '__main__':
    unittest.main()