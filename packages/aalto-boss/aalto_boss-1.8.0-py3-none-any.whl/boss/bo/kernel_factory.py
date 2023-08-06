import numpy as np

import GPy


class KernelFactory:
    """
    This class contains the construction of the kernel.
    """

    @staticmethod
    def construct_kernel(settings):
        """
        Creates the kernel.
        """
        kerns = [None] * (settings.dim)
        KernelFactory._select_kernels(kerns, settings)
        KernelFactory._set_constraints(kerns, settings)
        KernelFactory._set_priors(kerns, settings)

        # multiplies the kernels into one object and returns it
        Kernel = kerns[0]
        if len(kerns) > 1:
            for i in range(1, len(kerns)):
                Kernel = Kernel * kerns[i]

        # adds coregionalisation
        if settings.is_multi:
            Kernel = KernelFactory._set_coregionalisation(Kernel, settings)

        return Kernel

    @staticmethod
    def _select_kernels(kerns, settings):
        """
        Selects and creates kernel objects for each dimension. Hyperparameters
        are set to their initial values and default constraints removed.
        """
        for i in range(settings.dim):
            if i == 0:
                ksi = settings["thetainit"][0]
            else:
                ksi = 1.0
            klsi = settings["thetainit"][i + 1]
            kper = settings["periods"][i]

            ktype = settings["kernel"][i]
            if ktype == "stdp":
                kerns[i] = GPy.kern.StdPeriodic(
                    input_dim=1,
                    variance=ksi,
                    period=kper,
                    lengthscale=klsi,
                    ARD1=True,
                    ARD2=True,
                    active_dims=[i],
                    name="kern",
                )
            elif ktype == "rbf":
                kerns[i] = GPy.kern.RBF(
                    input_dim=1,
                    variance=ksi,
                    lengthscale=klsi,
                    ARD=True,
                    active_dims=[i],
                    name="kern",
                )
            elif ktype == "mat32":
                kerns[i] = GPy.kern.Matern32(
                    input_dim=1,
                    variance=ksi,
                    lengthscale=klsi,
                    ARD=True,
                    active_dims=[i],
                    name="kern",
                )
            elif ktype == "mat52":
                kerns[i] = GPy.kern.Matern52(
                    input_dim=1,
                    variance=ksi,
                    lengthscale=klsi,
                    ARD=True,
                    active_dims=[i],
                    name="kern",
                )
            else:
                raise TypeError(f"""Unknown kernel {settings['kernel'][i]}""")

    #            kerns[i].unconstrain()

    @staticmethod
    def _set_constraints(kerns, settings):
        """
        Sets hyperparameter constraints on kernels.
        """
        # variance
        if settings["thetabounds"] is not None:
            kerns[0].variance.constrain_bounded(
                settings["thetabounds"][0][0],
                settings["thetabounds"][0][1],
                warning=False,
            )
            # lengthscale
            for i in range(settings.dim):
                kerns[i].lengthscale.constrain_bounded(
                    settings["thetabounds"][i + 1][0],
                    settings["thetabounds"][i + 1][1],
                    warning=False,
                )
        # period
        for i in range(settings.dim):
            if settings["kernel"][i] == "stdp":  # pbc
                kerns[i].period.constrain_fixed(settings["periods"][i], warning=False)

        # other than the first kernel's variances
        if settings.dim > 1:
            for i in range(1, settings.dim):
                kerns[i].variance.constrain_fixed(1.0, warning=False)

    @staticmethod
    def _set_priors(kerns, settings):
        """
        Sets hyperparameter priors on kernels.
        """
        if settings["thetaprior"] is not None:
            prior = None
            if settings["thetaprior"] == "gamma":
                prior = GPy.priors.Gamma
            else:
                raise TypeError(
                    "Unknown value '"
                    + settings["thetaprior"]
                    + "' given in keyword thetaprior."
                )

            # variance
            kerns[0].variance.set_prior(
                prior(settings["thetapriorpar"][0][0], settings["thetapriorpar"][0][1]),
                warning=False,
            )
            # lengthscale
            for i in range(settings.dim):
                kerns[i].lengthscale.set_prior(
                    prior(
                        settings["thetapriorpar"][i + 1][0],
                        settings["thetapriorpar"][i + 1][1],
                    ),
                    warning=False,
                )

    @staticmethod
    def _set_coregionalisation(kernel, settings):
        """
        Sets coregionalisation on kernel.
        """
        # note: input is one kernel rather than kernel list. this is on
        # purpose as the model class is not equipped to handle other cases
        # atm
        kernel_list = [kernel]
        output_dim = settings["num_tasks"]
        kernel_multi = GPy.util.multioutput.LCM(settings.dim, output_dim,
                                                kernel_list,
                                                settings["W_rank"])

        # parameter dimensions
        d1 = output_dim
        d2 = settings["W_rank"]

        # fix base kernel variance to 1
        kernel_multi.parameters[0].variance.unset_priors()
        kernel_multi.parameters[0].variance.constrain_fixed(1.0)

        # set initial values
        kernel_multi.parameters[-1].W = settings["W_init"].reshape(d1, d2)
        kernel_multi.parameters[-1].kappa = settings["kappa_init"]

        # set priors
        if settings["W_prior"] is not None:
            param = kernel_multi.parameters[-1].W
            pname = settings["W_prior"]
            ppars = settings["W_priorpar"]
            if pname == "fixed_value":
                param.constrain_fixed(float(ppars))
            elif pname == "gaussian":
                param.set_prior(GPy.priors.Gaussian(ppars[0], ppars[1]), warning=False)
            else:
                raise TypeError("Unknown W_prior: {}".format(pname))
        if settings["kappa_prior"] is not None:
            param = kernel_multi.parameters[-1].kappa
            pname = settings["kappa_prior"]
            ppars = settings["kappa_priorpar"]
            if pname == "fixed_value":
                param.constrain_fixed(float(ppars))
            elif pname == "gamma":
                param.set_prior(GPy.priors.Gamma(ppars[0], ppars[1]), warning=False)
            else:
                raise TypeError("Unknown kappa_prior: {}".format(pname))

        return kernel_multi
