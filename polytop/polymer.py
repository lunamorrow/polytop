from __future__ import annotations

import json
import random
import re
from typing import Dict, List, Optional, Tuple, Union
from polytop.bonds import Bond
from polytop.junction import Junction, Junctions
from .topology import Topology
import datetime

class Polymer:

    def __init__(self, monomer):
        """ 
        A polymer is a topology with a set of junctions that represent the polymerization sites of the monomer.
        Args:
            monomer (Monomer): the monomer to create the polymer from
        """
        new_monomer = monomer.copy()
        self.topology = new_monomer.topology
        self.junctions = new_monomer.junctions

    def has_junction(self, name):
        """Returns True if the polymer has a junction with the given name """
        return any(junction.name == name for junction in self.junctions)
    
    def DFS(self, atom, visited, exclude=None):
        """ 
        Depth first search of the polymer to find all atoms connected to the atom including the atom itself 
        Args:
            atom (Atom): the atom to start the search from
            visited (set): a set of atoms that have already been visited
            exclude (Atom): an atom to exclude from the search (ie: the other side of the junction)
        """
        visited.add(atom)
        for neighbor in atom.bond_neighbours():
            if neighbor is not exclude and neighbor not in visited:
                self.DFS(neighbor, visited, exclude)

    def extend(self, monomer, from_junction_name, to_junction_name, keep_charge = False):
        """
        Extend the polymer by adding a monomer to the polymerization junctions of the polymer
        Args:
            monomer (Monomer): the monomer to add to the polymer
            from_junction_name (str): the name of the junction in the polymer to extend from
            to_junction_name (str): the name of the junction in the monomer to extend to
            keep_charge (bool): if True, the charge of the polymer is kept the same by forcing the final topology to be 
                the same net charge as the sum charge of the initial topology and the monomer 
        """
        if keep_charge:
            monomer_charge = monomer.topology.charge
            polymer_charge = self.topology.charge
        
        # take a copy of the topology of the monomer 
        new_monomer = monomer.copy()
        
        # renumber all atoms above the max atom id of the polymer
        new_monomer.topology.renumber_atoms(max(atom.atom_id for atom in self.topology.atoms)+1)
        
        atom_index_dict = self.topology.max_atom_index()
        
        # renumber all atom indexes for each atom type above the max atom index for that atom type in the polymer
        for atom_type in atom_index_dict:
            new_monomer.topology.renumber_atom_indexes({atom_type: atom_index_dict[atom_type]+1})

        # choose the first polymerization junction of the monomer named to_junction_name to extend this monomer from
        to_junction = next((junction for junction in new_monomer.junctions if junction.name == to_junction_name), None)
        if to_junction is None:
            raise ValueError(f"No junction named {to_junction_name} found in the monomer")
        else:
            new_monomer.junctions.remove(to_junction)

        # do a depth first search of the monomer to find all atoms connected to the to_junction including the first atom in the junction
        discard_from_monomer=set()
        self.DFS(to_junction.location.atom_a, discard_from_monomer, exclude=to_junction.location.atom_b)

        # choose a random polymerization junction of the polymer with from_junction_name to extend this monomer into
        from_junction = random.choice([junction for junction in self.junctions if junction.name == from_junction_name])
        if from_junction is None:
            raise ValueError(f"No junction named {from_junction_name} found in the polymer")
        else:
            self.junctions.remove(from_junction)
        
        # do a depth first search of the polymer to find all atoms connected to the from_junction including the second atom in the junction
        discard_from_polymer=set()
        self.DFS(from_junction.location.atom_b, discard_from_polymer, exclude=from_junction.location.atom_a)
        
        # Add the monomer's topology to the polymer
        self.topology.add(new_monomer.topology)
        for junction in new_monomer.junctions:
            atom_a_id = junction.location.atom_a.atom_id
            atom_b_id = junction.location.atom_b.atom_id
            self.junctions.add(Junction(junction.name, self.topology.get_bond(atom_a_id, atom_b_id)))
        
        # bond the two outer atoms at the junctions
        self.topology.bonds.append(Bond(from_junction.location.atom_a, to_junction.location.atom_b, 1, 1, 1))

        # TODO: copy the average of the 2 lost bond angles over the junction
        
        # remove the redundant atoms and bonds
        for atom in discard_from_monomer:
            self.topology.remove_atom(atom)
            
        for atom in discard_from_polymer:
            self.topology.remove_atom(atom)
            
        if keep_charge:
            new_charge = monomer_charge + polymer_charge 
            self.topology.charge = new_charge

        
    def save_to_file(self, filename: str) -> None:
        """Save the polymer to a json file"""
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def load_from_file(cls, filename: str) -> None:
        """ Load a polymer from a json file"""
        with open(filename, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(
        self,
    ) -> Dict[
        str,
        Union[
            List[Dict[str, Union[float, int]]],
            int,
            Optional[Dict[str, Union[float, int]]],
        ],
    ]:
        return {
            "topology": self.topology.to_dict(),
            "junctions": self.junctions.to_dict()
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[
            str,
            Union[
                List[Dict[str, Union[float, int]]],
                int,
                Optional[Dict[str, Union[float, int]]],
            ],
        ],
    ) -> Polymer:
        new_topology = Topology.from_dict(data["topology"])
        new_junctions = Junctions.from_dict(data["junctions"], new_topology.atoms)
        return cls(
            topology=new_topology,
            junctions=new_junctions,
        )
        
    def __repr__(self) -> str:
        return f"Polymer(({len(self.topology.atoms)} atoms), junctions:{self.junctions.count()})"