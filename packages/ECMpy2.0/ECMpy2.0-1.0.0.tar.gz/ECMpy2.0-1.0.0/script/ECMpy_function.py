# -*- coding: utf-8 -*-
# This code is used to introduce enzyme concentration constraint in GEMs
# by COBRApy and to calculate the parameters that need to be entered
# during the construction of the enzyme-constrained model.
#from warnings import warn

import json
import math
import random
import re
import os
import time
import statistics
from typing import Any, Dict, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import cobra
import numpy as np
import pandas as pd
from cobra.core import Reaction
from cobra.io.dict import model_to_dict
from cobra.util.solver import set_objective
import pubchempy as pcp
import requests
from Bio.SeqUtils.ProtParam import ProteinAnalysis
# import plotly.graph_objects as go

def create_file(store_path):
    if os.path.exists(store_path):
        print("path exists")
        #shutil.rmtree(store_path)
        #os.makedirs(store_path)
    else:      
        os.makedirs(store_path)
        print(store_path) 
        
def json_load(path: str) -> Dict[Any, Any]:
    """Loads the given JSON file and returns it as dictionary.

    Arguments
    ----------
    * path: str ~ The path of the JSON file
    """
    with open(path) as f:
        dictionary = json.load(f)
    return dictionary

def standardize_folder(folder: str) -> str:
    """Returns for the given folder path is returned in a more standardized way.

    I.e., folder paths with potential \\ are replaced with /. In addition, if
    a path does not end with / will get an added /.

    Argument
    ----------
    * folder: str ~ The folder path that shall be standardized.
    """
    # Standardize for \ or / as path separator character.
    folder = folder.replace("\\", "/")

    # If the last character is not a path separator, it is
    # added so that all standardized folder path strings
    # contain it.
    if folder[-1] != "/":
        folder += "/"

    return folder

def convert_to_irreversible(model):
    """Split reversible reactions into two irreversible reactions

    These two reactions will proceed in opposite directions. This
    guarentees that all reactions in the model will only allow
    positive flux values, which is useful for some modeling problems.

    Arguments
    ----------
    * model: cobra.Model ~ A Model object which will be modified in place.

    """
    #warn("deprecated, not applicable for optlang solvers", DeprecationWarning)
    reactions_to_add = []
    coefficients = {}
    for reaction in model.reactions:
        # If a reaction is reverse only, the forward reaction (which
        # will be constrained to 0) will be left in the model.
        if reaction.lower_bound < 0 and reaction.upper_bound > 0:
            reverse_reaction = Reaction(reaction.id + "_reverse")
            reverse_reaction.lower_bound = max(0, -reaction.upper_bound)
            reverse_reaction.upper_bound = -reaction.lower_bound
            coefficients[
                reverse_reaction] = reaction.objective_coefficient * -1
            reaction.lower_bound = max(0, reaction.lower_bound)
            reaction.upper_bound = max(0, reaction.upper_bound)
            # Make the directions aware of each other
            reaction.notes["reflection"] = reverse_reaction.id
            reverse_reaction.notes["reflection"] = reaction.id
            reaction_dict = {k: v * -1
                             for k, v in reaction._metabolites.items()}
            reverse_reaction.add_metabolites(reaction_dict)
            reverse_reaction._model = reaction._model
            reverse_reaction._genes = reaction._genes
            for gene in reaction._genes:
                gene._reaction.add(reverse_reaction)
            reverse_reaction.subsystem = reaction.subsystem
            reverse_reaction.gene_reaction_rule = reaction.gene_reaction_rule
            reactions_to_add.append(reverse_reaction)
    model.add_reactions(reactions_to_add)
    set_objective(model, coefficients, additive=True)
    
def get_genes_and_gpr(model,gene_outfile,gpr_outfile):
    """Retrieving genes and gene_reaction_rule from GEM.

    Arguments
    ----------
    * model: cobra.Model ~ A genome scale metabolic network model for
        constructing the enzyme-constrained model.

    :return: all genes and gpr in model.
    """
    model_dict = model_to_dict(model, sort=False)
    genes = pd.DataFrame(model_dict['genes']).set_index(['id'])
    genes.to_csv(gene_outfile)
    all_gpr = pd.DataFrame(model_dict['reactions']).set_index(['id'])
    all_gpr.to_csv(gpr_outfile)
    return [genes, all_gpr]

def isoenzyme_split(model):
    """Split isoenzyme reaction to mutiple reaction

    Arguments
    ----------
    * model: cobra.Model.
    
    :return: new cobra.Model.
    """  
    for r in model.reactions:
        if re.search(" or ", r.gene_reaction_rule):
            rea = r.copy()
            gene = r.gene_reaction_rule.split(" or ")
            for index, value in enumerate(gene):
                if index == 0:
                    r.id = r.id + "_num1"
                    r.gene_reaction_rule = value
                else:
                    r_add = rea.copy()
                    r_add.id = rea.id + "_num" + str(index+1)
                    r_add.gene_reaction_rule = value
                    model.add_reaction(r_add)
    for r in model.reactions:
        r.gene_reaction_rule = r.gene_reaction_rule.strip("( )")
    return model
        
def get_reaction_mw(sbml_path,project_folder,project_name,json_output_file,enzyme_unit_number_file):
    """Adds proteomic constraints according to sMOMENT to the given stoichiometric model and stores it as SBML.

    Arguments
    ----------

    * model: cobra.Model ~ A cobra Model representation of the metabolic network. This model will
      be changed using cobrapy functions in order to add the proteomic constraints.
    * project_folder: str ~ The folder in which the spreadsheets and JSONs with the model's supplemental
      data can be found.
    * project_name: str ~ The sMOMENTed model creation's name, which will be added at the beginning
      of the created SBML's name.

    Output
    ----------
    An .
    """
    if re.search('\.xml',sbml_path):
        model = cobra.io.read_sbml_model(sbml_path)
    elif re.search('\.json',sbml_path):
        model = cobra.io.json.load_json_model(sbml_path)
    basepath: str = project_folder + project_name
    # READ REACTIONS<->KEGG ID XLSX
    protein_id_mass_mapping: Dict[str, float] = json_load(
        basepath + "_protein_id_mass_mapping.json")
    if enzyme_unit_number_file != 'none':
        enzyme_unit_number=json_load(enzyme_unit_number_file)     
    convert_to_irreversible(model)
    #split isoenzyme
    model = isoenzyme_split(model)

    #subunit_num	1 and 1 and 1 
    reaction_mw={}
    for r in model.reactions:
            if re.search('_num',r.id):
                r_id=r.id.split('_num')[0]
            else:
                r_id=r.id            
        #if r_id in reactions_kcat_mapping_database.keys():
            #print(r.id,r.gene_reaction_rule)
            mass_sum = .0
            if re.search(' and ',r.gene_reaction_rule):
                genelist=r.gene_reaction_rule.split(' and ')
                for eachgene in genelist:
                    #enzyme_unit_number=1
                    if eachgene in protein_id_mass_mapping.keys():
                        #mass_sum += protein_id_mass_mapping[eachgene]['mw'] * enzyme_unit_number
                        if enzyme_unit_number_file != 'none' :
                            if eachgene in enzyme_unit_number[r.id].keys():
                                mass_sum += protein_id_mass_mapping[eachgene]['mw'] * int(enzyme_unit_number[r.id][eachgene])
                        else:
                            mass_sum += protein_id_mass_mapping[eachgene]['mw']
                #print(mass_sum)
                reaction_mw[r.id]=mass_sum
            else:  # Single enzyme
                eachgene=r.gene_reaction_rule
                #enzyme_unit_number = 1
                if eachgene in protein_id_mass_mapping.keys():
                    #print(protein_id_mass_mapping[eachgene] * enzyme_unit_number)
                    #reaction_mw[r.id]=protein_id_mass_mapping[eachgene]['mw'] * enzyme_unit_number
                    if enzyme_unit_number_file != 'none':
                        if eachgene in enzyme_unit_number[r.id].keys():
                            reaction_mw[r.id]=protein_id_mass_mapping[eachgene]['mw'] * int(enzyme_unit_number[r.id][eachgene])
                    else:
                        reaction_mw[r.id]=protein_id_mass_mapping[eachgene]['mw']
    json_write(json_output_file, reaction_mw)        
        
