from pyskema import Node, AtomType, validate


def test_record():

    data = {
        "title": "DFE for Diamond",
        "savename": "Diamond",
        "name": "Diamond",
        "main_dir": ".",
        "compet_dir": "compet",
        "host_dir": "host/supercell",
        "defects_dir": "defects",
        "dfe": {
            "me": 0.9174,
            "mh": 1.2899,
            "xmin": 0.0,
            "xmax": 6.03,
            "ymin": 0.0,
            "ymax": 12.0,
        },
        "conc": {
            "xmin": 800.0,
            "xmax": 1500.0,
            "ymin": 1.0,
            "ymax": 1e25,
            "dt": 30.0,
            "troom": 300.0,
        },
        "plot": {"show": False, "save_figure_fmt": "png"},
        "corrections": {
            "params": "params.csv",
            "bs": {"dEC": 0.92, "dEV": -0.99},
            "mp": {"eps": 5.66, "geom": "fcc", "mk": 1.9065},
        },
    }

    schema = Node.of_record(
        {
            "title": Node.of_atom(AtomType.STR, description="The title of the plot"),
            "savename": Node.of_atom(AtomType.STR, description="The name of the saved file"),
            "name": Node.of_atom(AtomType.STR, description="The name of the study"),
            "main_dir": Node.of_atom(
                AtomType.STR,
                description="Root dir of the study, all path are relative to this one",
            ),
            "compet_dir": Node.of_atom(
                AtomType.STR,
                description="Path to the competition phases relative to <main_dir>",
            ),
            "host_dir": Node.of_atom(
                AtomType.STR,
                description="Path to OUTCAR and DOSCAR files of the host supercell relative to <main_dir>",
            ),
            "defects_dir": Node.of_atom(
                AtomType.STR, description="Where to find the defects relative to <main_dir>"
            ),
            "q_subdir": Node.of_atom(AtomType.STR, optional=True, default="."),
            "load_store_cells": Node.of_atom(
                AtomType.BOOL, optional=True, default=False
            ),
            "load_store_mstudies": Node.of_atom(
                AtomType.BOOL, optional=True, default=False
            ),
            "export_study": Node.of_atom(AtomType.BOOL, optional=True, default=True),
            "dfe": Node.of_record(
                {
                    "me": Node.of_atom(
                        AtomType.FLOAT,
                        description="Effective mass of the electrons in the conductance band",
                    ),
                    "mh": Node.of_atom(
                        AtomType.FLOAT,
                        description="Effective mass of the holes in the valence band",
                    ),
                    "xmin": Node.of_atom(AtomType.FLOAT, description="Minimum of mu_Ef [eV]"),
                    "xmax": Node.of_atom(AtomType.FLOAT, description="Maximum of mu_Ef [eV]"),
                    "ymin": Node.of_atom(AtomType.FLOAT, description="Maximum of DFE [eV]"),
                    "ymax": Node.of_atom(AtomType.FLOAT, description="Maximum of DFE [eV]"),
                }
            ),
            "conc": Node.of_record(
                {
                    "xmin": Node.of_atom(
                        AtomType.FLOAT, description="Minimum of T_growth [K]"
                    ),
                    "xmax": Node.of_atom(
                        AtomType.FLOAT, description="Maximum of T_growth [K]"
                    ),
                    "ymin": Node.of_atom(
                        AtomType.FLOAT,
                        description="Minimum concentrations [cm-3] !!! The + is required in YAML scientific notation",
                    ),
                    "ymax": Node.of_atom(
                        AtomType.FLOAT, description="Maximum concentrations [cm-3]"
                    ),
                    "dt": Node.of_atom(AtomType.FLOAT, description="Delte T_growth"),
                    "troom": Node.of_atom(AtomType.FLOAT),
                }
            ),
            "plot": Node.of_record(
                {
                    "show": Node.of_atom(AtomType.BOOL),
                    "save_figure_fmt": Node.of_atom(AtomType.STR),
                }
            ),
            "corrections": Node.of_record(
                {
                    "params": Node.of_atom(
                        AtomType.STR,
                        description="Name of the .csv containing the different correction parameters",
                    ),
                    "bs": Node.of_record(
                        {
                            "apply": Node.of_atom(
                                AtomType.BOOL, optional=True, default=True
                            ),
                            "dEC": Node.of_atom(
                                AtomType.FLOAT,
                                description="Shift between CBM at the main functional and CBM at the precise functional",
                            ),
                            "dEV": Node.of_atom(
                                AtomType.FLOAT,
                                description="Shift between VBM at the main functional and VBM at the precise functional",
                            ),
                            # "gap": Node.of_atom(AtomType.OPTION, options=[float])
                        },
                        description="Band edge shift",
                    ),
                    "mb": Node.of_record(
                        {
                            "apply": Node.of_atom(
                                AtomType.BOOL, optional=True, default=True
                            )
                        },
                        description="Moss-Burstein corrections",
                        optional=True,
                    ),
                    "mp": Node.of_record(
                        {
                            "apply": Node.of_atom(
                                AtomType.BOOL, optional=True, default=True
                            ),
                            "eps": Node.of_atom(
                                AtomType.FLOAT,
                                description="Isotropic static dielectric tensor",
                            ),
                            "geom": Node.of_atom(
                                AtomType.OPTION,
                                options=["fcc", "bcc", "sc", "hcp", "other"],
                            ),
                            "mk": Node.of_atom(
                                AtomType.FLOAT,
                                description="In the case q=1 & e_r=1, equals to TEWEN for H in box",
                            ),
                        },
                        description="Makov-Payne corrections",
                    ),
                },
                description="Semicolon based CSV. Path relative to <main_dir>",
            ),
        }
    )

    assert validate(data, schema)
