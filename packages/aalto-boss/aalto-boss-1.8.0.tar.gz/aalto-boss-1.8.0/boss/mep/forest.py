import numpy as np
from boss.mep.node import Node


class Forest:
    def __init__(self, nodes):
        self.trees = nodes

    def get_closest_point(self, point, space):
        closest = self.trees[0]
        smallest_dist = np.linalg.norm(space.vec(closest.coords, point))
        for tree in self.trees:
            temp = tree.get_closest_point(point, space)
            if temp[1] < smallest_dist:
                closest = temp[0]
                smallest_dist = temp[1]
        return (closest, smallest_dist)

    def get_all_children(self):
        all_children = []
        for tree in self.trees:
            all_children.extend(tree.get_all_children())
        return all_children

    def grow(self, model, eps, max_e, space):
        boundlength = space.bounds[1, :] - space.bounds[0, :]
        dim = space.bounds.shape[1]
        new_point = np.random.random(dim) * boundlength + space.bounds[0, :]
        if dim < model.dim:
            new_point = np.hstack((new_point, 0))  # add task index
        new_e = model.predict(np.vstack(np.atleast_2d(new_point)))[0][0, 0]
        if new_e < max_e:
            closest, dist = self.get_closest_point(new_point, space)
            new_point = space.trace(closest.coords, new_point, model, eps, max_e)
            if not np.prod(new_point == closest.coords):
                closest.children.append(Node(new_point, closest))

    def get_random_child(self):
        all_children = self.get_all_children()
        return np.random.choice(all_children, size=1)[0]

    def merge(self, other_forest):
        for tree in other_forest.trees:
            self.trees.append(tree)

    def test_connectivity_once(self, forest_B, model, space, eps, max_e):
        random_A = self.get_random_child()
        closest_B, dist = forest_B.get_closest_point(random_A.coords, space)
        endpoint = space.trace(random_A.coords, closest_B.coords, model, eps, max_e)
        if np.prod(endpoint == closest_B.coords):
            return [random_A, closest_B]
        else:
            return None