# PUBLIC FUNCTIONS
def get_reaction_kcat_mw(model,project_folder, project_name,type_of_default_kcat_selection,enzyme_unit_number_file,json_output_file):
    """Adds proteomic constraints according to sMOMENT to the given stoichiometric model and stores it as SBML.

    Arguments
    ----------

    * model: cobra.Model ~ A cobra Model representation of the metabolic network. This model will
      be changed using cobrapy functions in order to add the proteomic constraints.
    * project_folder: str ~ The folder in which the spreadsheets and JSONs with the model's supplemental
      data can be found.
    * project_name: str ~ The sMOMENTed model creation's name, which will be added at the beginning
      of the created SBML's name.

    Output
    ----------
    An .
    """
    # Standardize project folder
    project_folder = standardize_folder(project_folder)

    # Set folder path for newly created SBML and name for the reaction ID addition (added at the end,
    # and used in order to have a programatically convinient way to separate additions such as 'reverse'
    # from the 'actual' reaction ID).
    basepath: str = project_folder + project_name
    id_addition: str = "_num"
    # READ REACTIONS<->KEGG ID XLSX
    protein_id_mass_mapping: Dict[str, float] = json_load(
        basepath + "_protein_id_mass_mapping.json")
    if enzyme_unit_number_file != 'none':
        enzyme_unit_number=json_load(enzyme_unit_number_file) 
    # Make model irreversible, separating all reversible reactions to which a gene rule is given
    # in order to save some reactions.
    convert_to_irreversible(model)
    #split isoenzyme
    model = isoenzyme_split(model)
    
    # Read reaction <-> kcat mapping :-)
    reactions_kcat_mapping_database = json_load(
        basepath + "_reactions_kcat_mapping_combined.json")

    # sMOMENT :D
    # Get all kcats which are not math.nan and calculate the median of them, which will be used as default kcat
    all_kcats = [x["forward"] for x in reactions_kcat_mapping_database.values()] + \
                [x["reverse"] for x in reactions_kcat_mapping_database.values()]
    all_kcats = [x for x in all_kcats if not math.isnan(x)]

    if type_of_default_kcat_selection == "median":
        default_kcat = statistics.median(all_kcats)
    elif type_of_default_kcat_selection == "mean":
        default_kcat = statistics.mean(all_kcats)
    elif type_of_default_kcat_selection == "max":
        default_kcat = np.max(all_kcats)
    elif type_of_default_kcat_selection == "random":
        default_kcat = random.choice(all_kcats)
    else:
        default_kcat = 'Null'

    print(f"Default kcat is: {default_kcat}")

    # Get all reaction IDs of the given model
    model_reaction_ids = [x.id for x in model.reactions]

    # Main loop :D, add enzyme constraints to reactions \o/
    reaction_kcat_mw={}
    for model_reaction_id in model_reaction_ids:
        # Get the reaction and split the ID at the ID addition
        reaction = model.reactions.get_by_id(model_reaction_id)
        splitted_id = reaction.id.split(id_addition)

        # If the reaction has no name, ignore it
        if splitted_id[0] == "":
            continue
        # Take the reaction ID from the first part of the split
        reaction_id = splitted_id[0]
        # Remove GPRSPLIT name addition from reactions with measured protein concentrations
        if "_GPRSPLIT_" in reaction_id:
            reaction_id = reaction_id.split("_GPRSPLIT_")[0]

        # Retrieve the reaction's forward and reverse kcats from the given reaction<->kcat database
        if re.search('_reverse',reaction_id):
            reaction_id=reaction_id.split('_reverse')[0]
        if reaction_id not in reactions_kcat_mapping_database.keys():
            continue
        forward_kcat = reactions_kcat_mapping_database[reaction_id]["forward"]
        reverse_kcat = reactions_kcat_mapping_database[reaction_id]["reverse"]

        # If the given reaction<->kcat database contains math.nan as the reaction's kcat,
        # set the default kcat as math.nan means that no kcat could be found.
        if math.isnan(forward_kcat):
            forward_kcat = default_kcat
        if math.isnan(reverse_kcat):
            reverse_kcat = default_kcat

        # Add the given forward or reverse kcat is the reaction was
        # splitted due to its reversibility.
        # If the reaction is not splitted, add the forward kcat (this
        # is the only possible direction for non-splitted=non-reversible
        # reactions)
        if model_reaction_id.endswith(id_addition + "forward"):
            reaction_kcat = forward_kcat
        elif model_reaction_id.endswith(id_addition + "reverse"):
            reaction_kcat = reverse_kcat
        else:
            reaction_kcat = forward_kcat

        reaction_kcat_mw[model_reaction_id]={}
        if reaction_kcat=='Null':
            continue
        reaction_kcat_mw[model_reaction_id]['kcat']=reaction_kcat
        
        #MW
        #subunit_num	1 and 1 and 1 
        reaction_mw={}
        for r in model.reactions:
                if re.search('_num',r.id):
                    r_id=r.id.split('_num')[0]
                else:
                    r_id=r.id            
            #if r_id in reactions_kcat_mapping_database.keys():
                #print(r.id,r.gene_reaction_rule)
                mass_sum = .0
                if re.search(' and ',r.gene_reaction_rule):
                    genelist=r.gene_reaction_rule.split(' and ')
                    for eachgene in genelist:
                        #enzyme_unit_number=1
                        if eachgene in protein_id_mass_mapping.keys():
                            #mass_sum += protein_id_mass_mapping[eachgene]['mw'] * enzyme_unit_number
                            if enzyme_unit_number_file != 'none':
                                if eachgene in enzyme_unit_number[r.id].keys():
                                    mass_sum += protein_id_mass_mapping[eachgene]['mw'] * int(enzyme_unit_number[r.id][eachgene])
                            else:
                                mass_sum += protein_id_mass_mapping[eachgene]['mw']
                    #print(mass_sum)
                    if mass_sum>0:
                        reaction_mw[r.id]=mass_sum
                else:  # Single enzyme
                    eachgene=r.gene_reaction_rule
                    #enzyme_unit_number = 1
                    if eachgene in protein_id_mass_mapping.keys():
                        #print(protein_id_mass_mapping[eachgene] * enzyme_unit_number)
                        #reaction_mw[r.id]=protein_id_mass_mapping[eachgene]['mw'] * enzyme_unit_number
                        if enzyme_unit_number_file != 'none':
                            if eachgene in enzyme_unit_number[r.id].keys(): 
                                reaction_mw[r.id]=protein_id_mass_mapping[eachgene]['mw'] * int(enzyme_unit_number[r.id][eachgene])
                        else:
                            reaction_mw[r.id]=protein_id_mass_mapping[eachgene]['mw']
        #print(model_reaction_id,reaction_mw.keys())
        if model_reaction_id in reaction_mw.keys():
            #print(model_reaction_id,reaction_mw[model_reaction_id])
            reaction_kcat_mw[model_reaction_id]['MW']=reaction_mw[model_reaction_id]#Kda
            reaction_kcat_mw[model_reaction_id]['kcat_MW']=reaction_kcat_mw[model_reaction_id]['kcat']*3600000/reaction_mw[model_reaction_id]
    reaction_kcat_mw_df = pd.DataFrame(reaction_kcat_mw)
    reaction_kcat_mw_df_T=reaction_kcat_mw_df.T
    reaction_kcat_mw_df_T_select=reaction_kcat_mw_df_T[abs(reaction_kcat_mw_df_T['kcat_MW'])>0]
    reaction_kcat_mw_df_T_select.to_csv(json_output_file)
    #reaction_kcat_mw_df_T.to_csv(project_folder + 'reaction_kcat_MW_total.csv')
    #return reaction_kcat_mw_df_T
    
def isoenzyme_split(model):
    """Split isoenzyme reaction to mutiple reaction

    Arguments
    ----------
    * model: cobra.Model.
    
    :return: new cobra.Model.
    """  
    for r in model.reactions:
        if re.search(" or ", r.gene_reaction_rule):
            rea = r.copy()
            gene = r.gene_reaction_rule.split(" or ")
            for index, value in enumerate(gene):
                if index == 0:
                    r.id = r.id + "_num1"
                    r.gene_reaction_rule = value
                else:
                    r_add = rea.copy()
                    r_add.id = rea.id + "_num" + str(index+1)
                    r_add.gene_reaction_rule = value
                    model.add_reaction(r_add)
    for r in model.reactions:
        r.gene_reaction_rule = r.gene_reaction_rule.strip("( )")
    return model

