from __future__ import print_function

import os
import sys

import numpy as np

from landlab.layers.eventlayers import (EventLayers,
                                        _deposit_or_erode,
                                        _get_surface_index,
                                        resize_array,
                                        _allocate_layers_for)


class MaterialLayersMixIn(object):

    """MixIn that adds a layers attribute to a ModelGrid."""

    @property
    def layers(self):
        """Layers for each cell."""
        try:
            self._layers
        except AttributeError:
            self._layers = MaterialLayers(self.number_of_cells)
        finally:
            return self._layers


class MaterialLayers(EventLayers):

    """Track layers where each layer has some material in it.

    Parameters
    ----------
    number_of_stacks : int
        Number of layer stacks to track.

    Examples
    --------
    >>> from landlab.layers.materiallayers import MaterialLayers

    Create an empty layer stack with 5 stacks.

    >>> layers = MaterialLayers(5)
    >>> layers.number_of_stacks
    5
    >>> layers.number_of_layers
    0

    Add a layer with a uniform thickness.

    >>> layers.add(1.5)
    >>> layers.number_of_layers
    1
    >>> layers.dz
    array([[ 1.5,  1.5,  1.5,  1.5,  1.5]])

    Add a second layer with uneven thickness.

    >>> layers.add([1., 2., .5, 5., 0.])
    >>> layers.dz
    array([[ 1.5,  1.5,  1.5,  1.5,  1.5],
           [ 1. ,  2. ,  0.5,  5. ,  0. ]])

    Adding a layer with negative thickness will remove
    existing layers for the top of the stack. Unlike
    EventLayers, it will not add a layer of zeros that
    represent an event with no deposition.

    >>> layers.add(-1)
    >>> layers.dz
    array([[ 1.5,  1.5,  1. ,  1.5,  0.5],
           [ 0. ,  1. ,  0. ,  4. ,  0. ]])

    Get the index value of the layer within each stack
    at the topographic surface.

    >>> layers.surface_index
    array([0, 1, 0, 1, 0])
    """

    def __init__(self, number_of_stacks, allocated=0):
        super(MaterialLayers, self).__init__(number_of_stacks, allocated=allocated)

    def add(self, dz, **kwds):
        """Add a layer to the  MaterialLayers stacks.

        Parameters
        ----------
        dz : float or array_like
            Thickness to add to each stack.

        Examples
        --------
        >>> from landlab.layers.materiallayers import MaterialLayers

        Create an empty layer stack with 3 stacks.

        >>> layers = MaterialLayers(3)
        >>> layers.number_of_layers
        0

        To add a layer of uniform thickness to every stack.

        >>> layers.add(1.5)
        >>> layers.number_of_layers
        1
        >>> layers.dz
        array([[ 1.5,  1.5,  1.5]])

        Add a second layer with uneven thickness.

        >>> layers.add([1., 2., .5])
        >>> layers.dz
        array([[ 1.5,  1.5,  1.5],
               [ 1. ,  2. ,  0.5]])

        Adding a layer with negative thickness will remove
        existing layers for the top of the stack.

        >>> layers.add(-1)
        >>> layers.dz
        array([[ 1.5,  1.5,  1. ],
               [ 0. ,  1. ,  0. ]])

        Use keywords to track properties of each layer. For instance,
        here we create a new stack and add a layer with a particular
        *age*. You can access the layer properties as if the object
        were a dictionary.

        >>> layers = MaterialLayers(3)
        >>> layers.add(1., age=3.)
        >>> layers.dz
        array([[ 1.,  1.,  1.]])
        >>> layers['age']
        array([[ 3.,  3.,  3.]])
        >>> layers.add(2., age=6.)
        >>> layers['age']
        array([[ 3.,  3.,  3.],
               [ 6.,  6.,  6.]])

        Attributes for each layer will exist even if the the layer is
        associated with erosion.

        >>> layers.add([-2, -1, 1], age=8.)
        >>> layers.dz
        array([[ 1.,  1.,  1.],
               [ 0.,  1.,  2.],
               [ 0.,  0.,  1.]])
        >>> layers['age']
        array([[ 3.,  3.,  3.],
               [ 6.,  6.,  6.],
               [ 8.,  8.,  8.]])

        To get the values at the surface of the layer stack:

        >>> layers.surface_values('age')
        array([ 3.,  6.,  8.])
        """
        if self.number_of_layers == 0:
            self._setup_layers(**kwds)

        # add an empty layer only if erosion is going to occur.
        if np.any(np.asarray(dz)>0.0):
            self._add_empty_layer()
            _deposit_or_erode(self._attrs['_dz'], self.number_of_layers, dz)
        else:
            _deposit_or_erode(self._attrs['_dz'], self.number_of_layers+1, dz)

        for name in kwds:
            try:
                self[name][-1] = kwds[name]
            except KeyError:
                print('{0} is not being tracked. Ignoring'.format(name),
                      file=sys.stderr)
