f'''#!/bin/bash
#SBATCH --job-name={self.prefix}
#SBATCH --nodes=1
#SBATCH --ntasks={self.cpus}
#SBATCH --partition={self.partition}
#SBATCH --time={self.hours}:00:00
#SBATCH --output={self.prefix}.o%j
#SBATCH --error={self.prefix}.e%j
#SBATCH --mem={self.memory}G
#SBATCH --mail-type=FAIL,REQUEUE
#SBATCH --mail-user=ajs0201@auburn.edu

start=`date +%s`

mpirun -np {self.cpus} pw.x -nk {self.nk} < {self.input_dir}/{self.prefix}.i > {self.input_dir}/{self.prefix}.out

end=`date +%s`

runtime=$((end-start))
echo $runtime
echo "Finished"

'''