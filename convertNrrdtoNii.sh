#!/bin/sh

Help()
{
	echo
	echo "Convert nrrd to nii files for a directory"
	echo
	echo "options:"
	echo "-h, --help Print this Help."
	echo "--nrrd_dir directory containing nrrd files"
	echo "--nii_dir  directory containing nii files"
}



ConvertNrrdToNii()
{
	subjects_paths=$nrrd_dir"*.nhdr"
	for subject in $subjects_paths
	do
		file_name=`basename $subject | cut -f1 -d'.'`
		nii_file="${nii_dir}${file_name}.nii"
		if test -f "$nii_file"; then
			echo "$nii_file exists."
		else
			DWIConvert --outputDirectory $nii_dir --conversionMode NrrdToFSL --inputVolume $subject -o $nii_file
		fi
	done
}



###
# Main 
###


nrrd_dir=""
nii_dir=""
previous=""

for var in "$@"
do
	if [ "$var" == "-h" ] || [ "$var" == "--help" ]; then
		Help
		exit;
	fi

	if [ "$previous" == "--nrrd_dir" ]; then
		nrrd_dir=$var
	fi

	if [ "$previous" == "--nii_dir" ]; then
		nii_dir=$var
	fi
	previous=$var
done

ConvertNrrdToNii