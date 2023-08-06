#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

import os
import json
from typing import OrderedDict, Union, List
import pathlib
import gemmi
import numpy as np
import copy


class GemmiStructureExt(object):
    """
    Helper class to extend gemmi Structure class
    """

    def __init__(self, parent_structure: gemmi.Structure):
        self.parent_structure = parent_structure
        for attr in dir(parent_structure):
            try:
                self.__dict__[attr] = copy.deepcopy(self.__getattribute__(attr))
            except TypeError:
                pass

    def __getattribute__(self, name: str):
        try:
            # self.parent_structure call results in recursion error here
            # use superclass method instead
            return getattr(
                super(GemmiStructureExt, self).__getattribute__("parent_structure"),
                name,
            )
        except AttributeError:
            return super(GemmiStructureExt, self).__getattribute__(name)


class GemmiModelUtils(object):
    """
    Operations on gemmi Structure object
    """

    def __init__(self, input_model: Union[pathlib.Path, str, gemmi.Structure]):

        self.structure = check_structure_inputs(
            input_model
        )  # gemmi.read_structure(modelfile)
        self.resolution = self.structure.resolution
        if os.path.isfile(input_model):
            self.file_ext = os.path.splitext(input_model)[1].lower()
            self.modelid: Union[str, None] = os.path.splitext(
                os.path.basename(input_model)
            )[0]
        else:
            self.file_ext = None
            self.modelid = None

    def write_structure_as_mmcif(self, mmcif_name):
        """Write a Gemmi structure out to an mmCIF file."""
        write_structure_as_mmcif(self.structure, mmcif_name)

    def write_structure_as_pdb(self, pdb_name):
        """Write a Gemmi structure out to an PDB file."""
        write_structure_as_pdb(self.structure, pdb_name)

    def shift_coordinates(
        self,
        trans_vector: Union[list, np.ndarray, tuple],
        out_model_path: Union[pathlib.Path, str] = None,
        remove_charges: bool = False,
        inplace: bool = False,
    ):
        """
        Shift atomic coordinates based on a translation vector (x,y,z)
        """
        if inplace:
            structure = self.structure
        else:
            structure = self.structure.clone()
        for model in structure:
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        atom.pos = gemmi.Position(
                            atom.pos.x + trans_vector[0],
                            atom.pos.y + trans_vector[1],
                            atom.pos.z + trans_vector[2],
                        )
                        if remove_charges:  # remove negative charges?
                            if atom.charge != 0:
                                atom.charge = 0
        if out_model_path:
            if os.path.splitext(out_model_path)[1].lower() in [".cif", ".mmcif"]:
                write_structure_as_mmcif(structure, out_model_path)
            else:
                write_structure_as_pdb(structure, out_model_path)
        return structure

    def remove_atomic_charges(
        self,
        out_model_path: Union[pathlib.Path, str] = None,
        inplace: bool = False,
    ):
        """
        Remove atomic charges from the model

        Arguments
        ---------
            :out_model_path:
                output atomic model with charges removed
        """
        if inplace:
            structure = self.structure
        else:
            structure = self.structure.clone()
        for model in structure:
            for chain in model:
                # skip non polymers
                # if not polymer: continue
                for residue in chain:
                    for atom in residue:
                        if atom.charge != 0:
                            atom.charge = 0
        if out_model_path:
            if os.path.splitext(out_model_path)[1].lower() in [".cif", ".mmcif"]:
                write_structure_as_mmcif(self.structure, out_model_path)
            else:
                write_structure_as_pdb(structure, out_model_path)
        return structure

    def set_residue_attribute(self, attr_name: str, dict_attribute: dict):
        """
        TODO: this is just a placeholder
        Add a new residue attribute to the current gemmi structure instance
        """
        for model in self.structure:
            if model.name not in dict_attribute:
                continue
            for chain in model:
                if chain.name in dict_attribute[model.name]:
                    for residue in chain:
                        pass
                        # try:
                        #     setattr(
                        #         residue,
                        #         attr_name,
                        #         dict_attribute[model.name][chain.name][
                        #             str(residue.seqid.num)
                        #         ],
                        #     )
                        # except KeyError:
                        #     pass

    def set_residue_types(self):
        """
        Set a dictionary to map residue IDs and names
        """
        self.dict_resnames = OrderedDict()
        for model in self.structure:
            self.dict_resnames[model.name] = {}
            for chain in model:
                if chain.name not in self.dict_resnames[model.name]:
                    self.dict_resnames[model.name][chain.name] = {}
                for residue in chain:
                    self.dict_resnames[model.name][chain.name][
                        str(residue.seqid.num)
                    ] = residue.name

    def get_avgbfact_deviation(
        self,
        calc_dev: bool = True,
        dist_dev: float = 3.0,
        save_obj: bool = False,
        out_json: str = None,
        skip_nonpoly: bool = True,
    ):
        """
        Get average atomic B-factors, and stdev of atomic B-factors
        around each residue in the model

        Returns
        -------
            Dict with B factors and  deviations
            {modelName:{chainName:
            {residueNum_residueName: [avg b-factor, b-factor dev]}}}
        """
        dict_bfact: dict = OrderedDict()
        for model in self.structure:
            if calc_dev:
                subcells = gemmi.NeighborSearch(
                    model, self.structure.cell, dist_dev + 5.0
                )
                subcells.populate(include_h=False)
                dict_bfact[model.name] = {}
            for chain in model:
                polymer = chain.get_polymer()
                # skip non polymers
                if not polymer and skip_nonpoly:
                    continue
                if chain.name not in dict_bfact[model.name]:
                    dict_bfact[model.name][chain.name] = {}
                for residue in chain:
                    if residue.entity_type == gemmi.EntityType.Water:
                        continue
                    residue_id = str(residue.seqid.num)  # + "_" + residue.name
                    list_bfact = []
                    list_neigh_bfact = []
                    for atom in residue:
                        list_bfact.append(atom.b_iso)
                    avg_bfact = round(sum(list_bfact) / float(len(list_bfact)), 5)
                    if calc_dev:
                        representative_atom = self.get_representative_atom(
                            residue=residue
                        )
                        representative_atom_b = representative_atom.b_iso
                        marks = subcells.find_neighbors(
                            representative_atom, min_dist=0.1, max_dist=dist_dev
                        )
                        for mark in marks:
                            cra = mark.to_cra(model)
                            neigh_atom = cra.atom
                            list_neigh_bfact.append(neigh_atom.b_iso)
                        list_neigh_bfact.append(representative_atom_b)
                    if len(list_neigh_bfact) > 0:
                        dict_bfact[model.name][chain.name][residue_id] = [
                            avg_bfact,
                            round(np.std(np.array(list_neigh_bfact)), 5),
                        ]
                    else:
                        dict_bfact[model.name][chain.name][residue_id] = [
                            avg_bfact,
                            0.0,
                        ]

        # if save_obj:  # save gemmi structure object instead of returned dict
        #     self.set_residue_attribute(
        #         attr_name="bfact_avg_dev", dict_attribute=dict_bfact
        #     )
        #     if out_json is not None:
        #         encode_simple_obj_to_json_file(
        #             GemmiStructureExt(self.structure), out_json
        #         )
        #     else:
        #         encode_simple_obj_to_json_file(
        #             GemmiStructureExt(self.structure),
        #             self.modelid + "_gemmistructure.json",
        #         )
        #     print(dir(GemmiStructureExt(self.structure)))
        if out_json is not None:
            with open(out_json, "w") as oj:
                json.dump(dict_bfact, oj)
        return dict_bfact

    def get_coordinates(
        self,
        atom_selection: Union[str, list] = "all",
        skip_non_poly: bool = False,
        return_list: bool = False,
        out_json: str = None,
    ):
        """
        Get model atomic coordinates based on user selection

        Arguments
        ---------
            in_model_path: str
                input atomic model
            gemmi_structure_instance: gemmi.Structure, optional
                gemmi structure instance if in_model_path is not input
            atom_selection: Union[str, list], optional
                atom selection for coordinate retrieval
                Input a list of atom names or any of the following keywords:
                    "all": all atoms in the model
                    "backbone": only model backbone atoms, all atoms for non polymers
                    "one_per_residue": representative atoms, e.g. CA for amino acids
                    "centre": geometric centre of the residue
            skip_non_poly: bool, optional
                skip non polymers?
            return_list: bool, optional
                Returns a list of residue IDs and a list of coordinates
            out_json: str, optional
                json file to save the output coordinate dictionary
                (if return_list is False)
        Returns
        -------
            A dictionary of coordinates or list of residue IDs + a list of coordinates
            {modelName:{chainName: {residueNum_residueName: [list atomic coordinates]}}}
        """
        dict_coord: dict = OrderedDict()
        list_ids = []
        list_coords = []
        polymertype = None
        # loop through structure
        for model in self.structure:
            if model.name not in dict_coord:
                dict_coord[model.name] = {}
            for chain in model:
                polymer = chain.get_polymer()
                # skip non polymers
                if not polymer and skip_non_poly:
                    continue
                if polymer.check_polymer_type() == gemmi.PolymerType.PeptideL:
                    polymertype = "protein"
                if chain.name not in dict_coord[model.name]:
                    dict_coord[model.name][chain.name] = {}
                for residue in chain:
                    list_residue_coords = []
                    if isinstance(atom_selection, list):  # specified atoms only
                        list_residue_coords = self.get_selected_atom_coordinates(
                            residue, atom_selection
                        )
                    elif atom_selection == "all":
                        for atom in residue:
                            list_residue_coords.append(
                                (atom.pos.x, atom.pos.y, atom.pos.z)
                            )
                    elif atom_selection == "backbone":  # all backbone
                        list_residue_coords = self.get_backbone_coordinates(
                            residue, polymertype=polymertype
                        )
                    elif atom_selection == "one_per_residue":  # ca or equivalent
                        residue_centre = self.get_representative_coordinate(
                            residue, polymertype=polymertype
                        )
                        list_residue_coords.append(residue_centre)
                    elif atom_selection == "centre":  # central atom
                        residue_centre = self.get_residue_centre_by_coordinates(residue)
                        list_residue_coords.append(residue_centre)
                    if return_list:
                        list_ids.extend(
                            len(list_residue_coords)
                            * [
                                "_".join(
                                    [
                                        model.name,
                                        str(chain.name),
                                        str(residue.seqid.num),
                                        residue.name,
                                    ]
                                )
                            ]
                        )
                        list_coords.extend(list_residue_coords)
                    else:
                        residue_coords = list_residue_coords
                        residue_id = str(residue.seqid.num)  # + "_" + residue.name
                        dict_coord[model.name][str(chain.name)][
                            residue_id
                        ] = residue_coords
        if not return_list:
            if out_json:
                with open(out_json, "w") as j:
                    json.dump(dict_coord, j)
            return dict_coord
        else:
            return list_ids, list_coords

    def get_selected_atom_coordinates(
        self, residue: gemmi.Residue, atom_selection: list
    ):
        """
        Get coordinates of selected atoms (list of atom names)
        from a given gemmi Residue instance
        """
        list_residue_coords = []
        for atom in residue:
            if atom.name in atom_selection:
                list_residue_coords.append((atom.pos.x, atom.pos.y, atom.pos.z))
        return list_residue_coords

    def get_representative_coordinate(
        self, residue: gemmi.Residue, polymertype: str = None
    ):
        """
        Get coordinates of one representative atom per residue
        from a given gemmi Residue instance
        """
        residue_centre: Union[tuple, None] = None
        if residue.name in ["A", "T", "C", "G", "U"]:  # nuc acid
            for atom in residue:
                if atom.name in ["P", "C3'", "C1'"]:
                    residue_centre = (atom.pos.x, atom.pos.y, atom.pos.z)
        elif not polymertype or polymertype == "protein":  # protein
            for atom in residue:
                # if atom.name == "CB" or (residue.name == "GLY" and atom.name == "CA"):
                if atom.name == "CA":
                    residue_centre = (atom.pos.x, atom.pos.y, atom.pos.z)
                    break
        if not residue_centre:  # non nuc acid / prot
            residue_centre = self.get_residue_centre_by_coordinates(residue)
        return residue_centre

    def get_representative_atom(self, residue: gemmi.Residue, polymertype: str = None):
        """
        Get one representative atom per residue
        from a given gemmi Residue instance
        """
        repr_atom = None
        if residue.name in ["A", "T", "C", "G", "U"]:  # nuc acid
            for atom in residue:
                if atom.name in ["P", "C3'", "C1'"]:
                    repr_atom = atom
        elif not polymertype or polymertype == "protein":  # protein
            for atom in residue:
                # if atom.name == "CB" or (residue.name == "GLY" and atom.name == "CA"):
                if atom.name == "CA":
                    repr_atom = atom
                    break
        if not repr_atom:  # non nuc acid / prot
            repr_atom = self.get_central_atom_by_sequence(residue)
        return repr_atom

    def get_backbone_coordinates(self, residue: gemmi.Residue, polymertype: str = None):
        """
        Get coordinates of the backbone atoms
        from a given gemmi Residue instance
        """
        list_residue_coords = []
        if residue.name in ["A", "T", "C", "G", "U"]:  # nuc acid
            for atom in residue:
                # TODO : fix the backbone atom list
                if atom.name in ["P", "C3'", "C1'"]:
                    list_residue_coords.append((atom.pos.x, atom.pos.y, atom.pos.z))
        elif residue.het_flag == "H":  # all het atoms
            for atom in residue:
                list_residue_coords.append((atom.pos.x, atom.pos.y, atom.pos.z))
        elif not polymertype or polymertype == "protein":  # protein
            for atom in residue:
                if atom.name in ["N", "CA", "C", "O"]:
                    list_residue_coords.append((atom.pos.x, atom.pos.y, atom.pos.z))
        if len(list_residue_coords) == 0:  # all
            for atom in residue:
                list_residue_coords.append((atom.pos.x, atom.pos.y, atom.pos.z))
        return list_residue_coords

    def get_residue_centre_by_coordinates(self, gemmi_residue_instance: gemmi.Residue):
        """
        Get coordinates of one central atom (sequence centre) per residue
        from a given gemmi Residue instance
        """
        list_coords = []
        for atom in gemmi_residue_instance:
            list_coords.append([atom.pos.x, atom.pos.y, atom.pos.z])
        return list(np.mean(np.array(list_coords), axis=0))

    def get_residue_centre_by_sequence(self, gemmi_residue_instance: gemmi.Residue):
        """
        Get coordinates of one central atom (sequence centre) per residue
        from a given gemmi Residue instance
        """
        try:
            center_index = int(len(gemmi_residue_instance) / 2)
            atom = gemmi_residue_instance[center_index]
            residue_centre = (atom.pos.x, atom.pos.y, atom.pos.z)
        except IndexError:
            for atom in gemmi_residue_instance:
                residue_centre = (atom.pos.x, atom.pos.y, atom.pos.z)
                break  # first atom
        return residue_centre

    def get_central_atom_by_sequence(self, gemmi_residue_instance: gemmi.Residue):
        """
        Get one central atom (sequence centre) per residue
        from a given gemmi Residue instance
        """
        try:
            center_index = int(len(gemmi_residue_instance) / 2)
            atom = gemmi_residue_instance[center_index]
            central_atom = atom
        except IndexError:
            for atom in gemmi_residue_instance:
                central_atom = atom
                break  # first atom
        return central_atom

    def get_sequence_from_atom_records(self):
        """
        Get polymer sequence from atom records
        """
        dict_seq = {}
        self.structure.add_entity_types(overwrite=True)
        self.structure.assign_subchains()  # assigns subchains in each chain
        self.structure.ensure_entities()  # each subchain linked to one Entity object
        for entity in self.structure.entities:
            if entity.entity_type == gemmi.EntityType.Polymer:
                seq_res_list = entity.full_sequence
                seq_res_list = [gemmi.Entity.first_mon(item) for item in seq_res_list]
                sequence = "".join(
                    [
                        gemmi.find_tabulated_residue(resname).one_letter_code
                        for resname in seq_res_list
                    ]
                )
                dict_seq[entity.name] = sequence
        return dict_seq

    def get_sequence_resnum_from_atom_records(self):
        """
        Get polymer sequence and list of residue number from model atom records

        Returns
        -------
            Dict of sequences of each chain
            Dict of residue numbers of each chain {'A': ['G 74', 'L 75', 'A 76', ....]}
        """
        dict_seq = {}
        dict_residues = {}
        for model in self.structure:
            for chain in model:
                polymer = chain.get_polymer()
                # skip non polymers
                if not polymer:
                    continue
                list_seq = []
                list_resnum = []
                for residue in chain:
                    rescode = gemmi.find_tabulated_residue(residue.name).one_letter_code
                    if rescode != " ":
                        list_seq.append(rescode)
                        list_resnum.append(rescode + " " + str(residue.seqid.num))
                sequence = "".join(list_seq)
                dict_seq[chain.name] = sequence
                dict_residues[chain.name] = list_resnum
        return dict_seq, dict_residues