def trans_model2enz_json_model_split_isoenzyme(model_file, reaction_kcat_mw_file, f, ptot, sigma, lowerbound, upperbound, json_output_file):
    """Tansform cobra model to json mode with  
    enzyme concentration constraintat.

    Arguments
    ----------
    * model_file:   The path of sbml model
    * reaction_kcat_mw_file: The path of storing kcat/MW value of the enzyme catalyzing each
     reaction in the GEM model
    * f: The enzyme mass fraction 
    * ptot: The total protein fraction in cell.  
    * sigma: The approximated average saturation of enzyme. 
    * lowerbound:  Lowerbound  of enzyme concentration constraint. 
    * upperbound:  Upperbound  of enzyme concentration constraint. 

    """
    if re.search('\.xml',model_file):
        model = cobra.io.read_sbml_model(model_file)
    elif re.search('\.json',model_file):
        model = cobra.io.json.load_json_model(model_file)
    convert_to_irreversible(model)
    model = isoenzyme_split(model)
    model_name = model_file.split('/')[-1].split('.')[0]
    json_path = "./model/%s_irreversible.json" % model_name
    cobra.io.save_json_model(model, json_path)
    dictionary_model = json_load(json_path)
    dictionary_model['enzyme_constraint'] = {'enzyme_mass_fraction': f, 'total_protein_fraction': ptot,
                                             'average_saturation': sigma, 'lowerbound': lowerbound, 'upperbound': upperbound}
    # Reaction-kcat_mw file.
    # eg. AADDGT,49389.2889,40.6396,1215.299582180927
    reaction_kcat_mw = pd.read_csv(reaction_kcat_mw_file, index_col=0)
    for eachreaction in range(len(dictionary_model['reactions'])):
        reaction_id = dictionary_model['reactions'][eachreaction]['id']
        #if re.search('_num',reaction_id):
        #    reaction_id=reaction_id.split('_num')[0]
        if reaction_id in reaction_kcat_mw.index:
            dictionary_model['reactions'][eachreaction]['kcat'] = reaction_kcat_mw.loc[reaction_id, 'kcat']
            dictionary_model['reactions'][eachreaction]['kcat_MW'] = reaction_kcat_mw.loc[reaction_id, 'kcat_MW']
        else:
            dictionary_model['reactions'][eachreaction]['kcat'] = ''
            dictionary_model['reactions'][eachreaction]['kcat_MW'] = ''
    json_write(json_output_file, dictionary_model)
    
def get_enzyme_constraint_model(json_model_file):
    """using enzyme concentration constraint
    json model to create a COBRApy model.

    Arguments
    ----------
    * json_model_file: json Model file.

    :return: Construct an enzyme-constrained model.
    """

    dictionary_model = json_load(json_model_file)
    model = cobra.io.json.load_json_model(json_model_file)

    coefficients = dict()
    for rxn in model.reactions:
        for eachr in dictionary_model['reactions']:
            if rxn.id == eachr['id']:
                if eachr['kcat_MW']:
                    coefficients[rxn.forward_variable] = 1 / float(eachr['kcat_MW'])
                break

    lowerbound = dictionary_model['enzyme_constraint']['lowerbound']
    upperbound = dictionary_model['enzyme_constraint']['upperbound']
    constraint = model.problem.Constraint(0, lb=lowerbound, ub=upperbound)
    model.add_cons_vars(constraint)
    model.solver.update()
    constraint.set_linear_coefficients(coefficients=coefficients)
    return model

def get_enzyme_constraint_model_percent(json_model_file,percent):
    """using enzyme concentration constraint
    json model to create a COBRApy model.

    Arguments
    ----------
    * json_model_file: json Model file.

    :return: Construct an enzyme-constrained model.
    """

    dictionary_model = json_load(json_model_file)
    model = cobra.io.json.load_json_model(json_model_file)

    coefficients = dict()
    for rxn in model.reactions:
        for eachr in dictionary_model['reactions']:
            if rxn.id == eachr['id']:
                if eachr['kcat_MW']:
                    coefficients[rxn.forward_variable] = 1 / float(eachr['kcat_MW'])
                break

    lowerbound = dictionary_model['enzyme_constraint']['lowerbound']
    upperbound = dictionary_model['enzyme_constraint']['upperbound']*percent
    constraint = model.problem.Constraint(0, lb=lowerbound, ub=upperbound)
    model.add_cons_vars(constraint)
    model.solver.update()
    constraint.set_linear_coefficients(coefficients=coefficients)
    return model

def get_fluxes_detail_in_model(model,model_pfba_solution,fluxes_outfile,json_model_file):
    """Get the detailed information of each reaction

    Arguments
    ----------
    * model: cobra.Model.
    * fluxes_outfile: reaction flux file.
    * reaction_kcat_mw_file: reaction kcat/mw file.

    :return: fluxes, kcat, MW and kcat_MW in dataframe.
    """
    dictionary_model = json_load(json_model_file)
    model_pfba_solution = model_pfba_solution.to_frame()
    model_pfba_solution_detail = pd.DataFrame()
    for index, row in model_pfba_solution.iterrows():
        reaction_detail = model.reactions.get_by_id(index)
        model_pfba_solution_detail.loc[index, 'fluxes'] = row['fluxes']
        for eachreaction in dictionary_model['reactions']:
            if index ==eachreaction['id']:
                if 'annotation' in eachreaction.keys():
                    if 'ec-code' in eachreaction['annotation'].keys():
                        if isinstance (eachreaction['annotation']['ec-code'],list):
                            model_pfba_solution_detail.loc[index, 'ec-code'] = (',').join(eachreaction['annotation']['ec-code'])
                        else:
                            model_pfba_solution_detail.loc[index, 'ec-code'] = eachreaction['annotation']['ec-code']    
                if 'kcat_MW' in eachreaction.keys():
                    if eachreaction['kcat_MW']:
                        model_pfba_solution_detail.loc[index, 'kcat_MW'] = eachreaction['kcat_MW']
                        model_pfba_solution_detail.loc[index, 'E'] = float(row['fluxes'])/float(eachreaction['kcat_MW'])
                break
        model_pfba_solution_detail.loc[index, 'equ'] = reaction_detail.reaction
    model_pfba_solution_detail.to_csv(fluxes_outfile)
    return model_pfba_solution_detail

def json_write(path, dictionary):
    """Writes a JSON file at the given path with the given dictionary as content.

    Arguments
    ----------
    * path:   The path of the JSON file that shall be written
    * dictionary: The dictionary which shalll be the content of
      the created JSON file
    """
    json_output = json.dumps(dictionary, indent=4)
    with open(path, "w", encoding="utf-8") as f:
        f.write(json_output)
        
def GENENAME_2_ACC_from_uniprot(query,outfile):
    '''
    get amin acid sequence and mass by Uniprot id
    
    Arguments
    ----------
    query: Uniprot ID list.
    outfile:  The path of the ACC file that shall be written
    '''
    #print(' '.join(query).replace('511145.',''))
    url = 'https://legacy.uniprot.org/uploadlists/'
    params = {
        'from': 'GENENAME',
        'to': 'ACC',
        'format': 'tab',
        'query': ' '.join(query),
        'columns':'id,entry name,protein names,genes,organism,ec,mass,database(PDB)'
    }
    data = urlencode(params).encode()
    request = Request(url, data)
    # Please set your email address here to help us debug in case of problems.
    contact = ""
    request.add_header('User-Agent', 'Python %s' % contact)
    response = urlopen(request)
    page = response.read()
    outFile = open(outfile,'w') 
    namesRegex = re.compile(r'yourlist:(.*)\n')
    outFile.write(namesRegex.sub('Gene ID\n',page.decode('utf-8')))
    #print(namesRegex.sub('Protein AC\t',page.decode('utf-8')))
    outFile.close()
    
def calculate_f_old(uni_model_gene_list, gene_abundance_file, gene_mw_file, gene_mw_colname,gene_abundance_colname):
    """Calculating f (the mass fraction of enzymes that are accounted
    in the model out of all proteins) based on the protein abundance
    which can be obtained from PAXdb database.

    Arguments
    ----------
    * genes: All the genes in the model.
    * gene_abundance_file: The protein abundance of each gene
     in the E. coli genome.
    * gene_mw_file: The molecular weight of the protein expressed by each gene.

    :return: The enzyme mass fraction f.
    """
    gene_abundance = pd.read_csv(gene_abundance_file, index_col=0)
    gene_mw = pd.read_csv(gene_mw_file, sep='\t', index_col=gene_mw_colname)
    enzy_abundance = 0
    pro_abundance = 0
    for gene_i in gene_abundance.index:
        if gene_i in gene_mw.index:
            if isinstance(gene_mw.loc[gene_i,'Mass'],str):
                abundance = gene_abundance.loc[gene_i, gene_abundance_colname] * int(gene_mw.loc[gene_i,'Mass'].replace(',',''))
            else:
                abundance = gene_abundance.loc[gene_i, gene_abundance_colname] * int(gene_mw.loc[gene_i,'Mass'][0].replace(',',''))
            pro_abundance += abundance
            if gene_i in uni_model_gene_list:
                enzy_abundance += abundance
    f = enzy_abundance/pro_abundance
    return f

