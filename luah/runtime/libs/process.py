import subprocess
import os
import sys
import signal
import threading
import queue as _queue


def yuriinject_process(yurilua, yurig):
    """
    Process management for Luah.
    Provides spawn, exec, kill, and pipe operations for external processes.
    """
    
    def yuriprocess_exec(yuricmd, yuriargs=None, yurishell=True, yuricwd=None, yurienv=None):
        """
        Execute a command and return stdout, stderr, and exit code.
        Args:
            cmd: Command to execute
            args: List of arguments (optional)
            shell: Run in shell (default true)
            cwd: Working directory (optional)
            env: Environment variables dict (optional)
        """
        yuricmd = str(yuricmd)
        
        # Build command
        if yuriargs and not yurishell:
            yurifullcmd = [yuricmd]
            for yuriarg in yuriargs.values():
                yurifullcmd.append(str(yuriarg))
        else:
            if yuriargs:
                yuriargstr = " ".join(str(a) for a in yuriargs.values())
                yurifullcmd = f"{yuricmd} {yuriargstr}"
            else:
                yurifullcmd = yuricmd
        
        # Prepare environment
        yurienvdict = None
        if yurienv:
            yurienvdict = dict(os.environ)
            for yurik, yuriv in yurienv.items():
                yurienvdict[str(yurik)] = str(yuriv)
        
        try:
            yuriresult = subprocess.run(
                yurifullcmd,
                shell=yurishell,
                cwd=yuricwd,
                env=yurienvdict,
                capture_output=True,
                text=True
            )
            
            return yurilua.table_from({
                "stdout":   yuriresult.stdout,
                "stderr":   yuriresult.stderr,
                "exitcode": yuriresult.returncode,
                "success":  yuriresult.returncode == 0,
            })
        except Exception as yuriex:
            return yurilua.table_from({
                "stdout":   "",
                "stderr":   str(yuriex),
                "exitcode": -1,
                "success":  False,
            })
    
    def yuriprocess_spawn(yuricmd, yuriargs=None, yurishell=True, yuricwd=None, yurienv=None):
        """
        Spawn a process without waiting for it to complete.
        Returns a process handle with pid.
        """
        yuricmd = str(yuricmd)
        
        # Build command
        if yuriargs and not yurishell:
            yurifullcmd = [yuricmd]
            for yuriarg in yuriargs.values():
                yurifullcmd.append(str(yuriarg))
        else:
            if yuriargs:
                yuriargstr = " ".join(str(a) for a in yuriargs.values())
                yurifullcmd = f"{yuricmd} {yuriargstr}"
            else:
                yurifullcmd = yuricmd
        
        # Prepare environment
        yurienvdict = None
        if yurienv:
            yurienvdict = dict(os.environ)
            for yurik, yuriv in yurienv.items():
                yurienvdict[str(yurik)] = str(yuriv)
        
        try:
            yuriproc = subprocess.Popen(
                yurifullcmd,
                shell=yurishell,
                cwd=yuricwd,
                env=yurienvdict,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            def yuriwait():
                yuriproc.wait()
                yuristdout, yuristderr = yuriproc.communicate()
                return yurilua.table_from({
                    "stdout":   yuristdout,
                    "stderr":   yuristderr,
                    "exitcode": yuriproc.returncode,
                    "success":  yuriproc.returncode == 0,
                })
            
            def yurikill():
                try:
                    yuriproc.kill()
                    return True
                except:
                    return False
            
            def yuriterminate():
                try:
                    yuriproc.terminate()
                    return True
                except:
                    return False
            
            def yuriisrunning():
                return yuriproc.poll() is None
            
            return yurilua.table_from({
                "pid":        yuriproc.pid,
                "wait":       yuriwait,
                "kill":       yurikill,
                "terminate":  yuriterminate,
                "isRunning":  yuriisrunning,
            })
        except Exception as yuriex:
            raise RuntimeError(f"Failed to spawn process: {yuriex}")
    
    def yuriprocess_pipe(yuricmds):
        """
        Pipe multiple commands together (Unix-style).
        Args:
            cmds: Array of commands to pipe
        Returns: stdout of final command
        """
        if not yuricmds:
            return ""
        
        yuriprocs = []
        yurilast_stdout = None
        
        try:
            for yuriiidx, yuricmd in enumerate(yuricmds.values(), 1):
                yuricmd = str(yuricmd)
                
                if yuriiidx == 1:
                    yuriproc = subprocess.Popen(
                        yuricmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                else:
                    yuriproc = subprocess.Popen(
                        yuricmd,
                        shell=True,
                        stdin=yurilast_stdout,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                
                yuriprocs.append(yuriproc)
                yurilast_stdout = yuriproc.stdout
            
            # Get final output
            yurifinal_stdout, yurifinal_stderr = yuriprocs[-1].communicate()
            
            return yurilua.table_from({
                "stdout":   yurifinal_stdout,
                "stderr":   yurifinal_stderr,
                "exitcode": yuriprocs[-1].returncode,
                "success":  yuriprocs[-1].returncode == 0,
            })
        except Exception as yuriex:
            return yurilua.table_from({
                "stdout":   "",
                "stderr":   str(yuriex),
                "exitcode": -1,
                "success":  False,
            })
    
    def yuriprocess_getpid():
        """Get current process ID"""
        return os.getpid()
    
    def yuriprocess_getppid():
        """Get parent process ID"""
        return os.getppid()
    
    def yuriprocess_exit(yuricode=0):
        """Exit the current process"""
        sys.exit(int(yuricode))
    
    def yuriprocess_kill_pid(yuripid, yurisignal=None):
        """
        Kill a process by PID.
        Args:
            pid: Process ID
            signal: Signal name (optional, default SIGTERM)
        """
        yuripid = int(yuripid)
        
        if yurisignal:
            yurisigname = str(yurisignal).upper()
            if not yurisigname.startswith("SIG"):
                yurisigname = "SIG" + yurisigname
            yurisignum = getattr(signal, yurisigname, signal.SIGTERM)
        else:
            yurisignum = signal.SIGTERM
        
        try:
            os.kill(yuripid, yurisignum)
            return True
        except:
            return False
    
    def yuriprocess_getcwd():
        """Get current working directory"""
        return os.getcwd()
    
    def yuriprocess_chdir(yuripath):
        """Change current working directory"""
        yuripath = str(yuripath)
        try:
            os.chdir(yuripath)
            return True
        except:
            return False
    
    # Inject process namespace
    yurig.process = yurilua.table_from({
        "exec":     yuriprocess_exec,
        "spawn":    yuriprocess_spawn,
        "pipe":     yuriprocess_pipe,
        "getPid":   yuriprocess_getpid,
        "getParentPid": yuriprocess_getppid,
        "exit":     yuriprocess_exit,
        "kill":     yuriprocess_kill_pid,
        "getCwd":   yuriprocess_getcwd,
        "chdir":    yuriprocess_chdir,
    })