def convert_pdb_to_mmcif(pdb_path, mmcif_path=None):
    """Convert coordinate file from PDB format to mmCIF/PDBx format"""
    structure = gemmi.read_structure(pdb_path)
    if mmcif_path is None:
        mmcif_path = os.path.splitext(pdb_path)[0] + ".cif"
    write_structure_as_mmcif(structure, mmcif_path)
    return mmcif_path


def write_structure_as_mmcif(structure, mmcif_name):
    """Write a Gemmi structure out to an mmCIF file."""
    # Refmac crashes for long _entry.id
    st_new = structure.clone()
    st_new.name = st_new.name[:78]  # in case of pdb this will be _entry.id
    if "_entry.id" in st_new.info:
        st_new.info["_entry.id"] = st_new.info["_entry.id"][:78]
    st_new.make_mmcif_document().write_file(mmcif_name)


def write_structure_as_pdb(structure, pdb_name):
    """Write a Gemmi structure out to a PDB file."""
    st_new = structure.clone()
    st_new.shorten_chain_names()
    st_new.write_pdb(pdb_name, use_linkr=True)


def convert_mmcif_to_pdb(mmcif_path, pdb_path=None):
    """Convert coordinate file from mmCIF/PDBx format to PDB format"""
    structure = gemmi.read_structure(mmcif_path)
    if pdb_path is None:
        pdb_path = os.path.splitext(pdb_path)[0] + ".pdb"
    write_structure_as_pdb(structure, pdb_path)
    return pdb_path


