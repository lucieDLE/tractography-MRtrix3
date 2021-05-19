import os
import subprocess
import argparse
from postprocess_mask import *

def main(args):
	###
	# data prepocessing : GOOD
	###	

	file_name = args.file_name[0]
	name, extension = os.path.splitext(file_name)

	if extension == ".mif" :
		name=name.split('/')[-1]
	
	elif extension == ".nii" :
		name=name.split('/')[-1]

		if (args.bval is not None ) & (args.bvec is not None):
			bval=args.bval
			bvec=args.bvec

	elif (extension == ".raw") | (extension == ".nhdr") | (extension == ".nrrd"):

		name=name.split('/')[-1]
		nhdr_file = file_name
		file_name= os.path.join(args.out_folder, name+ ".nii")
		if os.path.isfile(file_name):
			bval=args.bval
			bvec=args.bvec
		else:
			command=["DWIConvert", "--outputDirectory", args.out_folder,
								   "--conversionMode NrrdToFSL", 
								   "--inputVolume", nhdr_file,
								   "-o", file_name]
			execute=subprocess.run(command)

			bval = os.path.join(args.out_folder, name+".bval")
			bvec = os.path.join(args.out_folder, name+".bvec")



	subject=name.split('-')[0]

	brain_mask = args.brain_mask
	fa_b3000 = args.fa
	wm_mask = args.wm_mask

	###
	# Compute white matter mask
	###

	if brain_mask is None :
		brain_mask=os.path.join(args.out_folder, subject + "_brain_mask.nii")
		command=["dwi2mask", file_name, brain_mask, "-fslgrad", bvec, bval]
		execute=subprocess.run(command)

	if fa_b3000 is None :

		fa_tensor=os.path.join(args.out_folder, subject + "_tensor_fa.nii")
		tensor_image=os.path.join(args.out_folder, subject + "_tensor_image_fa.nii")
		fa_b3000=os.path.join(args.out_folder, subject + "_fa_b3000.nii")

		command = [ "dwi2tensor", file_name, fa_tensor, 
					"-mask", brain_mask, 
					"-fslgrad", bvec,  bval]

		execute=subprocess.run(command)

		command = [ "tensor2metric", fa_tensor, "-fa", fa_b3000 ]
		execute=subprocess.run(command)

		wm_mask = post_process(fa_b3000, args.out_folder, 2)
	

	elif (fa_b3000 is not None) & (wm_mask is None) :
		wm_mask = post_process(fa_b3000, args.out_folder, 2)


	###
	# FOD images
	### 

	response=os.path.join(args.out_folder, subject + "_tournier.txt")
	fod=os.path.join(args.out_folder, subject + "_FOD.nii")
	

	command=["dwi2response", "tournier", file_name, response, "-fslgrad", bvec, bval ]
	execute=subprocess.run(command)

	command=["dwi2fod", "csd", file_name, response, fod,
							 "-mask", brain_mask,
							 "-fslgrad", bvec, bval,
							 ]

	execute=subprocess.run(command)

	###
	# Tractography and filtering
	### 	
	tractography=os.path.join(args.out_folder, subject + "_tractography.tck")
	
	command=["tckgen", "-algorithm", "iFOD2", fod, tractography,
							  "-seed_image", wm_mask,
							  "-mask", brain_mask,
							  "-maxlength", str(args.maxlength),
							  "-minlength", str(args.minlength),
							  "-cutoff", "0.08",
							  "-fslgrad", bvec, bval,
							  "-force"
							  ]

	execute=subprocess.run(command)



	###	
	# Extract_fibers
	### 

	out = args.out_tracts

	i = 1
	temp_file= os.path.join(out, subject+ "_0.tck")
	fiber= os.path.join(out, subject+ "_0.vtk")

	command=["tckedit", tractography, temp_file, "-number","1"]
	execute=subprocess.run(command)

	command=["tckconvert", temp_file, fiber, "-force"]
	execute=subprocess.run(command)

	command=["rm", "-f", temp_file]
	execute=subprocess.run(command)

	while i < args.number_fibers :
		index="_" + str(i)
		temp_file=os.path.join(out, subject+index+".tck")
		fiber=os.path.join(out, subject+ index+ ".vtk")

		command=["tckedit", tractography, temp_file, "-number", "1", "-skip", str(i), "-force"]
		execute=subprocess.run(command)

		command=["tckconvert", temp_file, fiber]
		execute=subprocess.run(command)

		command=["rm", "-f", temp_file]
		execute=subprocess.run(command)
		i+=1


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Apply tractography with iFOD2 method and extract all fibers', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

	input_params = parser.add_argument_group('Input parameters : DWI')
	input_params.add_argument('--file_name', nargs='+', type=str, help='mif, nii or nhdr and raw files')

	input_params.add_argument('--bval', type=str, help='input bval file')
	input_params.add_argument('--bvec', type=str, help='input bvec file')

	mask_params = parser.add_argument_group('Input parameters : Masks')
	mask_params.add_argument('--brain_mask', type=str, help='whole-brain mask')
	mask_params.add_argument('--wm_mask', type=str, help='white matter mask')
	mask_params.add_argument('--fa', type=str, help='fa image')

	tractography = parser.add_argument_group('Tractography parameters')
	tractography.add_argument('--maxlength', type=int, help='maximum length of track in mm', default=290)
	tractography.add_argument('--minlength', type=int, help='minimum length of track in mm', default=14)

	extraction = parser.add_argument_group('Extraction fibers')
	extraction.add_argument('--number_fibers', type=int, help='number of extracted fibers', default=5000)

	output_params = parser.add_argument_group('Output parameters')
	output_params.add_argument('--out_folder', type=str, help='Output directory for files tractography', default="./")
	output_params.add_argument('--out_tracts', type=str, help='output directory for extrated fibers', default=None)

	args = parser.parse_args()

	main(args)

