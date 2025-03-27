"""
Command execution module with safety checks
"""
import os
import shlex
import subprocess
from typing import List, Optional, Set, Tuple

class CommandExecutor:
    def __init__(self):
        """Initialize the command executor with safety settings"""
        # List of dangerous commands that should be blocked
        self.dangerous_commands: Set[str] = {
            "rm -rf /",
            "mkfs",
            "dd",
            ":(){:|:&};:",
            "chmod -R 777 /",
            "sudo rm -rf /",
            "sudo mkfs",
            "sudo dd",
            "sudo chmod -R 777 /",
        }
        
        # List of safe commands that are allowed
        self.safe_commands: Set[str] = {
            # File and directory operations
            "ls", "pwd", "cd", "echo", "cat", "grep", "find",
            "mkdir", "rm", "cp", "mv", "chmod", "chown",
            "test", "file", "stat", "touch", "ln", "lns",
            "tree", "basename", "dirname", "realpath", "readlink",
            
            # System information and monitoring
            "ps", "top", "htop", "df", "du", "free",
            "netstat", "ping", "traceroute", "dig", "nslookup",
            "ifconfig", "ip", "route", "systemctl", "service",
            "journalctl", "dmesg", "lsof", "fuser", "uptime",
            "uname", "hostname", "whoami", "who", "w", "last",
            "vmstat", "iostat", "sar", "mpstat", "pidstat",
            "smartctl", "sensors", "lshw", "lspci", "lsusb",
            "lsblk", "fdisk", "parted", "mount", "umount",
            
            # Process management
            "kill", "killall", "pkill", "nice", "renice", "nohup",
            "screen", "tmux", "bg", "fg", "jobs", "wait",
            "time", "timeout", "watch", "crontab",
            
            # Text processing and analysis
            "vim", "nano", "less", "more", "head", "tail",
            "sort", "uniq", "wc", "cut", "paste", "tr",
            "sed", "awk", "xargs", "tee", "split", "join",
            "comm", "diff", "patch", "jq", "yq", "xxd",
            "strings", "base64", "md5sum", "sha256sum",
            
            # Development tools
            "make", "gcc", "g++", "clang", "python3", "pip3",
            "nodejs", "npm", "yarn", "go", "rustc", "cargo",
            "java", "javac", "mvn", "gradle", "ruby", "gem",
            "perl", "php", "composer", "dotnet", "swift",
            "cmake", "ninja", "bazel", "meson", "autoconf",
            "automake", "pkg-config", "gdb", "lldb", "strace",
            "valgrind", "perf", "objdump", "nm", "ar",
            
            # Container and orchestration
            "docker", "docker-compose", "kubectl", "helm",
            "terraform", "aws", "gcloud", "az", "vagrant",
            "podman", "buildah", "skopeo", "k9s", "minikube",
            "kind", "k3s", "rancher", "istioctl", "argocd",
            
            # Version control
            "git", "svn", "hg", "fossil",
            
            # Network tools
            "curl", "wget", "tar", "gzip", "unzip", "ssh", "scp", "rsync",
            "nc", "telnet", "socat", "nmap", "tcpdump", "wireshark",
            "iptables", "ufw", "firewall-cmd", "openssl", "ssh-keygen",
            "sftp", "ftp", "whois", "host", "mtr", "ss", "ethtool",
            
            # Package management
            "apt", "apt-get", "dpkg", "yum", "dnf", "rpm",
            "pacman", "brew", "port", "snap", "flatpak",
            
            # Compression and archiving
            "zip", "unzip", "gzip", "gunzip", "bzip2", "bunzip2",
            "xz", "7z", "rar", "tar", "cpio", "ar",
            
            # File system tools
            "fsck", "tune2fs", "resize2fs", "xfs_repair",
            "btrfs", "zfs", "zpool", "lvdisplay", "vgdisplay",
            "pvdisplay", "blkid", "findmnt", "diskutil",
            
            # System maintenance
            "sync", "updatedb", "logrotate", "chroot",
            "ldconfig", "locale-gen", "update-alternatives",
            
            # User management
            "passwd", "chage", "groups", "id", "newgrp",
            "sudo", "su", "usermod", "groupmod", "chsh",
            
            # Documentation
            "man", "info", "help", "whatis", "apropos",
            
            # Miscellaneous utilities
            "date", "cal", "bc", "expr", "seq", "yes",
            "logger", "wall", "script", "expect", "at",
            "column", "fmt", "fold", "nl", "od", "pr",
            "rev", "shuf", "tsort", "unexpand", "units"
        }
        
        # Safe command arguments
        self.safe_args: Set[str] = {
            # File test operations
            "-x", "-r", "-w", "-f", "-d", "-L", "-e",
            # File permissions
            "-u", "-g", "-k", "-s",
            # Common options
            "-l", "-h", "-v", "-i", "-n", "-z", "-a", "-R",
            "--help", "--version", "--all", "--recursive",
            "--verbose", "--quiet", "--silent", "--force",
            # List options
            "-1", "-C", "-F", "-H", "-S", "-t", "-X",
            # Sort options
            "-b", "-c", "-M", "-r", "-u",
            # Display options
            "-p", "-q", "--color", "--no-color",
            # Time options
            "-t", "-T", "--time", "--date",
            # Size options
            "-s", "-S", "--size", "--block-size",
            # Format options
            "-o", "-O", "--format", "--output",
            # Filter options
            "-E", "-P", "-m", "--include", "--exclude",
            # Common git options
            "--staged", "--cached", "--merged", "--no-merged",
            # Network options
            "-4", "-6", "-w", "--ipv4", "--ipv6", "--wait"
        }

    def is_safe_command(self, command: str) -> Tuple[bool, str]:
        """
        Check if a command is safe to execute
        
        Args:
            command: The command to check
            
        Returns:
            Tuple[bool, str]: (True if safe, explanation if unsafe)
        """
        # Split command into parts
        parts = shlex.split(command)
        if not parts:
            return False, "Empty command"
            
        # Get the base command (first part)
        base_command = parts[0]
        
        # Check if it's a dangerous command
        if command in self.dangerous_commands:
            return False, f"Command '{command}' is in the dangerous commands list"
            
        # Check if it's a safe command
        if base_command not in self.safe_commands:
            return False, f"Command '{base_command}' is not in the safe commands list"
            
        # For test command, validate arguments
        if base_command == "test":
            for arg in parts[1:]:
                if arg.startswith("-") and arg not in self.safe_args:
                    return False, f"Unsafe argument '{arg}' for test command"
                    
        return True, "Command is safe"

    def execute(self, command: str) -> Optional[str]:
        """
        Execute a command safely
        
        Args:
            command: The command to execute
            
        Returns:
            Optional[str]: Command output if successful, None otherwise
            
        Raises:
            ValueError: If the command is not safe
        """
        is_safe, explanation = self.is_safe_command(command)
        if not is_safe:
            raise ValueError(explanation)
            
        try:
            # Execute command and capture output
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Return output if successful
            if result.returncode == 0:
                return result.stdout
            else:
                raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command '{command}' timed out")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command failed: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Error executing command: {str(e)}") 