def calculate_f(sbml_path, gene_abundance_file, gene_mw_file, gene_mw_colname,gene_abundance_colname):
    """Calculating f (the mass fraction of enzymes that are accounted
    in the model out of all proteins) based on the protein abundance
    which can be obtained from PAXdb database.

    Arguments
    ----------
    * genes: All the genes in the model.
    * gene_abundance_file: The protein abundance of each gene
     in the E. coli genome.
    * gene_mw_file: The molecular weight of the protein expressed by each gene.

    :return: The enzyme mass fraction f.
    """
    model=cobra.io.read_sbml_model(sbml_path)
    model_gene_list=[]
    for eachg in model.genes:
        model_gene_list.append(eachg.id)
    uni_model_gene_list=list(set(model_gene_list))
    
    gene_abundance = pd.read_csv(gene_abundance_file, index_col=0)
    gene_list=list(set(gene_abundance.index))
    GENENAME_2_ACC_from_uniprot(gene_list,gene_mw_file)
    gene_mw = pd.read_csv(gene_mw_file, sep='\t', index_col=gene_mw_colname)
    enzy_abundance = 0
    pro_abundance = 0
    for gene_i in gene_abundance.index:
        if gene_i in gene_mw.index:
            if isinstance(gene_mw.loc[gene_i,'Mass'],str):
                abundance = gene_abundance.loc[gene_i, gene_abundance_colname] * int(gene_mw.loc[gene_i,'Mass'].replace(',',''))
            else:
                abundance = gene_abundance.loc[gene_i, gene_abundance_colname] * int(gene_mw.loc[gene_i,'Mass'][0].replace(',',''))
            pro_abundance += abundance
            if gene_i in uni_model_gene_list:
                enzy_abundance += abundance
    f = enzy_abundance/pro_abundance
    return f
def get_model_substrate_obj(use_model):
    '''
    change model substrate for single carbon source
    
    Arguments
    ----------
    use_model: cobra.Model ~ A Model object which will be modified in place.
    '''
    
    ATPM='No' 
    substrate_list=[]
    concentration_list=[]
    EX_exclude_reaction_list=['EX_pi_e','EX_h_e','EX_fe3_e','EX_mn2_e','EX_co2_e','EX_fe2_e','EX_h2_e','EX_zn2_e',\
                             'EX_mg2_e','EX_ca2_e','EX_so3_e','EX_ni2_e','EX_no_e','EX_cu2_e','EX_hg2_e','EX_cd2_e',\
                             'EX_h2o2_e','EX_h2o_e','EX_no2_e','EX_nh4_e','EX_so4_e','EX_k_e','EX_na1_e','EX_o2_e',\
                             'EX_o2s_e','EX_ag_e','EX_cu_e','EX_so2_e','EX_cl_e','EX_n2o_e','EX_cs1_e','EX_cobalt2_e']
    EX_exclude_reaction_list=EX_exclude_reaction_list+[i+'_reverse' for i in EX_exclude_reaction_list]
    for r in use_model.reactions:
        if r.objective_coefficient == 1:
            obj=r.id #Product name
        #elif not r.lower_bound==0 and not r.lower_bound==-1000 and not r.lower_bound==-999999 and abs(r.lower_bound)>0.1:#排除很小的值
        elif not r.upper_bound==0 and not r.upper_bound==1000 and not r.upper_bound==999999 and abs(r.upper_bound)>0.1:#排除很小的值
            #print(r.id,r.upper_bound,r.lower_bound)
            if r.id=='ATPM':
                if r.upper_bound>0:
                    ATPM='Yes' #ATP maintenance requirement
            elif r.id not in EX_exclude_reaction_list:
                #print(r.id,r.upper_bound,r.lower_bound)
                #substrate=r.id #Substrate name
                substrate_list.append(r.id)
                #concentration=r.upper_bound #Substrate uptake rate  
                concentration_list.append(r.upper_bound)
    return(obj,substrate_list,concentration_list,ATPM)

def parse_sabio_rk_for_eclist(ec_numbers_list: List[str], json_output_path: str, bigg_id_name_mapping_path: str) -> None:
    """Retrieves kcats from SABIO-RK for the given model and stores it in a JSON for the given model in the given path.

    Algorithm
    ----------
    Using the SABIO-RK REST API (as of 2019/30/04, it is explained under
    http://sabiork.h-its.org/layouts/content/docuRESTfulWeb/RESTWebserviceIntro.gsp),


    Arguments
    ----------
    * eclist: List[str] ~ eclist.
    * json_output_path: str ~ The path of the JSON that shall be created

    Output
    ----------
    * A JSON in the given project folder with the following structure:
    <pre>
        {
            "$EC_NUMBER_OR_KEGG_REACTION_ID": {
                "$SUBSTRATE_WITH_BIGG_ID_1": {
                    "$ORGANISM_1": [
                        $kcat_1,
                        (...)
                        $kcat_n,
                    ]
                },
                (...),
                "REST": {
                    "$ORGANISM_1": [
                        $kcat_1,
                        (...)
                        $kcat_n,
                    ]
                }
            }
            (...),
        }
    </pre>
    'REST' stands for a substrate without found BIGG ID.
    """
    # GET KCATS FOR EC NUMBERS
    ec_number_kcat_mapping = get_ec_number_kcats_wildcard_search(
        ec_numbers_list, bigg_id_name_mapping_path)

    json_write(json_output_path, ec_number_kcat_mapping)
    
    
def get_protein_mass_mapping_from_local(sbml_path: str, project_folder: str, project_name: str,uniprot_data_file: str) -> None:
    """Returns a JSON with a mapping of protein IDs as keys, and as values the protein mass in kDa.

    The protein masses are calculated using the amino acid sequence from UniProt (retrieved using
    UniProt's REST API).

    Arguments
    ----------
    * model: cobra.Model ~ The model in the cobrapy format
    * project_folder: str ~ The folder in which the JSON shall be created
    * project_name: str ~ The beginning of the JSON's file name
    * uniprot_data_file: str ~ The gene information obtained from uniprot
    Output
    ----------
    A JSON file with the path project_folder+project_name+'_protein_id_mass_mapping.json'
    and the following structure:
    <pre>
    {
        "$PROTEIN_ID": $PROTEIN_MASS_IN_KDA,
        (...),
    }
    </pre>
    """
    # Standardize project folder
    project_folder = standardize_folder(project_folder)

    # The beginning of the created JSON's path :D
    basepath: str = project_folder + project_name
    model= cobra.io.read_sbml_model(sbml_path)
    # GET UNIPROT ID - PROTEIN MAPPING
    uniprot_id_protein_id_mapping: Dict[str, List[str]] = {}
    for gene in model.genes:
        # Without a UniProt ID, no mass mapping can be found
        if "uniprot" not in gene.annotation:
            continue
        uniprot_id = gene.annotation["uniprot"]
        if uniprot_id in uniprot_id_protein_id_mapping.keys():
            uniprot_id_protein_id_mapping[uniprot_id].append(gene.id)
        else:
            uniprot_id_protein_id_mapping[uniprot_id] = [gene.id]

    # GET UNIPROT ID<->PROTEIN MASS MAPPING
    uniprot_id_protein_mass_mapping = json_load(uniprot_data_file)
    
    # Create the final protein ID <-> mass mapping
    protein_id_mass_mapping: Dict[str, float] = {}
    for uniprot_id in list(uniprot_id_protein_mass_mapping.keys()):
        try:
            protein_ids = uniprot_id_protein_id_mapping[uniprot_id]
        except Exception:
            #print(f"No mass found for {uniprot_id}!")
            continue
        for protein_id in protein_ids:
            protein_id_mass_mapping[protein_id] = uniprot_id_protein_mass_mapping[uniprot_id]

    # Write protein mass list JSON :D
    #print("Protein ID<->Mass mapping done!")
    json_write(basepath+"_protein_id_mass_mapping.json", protein_id_mass_mapping)
    
    
