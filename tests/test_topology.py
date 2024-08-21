import json
from pathlib import Path
from polytop import *
from polytop.polytop.atoms import Atom
from polytop.polytop.bonds import Bond
from polytop.topology import Topology
from polytop.visualize import Visualize
import pytest

def test_invalid_file(data_dir: Path):
    with pytest.raises(FileNotFoundError):
        Topology.from_ITP(data_dir/"non_existent.itp")

def test_invalid_section_warning(data_dir: Path):
    with pytest.warns(UserWarning, match="Unknown section"):
        Topology.from_ITP(data_dir/"invalid_section.itp")

def test_glucose_missing_index(data_dir: Path):
    with pytest.raises(ValueError, match="No index"):
        Topology.from_ITP(data_dir/"glucose_faulty.itp")

def test_bad_name_warning(data_dir: Path):
    with pytest.warns(UserWarning, match="Atom type"):
        Topology.from_ITP(data_dir/"glucose_badname.itp")

def test_bad_type_warning(data_dir: Path):
    with pytest.warns(UserWarning, match="Have extracted"):
        Topology.from_ITP(data_dir/"glucose_badtype.itp")

def test_preprocess_numeric_oxygens(data_dir: Path):
    with pytest.warns(UserWarning, match="Have extracted"):
        glucose = Topology.from_ITP(data_dir/"glucose_numeric_oxygens.itp", preprocess=Topology.numerically_order_oxygens)
        assert glucose.atoms[1].atom_name == "O6"

def test_ph1_gromos_54a7_forcefieldbonds_angles_dihedrals(data_dir: Path):
    ph1 = Topology.from_ITP(data_dir/"PH1.itp")
    assert len(ph1.bonds) == 59
    assert len(ph1.angles) == 80
    assert len(ph1.dihedrals) == 60

def test_glucose_bonds_angles_dihedrals(data_dir: Path):
    glucose = Topology.from_ITP(data_dir/"glucose.itp")
    assert len(glucose.bonds) == 24
    assert len(glucose.angles) == 42
    assert len(glucose.dihedrals) == 12

def test_arginine_bonds_angles_dihedrals(data_dir: Path):
    arginine = Topology.from_ITP(data_dir/"arginine.itp")
    assert len(arginine.bonds) == 25
    assert len(arginine.angles) == 41
    assert len(arginine.dihedrals) == 12

def test_glutamine_bonds_angles_dihedrals(data_dir: Path):
    glutamine = Topology.from_ITP(data_dir/"glutamine.itp")
    assert len(glutamine.bonds) == 19
    assert len(glutamine.angles) == 31
    assert len(glutamine.dihedrals) == 10

def test_glucose_molecule_type(data_dir: Path):
    glucose = Topology.from_ITP(data_dir/"glucose.itp")
    assert glucose.molecule_type.name == "NWU6"
    assert glucose.molecule_type.nrexcl == 3

def test_ph1_molecule_type(data_dir: Path):
    ph1 = Topology.from_ITP(data_dir/"PH1.itp")
    assert ph1.molecule_type.name == "G36Q"
    assert ph1.molecule_type.nrexcl == 3

def test_arginine_molecule_type(data_dir: Path):
    arginine = Topology.from_ITP(data_dir/"arginine.itp")
    assert arginine.molecule_type.name == "AE97"
    assert arginine.molecule_type.nrexcl == 3

def test_glutamine_molecule_type(data_dir: Path):
    glutamine = Topology.from_ITP(data_dir/"glutamine.itp")
    assert glutamine.molecule_type.name == "9NF5"
    assert glutamine.molecule_type.nrexcl == 3

