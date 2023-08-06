import numpy as np
import warnings
import itertools

import boss.utils.sobol_seq as sobol_seq


class InitManager:
    def __init__(self, inittype, bounds, initpts, seed=None):
        """
        Creates initial points which can be queried with the get_x and get_all
        methods. Available types of initial points (parameter inittype) are:
            sobol
            random
            grid
        """
        dim = bounds.shape[0]
        self.init_data = None
        if inittype.lower() == "sobol":
            self.init_data = self._sobol(dim, bounds, initpts)
        elif inittype.lower() == "random":
            self.init_data = self._random(dim, bounds, initpts, seed=seed)
        elif inittype.lower() == "grid":
            npts = np.power(initpts, 1.0 / dim).astype(int)
            if not np.all(initpts == npts ** dim):
                initpts = npts ** dim
                warnings.warn(
                    "Grid based initial point creation modifies"
                    + " initpts so that nth root of it is an integer"
                    + " , where n in the number of dimensions."
                )
            self.init_data = self._grid(bounds, npts)
        else:
            raise TypeError(
                "Unknown option set to keyword inittype. "
                + "Unable to determine initial data."
            )

    def get_x(self, i):
        """
        Returns the i:th initial point
        """
        return self.init_data[i, :]

    def get_all(self):
        """
        Returns all generated initial points
        """
        return self.init_data

    def _sobol(self, dim, bounds, initpts):
        """
        Initial points with the quasi-random Sobol sequence
        """
        npts = np.max(initpts)
        if npts < 1:
            return  ### STOP here if npts < 1
        sobs = np.transpose(sobol_seq.i4_sobol_generate(dim, npts, 1))
        pts = np.array([]).reshape(0, dim)
        for p in range(npts):
            point = np.array([])
            for d in range(dim):
                a = sobs[p, d] * (bounds[d][1] - bounds[d][0]) + bounds[d][0]
                point = np.append(point, a)
            pts = np.append(pts, [point], axis=0)
        if not np.isscalar(initpts) and len(initpts) > 1:
            pts = self._extend(pts, initpts)
        return pts

    def _random(self, dim, bounds, initpts, seed=None):
        """
        Initial points randomly
        """
        random_state = np.random.RandomState(seed)
        npts = np.max(initpts)
        pts = random_state.rand(npts*dim).reshape(npts, dim)
        pts = pts * (bounds[:,1]-bounds[:,0]) + bounds[:,0]
        if not np.isscalar(initpts) and len(initpts) > 1:
            pts = self._extend(pts, initpts)
        return pts

    def _grid(self, bounds, npts):
        """
        Initial points in a grid. Total number of points returned is npts^dim.
        """
        if not np.isscalar(npts) and len(npts) > 1:
            pts = []
            for task, task_npts in enumerate(npts):
                task_pts = self._make_grid(bounds, task_npts)
                pts.append(np.hstack((task_pts, np.full((len(task_pts), 1), task))))
            pts = np.vstack(pts)
        else:
            pts = self._make_grid(bounds, int(npts))
        return pts

    def _make_grid(self, bounds, npts):
        """
        Return grid with npts points across bounds in each dimension.
        """
        base = [np.linspace(*b, num=npts, endpoint=False) for b in bounds]
        return np.array(list(itertools.product(*base))).astype(float)

    def _extend(self, data, npts):
        """
        Extend initial points with task index.
        """
        data = np.atleast_2d(data)
        data_extended = []
        for task, task_npts in enumerate(npts):
            task_data = np.hstack((data[:task_npts], np.full((task_npts, 1), task)))
            data_extended.append(task_data)
        data_extended = np.vstack(data_extended)
        return data_extended
