#!/usr/bin/env python3
import os
import glob
import argparse
import subprocess
import sys
import nibabel as ni
import re

from iFOD2 import *
from scaling import *
from postprocess import *

def main(args):
	###
	# paths folders
	###	
	DATA_DIR="/app/"

	us_famli_dir=os.path.join(DATA_DIR, "US-famli/")
	fly_by_dir=os.path.join(DATA_DIR, "fly-by-cnn/")

	outlier_dir=os.path.join(DATA_DIR, "msma/")

	predict_v2=os.path.join(us_famli_dir, "src/py/dl/predict_v2.py")
	flyby_script=os.path.join(fly_by_dir, "src/py/fly_by_features.py")
	
	# tractography_script=os.path.join(tractography_dir, "iFOD2.py" )
	# predict_ocsvm=os.path.join(outlier_dir, "predict_multiple_classes.py" )
	# predict_score==os.path.join(outlier_dir, "evaluation.py" )   # ??? are train and predict in the same file ? maybe have to change something

	###
	# Create architecture
	###	

	dir_subject=os.path.normpath(args.out)
	subject_id = os.path.split(dir_subject)[1]

	dir_tractography=os.path.join(dir_subject, "tractography")
	dir_tracts=os.path.join(dir_tractography, "tracts")
	dir_fibers=os.path.join(dir_subject, "fibers")
	dir_features=os.path.join(dir_subject, "features")

	command = [ "mkdir", dir_tractography, dir_tracts, dir_fibers, dir_features ]
	# execute=subprocess.run(command)

	###
	# MRTRIX Tractography
	###
	if len(args.input) > 1 :
		input_files = args.input[0] + " " +args.input[1]
	else :
		input_files = args.input[0]

	command = [ "python3", "iFOD2.py",
				"--file_name", input_files,
				"--bval", args.bval, 
				"--bvec", args.bvec,
				"--brain_mask", args.brain_mask,
				"--wm_mask", args.wm_mask,
				"--fa", args.fa,
				"--out_folder", dir_tractography, 
				"--out_tracts", dir_tracts ]
	# print(command)
	# execute=subprocess.run(command)

	###
	# Fly-by-features 
	###	

	command=[ "python3", "scaling.py", "--nii", args.input[0] ]
	proc = execute=subprocess.run(command, stdout=subprocess.PIPE)

	out=proc.stdout
	decode=out.decode("utf-8")
	list_split= re.split(' |\[|\]|\n', decode)
	values=[]
	for elt in list_split:
		if (elt != ''):
			values.append(float(elt))
	
	command=[ "python3", flyby_script, 
				  "--dir", dir_tracts, 
				  "--out", dir_fibers, 
				  "--subject", subject_id,
				  "--spiral", str(args.sample),
				  "--scaling", str(values[0]),
				  "--translate", str(values[1]), str(values[2]), str(values[3]),
				  "--shape", str(int(values[4])), str(int(values[5])), str(int(values[6])),
				  "--fiber", "1" ]

	# execute=subprocess.run(command)


	###
	# VGG19 - Extract features 
	###	

	command = [ "python3", predict_v2, 
				"--dir", dir_fibers, 
				"--image_dimension", "3", 
				"--pixel_dimension", "3", 
				"--batch_prediction", "1", 
				"--model", args.vgg_model, 
				"--out", dir_features ]
	# print(command)
	# execute=subprocess.run(command)

	###
	# Classifier - predict label 
	###	

	prediction_file=os.path.join(dir_subject, "prediction.csv")

	command = [ "python3", predict_v2, 
				"--dir", dir_features, 
				"--image_dimension", "1", 
				"--pixel_dimension", "-1",  
				"--model", args.classifier_model, 
				"--prediction_type", "class",
				"--out", prediction_file ]
	# print(command)
	# execute=subprocess.run(command)

	###
	# Outlier detection - predict score 
	###	
	# prediction_file='/opt/lumargot/spiral_64/MRTRIX/102311/prediction.csv'
	# command = [ "python3", predict_ocsvm, 
	# 			"--folder_model", args.msma_checkpoint, 
	# 			"--json", args.json, 
	# 			"--csv", prediction_file,  
	# 			"--analysis", dir_subject]

	# print(command)
	execute=subprocess.run(command)

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

	in_group = parser.add_argument_group('Input parameters')
	in_group.add_argument('--input', nargs='+', help='mif, nii or nhdr and raw files', type=str)
	
	# option
	in_group.add_argument('--bvec', help='input bvec file', type=str, default='None')
	in_group.add_argument('--bval', help='input bval file', type=str, default='None')
	in_group.add_argument('--brain_mask', type=str, help='whole-brain mask', default='None')
	in_group.add_argument('--wm_mask', type=str, help='white matter mask', default='None')
	in_group.add_argument('--fa', type=str, help='fa image', default='None')

	flyby_group = parser.add_argument_group('Fly-by-cnn parameters')
	flyby_group.add_argument('--sample', help='Number of samples along the spherical spiral', type=str, default=64)


	nn_group = parser.add_argument_group('Neural Networks parameters')
	nn_group.add_argument('--vgg_model', help='', required=True, type=str)
	nn_group.add_argument('--classifier_model', help='', required=True, type=str)
	nn_group.add_argument('--msma_checkpoint', help='Dirname containing checkpoint of the model', required=True)
	# nn_group.add_argument('--json', help='json file with the description of the input, generate with tfRecords.py from US-famli', default='None')
	
	out_group = parser.add_argument_group('Output')
	out_group.add_argument('--out', help='Output dirname for the subject files generated', required=True)
	

	args = parser.parse_args()

	main(args)