def test_arginine(data_dir: Path, output_dir: Path):
    arginine = Topology.from_ITP(data_dir/"arginine.itp")
    arginine.to_ITP(output_dir/"arginine_new.itp")
    loaded_arginine = Topology.from_ITP(output_dir/"arginine_new.itp")
    assert (
        len(loaded_arginine.atoms) == 26
    )  # verify that the number of atoms is correct
    assert loaded_arginine.get_atom(26)  # verify that the atom with id 26 exists
    assert loaded_arginine.get_bond(
        20, 22
    )  # verify that the bond between atoms 20 and 22 exists
    assert loaded_arginine.get_angle(
        9, 12, 15
    )  # verify that the angle between atoms 9, 12 and 15 exists
    assert loaded_arginine.get_dihedral(
        4, 2, 5, 8
    )  # verify that the improper dihedral between atoms 4, 2, 5 and 8 exists
    assert loaded_arginine.get_dihedral(
        2, 4, 8, 9
    )  # verify that the proper dihedral between atoms 2, 4, 8 and 9 exists

def test_glutamine(data_dir: Path, output_dir: Path):
    glutamine = Topology.from_ITP(data_dir/"glutamine.itp")
    glutamine.to_ITP(output_dir/"glutamine_new.itp")
    loaded_glutamine = Topology.from_ITP(output_dir/"glutamine_new.itp")
    assert len(loaded_glutamine.atoms) == 20
    assert loaded_glutamine.get_atom(20)
    assert loaded_glutamine.get_bond(5, 10)
    assert loaded_glutamine.get_angle(5, 10, 13)

def test_topology_max_atom_index(data_dir: Path, output_dir: Path):
    arginine = Topology.from_ITP(data_dir/"arginine.itp")
    arg_max_atom_index = arginine.max_atom_index()
    assert arg_max_atom_index["H"] == 26
    assert arg_max_atom_index["C"] == 12
    assert arg_max_atom_index["N"] == 6
    assert arg_max_atom_index["O"] == 2

def test_topology_reorder_atom_indexes(data_dir: Path, output_dir: Path):
    arginine = Topology.from_ITP(data_dir/"arginine.itp")
    for element, number in { "H": 26, "C": 12, "N": 6, "O": 2 }.items(): 
        arginine.reorder_atom_indexes(element, number)
    arg_max_atom_index = arginine.max_atom_index()
    assert arg_max_atom_index["H"] == 39
    assert arg_max_atom_index["C"] == 17
    assert arg_max_atom_index["N"] == 9
    assert arg_max_atom_index["O"] == 3
    
def test_topology_auto_rename_atoms(data_dir: Path, output_dir: Path):
    arginine = Topology.from_ITP(data_dir/"arginine.itp")
    arginine.auto_rename_atoms()
    arg_max_atom_index = arginine.max_atom_index()
    assert arg_max_atom_index["H"] == 14
    assert arg_max_atom_index["C"] == 6
    assert arg_max_atom_index["N"] == 4
    assert arg_max_atom_index["O"] == 2

def test_reverse_topology(data_dir: Path, output_dir: Path):
    glu = Topology.from_ITP(data_dir/"glutamine.itp")
    reverse_glu = glu.reverse()
    reverse_glu.to_ITP(output_dir/"reverse_glutamine.itp")
    
    def same_properties(atom_a,atom_b)-> bool: 
        if glu_atom.atom_type != rev_glu_atom.atom_type:
            return False
        if glu_atom.residue_name != rev_glu_atom.residue_name:
            return False
        if glu_atom.residue_id != rev_glu_atom.residue_id:
            return False
        # assert arg_atoms[i].charge_group_num == rev_arg_atom.charge_group_num # it is not dependent on order but grouping
        if glu_atom.partial_charge != rev_glu_atom.partial_charge:
            return False
        if glu_atom.mass != rev_glu_atom.mass:
            return False
        return True
        
    glu_atoms = glu.atoms
    reverse_glu_atoms = reverse_glu.atoms
    assert len(glu_atoms) == len(reverse_glu_atoms)
    for i in range(len(glu_atoms)):
        glu_atom = glu_atoms[i]
        rev_glu_atom = reverse_glu_atoms[-i-1]
        assert same_properties(glu_atom, rev_glu_atom)
        for atom in glu_atom.bond_neighbours():
            assert any(same_properties(atom, rev_atom) for rev_atom in rev_glu_atom.bond_neighbours())
        for atom in glu_atom.angle_neighbours():
            assert any(same_properties(atom, rev_atom) for rev_atom in rev_glu_atom.angle_neighbours())
        for atom in glu_atom.dihedral_neighbours():
            assert any(same_properties(atom, rev_atom) for rev_atom in rev_glu_atom.dihedral_neighbours())
        