def change_reaction_kcat_by_database(json_model_path,select_reactionlist, EC_max_file, reaction_kcat_mw_file, reaction_kapp_change_file):
    """Use the kcat in database to change reaction kcat in model

    Arguments
    ----------
    * json_model_path: The file storing json model.
    * select_reactionlist: reaction list need to change.
    * kcat_database_combined_file: combined kcat file got from autoPACMEN.
    * reaction_kcat_mw_file: reaction kcat/mw file.
    * reaction_kapp_change_file: changed file stored reaction kcat/mw.

    :return: a dataframe stored new reaction kcat/mw .
    """
    reaction_kcat_mw = pd.read_csv(reaction_kcat_mw_file, index_col=0)
    Brenda_sabio_combined_select = json_load(EC_max_file)
    
    json_model=cobra.io.load_json_model(json_model_path)
    reaction_change_accord_database = []
    for eachreaction in select_reactionlist:
        select_reaction = json_model.reactions.get_by_id(eachreaction)
        if "ec-code" in select_reaction.annotation.keys():
            ec_number = select_reaction.annotation["ec-code"]
            kcat_max_list = []
            if isinstance(ec_number, str):
                if ec_number in Brenda_sabio_combined_select.keys():
                    reaction_kcat_max = Brenda_sabio_combined_select[ec_number]['kcat_max']
                    if reaction_kcat_mw.loc[eachreaction, 'kcat'] < reaction_kcat_max :
                        reaction_kcat_mw.loc[eachreaction,'kcat'] = reaction_kcat_max #h_1
                        reaction_kcat_mw.loc[eachreaction, 'kcat_MW'] = reaction_kcat_max * 3600*1000/reaction_kcat_mw.loc[eachreaction, 'MW']
                        reaction_change_accord_database.append(eachreaction) 
            else:
                for eachec in ec_number:
                    if eachec in Brenda_sabio_combined_select.keys():
                        kcat_max_list.append(Brenda_sabio_combined_select[eachec]['kcat_max'])
                reaction_kcat_max = np.max(kcat_max_list)     
                if reaction_kcat_mw.loc[eachreaction, 'kcat'] < reaction_kcat_max:
                    reaction_kcat_mw.loc[eachreaction,'kcat'] = reaction_kcat_max
                    reaction_kcat_mw.loc[eachreaction, 'kcat_MW'] = reaction_kcat_max * 3600*1000/reaction_kcat_mw.loc[eachreaction, 'MW']
                    reaction_change_accord_database.append(eachreaction)    
                
    reaction_kcat_mw.to_csv(reaction_kapp_change_file)
    return(reaction_change_accord_database)

def get_enz_model_use_enz_usage_by_eckcat(enz_ratio,json_model_path, reaction_flux_file, EC_max_file, reaction_kcat_mw_file, f, \
                                          ptot, sigma, lowerbound, upperbound, json_output_file, reaction_mw_outfile):

    """Get new enzyme model using enzyme usage to calibration

    Arguments
    ----------
    * enz_ratio: enzyme ratio which needed change.
    * json_model_path: The file storing json model.
    * reaction_flux_file: reaction-flux file.
    * reaction_kcat_mw_file: reaction kcat/mw file.
    * reaction_enz_usage_file： enzyme usage of each reaction.
    * kcat_database_combined_file: combined kcat file got from autoPACMEN.
    * model_file: cobra model.
    * f: The enzyme mass fraction 
    * ptot: The total protein fraction in cell.  
    * sigma: The approximated average saturation of enzyme. 
    * lowerbound:  Lowerbound  of enzyme concentration constraint. 
    * upperbound:  Upperbound  of enzyme concentration constraint.  
    * json_output_file: json file store json model
    * reaction_mw_outfile: changed file stored reaction kcat/mw.

    :return: new enzyme model
    """ 
    reaction_fluxes = pd.read_csv(reaction_flux_file, index_col=0)
    reaction_fluxes['enz ratio'] = reaction_fluxes['E']/np.sum(reaction_fluxes['E'])
    reaction_fluxes=reaction_fluxes.sort_values(by="enz ratio", axis=0, ascending=False)
    
    select_reaction = list(
        reaction_fluxes[reaction_fluxes['enz ratio'] > enz_ratio].index)  # more than 1%
    print('need changing reaction: ')
    print(select_reaction)
    change_reaction_list_round1 = change_reaction_kcat_by_database(json_model_path,select_reaction, EC_max_file, reaction_kcat_mw_file, reaction_mw_outfile)
    print('changed reaction: ')
    print(change_reaction_list_round1)

    trans_model2enz_json_model_split_isoenzyme(
        json_model_path, reaction_mw_outfile, f, ptot, sigma, lowerbound, upperbound, json_output_file)

    enz_model = get_enzyme_constraint_model(json_output_file)
    return enz_model

def get_EC_kcat_max(inputfile):
    EC_data = json_load(inputfile)
    EC_kcat_max={}
    for eachEC in EC_data.keys():
        EC_max=0
        EC_max_org=''
        EC_TRANSFER_ID=''
        for eachmet in EC_data[eachEC].keys():
            if isinstance(EC_data[eachEC][eachmet],dict):
                for eachorg in EC_data[eachEC][eachmet].keys():
                    #print(eachmet,EC_data[eachEC][eachmet][eachorg],np.max(EC_data[eachEC][eachmet][eachorg]))
                    if np.max(EC_data[eachEC][eachmet][eachorg])>EC_max:
                        EC_max=np.max(EC_data[eachEC][eachmet][eachorg])
                        EC_max_org=eachorg
            else:
                if re.search(' and ec ',EC_data[eachEC][eachmet]):
                    new_EC_list=EC_data[eachEC][eachmet].split(' and ec ')
                    EC_TRANSFER_ID=EC_data[eachEC][eachmet].replace(' and ec ',' and ')
                    for eachec in new_EC_list:
                        if eachec in EC_data.keys():
                            for eachmet2 in EC_data[eachec].keys():
                                if isinstance(EC_data[eachec][eachmet2],dict):
                                    for eachorg in EC_data[eachec][eachmet2].keys():
                                        #print(np.max(EC_data[EC_data[eachEC][eachmet]][eachmet2][eachorg]),EC_max)
                                        if np.max(EC_data[eachec][eachmet2][eachorg])>EC_max:
                                            EC_max=np.max(EC_data[eachec][eachmet2][eachorg])
                                            EC_max_org=eachorg
                                else:
                                    print(EC_data[eachec][eachmet2])  
                else:        
                    EC_TRANSFER_ID=EC_data[eachEC][eachmet]
                    if EC_TRANSFER_ID in EC_data.keys():
                        for eachmet2 in EC_data[EC_data[eachEC][eachmet]].keys():
                            if isinstance(EC_data[EC_data[eachEC][eachmet]][eachmet2],dict):
                                for eachorg in EC_data[EC_data[eachEC][eachmet]][eachmet2].keys():
                                    #print(np.max(EC_data[EC_data[eachEC][eachmet]][eachmet2][eachorg]),EC_max)
                                    if np.max(EC_data[EC_data[eachEC][eachmet]][eachmet2][eachorg])>EC_max:
                                        EC_max=np.max(EC_data[EC_data[eachEC][eachmet]][eachmet2][eachorg])
                                        EC_max_org=eachorg
                            else:
                                print(EC_data[EC_data[eachEC][eachmet]][eachmet2])
        if EC_max!=0:
            EC_kcat_max[eachEC]={}
            EC_kcat_max[eachEC]['kcat_max']=EC_max
            EC_kcat_max[eachEC]['org']=EC_max_org
            EC_kcat_max[eachEC]['EC_TRANSFER_ID']=EC_TRANSFER_ID
        #break
    return(EC_kcat_max) 

def adj_reaction_kcat_by_database(json_model_path,select_reactionlist, need_change_reaction_list, changed_reaction_list,EC_max_file, reaction_kcat_mw):
    """Use the kcat in database to change reaction kcat in model

    Arguments
    ----------
    * json_model_path: The file storing json model.
    * select_reactionlist: reaction list need to change.
    * kcat_database_combined_file: combined kcat file got from autoPACMEN.
    * reaction_kcat_mw_file: reaction kcat/mw file.
    * reaction_kapp_change_file: changed file stored reaction kcat/mw.

    :return: a dataframe stored new reaction kcat/mw .
    """
    Brenda_sabio_combined_select = json_load(EC_max_file)
    
    json_model=cobra.io.load_json_model(json_model_path)
    for eachreaction in select_reactionlist:
        need_change_reaction_list.append(eachreaction)
        select_reaction = json_model.reactions.get_by_id(eachreaction)
        if "ec-code" in select_reaction.annotation.keys():
            ec_number = select_reaction.annotation["ec-code"]
            kcat_max_list = []
            if isinstance(ec_number, str):
                if ec_number in Brenda_sabio_combined_select.keys():
                    reaction_kcat_max = Brenda_sabio_combined_select[ec_number]['kcat_max']
                    if reaction_kcat_mw.loc[eachreaction, 'kcat'] < reaction_kcat_max:
                        reaction_kcat_mw.loc[eachreaction,'kcat'] = reaction_kcat_max#h_1
                        reaction_kcat_mw.loc[eachreaction, 'kcat_MW'] = reaction_kcat_max * 3600*1000/reaction_kcat_mw.loc[eachreaction, 'MW']
                        changed_reaction_list.append(eachreaction) 
            else:
                for eachec in ec_number:
                    if eachec in Brenda_sabio_combined_select.keys():
                        kcat_max_list.append(Brenda_sabio_combined_select[eachec]['kcat_max'])
                reaction_kcat_max = np.max(kcat_max_list)     
                if reaction_kcat_mw.loc[eachreaction, 'kcat'] < reaction_kcat_max:
                    reaction_kcat_mw.loc[eachreaction,'kcat'] = reaction_kcat_max
                    reaction_kcat_mw.loc[eachreaction, 'kcat_MW'] = reaction_kcat_max * 3600*1000/reaction_kcat_mw.loc[eachreaction, 'MW']
                    changed_reaction_list.append(eachreaction)    
                
    return(need_change_reaction_list,changed_reaction_list,reaction_kcat_mw)