def check_structure_inputs(input_structure: Union[str, pathlib.Path, gemmi.Structure]):
    """
    Check if the given input is a model file path or a gemmi Structure instance

    Returns
    -------
    gemmi Structure instance
    """
    if isinstance(input_structure, gemmi.Structure):
        structure = input_structure
    elif input_structure is not None and os.path.isfile(input_structure):
        structure = gemmi.read_structure(input_structure)
    else:
        raise IOError("Input either a valid model file or a gemmi structure instance")
    return structure


def get_residue_attribute(list_ids: List[str], list_attr: List[Union[float, int]]):
    """
    Get residue attributes as average of atom attributes

    Arguments
    ---------
        :list_ids:
            list of residue or atom IDs of the format:
            residue_id = "_".join(
                    [
                        model name,
                        chain name,
                        str(residue number),
                        residue name,
                    ]
                )
            atom_id = "_".join([residue_id, atom name])
        :list_attr:
            list of atom attributes (same length as list_ids)

    Returns:
        Lists of residue IDs and average attributes
    """
    list_res_ids = []
    list_res_attr = []
    dict_current_res: dict = {}
    # model.name_chain.name_residue.seqid.num_residue.name
    atom_number = 0
    previous_res_id = None
    for atom_id in list_ids:
        atom_id_split = atom_id.split("_")
        if len(atom_id_split) > 4:  # has atom identifier
            res_id = "_".join(atom_id_split[:4])
        else:
            res_id = atom_id
        try:
            dict_current_res[res_id].append(list_attr[atom_number])
        except KeyError:
            if previous_res_id:
                list_res_ids.append(previous_res_id)
                if len(dict_current_res[previous_res_id]) == 1:
                    list_res_attr.append(dict_current_res[previous_res_id][0])
                elif len(dict_current_res[previous_res_id]) > 1:
                    list_res_attr.append(
                        round(
                            np.sum(dict_current_res[previous_res_id])
                            / len(dict_current_res[previous_res_id]),
                            5,
                        )
                    )
            dict_current_res = {}  # reinitialize
            dict_current_res[res_id] = [list_attr[atom_number]]
        previous_res_id = res_id
        atom_number += 1
    if previous_res_id:
        list_res_ids.append(previous_res_id)
        if len(dict_current_res[previous_res_id]) == 1:
            list_res_attr.append(dict_current_res[previous_res_id][0])
        elif len(dict_current_res[previous_res_id]) > 1:
            list_res_attr.append(
                round(
                    np.sum(dict_current_res[previous_res_id])
                    / len(dict_current_res[previous_res_id]),
                    5,
                )
            )
    return list_res_ids, list_res_attr


