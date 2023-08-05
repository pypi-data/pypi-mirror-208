import json
import re
import sys
import traceback as tb
from collections import defaultdict
from pathlib import Path

import pandas as pd
import pronto as pt
from appdirs import user_config_dir
from polly_validator.config import CONFIG


LATEST_COMMIT_FOR_OBO_ONTOLOGY_FILES = CONFIG.get('last_commit_for_obo_ontology_files', 'master')
LATEST_COMMIT_FOR_COMPRESSED_ONTOLOGY_FILES = CONFIG.get('last_commit_for_compressed_ontology_files', 'master')


class SetEncoder(json.JSONEncoder):
    """
    Encoder class to convert set to list when writing to file from a JSON object.
    """

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def collect_valid_names():
    try:
        search_for_disease, search_for_organism = 'MESH', 'NCBITaxon'
        print('Retrieving ontological names...')

        tissues = pt.Ontology(f'https://raw.githubusercontent.com/bioinfo-el/ontologies/'
                              f'{LATEST_COMMIT_FOR_OBO_ONTOLOGY_FILES}/obo/tissue.obo')

        cell_types = pt.Ontology(f'https://raw.githubusercontent.com/bioinfo-el/ontologies/'
                                 f'{LATEST_COMMIT_FOR_OBO_ONTOLOGY_FILES}/obo/cell_type.obo')

        cell_line = pt.Ontology(f'https://raw.githubusercontent.com/bioinfo-el/ontologies/'
                                f'{LATEST_COMMIT_FOR_OBO_ONTOLOGY_FILES}/obo/cell_line.obo')

        drugs = pt.Ontology(f'https://raw.githubusercontent.com/bioinfo-el/ontologies/'
                            f'{LATEST_COMMIT_FOR_OBO_ONTOLOGY_FILES}/obo/drug.obo')

        diseases = pt.Ontology(f'https://raw.githubusercontent.com/bioinfo-el/ontologies/'
                               f'{LATEST_COMMIT_FOR_OBO_ONTOLOGY_FILES}/obo/disease.obo')

        organism_df = pd.read_csv(f'https://github.com/bioinfo-el/ontologies/blob/'
                                  f'{LATEST_COMMIT_FOR_COMPRESSED_ONTOLOGY_FILES}/compressed/organism.xz?raw=true',
                                  sep='|',
                                  compression='xz')

        all_names = {'tissue': set(),
                     'cell_type': set(),
                     'cell_line': dict(),
                     'disease': set(),
                     'drug': set(),
                     'organism': set()}
        for term in tissues.terms():
            """Specific check for tissue"""
            if 'tissue' in term.subsets:
                all_names['tissue'].add(term.name)

        for term in cell_types.terms():
            all_names['cell_type'].add(term.name)
        for term in diseases.terms():
            all_names['disease'].add(term.name)
        for term in drugs.terms():
            all_names['drug'].add(term.name)

        all_names['organism'] = set(organism_df['root'])

        """Creating mapping between Cell Lines and Diseases..."""
        cell_line_disease_dict = defaultdict(set)
        for term in cell_line.terms():
            search_res = [item.description for item in term.xrefs if re.search(search_for_disease, item.id)]
            if search_res:
                cell_line_disease_dict[search_res[0]].add(term.name)

        """Creating mapping between Cell Lines and Organisms..."""
        cell_line_organism_dict = defaultdict(set)
        for term in cell_line.terms():
            search_res = [item.description for item in term.xrefs if re.search(search_for_organism, item.id)]
            if search_res:
                cell_line_organism_dict[search_res[0]].add(term.name)

        valid_cell_line_names = []
        for term in cell_line.terms():
            valid_cell_line_names.append(term.name)
        all_names['cell_line'] = {'valid_cell_line_names': valid_cell_line_names,
                                  'organism': cell_line_organism_dict,
                                  'disease': cell_line_disease_dict}

        folder_path = Path(Path(user_config_dir()) / 'polly-validator')
        with open(folder_path / 'valid_names.json', 'w+') as openfile:
            json.dump(all_names, openfile, cls=SetEncoder, indent=4)
    except Exception as e:
        print(tb.format_exc())
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
