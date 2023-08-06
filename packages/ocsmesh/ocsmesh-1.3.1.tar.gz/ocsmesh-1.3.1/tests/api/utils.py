#! python
import unittest
from copy import deepcopy

import numpy as np
from shapely.geometry import (
    Point,
    LineString,
    box,
    Polygon,
    MultiPolygon,
    GeometryCollection,
)

from ocsmesh import utils

from tests.api.common import (
    create_rectangle_mesh,
    msht_from_numpy,
)


class FinalizeMesh(unittest.TestCase):

    def test_cleanup_mesh_and_generate_valid_mesh(self):
        msh_t1 = create_rectangle_mesh(
            nx=40, ny=40,
            holes=[50, 51],
            quads=np.hstack((
                np.arange(130, 150),
                np.arange(170, 190),
            )),
            x_extent=(-2, 2), y_extent=(-2, 2))

        msh_t2 = create_rectangle_mesh(
            nx=20, ny=20,
            holes=[],
            x_extent=(-3.5, -3), y_extent=(0, 1))

        verts = msh_t1.vert2['coord']
        verts = np.vstack((verts, msh_t2.vert2['coord']))

        trias = msh_t1.tria3['index']
        trias = np.vstack((trias, msh_t2.tria3['index'] + len(msh_t1.vert2)))

        quads = msh_t1.quad4['index']
        quads = np.vstack((quads, msh_t2.quad4['index'] + len(msh_t1.vert2)))

        msh_t = msht_from_numpy(verts, trias, quads)

        utils.finalize_mesh(msh_t)


class RemovePolygonHoles(unittest.TestCase):

    def setUp(self):
        self._main = box(0, 0, 10, 6)
        self._aux = box(-3, -3, -1, 3)
        self._hole1 = Point(3, 3).buffer(1.5)
        self._hole2 = Point(7.17, 4.13).buffer(1.43)
        self._hole1_island = Point(3.15, 3.25).buffer(1)
        self._hole1_island_hole1 = Point(3.20, 2.99).buffer(0.25)

        self._poly = Polygon(
            self._main.boundary,
            [
                self._hole1.boundary,
                self._hole2.boundary
            ]
        )
        self._island = Polygon(
            self._hole1_island.boundary,
            [
                self._hole1_island_hole1.boundary
            ]
        )
        self._multipoly1 = MultiPolygon([self._poly, self._island])
        self._multipoly2 = MultiPolygon([self._poly, self._island, self._aux])


    def test_invalid_input_raises(self):
        self.assertRaises(
            ValueError, utils.remove_holes, Point(0, 0)
        )
        self.assertRaises(
            ValueError, utils.remove_holes, LineString([[0, 0], [1, 1]])
        )
        self.assertRaises(
            ValueError, utils.remove_holes, GeometryCollection()
        )

        self.assertRaises(
            ValueError, utils.remove_holes_by_relative_size, Point(0, 0)
        )
        self.assertRaises(
            ValueError, utils.remove_holes_by_relative_size, LineString([[0, 0], [1, 1]])
        )
        self.assertRaises(
            ValueError, utils.remove_holes_by_relative_size, GeometryCollection()
        )


    def test_no_mutate_input_1(self):

        utils.remove_holes(self._poly)
        self.assertEqual(
            len(self._poly.interiors), 2
        )


    def test_no_mutate_input_2(self):

        utils.remove_holes_by_relative_size(self._poly, 1)
        self.assertEqual(
            len(self._poly.interiors), 2
        )


    def test_remove_polygon_holes(self):

        self.assertIsInstance(
            utils.remove_holes(self._poly), Polygon
        )
        self.assertTrue(
            utils.remove_holes(self._poly).is_valid
        )
        self.assertEqual(
            self._main,
            utils.remove_holes(self._main)
        )
        self.assertEqual(
            len(utils.remove_holes(self._poly).interiors),
            0
        )


    def test_remove_multipolygon_holes(self):

        self.assertIsInstance(
            utils.remove_holes(self._multipoly1), Polygon
        )
        self.assertTrue(
            utils.remove_holes(self._multipoly1).is_valid
        )
        self.assertEqual(
            len(utils.remove_holes(self._multipoly1).interiors),
            0
        )

        self.assertIsInstance(
            utils.remove_holes(self._multipoly2), MultiPolygon
        )
        self.assertTrue(
            utils.remove_holes(self._multipoly2).is_valid
        )
        self.assertEqual(
            sum(len(p.interiors) for p in utils.remove_holes(self._multipoly2).geoms),
            0
        )


    def test_remove_polygon_holes_with_size(self):
        self.assertIsInstance(
            utils.remove_holes_by_relative_size(self._poly, 1), Polygon
        )
        self.assertTrue(
            utils.remove_holes_by_relative_size(self._poly, 1).is_valid
        )
        self.assertEqual(
            self._main,
            utils.remove_holes_by_relative_size(self._main, 1)
        )
        self.assertEqual(
            len(
               utils.remove_holes_by_relative_size(
                    self._poly, 1
               ).interiors
            ),
            0
        )
        self.assertEqual(
            len(
               utils.remove_holes_by_relative_size(
                    self._poly, 0.5
               ).interiors
            ),
            0
        )
        self.assertEqual(
            len(
               utils.remove_holes_by_relative_size(
                    self._poly, 0.15
               ).interiors
            ),
            1
        )
        self.assertEqual(
            len(
               utils.remove_holes_by_relative_size(
                    self._poly, 0
               ).interiors
            ),
            2
        )



    def test_remove_multipolygon_holes_with_size(self):

        self.assertIsInstance(
            utils.remove_holes_by_relative_size(self._multipoly1, 1),
            Polygon
        )
        self.assertTrue(
            utils.remove_holes_by_relative_size(
                self._multipoly1, 1
            ).is_valid
        )
        self.assertEqual(
            len(
                utils.remove_holes_by_relative_size(
                    self._multipoly1, 1
                ).interiors
            ),
            0
        )
        self.assertEqual(
            sum(
                len(p.interiors) for p in 
                utils.remove_holes_by_relative_size(
                    self._multipoly1,
                    0
                ).geoms
            ),
            3
        )
        self.assertEqual(
            sum(
                len(p.interiors) for p in 
                utils.remove_holes_by_relative_size(
                    self._multipoly1,
                    0.1
                ).geoms
            ),
            2
        )
        self.assertEqual(
            sum(
                len(p.interiors) for p in 
                utils.remove_holes_by_relative_size(
                    self._multipoly1,
                    0.15
                ).geoms
            ),
            1
        )
        self.assertEqual(
            len(
                utils.remove_holes_by_relative_size(
                    self._multipoly1, 0.2
                ).interiors
            ),
            0
        )

        self.assertIsInstance(
            utils.remove_holes_by_relative_size(self._multipoly2, 1), MultiPolygon
        )
        self.assertTrue(
            utils.remove_holes_by_relative_size(self._multipoly2, 1).is_valid
        )
        self.assertEqual(
            sum(len(p.interiors) for p in utils.remove_holes_by_relative_size(self._multipoly2, 1).geoms),
            0
        )


if __name__ == '__main__':
    unittest.main()
