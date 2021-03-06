#! /usr/bin/env python

import numpy as np
import unyt


def get_velocity_dispersion_matrix(mass_fraction, velocity, ref_velocity):
    """
    Compute the velocity dispersion matrix for the particles with the given
    fractional mass (particle mass divided by total mass) and velocity, using
    the given reference velocity as the centre of mass velocity.

    The result is a 6 element vector containing the unique components XX, YY,
    ZZ, XY, XZ and YZ of the velocity dispersion matrix.
    """

    result = unyt.unyt_array(np.zeros(6), dtype=np.float32, units=velocity.units**2)

    vrel = velocity - ref_velocity[None, :]
    result[0] += (mass_fraction * vrel[:, 0] * vrel[:, 0]).sum()
    result[1] += (mass_fraction * vrel[:, 1] * vrel[:, 1]).sum()
    result[2] += (mass_fraction * vrel[:, 2] * vrel[:, 2]).sum()
    result[3] += (mass_fraction * vrel[:, 0] * vrel[:, 1]).sum()
    result[4] += (mass_fraction * vrel[:, 0] * vrel[:, 2]).sum()
    result[5] += (mass_fraction * vrel[:, 1] * vrel[:, 2]).sum()

    return result


def get_angular_momentum(mass, position, velocity, ref_position, ref_velocity):
    """
    Compute the total angular momentum vector for the particles with the given
    masses, positions and velocities, and using the given reference position
    and velocity as the centre of mass (velocity).
    """

    prel = position - ref_position[None, :]
    vrel = velocity - ref_velocity[None, :]
    return (mass[:, None] * unyt.array.ucross(prel, vrel)).sum(axis=0)


def get_angular_momentum_and_kappa_corot(
    mass, position, velocity, ref_position, ref_velocity
):
    """
    Get the total angular momentum vector (as in get_angular_momentum()) and
    kappa_corot (Correa et al., 2017) for the particles with the given masses,
    positions and velocities, and using the given reference position and
    velocity as centre of mass (velocity).

    If both kappa_corot and the angular momentum vector are desired, it is more
    efficient to use this function that calling get_angular_momentum() (and
    get_kappa_corot(), if that would ever exist).
    """

    kappa_corot = unyt.unyt_array(
        0.0, dtype=np.float32, units="dimensionless", registry=mass.units.registry
    )

    prel = position - ref_position[None, :]
    vrel = velocity - ref_velocity[None, :]
    Lpart = mass[:, None] * unyt.array.ucross(prel, vrel)
    Ltot = Lpart.sum(axis=0)
    Lnrm = unyt.array.unorm(Ltot)

    if Lnrm > 0.0 * Lnrm.units:
        K = 0.5 * (mass[:, None] * vrel**2).sum()
        if K > 0.0 * K.units:
            Ldir = Ltot / Lnrm
            Li = (Lpart * Ldir[None, :]).sum(axis=1)
            r2 = prel[:, 0] ** 2 + prel[:, 1] ** 2 + prel[:, 2] ** 2
            rdotL = (prel * Ldir[None, :]).sum(axis=1)
            Ri2 = r2 - rdotL**2
            Krot = 0.5 * (Li**2 / (mass * Ri2))
            Kcorot = Krot[Li > 0.0 * Li.units].sum()
            kappa_corot += Kcorot / K

    return Ltot, kappa_corot
