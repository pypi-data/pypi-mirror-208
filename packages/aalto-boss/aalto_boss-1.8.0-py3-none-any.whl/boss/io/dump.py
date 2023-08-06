"""
Functionality to output raw data on request to files outside of the main
output (*.out) file and the restart (*.rst) file.
"""
import numpy as np
import os

import boss.io.ioutils as ioutils
from boss.keywords import stringify


def dump_input_file(new_file_path, keywords, results_header=False):
    with open(new_file_path, "w") as fd:
        for key in sorted(keywords):
            val_str = stringify(keywords[key])
            fd.write(f"{key} {val_str}\n")
        if results_header:
            fd.write("\nRESULTS:")


def build_query_points(settings, defaults):
    """Build array of query points."""
    npts_per_dim = settings["pp_model_slice"][2]
    slice1 = settings["pp_model_slice"][0]
    slice2 = settings["pp_model_slice"][1]
    bounds = settings["bounds"]
    is_2d = slice1 != slice2

    # Construct query points for required slices
    x1 = np.linspace(*bounds[slice1], npts_per_dim)
    if is_2d:
        # 2D slice
        x2 = np.linspace(*bounds[slice2], npts_per_dim)
        x1, x2 = np.meshgrid(x1, x2)
        x1 = x1.ravel()
        x2 = x2.ravel()
        npts = npts_per_dim**2
    else:
        # 1D slice
        npts = npts_per_dim
    assert len(x1) == npts

    # Full ND array of query points
    X = np.empty((npts, np.atleast_2d(defaults).shape[1]))

    # Fill ND query point array with default values
    if settings["pp_var_defaults"] is None:
        X[:] = defaults
    else:
        X[:] = settings["pp_var_defaults"]

    # Use actual query values at correct dimensions
    X[:, slice1] = x1
    if is_2d:
        X[:, slice2] = x2
    return X


def build_header_line(settings, name):
    npts_per_dim = settings["pp_model_slice"][2]
    slice1 = settings["pp_model_slice"][0]
    slice2 = settings["pp_model_slice"][1]
    is_2d = slice1 != slice2
    header = f"# {name}, grid of "
    if is_2d:
        header += "%ix%i=" % (npts_per_dim, npts_per_dim)
        npts = npts_per_dim**2
    else:
        npts = npts_per_dim
    header += "%i pts\n" % npts
    return header


def dump_model(settings, dest_file, model, mod_params, x_glmin):
    """
    Outputs model slice (up to 2D) mean and variance in a grid to
    models/it#.dat
    """
    X = build_query_points(settings, x_glmin)
    mu, var = model.predict(X)
    nu = np.sqrt(var)
    data = np.hstack((X, mu, nu))

    header = build_header_line(settings, "Model output (x mu nu)")
    header += (
        "# Model parameter values "
        + "({}): ".format(' '.join(mod_params.keys()))
        + format(tuple(mod_params.values()))
        + "\n"
    )

    with open(dest_file, 'w') as fd:
        fd.write(header)
        np.savetxt(fd, data, fmt='%18.8e')


def dump_acqfn(settings, dest_file, acqfn, defs):
    """
    Outputs acquisition function slice (up to 2D) in a grid to
    acqfns/it#.dat
    """
    X = build_query_points(settings, defs)

    if settings['costfn'] is None:
        af = acqfn(X)
        data = np.hstack((X, af))
    else:
        data = []
        for x in X:
            af = acqfn(x)
            data.append(np.concatenate((x, af[0])))
        data = np.array(data)

    header = build_header_line(settings, "Acquisition function (x af)")

    with open(dest_file, 'w') as fd:
        fd.write(header)
        np.savetxt(fd, data, fmt='%18.8e')


def dump_truef(settings, dest_file, last_xhat):
    """
    Outputs true function slice (up to 2D) in a grid
    """
    truef_data = [[]] * (settings.dim + 1)  # coords + truef
    npts = settings["pp_truef_npts"]
    coords = np.array(
        [
            np.linspace(settings["bounds"][i, 0], settings["bounds"][i, 1], npts)
            for i in settings["pp_model_slice"][:2]
        ]
    )
    defaults = (
        last_xhat
        if settings["pp_var_defaults"] is None
        else settings["pp_var_defaults"]
    )
    if settings["pp_model_slice"][0] != settings["pp_model_slice"][1]:
        # 2D slice
        x1, x2 = np.meshgrid(coords[0], coords[1])
        for i in range(npts):
            for j in range(npts):
                p = np.array([x1[i, j], x2[i, j]])
                for d in range(settings.dim):
                    if d not in settings["pp_model_slice"][:2]:
                        p = np.insert(p, d, defaults[d])

                tf = settings.f(np.atleast_2d(p))[1][0].item()

                os.chdir(settings.dir)
                p = np.insert(p, len(p), float(tf))
                truef_data = np.insert(truef_data, len(truef_data[0]), p, axis=1)
        titleLine = "# True function output (x" + " f), grid of %ix%i=%i pts" % (
            npts,
            npts,
            npts ** 2,
        )
    else:
        # 1D slice
        x1 = coords[0]
        for i in range(npts):
            p = np.array([x1[i]])
            for d in range(settings.dim):
                if d not in settings["pp_model_slice"][:2]:
                    p = np.insert(p, d, defaults[d])
            tf = settings.f(np.atleast_2d(p))[1][0].item()
            os.chdir(settings.dir)
            p = np.insert(p, len(p), float(tf))
            truef_data = np.insert(truef_data, len(truef_data[0]), p, axis=1)
        titleLine = "# True function output (x" + " f), grid of %i pts" % (npts)

    ioutils.write_cols(dest_file, truef_data, "    ", titleLine, "%18.8E")


def dump_mep(path):
    """
    Outputs the coordinates of each minimum energy path into files
    """
    crds = path.crds
    i = path.mi
    j = path.mj
    s = "# From minima " + str(i) + " ("
    for crd in crds[0, :]:
        s += "  %f" % crd
    s += ")\n#   to minima " + str(j) + " ("
    for crd in crds[crds.shape[0] - 1, :]:
        s += "  %f" % crd
    s += ")\n"
    s += "# Highest energy: %8.3E\n\n" % path.maxe
    s += "# coordinates, energy\n"

    for ci in range(crds.shape[0]):
        for crd in crds[ci, :]:
            s += "  %f" % crd
        s += "  %8.3E\n" % path.energy[ci]
    ioutils.overwrite("mep/pathcrds_" + str(i) + "_" + str(j) + ".dat", s)
