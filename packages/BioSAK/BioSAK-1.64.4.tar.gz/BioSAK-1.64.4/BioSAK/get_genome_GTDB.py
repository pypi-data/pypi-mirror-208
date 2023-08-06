import os
import argparse

get_genome_GTDB_parser_usage = '''
================================== get_genome_GTDB example commands ==================================

# Example commands
BioSAK get_genome_GTDB -id genome.txt -fastani_dir release214/fastani -out op_gnm_folder

# -dir: the folder which hold genome_paths.tsv
# genome paths: in the fastani folder from GTDB auxillary_files
# example of genome id file (one id per line):
GCA_902608175.1
GCA_903901015.1
GCF_000007225.1

=====================================================================================================
'''


def get_genome_GTDB(args):

    gnm_id_txt =            args['id']
    gtdb_ref_gnm_folder =   args['fastani_dir']
    op_gnm_folder =         args['out']

    gtdb_ref_gnm_path_txt = '%s/genome_paths.tsv'
    if os.path.isfile(gtdb_ref_gnm_path_txt) is False:
        print('genome_paths.tsv not found in %s, program exited!' % gtdb_ref_gnm_folder)
        exit()
    os.mkdir(op_gnm_folder)

    gnms_not_found_txt = '%s_genomes_not_in_GTDB.txt' % op_gnm_folder

    # read in gtdb_ref_gnm_path_txt
    ref_gnm_to_path_dict = {}
    for each_ref_gnm in open(gtdb_ref_gnm_path_txt):
        ref_gnm_split = each_ref_gnm.strip().split(' ')
        ref_accession = ref_gnm_split[0].split('_genomic')[0]
        pwd_ref_gnm = '%s/%s%s' % (gtdb_ref_gnm_folder, ref_gnm_split[1], ref_gnm_split[0])
        ref_gnm_to_path_dict[ref_accession] = pwd_ref_gnm

    gnm_not_in_gtdb_set = set()
    for each_gnm in open(gnm_id_txt):

        # get gnm_id
        if ' ' in each_gnm:
            gnm_id = each_gnm.strip().split(' ')[0]
        elif '\t' in each_gnm:
            gnm_id = each_gnm.strip().split('\t')[0]
        else:
            gnm_id = each_gnm.strip()

        if gnm_id in ref_gnm_to_path_dict:
            pwd_gnm = ref_gnm_to_path_dict[gnm_id]
            cmd_cp = 'cp %s %s/' % (pwd_gnm, op_gnm_folder)
            cmd_gunzip = 'gunzip %s/%s_genomic.fna.gz' % (op_gnm_folder, gnm_id)
            cmd_rename = 'mv %s/%s_genomic.fna %s/%s.fna' % (op_gnm_folder, gnm_id, op_gnm_folder, gnm_id)
            os.system(cmd_cp)
            os.system(cmd_gunzip)
            os.system(cmd_rename)
        else:
            gnm_not_in_gtdb_set.add(gnm_id)

    if len(gnm_not_in_gtdb_set) > 0:
        print('Genomes not found in GTDB: %s, see details in %s' % (len(gnm_not_in_gtdb_set), gnms_not_found_txt))
        gnms_not_found_txt_handle = open(gnms_not_found_txt, 'w')
        for each_unfound_gnm in gnm_not_in_gtdb_set:
            gnms_not_found_txt_handle.write('%s\n' % each_unfound_gnm)
        gnms_not_found_txt_handle.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-id',          required=True,  help='genome id')
    parser.add_argument('-fastani_dir', required=True,  help='the "fastani" dir')
    parser.add_argument('-out',         required=True,  help='output folder')
    args = vars(parser.parse_args())
    get_genome_GTDB(args)
