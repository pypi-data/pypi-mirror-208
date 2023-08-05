f'''

#PBS -N {self.prefix}
#PBS -l mem={self.memory}gb,nodes=1:ppn={self.cpus},walltime={self.hours}:00:00
#PBS -q {self.partition}

start=`date +%s`

mpirun -np {self.cpus} pw.x -nk {self.nk} < {self.input_dir}/{self.prefix}.i > {self.input_dir}/{self.prefix}.out

end=`date +%s`

runtime=$((end-start))
echo $runtime
echo "Finished"

'''