def test_vizualization(data_dir: Path, output_dir: Path):
    import py3Dmol 
    from rdkit import Chem
    from rdkit.Chem import AllChem

    arg = Topology.from_ITP(data_dir/"arginine.itp")
    viewer = py3Dmol.view(width=400, height=400)
    Visualize(arg).draw3D(viewer)

def test_infer_bond_order(data_dir: Path, output_dir: Path):
    arg = Topology.from_ITP(data_dir/"arginine.itp")
    arg = Visualize(arg).topology # visualize constructor infers bond order in it's internal instance of the topology 
    for bond in arg.bonds:
        assert bond.order is not None
        if bond is arg.get_bond(23,24):
            assert bond.order == 2
        elif bond is arg.get_bond(4,8):
            assert bond.order == 2
        else:
            assert bond.order == 1
            
def test_remove(data_dir: Path, output_dir: Path):
    arg = Topology.from_ITP(data_dir/"arginine.itp")
    assert len(arg.atoms) == 26
    assert len(arg.bonds) == 25
    assert len(arg.angles) == 41
    assert len(arg.dihedrals) == 12
    atom = arg.get_atom(1)
    arg.remove_atom(atom)
    assert len(arg.atoms) == 25
    assert len(arg.bonds) == 24
    assert len(arg.angles) == 39
    assert len(arg.dihedrals) == 12
    atom = arg.get_atom(2)
    arg.remove_atom(atom)
    assert len(arg.atoms) == 24
    assert len(arg.bonds) == 22
    assert len(arg.angles) == 36
    assert len(arg.dihedrals) == 9
    atom = arg.get_atom(26)
    arg.remove_atom(atom)
    assert len(arg.atoms) == 23
    assert len(arg.bonds) == 21
    assert len(arg.angles) == 35
    assert len(arg.dihedrals) == 8


def test_serialization(data_dir: Path, output_dir: Path):
    arg = Topology.from_ITP(data_dir/"arginine.itp")
    
    # Write to the file
    (output_dir / "arg.json").write_text(json.dumps(arg.to_dict()))

    # Read from the file
    new_dihedral = Topology.from_dict(json.loads((output_dir/"arg.json").read_text()))
    
    assert len(arg.atoms) == len(new_dihedral.atoms)
    assert len(arg.bonds) == len(new_dihedral.bonds)
    assert len(arg.angles) == len(new_dihedral.angles)
    assert len(arg.dihedrals) == len(new_dihedral.dihedrals)
    assert len(arg.preamble) == len(new_dihedral.preamble)
    assert len(arg.pairs) == len(new_dihedral.pairs)
    assert len(arg.exclusions) == len(new_dihedral.exclusions)
    assert arg.molecule_type == new_dihedral.molecule_type

def is_close(actual,expected) -> bool:
    return abs(actual-expected) < 1e-6
    
def test_net_charge(data_dir: Path, output_dir: Path):
    arg = Topology.from_ITP(data_dir/"arginine.itp")
    assert is_close(arg.netcharge, 0)
    # change the net charge 
    arg.netcharge = 1
    assert is_close(arg.netcharge, 1)
    # change the net charge to a fraction of a negative value
    arg.netcharge = -0.5
    assert is_close(arg.netcharge, -0.5)
    arg.to_ITP(output_dir/"arginine_negative_charge.itp")
    
    new_arg = Topology.from_ITP(data_dir/"arginine.itp")
    new_arg.proportional_charge_change(-0.5)
    assert is_close(new_arg.netcharge, -0.5)
    assert not is_close(new_arg.atoms[0].partial_charge, arg.atoms[0].partial_charge)
    arg.to_ITP(output_dir/"arginine_negative_charge_proportional.itp")
    
