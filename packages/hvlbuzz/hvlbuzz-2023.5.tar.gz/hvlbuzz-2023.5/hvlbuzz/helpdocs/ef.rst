Charge Simulation Method
========================

Conductor placement within a bundle:

The placement depends on the number of conductors and the bundle radius defined
when a new line is added. The line coordinates will be taken as a midpoint
for the conductor bundle.

.. image:: helpdocs/equations/conductor_x.png
.. image:: helpdocs/equations/conductor_y.png

Contour points on the conductor surfaces:

increasing the number of conductor surfaces increases the accuracy of the
electric field calculation but also calculation times. The number of contour
points can be determind in the Electric Field settings page.

.. image:: helpdocs/equations/contour_x.png
.. image:: helpdocs/equations/contour_y.png

Charge radius within the the conductor:

.. image:: helpdocs/equations/charge_radius.png

Charge placement within conductors:

Every line charge comes in pair with a surface contour point.

.. image:: helpdocs/equations/charge_x.png
.. image:: helpdocs/equations/charge_y.png

Mirror charge placement to simulate the ground with zero potential

The line charge in the conductors and their mirror charges also come in pairs.
The mirror charges are required to simulate the zero potential on ground.

.. image:: helpdocs/equations/mirror_x.png
.. image:: helpdocs/equations/mirror_y.png

Potential coefficients:

.. image:: helpdocs/equations/potential_coefficients.png

AC and DC voltage vectors:

.. image:: helpdocs/equations/voltage_ac.png
.. image:: helpdocs/equations/voltage_dc.png

AC and DC line charge vectors:

.. image:: helpdocs/equations/charge_vector_ac.png
.. image:: helpdocs/equations/charge_vector_dc.png

Electric field on ground:

.. image:: helpdocs/equations/electric_field_ground.png

Electric field on conductor surfaces (surface gradients):

.. image:: helpdocs/equations/electric_field_conductor.png
