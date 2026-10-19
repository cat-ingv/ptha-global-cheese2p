import sys
import subprocess
'''

python run_example01.py greens_functions_path

'''
gf_path = sys.argv[1]

# Run the called script with arguments
subprocess.run(['python', '../pygptha.py', 
				'--subd', 'kurilsjapan', 
				'--poi', 'DART-21401', 
				'--input_path', 'example01/input', 
				'--output_path', 'example01/output', 
				'--gf_path', gf_path, 
				'--oq', '--plot', '--save'])

