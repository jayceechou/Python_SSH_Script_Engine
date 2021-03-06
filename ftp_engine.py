import sys;
import os;
import time;

from ssh_engine import SSH_Cmd;

class FTP_Engine:

	def __init__(self,user,passwd,port,host,is_remote=False,script_path=""):
		self.username = user;
		self.password = passwd;
		self.port = port;
		self.host = host;
		self.is_remote = is_remote;
		self.script_path = script_path;

		self.cmd_list = [];
		self.script_name = "ftp__script.txt";

	def clear_cmd(self):
		del self.cmd_list[:]; # empty the cmd list.

	# Remember your new lines where they're supposed to go.
	def add_cmd(self,cmd):
		self.cmd_list.append(cmd);
	
	def run_local_ftp(self):
		self.get_cmd_list(False);
		print "\nRunning Local FTP: "+self.script_path + self.script_name+"\n";
		os.system("cat "+self.script_path + self.script_name+" | ftp -n "+self.host);
		os.remove(self.script_path + self.script_name);

	def local_cmd_list(self):
		# setup the creds for the script.
		f = open(self.script_path + self.script_name,"w");
		f.write("open "+str(self.host)+" "+str(self.port)+"\n");
		f.write("quote user "+self.username+"\n");
		f.write("quote pass "+self.password+"\n");
		f.write("binary\n");
		for c in self.cmd_list:
			f.write(c); # That's right. It's up to the user to mark where the new lines go.

		# Close the FTP session.
		f.write("disconnect\n");
		f.write("quit\n");
		f.flush();
		# close the stream
		f.close();
		return None;
	
	def remote_cmd_list(self):
		result = [];
		# cat is cleaner.  old way was to use vim [it worked, but was nasty b/c of clearing the console]: "vim \""+self.script_path + self.script_name + "\"\n"
		result.append(SSH_Cmd("cat > \""+self.script_path + self.script_name + "\"\n",False,False)); # don't wait for prompt.
		result.append(SSH_Cmd("open "+str(self.host)+" "+str(self.port)+"\n",False,False));
		result.append(SSH_Cmd("quote user "+self.username+"\n",False,False));
		result.append(SSH_Cmd("quote pass "+self.password+"\n",False,False));
		result.append(SSH_Cmd("binary\n",False,False));
		for c in self.cmd_list:
			result.append(SSH_Cmd(c,False,False));
		result.append(SSH_Cmd("disconnect\n",False,False));
		result.append(SSH_Cmd("quit\n",False,False));
		result.append(SSH_Cmd("",True,False)); # exit cat, remember that this needs no-wait to be True.
		result.append("cat \"" + self.script_path + self.script_name +"\" | ftp -n\n");
		result.append(SSH_Cmd("rm -f "+ self.script_path + self.script_name +"\n",False,True));
		return result;

	def run_remote_ftp(self,ssh_engine):
		raw_cmd_list = self.remote_cmd_list();
		cmd_list = [];
		# reverse the order, so we can insert them in sequence to the same index (0).
		for c in raw_cmd_list:
			cmd_list.insert(0,c);
		for c in cmd_list:
			ssh_engine.insert_cmd(c,0);
		if(not ssh_engine.engine_active):
			ssh_engine.run_ssh();

	def get_cmd_list(self,is_remote=None):
		t_remote = self.is_remote;
		if(is_remote != None):
			t_remote = is_remote;
		if(t_remote):
			return self.remote_cmd_list();
		return self.local_cmd_list();