def adj_trans_model2enz_model(model_file, reaction_kcat_mw, f, ptot, sigma, lowerbound, upperbound, json_output_file):
    """Tansform cobra model to json mode with  
    enzyme concentration constraintat.

    Arguments
    ----------
    * model_file:   The path of sbml model
    * reaction_kcat_mw_file: The path of storing kcat/MW value of the enzyme catalyzing each
     reaction in the GEM model
    * f: The enzyme mass fraction 
    * ptot: The total protein fraction in cell.  
    * sigma: The approximated average saturation of enzyme. 
    * lowerbound:  Lowerbound  of enzyme concentration constraint. 
    * upperbound:  Upperbound  of enzyme concentration constraint. 

    """
    if re.search('\.xml',model_file):
        model = cobra.io.read_sbml_model(model_file)
    elif re.search('\.json',model_file):
        model = cobra.io.json.load_json_model(model_file)
    convert_to_irreversible(model)
    model = isoenzyme_split(model)
    model_name = model_file.split('/')[-1].split('.')[0]
    json_path = "./model/%s_irreversible.json" % model_name
    cobra.io.save_json_model(model, json_path)
    dictionary_model = json_load(json_path)
    dictionary_model['enzyme_constraint'] = {'enzyme_mass_fraction': f, 'total_protein_fraction': ptot,
                                             'average_saturation': sigma, 'lowerbound': lowerbound, 'upperbound': upperbound}
    # Reaction-kcat_mw file.
    # eg. AADDGT,49389.2889,40.6396,1215.299582180927
    for eachreaction in range(len(dictionary_model['reactions'])):
        reaction_id = dictionary_model['reactions'][eachreaction]['id']
        #if re.search('_num',reaction_id):
        #    reaction_id=reaction_id.split('_num')[0]
        if reaction_id in reaction_kcat_mw.index:
            dictionary_model['reactions'][eachreaction]['kcat'] = reaction_kcat_mw.loc[reaction_id, 'kcat']
            dictionary_model['reactions'][eachreaction]['kcat_MW'] = reaction_kcat_mw.loc[reaction_id, 'kcat_MW']
        else:
            dictionary_model['reactions'][eachreaction]['kcat'] = ''
            dictionary_model['reactions'][eachreaction]['kcat_MW'] = ''
    json_write(json_output_file, dictionary_model)
    
def change_enz_model_by_enz_usage(enz_ratio,json_model_path, reaction_flux_file, EC_max_file, reaction_kcat_mw, need_change_reaction_list, changed_reaction_list,f, ptot, sigma, lowerbound, upperbound, json_output_file):

    """Get new enzyme model using enzyme usage to calibration

    Arguments
    ----------
    * enz_ratio: enzyme ratio which needed change.
    * json_model_path: The file storing json model.
    * reaction_flux_file: reaction-flux file.
    * reaction_kcat_mw_file: reaction kcat/mw file.
    * reaction_enz_usage_file： enzyme usage of each reaction.
    * kcat_database_combined_file: combined kcat file got from autoPACMEN.
    * model_file: cobra model.
    * f: The enzyme mass fraction 
    * ptot: The total protein fraction in cell.  
    * sigma: The approximated average saturation of enzyme. 
    * lowerbound:  Lowerbound  of enzyme concentration constraint. 
    * upperbound:  Upperbound  of enzyme concentration constraint.  
    * json_output_file: json file store json model
    * reaction_mw_outfile: changed file stored reaction kcat/mw.

    :return: new enzyme model
    """ 
    reaction_fluxes = pd.read_csv(reaction_flux_file, index_col=0)
    reaction_fluxes['enz ratio'] = reaction_fluxes['E']/np.sum(reaction_fluxes['E'])
    reaction_fluxes=reaction_fluxes.sort_values(by="enz ratio", axis=0, ascending=False)
    #每次只选第一个
    i=0
    select_reaction = reaction_fluxes.index[0]
    while (select_reaction in need_change_reaction_list):
        i=i+1
        #print(i)
        select_reaction = reaction_fluxes.index[i+1]
        
    print('Need changing reaction: ')
    print(select_reaction)
    [need_change_reaction_list, changed_reaction_list,reaction_kcat_mw] = adj_reaction_kcat_by_database(json_model_path,[select_reaction], need_change_reaction_list, changed_reaction_list, EC_max_file, reaction_kcat_mw)
    print('Changed reaction: ')
    print(changed_reaction_list)

    adj_trans_model2enz_model(json_model_path, reaction_kcat_mw, f, ptot, sigma, lowerbound, upperbound, json_output_file)

    enz_model = get_enzyme_constraint_model(json_output_file)
    return (enz_model,reaction_kcat_mw,need_change_reaction_list, changed_reaction_list)

def get_met_bigg_id(model):
    '''
    This function is used to get the bigg id of metabolites in the model.

    Arguments
    ----------
    * model: cobra.Model ~ A Model object which will be modified in place.

    '''

    metlist = []
    metnamelist = []
    for met in model.metabolites:
        if '_c' in str(met):
            metlist.append(str(met.id).split('_c')[0])
            metnamelist.append(str(met.name))
        elif '_e' in str(met):
            metlist.append(str(met.id).split('_e')[0])
            metnamelist.append(str(met.name))
        elif '_p' in str(met):
            metlist.append(str(met.id).split('_p')[0])
            metnamelist.append(str(met.name))
        else:
            metlist.append(str(met.id))
            metnamelist.append(str(met.name))

    metdf = pd.DataFrame()
    metdf_unique = pd.DataFrame()

    metdf['met'] = metlist
    metdf['name'] = metnamelist
    metdf.set_index('met', inplace=True)

    metlist = list(set(metlist))
    metdf_unique['met'] = metlist
    metdf_unique.set_index('met', inplace=True)

    for row in metdf_unique.itertuples():
        if type(metdf.loc[str(row.Index), 'name']) == str:
            metdf_unique.loc[str(row.Index), 'name'] = metdf.loc[str(row.Index), 'name']
        else:
            for i in metdf.loc[str(row.Index), 'name']:
                metdf_unique.loc[str(row.Index), 'name'] = i
    metdf_unique.reset_index(inplace=True)
    # metdf_unique.to_csv('./metbigg_name_unique.csv')
    return metdf_unique

def convert_bigg_met_to_inckikey(metlist):
    '''
    This function is used to convert the bigg id of metabolites in the model to inchikey.
    
    Arguments
    ----------
    * model: cobra.Model ~ A Model object which will be modified in place.

    '''

    inchkeydf = pd.DataFrame(columns=['metname', 'inchikey'])
    inchikeylist = []
    for met in metlist:
        try:
            url = 'http://bigg.ucsd.edu/api/v2/universal/metabolites/' + met
            response = requests.get(url, headers={"Accept": "application/json"})
            jsonData = json.loads(response.text)
            inchikeylist.append(jsonData['database_links']['InChI Key'][0]['id'])           
        except:            
            inchikeylist.append('NA')

    inchkeydf['metname'] = metlist
    inchkeydf['inchikey'] = inchikeylist

    # inchkeydf.to_csv('inchikey_list.csv')
    return inchkeydf

