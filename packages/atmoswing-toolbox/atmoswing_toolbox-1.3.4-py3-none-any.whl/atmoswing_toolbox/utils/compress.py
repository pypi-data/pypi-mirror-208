import glob
import gzip
import os
import shutil
import zipfile


def compress_optimization_outputs(base_path):
    def pack_file(f):
        with open(f, 'rb') as f_in:
            with gzip.open(f + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(f)
        print(f + ' compressed')

    for x in os.listdir(base_path):
        path = os.path.join(base_path, x, 'results')
        final = glob.glob(path + '/*best_individual.txt')
        if len(final) > 0:
            # If optimization ended, compress all files.
            files_generations = glob.glob(path + '/*generations.txt')
            files_operators = glob.glob(path + '/*operators.txt')
            for file in files_generations:
                pack_file(file)
            for file in files_operators:
                pack_file(file)
        else:
            # If not, compress all files but the last.
            files_generations = glob.glob(path + '/*generations.txt')
            files_generations.sort()
            files_operators = glob.glob(path + '/*operators.txt')
            files_operators.sort()
            for file in files_generations[:-1]:
                pack_file(file)
            for file in files_operators[:-1]:
                pack_file(file)


def compress_log_files(base_path):
    for x in os.listdir(base_path):
        path = os.path.join(base_path, x)
        print(path)
        log_file = glob.glob(path + '/AtmoSwingOptimizer*.log')
        if len(log_file) > 0:
            zip_obj = zipfile.ZipFile(path + '/log.zip', 'w', zipfile.ZIP_DEFLATED)
            for f in log_file:
                file_name = f.replace(path, '')
                file_name = file_name[1:]
                zip_obj.write(f, file_name)
                os.remove(f)
                print(file_name + ' compressed')
            zip_obj.close()
        else:
            print("No log file found.")
