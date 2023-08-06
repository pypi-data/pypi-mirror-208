#!/usr/bin/env python3

"""
Name: genome_annotator.py
Author: Xiaoyu Yu
Date: 01 June 2022
Description: Annotate genomes based on closest reference sequence annotation. 

Options:
    :param raw_fasta: Raw sequences with reference in name tag in fasta format (Required)
    :param reference_sequence: Annotated reference sequences in json format (Required)
    :param annotated_json: Output list of sequences annotated in json format (Default: referenced.json)

This file is part of PANGEA HIV project (www.pangea-hiv.org).
Copyright 2021 Xiaoyu Yu (xiaoyu.yu@ed.ac.uk).
"""

import json
import sys
import parasail
import re
from Bio import SeqIO
from Bio.Seq import Seq
import datetime as dt
from genofunc.utils import *


def extract_int(base_pos,input_string):
    temp_string = ""
    for j in input_string[base_pos:]:
        if j.isdigit():
            temp_string += j
        else:
            break
    return int(temp_string)
def createCigarDic(cigar):
    base_position = 1
    cigar_pos = 0
    cigar_dic = {}
    cigar_dic["deletion"] = []
    cigar_dic["insertion"] = []
    while cigar_pos < len(cigar):
        matching_move = extract_int(cigar_pos,cigar)
        cigar_pos += len(str(matching_move))
        if cigar[cigar_pos] in ["=","X"]:
            base_position += matching_move                
        elif cigar[cigar_pos] == "D":
            cigar_dic["deletion"].append([base_position,matching_move])
            base_position += matching_move                
        elif cigar[cigar_pos] == "I":
            cigar_dic["insertion"].append([base_position,matching_move])
            base_position += matching_move                
        else:
            print("Invalid Cigar Operator: " + cigar[cigar_pos])
        cigar_pos += 1
    return cigar_dic
def countmatch(cigar):
    cigar_pos = 0
    match_counter = 0
    while cigar_pos < len(cigar):
        matching_move = extract_int(cigar_pos,cigar)
        cigar_pos += len(str(matching_move))
        if cigar[cigar_pos] in ["="]:
            match_counter += matching_move
        cigar_pos += 1
    return match_counter



time_start = dt.datetime.now()
location_dic = {}
query_dic = {}
sequence_dic = {}
features = []
raw_fasta = "ref_test/referenced_sequence_1250_2.fasta"
reference_sequence = "ref_test/hiv_reference_1250.json"
annotated_json = "ref_test/annotated_1250.json"
stats = open("ref_test/stats_1250.csv","w")
log_file = open("ref_test/annotator.log","w")

user_matrix = parasail.matrix_create("ACGTRY?", 5, -4)
user_matrix[0,2] = -1   #A-G
user_matrix[0,4] = 0    #A-R
user_matrix[0,6] = 0    #A-?
user_matrix[1,3] = -1   #C-T
user_matrix[1,5] = 0    #C-Y
user_matrix[1,6] = 0    #C-?
user_matrix[2,0] = -1   #G-A
user_matrix[2,4] = 0    #G-R
user_matrix[2,6] = 0    #G-?
user_matrix[3,1] = -1   #T-C
user_matrix[3,5] = 0    #T-Y
user_matrix[3,6] = 0    #T-?
user_matrix[4,0] = 0    #R-A
user_matrix[4,2] = 0    #R-G
user_matrix[4,6] = 0    #R-?
user_matrix[5,1] = 0    #Y-C
user_matrix[5,3] = 0    #Y-T
user_matrix[5,6] = 0    #Y-?
user_matrix[6,0] = 0    #?-A
user_matrix[6,1] = 0    #?-C
user_matrix[6,2] = 0    #?-G
user_matrix[6,3] = 0    #?-T
user_matrix[6,4] = 0    #?-R
user_matrix[6,5] = 0    #?-Y
user_matrix[6,5] = 0    #?-N
user_matrix[6,6] = 0    #?-?


with open(reference_sequence,"r") as f:
    reference_data = json.load(f)

