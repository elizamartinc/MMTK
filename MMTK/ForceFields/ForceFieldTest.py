# This module implements test functions.
#
# Written by Konrad Hinsen
#

"""
Force field consistency tests
"""

__docformat__ = 'epytext'

from MMTK import Utility
from Scientific.Geometry import Vector, ex, ey, ez
from Scientific import N
import itertools

#
# Check consistency of energies and gradients.
#
def gradientTest(universe, atoms = None, delta = 0.0001):
    """
    Test gradients by comparing to numerical derivatives of the energy.
    @param universe: the universe on which the test is performed
    @type universe: L{MMTK.Universe.Universe}
    @param atoms: the atoms of the universe for which the gradient
                  is tested (default: all atoms)
    @type atoms: C{list}
    @param delta: the step size used in calculating the numerical derivatives
    @type delta: C{float}
    """
    e0, grad = universe.energyAndGradients()
    print 'Energy: ', e0
    if atoms is None:
        atoms = universe.atomList()
    for a in atoms:
        for b in a.beads():
            print a, " bead ", b.bead_number
            print grad[b]
            num_grad = []
            for v in [ex, ey, ez]:
                x = b.position()
                b.setPosition(x+delta*v)
                eplus = universe.energy()
                b.setPosition(x-delta*v)
                eminus = universe.energy()
                b.setPosition(x)
                num_grad.append(0.5*(eplus-eminus)/delta)
            print Vector(num_grad)

#
# Check consistency of gradients and force constants.
#
def forceConstantTest(universe, atoms = None, delta = 0.0001):
    """
    Test force constants by comparing to the numerical derivatives
    of the gradients.
    @param universe: the universe on which the test is performed
    @type universe: L{MMTK.Universe.Universe}
    @param atoms: the atoms of the universe for which the gradient
                  is tested (default: all atoms)
    @type atoms: C{list}
    @param delta: the step size used in calculating the numerical derivatives
    @type delta: C{float}
    """
    e0, grad0, fc = universe.energyGradientsAndForceConstants()
    if atoms is None:
        atoms = universe.atomList()
    for a1, a2 in itertools.chain(itertools.izip(atoms, atoms),
                                  Utility.pairs(atoms)):
        for b1, b2 in zip(a1.beads(), a2.beads()):
            print a1, a2, " bead ", b1.bead_number
            print fc[b1, b2]
            num_fc = []
            for v in [ex, ey, ez]:
                x = b1.position()
                b1.setPosition(x+delta*v)
                e_plus, grad_plus = universe.energyAndGradients()
                b1.setPosition(x-delta*v)
                e_minus, grad_minus = universe.energyAndGradients()
                b1.setPosition(x)
                num_fc.append(0.5*(grad_plus[b2]-grad_minus[b2])/delta)
            print N.array(map(lambda a: a.array, num_fc))

#
# Check consistency of gradients and virial
#
def virialTest(universe):
    """
    Test the virial by comparing to an explicit computation from
    positions and gradients.
    @param universe: the universe on which the test is performed
    @type universe: L{MMTK.Universe.Universe}
    """
    ev = universe.energyEvaluator()
    e, grad = ev(gradients = True)
    virial = ev.lastVirial()
    conf = universe.configuration()
    print virial, -(conf*grad).sumOverParticles()

if __name__ == '__main__':

    from MMTK import *
    from MMTK.ForceFields import Amber94ForceField
    delta = 0.001
    world = InfiniteUniverse(Amber94ForceField())
    m = Molecule('water')
    m.O.translateBy(Vector(0.,0.,0.01))
    m.H1.translateBy(Vector(0.01,0.,0.))
    atoms = None
    world.addObject(m)
    gradientTest(world, atoms, delta)
    forceConstantTest(world, atoms, delta)
    virialTest(world)
    
