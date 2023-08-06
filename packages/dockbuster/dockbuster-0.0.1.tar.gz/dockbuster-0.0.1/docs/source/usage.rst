

Usage
====================================


Command line
------------------------------------

.. code-block:: bash

    # check re-docked ligand (new ligand into protein).
    bust redock ligand_pred.sdf mol_true.sdf mol_cond.pdb

    # check docked ligand (where crystal protein-ligand structure is known).
    bust dock ligand_pred.sdf protein.pdb

    # check generated molecule (only check ligand).
    bust mol molecule_pred.sdf

    # check multiple of the three above using a .csv input:
    bust table file_table.csv


Python library
------------------------------------

.. code-block:: python

    from dockbuster import DockBuster

    # check re-docked ligand where protein-ligand crystal structure is available
    DockBuster().bust_redock(ligand_pred, ligand_crystal, protein_crystal)

    # check docked ligand
    DockBuster().bust_dock(ligand_pred, protein_crystal)

    # check molecule
    DockBuster().bust_dock(ligand_pred)



.. todo::
    Add CLI options to set all parameters manually other than providing configuration file.

.. todo::
    Add option to run each module separately.