def convert_inchikey_to_smiles(inchkeydf):
    '''
    This function is used to convert the inchikey of metabolites in the model to smiles.

    Arguments
    ----------
    * inchkeydf: pandas.DataFrame ~ A DataFrame object which contains the inchikey of metabolites.
    '''

    inchkeydf.set_index('metname', inplace=True)
    for eachc in inchkeydf.index:
        if pd.isnull(inchkeydf.loc[eachc,'inchikey']):
            inchkeydf.loc[eachc,'Canonical_SMILES']='noinchikey'
        else:
            clist = pcp.get_compounds(inchkeydf.loc[eachc,'inchikey'], 'inchikey')
            if len(clist)==0:
                inchkeydf.loc[eachc,'Canonical_SMILES']='noinchikey_inpubchem'                            
            elif len(clist) == 1 :               
                for compound in clist:
                    try:
                        inchkeydf.loc[eachc,'Canonical_SMILES']=compound.canonical_smiles
                    except:
                        inchkeydf.loc[eachc,'Canonical_SMILES']='nosmiles'
            else:
                compound = clist[0]
                try:
                    inchkeydf.loc[eachc,'Canonical_SMILES']=compound.canonical_smiles
                except:
                    inchkeydf.loc[eachc,'Canonical_SMILES']='nosmiles'
        time.sleep(6)
    inchkeydf.reset_index(inplace=True)        
    # inchkeydf.to_csv('inchikey_list_smiles.csv')
    return inchkeydf   

def get_model_protein_sequence_and_mass(model):
    '''
    This function is used to get the protein sequence and mass of the model.
    
    Arguments
    ----------
    * model: cobra.Model ~ A Model object which will be modified in place.
    '''

    genelist = []
    prolist = []

    for gene in model.genes:
        if 'uniprot' in str(gene.annotation):     
            pro = gene.annotation['uniprot']

            genelist.append(gene.id)
            prolist.append(str(pro))
    # prolist = list(set(prolist))

    prodf = pd.DataFrame(columns=['geneid', 'pro'])
    prodf['geneid'] = genelist
    prodf['pro'] = prolist

    for row in prodf.itertuples():
        query = str(row.pro)
        uniprot_query_url = f"https://rest.uniprot.org/uniprotkb/search?query=accession:{query}&format=tsv&fields=accession,sequence"

        # Call UniProt's API :-)
        uniprot_data = requests.get(uniprot_query_url).text.split("\n")[1].split("\t")[1]
        prodf.loc[row.Index,'aaseq'] = uniprot_data
        mass = ProteinAnalysis(uniprot_data, monoisotopic=False).molecular_weight()
        prodf.loc[row.Index,'mass'] = mass
        # Wait in order to cool down their server :-)
        time.sleep(2.0)    

    # prodf.to_csv('pro_list_mw.csv')
    return prodf

def split_substrate_to_match_gene(model):
    '''
    This function is used to split the substrate of reactions to match the gene of reactions.

    Arguments
    ----------
    * model: cobra.Model ~ A Model object which will be modified in place.
    '''

    currencytotal = []
    currencylist1 = ['coa_c', 'co2_c', 'co2_e', 'co2_p', 'cobalt2_c', 'cobalt2_e', 'cobalt2_p', 'h_c', 'h_e', 'h_p', 'h2_c', 'h2_e', 'h2_p', 'h2o_c', 'h2o_e', 'h2o_p', 'h2o2_c', 'h2o2_e', 'h2o2_p', 'nh4_c', 'nh4_e', 'nh4_p', 'o2_c', 'o2_e', 'o2_p', 'pi_c', 'pi_e', 'pi_p', 'ppi_c', 'pppi_c', 'q8_c', 'q8h2_c', 'no_p', 'no3_p', 'no3_e', 'no_c', 'no2_c', 'no_e', 'no3_c', 'no2_e', 'no2_p', 'n2o_c', 'n2o_e', 'n2o_p', 'h2s_c', 'so3_c', 'so3_p', 'o2s_c', 'h2s_p', 'so2_e', 'so4_e', 'h2s_e', 'o2s_p', 'o2s_e', 'so4_c', 'so4_p', 'so3_e', 'so2_c', 'so2_p', 'ag_c', 'ag_e', 'ag_p','na1_c','na1_e','na1_p','ca2_c', 'ca2_e', 'ca2_p', 'cl_c', 'cl_e', 'cl_p', 'cd2_c', 'cd2_e', 'cd2_p', 'cu_c', 'cu_e', 'cu_p', 'cu2_c', 'cu2_e', 'cu2_p', 'fe2_c', 'fe2_e', 'fe2_p', 'fe3_c', 'fe3_e', 'fe3_p', 'hg2_c', 'hg2_e', 'hg2_p', 'k_c', 'k_e', 'k_p', 'mg2_c', 'mg2_e', 'mg2_p', 'mn2_c', 'mn2_e', 'mn2_p', 'zn2_c', 'zn2_e', 'zn2_p','nh3']
    currencylist2 = ['amp_c', 'amp_e', 'amp_p', 'adp_c', 'adp_e', 'adp_p', 'atp_c', 'atp_e', 'atp_p', 'cmp_c', 'cmp_e', 'cmp_p', 'cdp_c', 'cdp_e', 'cdp_p', 'ctp_c', 'ctp_e', 'ctp_p', 'gmp_c', 'gmp_e', 'gmp_p', 'gdp_c', 'gdp_e', 'gdp_p', 'gtp_c', 'gtp_e', 'gtp_p', 'imp_c', 'imp_e', 'imp_p', 'idp_c', 'idp_e', 'idp_p', 'itp_c', 'itp_e', 'itp_p', 'ump_c', 'ump_e', 'ump_p', 'udp_c', 'udp_e', 'udp_p', 'utp_c', 'utp_e', 'utp_p', 'xmp_e', 'xmp_c', 'xmp_p', 'xdp_c', 'xdp_e', 'xdp_p', 'xtp_c', 'xtp_e', 'xtp_p', 'damp_c', 'damp_e', 'damp_p', 'dadp_c', 'dadp_e', 'dadp_p', 'datp_c', 'datp_e', 'datp_p', 'dcmp_c', 'dcmp_e', 'dcmp_p', 'dcdp_c', 'dcdp_e', 'dcdp_p', 'dctp_c', 'dctp_e', 'dctp_p', 'dgmp_c', 'dgmp_e', 'dgmp_p', 'dgdp_c', 'dgdp_e', 'dgdp_p', 'dgtp_c', 'dgtp_e', 'dgtp_p', 'dimp_c', 'dimp_e', 'dimp_p', 'didp_c', 'didp_e', 'didp_p', 'ditp_c', 'ditp_e', 'ditp_p', 'dump_c', 'dump_e', 'dump_p', 'dudp_c', 'dudp_e', 'dudp_p', 'dutp_c', 'dutp_e', 'dutp_p', 'dtmp_c', 'dtmp_e', 'dtmp_p', 'dtdp_c', 'dtdp_e', 'dtdp_p', 'dttp_c', 'dttp_e', 'dttp_c', 'fad_c', 'fad_p', 'fad_e', 'fadh2_c', 'fadh2_e', 'fadh2_p', 'nad_c', 'nad_e', 'nad_p', 'nadh_c', 'nadh_e', 'nadh_p', 'nadp_c', 'nadp_e', 'nadp_p', 'nadph_c', 'nadph_e', 'nadph_p']
    currencylist3 = ['cdp', 'ag', 'dctp', 'dutp', 'ctp', 'gdp', 'gtp', 'ump', 'ca2', 'h2o', 'datp', 'co2', 'no2', 'no', 'k', 'zn2', 'no3', 'o2', 'cl', 'udp', 'damp', 'ditp', 'dump', 'q8h2', 'pppi', 'idp', 'dimp', 'pi', 'dttp', 'so4', 'adp', 'xtp', 'dgtp', 'dadp', 'coa', 'ppi', 'h2', 'cmp', 'fe2', 'o2s', 'h', 'gmp', 'itp', 'q8', 'cobalt2', 'n2o', 'xmp', 'xdp', 'nadph', 'cu', 'cu2', 'atp', 'dgmp', 'imp', 'h2s', 'utp', 'dtmp', 'fadh2', 'so3', 'fad', 'cd2', 'dgdp', 'nad', 'nadh', 'hg2', 'dcmp', 'dudp', 'dtdp', 'didp', 'mn2', 'dcdp', 'nh4', 'amp', 'fe3', 'nadp', 'so2', 'h2o2', 'mg2']
    currencytotal = currencylist1+currencylist2+currencylist3
    rlist = []
    sublist = []
    subtotal = []
    gprlist = []
    genetotal = []
    
    convert_to_irreversible(model)
    model = isoenzyme_split(model)
    
    for eachr in model.reactions:
        mlist = []
        for eachm in eachr.reactants:
            if eachm.id not in currencytotal:
                if len(eachr.gene_reaction_rule) != 0:
                    # abstract the gene_reaction_rule to a list of genes
                    mlist.append(eachm.id)
        if len(eachr.gene_reaction_rule) != 0:
            if len(mlist)>1:
                #preprocess the multimetbolite reactions
                for eachm2 in mlist:
                    #remove currency metabolites from the list of metabolites
                    if eachm2 not in currencytotal:
                        if 'and' in eachr.gene_reaction_rule:
                            genelist = []
                            genelist = eachr.gene_reaction_rule.split(' and ')
                            for eachgene in genelist:
                                #preprocess the multigene reactions
                                rlist.append(eachr.id)
                                sublist.append(mlist)
                                gprlist.append(eachr.gene_reaction_rule)
                                genetotal.append(eachgene)
                                if '_c' in eachm2:
                                    subtotal.append(eachm2.split('_c')[0])
                                elif '_p' in eachm2:
                                    subtotal.append(eachm2.split('_p')[0])  
                                else:
                                    subtotal.append(eachm2.split('_e')[0])
                        else:
                            rlist.append(eachr.id)
                            sublist.append(mlist)
                            gprlist.append(eachr.gene_reaction_rule)
                            genetotal.append(eachr.gene_reaction_rule)
                            if '_c' in eachm2:
                                subtotal.append(eachm2.split('_c')[0])
                            elif '_p' in eachm2:
                                subtotal.append(eachm2.split('_p')[0])
                            else:
                                subtotal.append(eachm2.split('_e')[0])
                        
            else:
                if eachm.id not in currencytotal:
                    if 'and' in eachr.gene_reaction_rule:
                        genelist = []
                        genelist = eachr.gene_reaction_rule.split(' and ')
                        for eachgene in genelist:
                            rlist.append(eachr.id)
                            sublist.append(eachm.id)
                            gprlist.append(eachr.gene_reaction_rule)
                            genetotal.append(eachgene)
                            if '_c' in eachm.id:
                                subtotal.append(eachm.id.split('_c')[0])  
                            elif '_p' in eachm.id:
                                subtotal.append(eachm.id.split('_p')[0])
                            else:
                                subtotal.append(eachm.id.split('_e')[0])
                    else:
                        rlist.append(eachr.id)
                        sublist.append(eachm.id)
                        gprlist.append(eachr.gene_reaction_rule)
                        genetotal.append(eachr.gene_reaction_rule)
                        if '_c' in eachm.id:
                            subtotal.append(eachm.id.split('_c')[0])  
                        elif '_p' in eachm.id:
                            # print(eachm)
                            subtotal.append(eachm.id.split('_p')[0])
                        else:
                            subtotal.append(eachm.id.split('_e')[0])
                            

    metdf = pd.DataFrame()
    metdf['reactions'] = rlist
    metdf['metabolites'] = sublist
    metdf['metabolitestotal'] = subtotal
    metdf['gpr'] = gprlist
    metdf['genes'] = genetotal

    # metdf.to_csv('metabolites_reactions_gpr.csv', index=False)
    return metdf

