import json
from polytop.monomer import Monomer
from polytop.topology import Topology


def test_monomer():
    arg = Topology.from_ITP("tests/samples/arginine.itp")
    bond_a = arg.get_bond('N3','H20')
    bond_b = arg.get_bond('C11','O1')
    monomer = Monomer(arg, bond_a, bond_b)
    assert len(monomer.LHS.atoms) == 2
    assert len(monomer.link.atoms) == 26-3+2
    assert len(monomer.RHS.atoms) == 3
    
def test_serializable():
    arg = Topology.from_ITP("tests/samples/arginine.itp")
    bond_a = arg.get_bond('N3','H20')
    bond_b = arg.get_bond('C11','O1')
    monomer = Monomer(arg, bond_a, bond_b)
    monomer.save("tests/samples/arg.json")
    
    new_monomer = Monomer.load("tests/samples/arg.json")
    assert len(monomer.topology.atoms) == len(new_monomer.topology.atoms)
    assert monomer.bond_a.atom_a.atom_id == new_monomer.bond_a.atom_a.atom_id
    assert monomer.bond_a.atom_b.atom_id == new_monomer.bond_a.atom_b.atom_id
    
    
    