def convert_dict_attributes_to_list(dict_attr):
    list_ids = []
    list_attr = []
    for model in dict_attr:
        for chain in dict_attr[model]:
            for residue in dict_attr[model][chain]:
                if isinstance(dict_attr[model][chain][residue], dict):
                    for atom in dict_attr[model][chain][residue]:
                        atom_id = "_".join([model, str(chain), str(residue), str(atom)])
                        list_ids.extend(
                            len(dict_attr[model][chain][residue][atom]) * [atom_id]
                        )
                        list_attr.extend(dict_attr[model][chain][residue][atom])

                else:
                    res_id = "_".join([model, str(chain), str(residue)])
                    list_ids.extend(len(dict_attr[model][chain][residue]) * [res_id])
                    list_attr.extend(dict_attr[model][chain][residue])
    return list_ids, list_attr


def set_bfactor_attributes(
    in_model_path: Union[str, pathlib.Path],
    dict_attr: dict,
    skip_non_poly: bool = True,
    attr_name: str = "",
    out_dir: str = None,
):
    """
    Replace atomic B-factors with the given attributes
    Use this for visualisation purpose (colr by b-factors) only

    Arguments
    ---------
        in_model_path:
            input atomic model path
        dict_attr:
            Dictionary of residue or atom attributes
            Dict keys are residue or atom IDs of the format:
            residue_id = "_".join(
                    [
                        model name,
                        chain name,
                        str(residue number),
                        residue name,
                    ]
                )
            atom_id = "_".join([residue_id, atom name])
        skip_non_poly: bool, optional
            skip non polymers?
    Returns
    -------
        A dictionary of coordinates or list of residue IDs + a list of coordinates

    """
    structure = gemmi.read_structure(in_model_path)
    # setup entities in case that nothing were set when reading the file
    structure.setup_entities()
    structure.assign_label_seq_id()
    count_atom = 0
    for model in structure:
        for chain in model:
            polymer = chain.get_polymer()
            # skip non polymers
            if not polymer and skip_non_poly:
                continue
            for residue in chain:
                residue_id = "_".join(
                    [
                        model.name,
                        str(chain.name),
                        str(residue.seqid.num),
                        residue.name,
                    ]
                )
                for atom in residue:
                    atom_id = "_".join([residue_id, atom.name])
                    if atom_id in dict_attr:
                        atom.b_iso = dict_attr[atom_id]
                    elif residue_id in dict_attr:
                        atom.b_iso = dict_attr[residue_id]
                    else:
                        atom.b_iso = 0.0
                    count_atom += 1
    if out_dir:
        structure.write_pdb(
            os.path.join(
                out_dir,
                os.path.splitext(os.path.basename(in_model_path))[0]
                + "_"
                + attr_name
                + "_attr.pdb",
            )
        )
    else:
        structure.write_pdb(
            os.path.splitext(os.path.basename(in_model_path))[0]
            + "_"
            + attr_name
            + "_attr.pdb"
        )