def combine_reactions_simles_sequence(metdf,smilesdf,prodf):
    '''
    This function is used to combine the reaction--substrate--gene--protein_sequnce--mass.
    
    Arguments:
    * metdf: metabolites_reactions_gpr
    * similesdf: inchkeydf
    * prodf: prodf
    '''
    # match metabolites to similes
    # match metabolites to similes
    for index,row in metdf.iterrows():
        # print(row['metabolitestotal'])
        if row['metabolitestotal'] in list(smilesdf['metname']):
            # print(list(smilesdf[smilesdf['metname']==row['metabolitestotal']]['Canonical_SMILES']))
            metdf.loc[index,'similes']=list(smilesdf[smilesdf['metname']==row['metabolitestotal']]['Canonical_SMILES'])[0]
 
        if row['genes'] in list(prodf['geneid']):
            metdf.loc[index,'prosequence']=list(prodf[prodf['geneid']==row['genes']]['aaseq'])[0]            
 
        if row['genes'] in list(prodf['geneid']):
            metdf.loc[index,'mass']=list(prodf[prodf['geneid']==row['genes']]['mass'])[0]  

    # # match gene to prosequence
    # metdf['prosequence'] = ''
    # for eachrow in metdf.iterrows():
    #     for eachpro in prodf.iterrows():
    #         if eachrow[1]['genes'] == eachpro[1]['geneid']:
    #             metdf.loc[eachrow[0], 'prosequence'] = eachpro[1]['aaseq']
    # # match gene to mass
    # metdf['mass'] = ''
    # for eachrow in metdf.iterrows():
    #     for eachpro in prodf.iterrows():
    #         if eachrow[1]['genes'] == eachpro[1]['geneid']:
    #             metdf.loc[eachrow[0], 'mass'] = eachpro[1]['mass']
                
    # metdf.to_csv('metabolites_reactions_gpr_similes_prosequence_mass.csv', index=False)
    return metdf 

def generate_DLKCAT_input(metdf,metdf_name,metdf_outfile,DLinputdf_file):
    '''
    This function is used to generate the DLKCAT input file.
    
    Arguments:
    * metdf: reaction--substrate--gene--protein_sequnce--mass

    '''
    # generate the DLKCAT input file
    metdf_name.index=metdf_name['met']
    for row in metdf.itertuples():
        metdf.loc[row.Index,'metname'] = metdf_name.loc[row.metabolitestotal,'name']

    DLinputdf = pd.DataFrame()
    metdf.dropna(subset=['prosequence'], inplace=True)

    # replace noinchikey_inpubchem to None
    metdf.loc[metdf['similes'] == 'noinchikey_inpubchem', 'similes'] = 'None'
    metdf.loc[metdf['similes'] == 'noinchikey', 'similes'] = 'None'

    for row in metdf.itertuples():
        if '.' in row.similes:
            metdf.loc[row.Index,'similes'] = str(row.similes).split('.')[0]


    metdf.reset_index(drop=True, inplace=True)
    metdf.to_csv(metdf_outfile, index=False)

    DLinputdf['metname'] = metdf['metname']
    DLinputdf['similes'] = metdf['similes']
    DLinputdf['prosequence'] = metdf['prosequence']
    DLinputdf.reset_index(drop=True, inplace=True)
    DLinputdf.to_csv(DLinputdf_file, sep='\t', index=False)
    print('DLKCAT input file generated')
    # DLinputdf
    return DLinputdf    

def DL_kcat_mw_calculation(DLouputdf, metdf):
    '''
    make the kcat_mw input file for ecGEM construction

    ----------
    Arguments:
    * DLouputdf: DLinputdf from DLKCAT
    * metdf: metabolites_reactions_gpr_similes_prosequence_mass_dropna
    '''
    DLouputdf.reset_index(drop=True, inplace=True)
    # metdf = pd.read_csv('metabolites_reactions_gpr_similes_prosequence_mass_noinchikey.csv')
    metdf.reset_index(drop=True, inplace=True)
    #combine DLouputdf and metdf
    DLoutputdf_rex = pd.concat([metdf,DLouputdf['Kcat value (1/s)']], axis=1)
    #DLoutputdf_rex.to_csv('DLoutput.csv', index=False)
    # remove none rows from DLoutputdf_rex
    DLoutputdf_rex = DLoutputdf_rex.drop(index = DLoutputdf_rex[ DLoutputdf_rex['Kcat value (1/s)'] == 'None'].index.tolist())
    #change Kcat value (1/s) to float
    DLoutputdf_rex['Kcat value (1/s)'] = DLoutputdf_rex['Kcat value (1/s)'].astype(float)
    #choose kcat max
    DLoutputdf_rex= DLoutputdf_rex.sort_values('Kcat value (1/s)', ascending=False).drop_duplicates(subset=['reactions'], keep='first')
    #calculation kcat_mw
    for row in DLoutputdf_rex.iterrows():

        DLoutputdf_rex.loc[row[0], 'kcat_mw'] = float(row[1]['Kcat value (1/s)']) *3600*1000/float(row[1]['mass'])

    #DLoutputdf_rex.to_csv('DLoutput_rex_kcat_mw.csv', sep=',', index=False)
    #
    DL_reaction_kact_mw = pd.DataFrame()
    DL_reaction_kact_mw['reactions'] = DLoutputdf_rex['reactions']
    DL_reaction_kact_mw['kcat'] = DLoutputdf_rex['Kcat value (1/s)']
    DL_reaction_kact_mw['MW'] = DLoutputdf_rex['mass']
    DL_reaction_kact_mw['kcat_MW'] = DLoutputdf_rex['kcat_mw']
    DL_reaction_kact_mw.reset_index(drop=True, inplace=True)
    #DL_reaction_kact_mw.to_csv('DL_reaction_kact_mw.csv', sep=',', index=False)
    print('DL_reaction_kact_mw generated')
    return DL_reaction_kact_mw 