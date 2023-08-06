import numpy as np
from boss.utils.arrays import shape_consistent_XY


class UserFunc:
    """Wrapper class for BOSS user functions. """

    def __init__(self, func, dim):
        self.func = func
        self.dim = dim

    def eval(self, X_in, ygrad=False):
        X_in = np.atleast_2d(X_in)
        output = self.func(X_in)

        if isinstance(output, tuple):
            if not ygrad:
                X_out = output[0]
                Y = output[1]
            else:
                if len(output) > 2:
                    X_out = output[0]
                    Y = np.atleast_2d(output[1])
                    dY = np.atleast_2d(output[2])
                else:
                    X_out = X_in
                    Y = np.atleast_2d(output[0])
                    dY = np.atleast_2d(output[1])
                Y = np.concatenate((Y, dY), axis=1)
        else:
            Y = output
            X_out = X_in

        return shape_consistent_XY(X_out, Y, self.dim, ygrad=ygrad)

    def __call__(self, X_in):
        return self.eval(X_in)


class UserFuncList(UserFunc):
    """Wrapper class for multiple BOSS user functions."""

    def __init__(self, func_list, dim):
        self.func_list = func_list
        self.dim = dim + 1

    def __len__(self):
        return len(self.func_list)

    def eval(self, X_in, ygrad=False):
        X_in, index = np.split(np.squeeze(X_in), [self.dim - 1])
        X_in = X_in.reshape(1, self.dim - 1)
        index = int(index)

        output = self.func_list[index](X_in)

        if isinstance(output, tuple):
            if not ygrad:
                X_out = output[0].reshape(-1, self.dim - 1)
                Y = output[1]
            else:
                if len(output) > 2:
                    X_out = output[0].reshape(-1, self.dim - 1)
                    Y = np.atleast_2d(output[1])
                    dY = np.atleast_2d(output[2])
                else:
                    X_out = X_in
                    Y = np.atleast_2d(output[0])
                    dY = np.atleast_2d(output[1])
                Y = np.concatenate((Y, dY), axis=1)
        else:
            Y = output
            X_out = X_in

        X_out = np.hstack((X_out, np.full((len(X_out), 1), index)))
        return shape_consistent_XY(X_out, Y, self.dim)
