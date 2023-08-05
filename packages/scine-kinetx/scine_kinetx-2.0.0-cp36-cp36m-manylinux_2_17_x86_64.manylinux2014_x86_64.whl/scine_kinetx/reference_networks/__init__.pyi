"""The ``reference_networks`` submodule defines a set of known fixed networks."""
import scine_kinetx.reference_networks
import typing
from typing import Union
import numpy
import scine_kinetx

__all__ = [
    "get_bray_liebhafsky"
]


def get_bray_liebhafsky() -> typing.Tuple[scine_kinetx.Network, numpy.ndarray]:
    """
          Get a model for the Bray–Liebhafsky reaction.
          The model used here can be found in:
          "Improvement of the stoichiometric network analysis for determination of
          instability conditions of complex nonlinear reaction systems"
          Ljiljana Kolar-Anic, Zeljko Cupic, Guy Schmitz, Slobodan Anic
          Chemical Engineering Science, 65, (2010), 3718-3728
          https://www.sciencedirect.com/science/article/pii/S0009250910001569

          :return The newtork and a set of initial concentrations.
        
    """
