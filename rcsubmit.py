
import os
from glob import glob

class Cluster():
    def __init__(self, name, remote_dir=None):
        self._name = name
        if remote_dir is None:
            self._temp_remote_dir = True
            self._remote_dir = '~/blah_todo'
            self.ssh('mkdir {}'.format(self.remote_dir))
        else:
            self._temp_remote_dir = False
            self._remote_dir = remote_dir
    @property
    def name(self): return self._name
    @property
    def remote_dir(self): return self._remote_dir

    @property
    def ssh_cmd(self):
        return 'ssh {}'.format(self.name)
    
    def ssh(self, *cmds):
        return subprocess.check_output("{} '{}'".format(self.ssh_cmd, " && ".join(cmds),
                                       shell=True)
    
    def copy_files(self, files):
        return subprocess.check_output("scp {} {}:~/{}/".format(" ".join(files), self.name, self.remote_dir),
                                       shell=True)
        
    def start(self):
        pass
        
    def terminate(self):
        pass
        
class StarCluster(Cluster):
    @property
    def ssh_cmd(self):
        return 'ssh starcluster'
    def copy_files(self,files):
        for f in files:
            os.system("starcluster put {} {} {}".format(self.name,f,self.remote_dir))
    def start(self):
        import commands
        clusters = commands.getoutput("starcluster listinstances").split('>>> ')[1:]
        if self.name in clusters:
            self._did_start = False
        else:
            self._did_start = True
            os.system("starcluster start {}".format(self.name))
        
    def terminate(self):
        if self._did_start:
            os.system("starcluster terminate {}".format(self.name))
               

class Submission():
    def __init__(self, cluster, submit_cmd, submit_file=False, tag_wd='<<WD>>', 
        do_wait=True, *files):
        """
        Args:
            cluster (Cluster): Cluster that job should be submitted to.
            submit_cmd (str): Command that should be used to submit the job to 
                the cluster. (e.g. qsub for Moab Torque scheduler)
            submit_file (str): Job submission script.
            \*files (str): Optional files that should be copied over to the  
                cluster for the job.
            \*\*kwargs: Optional keyword arguments
        """

        
        self.cluster = cluster
        self.submit_cmd = submit_cmd
        self.local_files = [submit_file] if submit_file else []
        for f in files:
            self.local_files += glob(f)

        self.submit_file = os.path.basename(submit_file) if submit_file else ""
        self.tag_wd = tag_wd
        self.do_wait = do_wait
        
        self._status = 'Not Started'
        
    
        
    @property
    def cd_wd_cmd(self):
        return "cd {}".format(self.cluster.remote_dir)
        
    @property
    def replace_wd_cmd(self):
        return "sed '/s/{}/{}/g' ".format(self.tag_wd, self.cluster.remote_dir)
    def replace_wd(self):
        self.ssh(self.cd_wd_cmd, self.replace_wd_cmd)
    
    @property
    def submit_job_cmd(self):
        return "{} {}".format(self.submit_cmd, self.submit_file)
    def submit_job(self):
        self.ssh(self.cd_wd_cmd, self.submit_job_cmd)
        
    @property
    def status(self):
        return self._status
        
    @property
    def progress(self):
        if self._status == 'Not Started':
            return 0
        elif self._status == 'Running':
            return 0.5 # TODO: check status
        elif self._status == 'Complete':
            return 1
        else:
            return 0
        
    def retrieve_results(self):
        # TODO: do this
        pass
        
    def endrun(self):
        self.retrieve_results()
        self.cluster.terminate()
    
    def run(self):
        self.cluster.start()
        self._status = 'Running'
            
        self.server.copy_files(self.local_files)
        self.ssh(self.cd_wd_cm, self.replace_wd_cmd, self.submit_job_cmd)
          
    
       # wait for job to complete?
       if not self.do_wait:
           # return pickle???
           return
           
       while self.status != 'Complete':
           # TODO: logger with current status
           sleep(60)
           
       self.endrun()
       
    
s = Submission('recognized_server_name', 'qsub', 'PBSfilename', ['other', 'files', 'to', 'copy', 'including/*txt'])
s = Submission(StarCluster('mycluster'), 'qsub', 'job.pbs', 'script.py').run()
s = Submission(Cluster('estrella'), 'qsub', 'job.pbs', 'script.py').run()


# TODO: figure out what files to retrieve
# TODO: figure out how to get status from cluster (get pid when submitting and then run qstat)
# TODO: test pickle