def test_deduplicate_topology(data_dir:Path):
    arg = Topology.from_ITP(data_dir/"arginine.itp")
    bonds = arg.bonds
    assert len(bonds) == 25
    # replicate the first bond
    bond1 = bonds[0]
    atom1 = bond1.atom_a
    atom2 = bond1.atom_b
    bond2 = Bond(atom1, atom2, bond_type="1", bond_length=0.147, force_constant=265265.0)
    assert len(arg.bonds) == 26
    arg.deduplicate()
    assert len(arg.bonds) == 25

def test_clone_topology_changing(data_dir : Path):
    arg = Topology.from_ITP(data_dir/"arginine.itp")
    old_atom = arg.get_atom(1)
    # add a new hydrogen atom - use rubbish values for the remaining fields
    new_atom = Atom(atom_id=27, atom_type="H", residue_id=1, residue_name="ARG", atom_name="CL0", charge_group_num=26, partial_charge=0.412, mass=1.0080)

    # collect original topology around old_atom
    old_bonds = old_atom.bonds
    old_otheratoms = []
    old_angles = []
    old_dihedrals = []
    for bond in old_bonds:
        old_otheratoms.append(bond.other_atom(old_atom))
        for angle in bond.angles:
            if angle.contains_atom(old_atom):
                old_angles.append(angle)
                for dihedral in angle.dihedrals:
                    if dihedral.contains_atom(old_atom):
                        old_dihedrals.append(dihedral)
    arg.change_atom(old_atom, new_atom)

    # assert that the old atom is no longer in the topology, and new_atom is
    assert not arg.contains_atom(old_atom)
    assert arg.contains_atom(new_atom)

    # assert that the bonds, angles and dihedrals have been updated
    for bond in new_atom.bonds:
        assert bond.contains_atom(new_atom)
        assert not bond.contains_atom(old_atom)
        assert bond.other_atom(new_atom) in old_otheratoms
        for angle in bond.angles:
            assert angle.contains_atom(new_atom)
            assert not angle.contains_atom(old_atom)
            for dihedral in angle.dihedrals:
                assert dihedral.contains_atom(new_atom)
                assert not dihedral.contains_atom(old_atom)

def test_add_topologies(data_dir: Path):
    # test of operator overloading used in debugging polymer extension
    arg = Topology.from_ITP(data_dir/"arginine.itp")
    glu = Topology.from_ITP(data_dir/"glutamine.itp")
    arg_glu = arg+glu
    assert len(arg_glu.atoms) == len(arg.atoms) + len(glu.atoms)
    arg += glu
    assert len(arg.atoms) == len(arg_glu.atoms)

def test_topology_repr(data_dir: Path):
    # test of repr used in debugging polymer extend
    arg = Topology.from_ITP(data_dir/"arginine.itp")
    assert arg.__repr__() == "(26) [H26,N5,H25,C12,N6,H23,H24,N4,C10,H18,H19,C8,H15,H16,C7,H13,H14,C9,H17,N3,H20,H21,C11,O2,O1,H22] netcharge=-1.0581813203458523e-16"

