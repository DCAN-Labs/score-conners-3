# Create a conda environment according to the requirements.txt file and activate that requirement.
export PYTHONPATH=$PYTHONPATH:./src

python ./src/main.py --input_file_name $1 --age $2 --sex $3 --reporter $4
