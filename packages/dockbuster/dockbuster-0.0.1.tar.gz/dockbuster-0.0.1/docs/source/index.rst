.. dockbuster documentation master file, created by
   sphinx-quickstart on Thu May 11 14:30:14 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root ``toctree`` directive.


DockBuster documentation
====================================

``dockbuster`` is a command line tool and Python library for checking the chemical consistency and physical sensibility of docked ligands.


.. note::

   This project is under active development.


Installation
====================================

Installing ``dockbuster`` will install the command line tool and the Python library.

.. code-block:: bash

   # install with pip from PyPI
   pip install dockbuster

   # install with conda from conda-forge
   conda install dockbuster -c conda-forge

   # install from source
   git clone https://github.com/maabuu/dockbuster.git
   cd dockbuster
   pip install flit
   flit install


Usage
====================================


DockBuster is a command line tool:

.. code-block:: bash

    # check re-docked ligand (new ligand into protein).
    bust redock ligand_pred.sdf mol_true.sdf mol_cond.pdb

    # check docked ligand (where crystal protein-ligand structure is known).
    bust dock ligand_pred.sdf protein.pdb

    # check generated molecule (only check ligand).
    bust mol molecule_pred.sdf

    # check multiple of the three above using a .csv input:
    bust table file_table.csv


And can also be used as a Python library:

.. code-block:: python

    from dockbuster import DockBuster

    # check re-docked ligand where protein-ligand crystal structure is available
    DockBuster().bust_redock(ligand_pred, ligand_crystal, protein_crystal)

    # check docked ligand
    DockBuster().bust_dock(ligand_pred, protein_crystal)

    # check molecule
    DockBuster().bust_dock(ligand_pred)


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quick_start.ipynb
   usage


Indices and tables
====================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
