"""Pybind11 Bindings for SCINE-Kinetx"""
import scine_kinetx
import typing
from typing import Union
import scine_kinetx.reference_networks as reference_networks
import numpy
import scipy.sparse

__all__ = [
    "Integrator",
    "Network",
    "NetworkBuilder",
    "RandomNetworkFactory",
    "get_integrator",
    "integrate",
    "reference_networks"
]


class Integrator():
    """
    Members:

      cash_karp_5

      explicit_euler

      implicit_euler
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    __members__: dict # value = {'cash_karp_5': <Integrator.cash_karp_5: 0>, 'explicit_euler': <Integrator.explicit_euler: 1>, 'implicit_euler': <Integrator.implicit_euler: 2>}
    cash_karp_5: scine_kinetx.Integrator # value = <Integrator.cash_karp_5: 0>
    explicit_euler: scine_kinetx.Integrator # value = <Integrator.explicit_euler: 1>
    implicit_euler: scine_kinetx.Integrator # value = <Integrator.implicit_euler: 2>
    pass
class Network():
    def __init__(self, arg0: numpy.ndarray, arg1: typing.Tuple[scipy.sparse.csc_matrix[numpy.float64], scipy.sparse.csc_matrix[numpy.float64]], arg2: typing.Tuple[scipy.sparse.csc_matrix[numpy.int32], scipy.sparse.csc_matrix[numpy.int32]], arg3: typing.List[str]) -> None: 
        """
                Constructor.
              :param masses:          The masses of the compounds in the network.
              :param rate_constants:  The rate constants ({forward, backward}) of all reactions and
                                      channels (matrix order: (reaction index, channel index)).
              :param stoichiometry:   The stoichiometry of all reactions in the network ({lhs, rhs})
                                      Matrix ordering is (reaction index, compound index).
              :param compound_labels: The compound labels.
            
        """
    @property
    def added_stoichiometry(self) -> scipy.sparse.csc_matrix[numpy.int32]:
        """
              The sum of forward and backwards stoichiometry.
            

        :type: scipy.sparse.csc_matrix[numpy.int32]
        """
    @property
    def compound_labels(self) -> typing.List[str]:
        """
              Getter for the labels of all compounds in the network.
            

        :type: typing.List[str]
        """
    @property
    def masses(self) -> numpy.ndarray:
        """
              The molecular masses of the compounds in the network.
            

        :type: numpy.ndarray
        """
    @property
    def n_compounds(self) -> int:
        """
              The number of compounds in the network.
            

        :type: int
        """
    @property
    def n_reactions(self) -> int:
        """
              The number of reactions in the network.
            

        :type: int
        """
    @property
    def rate_constants(self) -> typing.Tuple[numpy.ndarray, numpy.ndarray]:
        """
              The rate constants ({forward, backward}) of all reactions and
              channels (matrix order: (reaction index, channel index)).
            

        :type: typing.Tuple[numpy.ndarray, numpy.ndarray]
        """
    @property
    def stoichiometry(self) -> typing.Tuple[scipy.sparse.csc_matrix[numpy.int32], scipy.sparse.csc_matrix[numpy.int32]]:
        """
              The stoichiometry of all reactions in the network ({lhs, rhs})
              Matrix ordering is (reaction index, compound index).
            

        :type: typing.Tuple[scipy.sparse.csc_matrix[numpy.int32], scipy.sparse.csc_matrix[numpy.int32]]
        """
    @property
    def total_stoichiometry(self) -> scipy.sparse.csc_matrix[numpy.int32]:
        """
              The difference of backwards and forwards stoichiometry.
            

        :type: scipy.sparse.csc_matrix[numpy.int32]
        """
    pass
class NetworkBuilder():
    def __init__(self) -> None: 
        """
              Initialize a network builder.
            
        """
    def add_compound(self, mass: float, label: str = '') -> None: 
        """
              Adds a single new compound to the network.
              (Expands fields if required.)
              :param mass: The molecular mass of the compound to add.
              :param label: Optional: The label of the compound.
            
        """
    def add_reaction(self, forward_rates: typing.List[float], backward_rates: typing.List[float], left_hand_side: typing.List[typing.Tuple[int, int]], right_hand_side: typing.List[typing.Tuple[int, int]]) -> None: 
        """
              Adds a new reaction to the network, auto expands fields if required.
              :param forward_rates: Reaction rates for the forward reaction (one per channel).
              :param backward_rates: Reaction rates for the backward reaction (one per channel).
              :param left_hand_side: Stoichiometry of the LHS of the reaction.
                                     (Format: [(Compound1, Equivalents1), (Compound2, Equivalents2), ...] ).
              :param right_hand_side: Stoichiometry of the RHS of the reaction.
                                     (Format: [(Compound1, Equivalents1), (Compound2, Equivalents2), ...] ).
            
        """
    def add_reaction_channel(self, reaction: int, forward_rate: float, backward_rate: float) -> None: 
        """
              Adds a single reaction channel to an existing reaction.
              (Expands fields if required.)
              :param reaction: The number (index, 0 based) of the reaction to add to.
              :param forward_rate: The reaction rate for the forward reaction.
              :param backward_rate: The reaction rate fot the backward reaction.
            
        """
    def generate(self) -> Network: 
        """
              Generates the final network.
            
        """
    def reserve(self, n_compounds: int, n_reactions: int, n_channels_per_reaction: int) -> None: 
        """
              Reserves space in the underlying data objects, allowing for faster inserts.
              :param n_compounds: The maximum number of compounds.
              :param n_reactions: The maximum number of reactions.
              :param n_channels_per_reaction: The maximum number of reaction channels per reaction.
            
        """
    pass
class RandomNetworkFactory():
    @staticmethod
    def random() -> Network: 
        """
              A random generator for physical networks
              The basis of this algorithm was called ``AutoNetGen`` in:
               "Mechanism Deduction from Noisy Chemical Reaction Networks"
                - Jonny Proppe and Markus Reiher
               https://doi.org/10.1021/acs.jctc.8b00310

              Small modifications may have been made w.r.t. to its original
              implementation.

              :return Network A noisy test network.
            
        """
    pass
def get_integrator(integrator: str) -> Integrator:
    """
          Resolve the integrator name string to its enum.
          :param integrator:   The name of the integrator to be used by kinetx.
        
    """
def integrate(network: Network, y_start: typing.List[float], t_start: float, dt: float, integrator_name: Integrator, batch_interval: int = 1000, n_batches: int = 100000, convergence: float = 1e-10, integrateByTime: bool = False, maxTime: float = 100000.0) -> typing.Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]:
    """
          Propagate the time by n_batches x batch_interval x dt.
          :param network:         The reaction network.
          :param y_start:         The values to integrate (e.g. start concentrations).
          :param t_start:         The starting time.
          :param dt:              The time step.
          :param integrator_name: The integrator.
          :param batch_interval:  The number of time steps for each step batch (default: 1000).
          :param n_batches:       The number of batches (default: 100000).
          :param convergence:     The maximum change of concentration between two batches before considering
                                  the kinetic model to be converged (default: 1e-10).
          :param integrateByTime  If true, the numerical integration is done up to the specified maxTime (default: False).
          :param maxTime          The maximum time to integrate. This is only used if integrateByTime is true (default: 1e+5).
        
    """