def test_copy_toplology(data_dir: Path):
    # test of copy used in debugging polymer extend
    arg = Topology.from_ITP(data_dir/"arginine.itp")
    arg_copy = arg.copy()
    assert len(arg.atoms) == len(arg_copy.atoms)
    assert arg.netcharge == arg_copy.netcharge
    for atom in arg.atoms:
        atom_copy = arg_copy.get_atom(atom.atom_id)
        assert atom.atom_id == atom_copy.atom_id, "atom id mismatch"
        assert atom.atom_type == atom_copy.atom_type, "atom type mismatch"
        assert atom.residue_id == atom_copy.residue_id, "residue id mismatch"
        assert atom.residue_name == atom_copy.residue_name, "residue name mismatch"
        assert atom.charge_group_num == atom_copy.charge_group_num, "charge group number mismatch"
        assert atom.partial_charge == atom_copy.partial_charge, "partial charge mismatch"
        assert atom.mass == atom_copy.mass, "mass mismatch"
        assert len(atom.bonds) == len(atom_copy.bonds), "number of bonds mismatch"
        for bond in atom.bonds:
            bond_copy = arg_copy.get_bond(bond.atom_a.atom_id, bond.atom_b.atom_id)
            # that there exists a bond between the same atoms in the copy
            assert bond_copy is not None, "bond not found in copy"
            # that the bond in the copy is a different object than the bond in the original
            assert bond is not bond_copy, "bond is the same object in copy"
            for angle in bond.angles:
                angle_copy = arg_copy.get_angle(angle.atom_a.atom_id, angle.atom_b.atom_id, angle.atom_c.atom_id)
                # that there exists an angle between the same atoms in the copy
                assert angle_copy is not None, "angle not found in copy"
                # that the angle in the copy is a different object than the angle in the original
                assert angle is not angle_copy, "angle is the same object in copy"
                for dihedral in angle.dihedrals:
                    dihedral_copy = arg_copy.get_dihedral(dihedral.atom_a.atom_id, dihedral.atom_b.atom_id, dihedral.atom_c.atom_id, dihedral.atom_d.atom_id)
                    # that there exists a dihedral between the same atoms in the copy
                    assert dihedral_copy is not None, "dihedral not found in copy"
                    # that the dihedral in the copy is a different object than the dihedral in the original
                    assert dihedral is not dihedral_copy, "dihedral is the same object in copy"
        for pair in atom.pairs:
            pair_copy = arg_copy.get_pair(pair.atom_a.atom_id, pair.atom_b.atom_id)
            # that there exists a pair between the same atoms in the copy
            assert pair_copy is not None, "pair not found in copy"
            # that the pair in the copy is a different object than the pair in the original
            assert pair is not pair_copy, "pair is the same object in copy"
        for exclusion in atom.exclusions:
            exclusion_copy = arg_copy.get_exclusion(exclusion.atom_a.atom_id, exclusion.atom_b.atom_id)
            # that there exists an exclusion between the same atoms in the copy
            assert exclusion_copy is not None, "exclusion not found in copy"
            # that the exclusion in the copy is a different object than the exclusion in the original
            assert exclusion is not exclusion_copy, "exclusion is the same object in copy"
    # check arg.preamble is a different object than arg_copy.preamble
    assert arg.preamble is not arg_copy.preamble, "preamble is the same object in copy"
    for i in range(len(arg.preamble)):
        # assert the string in the preamble has teh same content but are independent objects 
        assert arg.preamble[i] == arg_copy.preamble[i], "preamble content is different in copy"
    # check arg.molecule_type is not the same object as arg_copy.molecule_type
    assert not arg.molecule_type is arg_copy.molecule_type, "molecule type is same object"
    # check arg.molecule_type attributes are the same as arg_copy.molecule_types
    assert arg.molecule_type.name == arg_copy.molecule_type.name, "molecule type name mismatch"
    assert arg.molecule_type.nrexcl == arg_copy.molecule_type.nrexcl, "molecule type nrexcl mismatch"

def test_topology_with_exclusions(data_dir: Path):
    eth = Topology.from_ITP(data_dir/"ethylene_terephthalate.itp")
    assert len(eth.atoms) == 25, "number of atoms mismatch"
    assert len(eth.bonds) == 25, "number of bonds mismatch"
    assert len(eth.angles) == 39, "number of angles mismatch"
    assert len(eth.dihedrals) == 21, "number of dihedrals mismatch"
    assert len(eth.pairs) == 45 , "number of pairs mismatch"
    assert len(eth.exclusions) == 3 == eth.molecule_type.nrexcl, "number of exclusions mismatch or mismatch in molecule type nrexcl"