for k,v in reference_data.items():
    for i in v:
        sequence_dic[i["accession"]] = i["sequence"]
        location_dic[i["accession"]] = {}
        location_dic[i["accession"]]["sequence"] = i["sequence"]
        for genes in i["locations"]["location"]:
            temp_list = []
            if genes["featureId"] not in features:
                features.append(genes["featureId"])
            if isinstance(genes["fragment"], list):
                for j in genes["fragment"]:
                    temp_list.append(j["from"])
                    temp_list.append(j["to"])
            else:
                for k,v in genes["fragment"].items():
                    temp_list.append(v)
            location_dic[i["accession"]][genes["featureId"]] = "|".join(temp_list)

for record in SeqIO.parse(raw_fasta, "fasta"):
    temp_list = record.id.split("|")
    id = temp_list[0]
    if record.id.find(".") > -1:
        reference_strain = record.id.split(".")[-1]
    else:
        reference_strain = temp_list[-1]
    cigarResults = parasail.sg_trace_striped_32(str(sequence_dic[reference_strain]), str(record.seq.upper().replace("?","N")), 10, 1, user_matrix)
    query_dic[id] = {}
    query_dic[id]["sequence"] = cigarResults.traceback.ref
    query_cigar_dic = createCigarDic(cigarResults.cigar.decode.decode('ascii'))
    for genes in features:
        query_coordinates = []
        if genes not in location_dic[reference_strain].keys():
            print(record.id + " does not contain " + genes + " region.\n")
            continue
        else:
            ref_coordinates = location_dic[reference_strain][genes].split("|")
            for i in range(len(ref_coordinates)):
                counter = 0
                gene_coordinate = int(ref_coordinates[i])
                for j in query_cigar_dic["deletion"]:
                    deletion_base = int(j[0])
                    if deletion_base <= gene_coordinate:
                        counter += int(j[1])
                    else:
                        break
                query_coordinates.append(str(gene_coordinate + counter))
            query_dic[id][genes] = "|".join(query_coordinates)

            for i in range(0,len(query_coordinates),2):
                query_seq = query_dic[id]["sequence"][int(query_coordinates[i]):int(query_coordinates[i+1])].replace("-","")
                query_gene = Seq(query_seq)
                query_prot = query_gene.translate()
                ref_gene = Seq(sequence_dic[reference_strain][int(ref_coordinates[i]):int(ref_coordinates[i+1])])
                ref_prot = ref_gene.translate()
                #prot_cigarResults = parasail.sg_trace(str(ref_prot), str(query_prot), 10, 1, parasail.blosum62)
                prot_cigarResults = parasail.sg_trace(str(ref_gene), str(query_gene), 10, 1, user_matrix)
                gene_out = prot_cigarResults.traceback.ref
                match_count = countmatch(prot_cigarResults.cigar.decode.decode('ascii'))
                log_file.write("Query sequence: " + id + "\n")
                log_file.write("Ref sequence: " + reference_strain + "\n") 
                log_file.write("genes: " + genes + "\n")
                log_file.write("query coordinates: " + "|".join(query_coordinates) + "\n")
                log_file.write("ref coordinates: " + "|".join(ref_coordinates) + "\n")
                log_file.write("query gene DNA: " + str(query_gene) + "\n")
                log_file.write("ref gene DNA: " + str(ref_gene) + "\n")
                #log_file.write("query gene Protein: " + str(query_prot) + "\n")
                #log_file.write("ref gene Protein: " + str(ref_prot) + "\n")
                #log_file.write("Protein Alignment Length: " + str(len(gene_out)) + "\n")
                log_file.write("DNA Alignment Length: " + str(len(gene_out)) + "\n")
                log_file.write("Number of Matches: " + str(match_count) + "\n")
                match_ratio = float(match_count)/len(gene_out)
                log_file.write("\n")
                stats.write(",".join([genes,str(match_ratio)])+"\n")
    log_file.write("\n")

with open(annotated_json, 'w') as f:
    json_dumps_str = json.dumps(query_dic, indent=4)
    print(json_dumps_str, file=f)

log_file.close()
time_ran = dt.datetime.now() - time_start
print("Time Lapse:", time_ran.total_seconds() / 60, "Minutes")
