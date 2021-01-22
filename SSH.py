"""
Here goes all the processing and info retrieving via SSH
"""

from pssh.clients import SSHClient
import utils


class SSH:
    """
    This class contains all methods to retieve information from the remote system
    """

    conn = False
    client = None

    def __init__(self, ip, user, password):
        self.HOST = ip
        self.USER = user
        self.PASSWD = password

        self.last_idle = 0.0
        self.last_total = 0.0

        print(utils.get_time() + "\tConnecting to " + ip)
        try:
            self.client = SSHClient(self.HOST, self.USER, self.PASSWD, timeout=1, num_retries=2)
            print(utils.get_time() + "\tSession started")
            self.conn = True
        except Exception:
            print(utils.get_time() + "\tSession not stablisehd. Closing")
            exit(-1)

    def finalize_conn(self):
        """
        Finalizes the SSH connection
        """
        self.client.session.disconnect()
        print(utils.get_time() + "\tClosing session")

    def get_GPU_temp(self):
        """
        Obtains the GPU temperature via the vcgencmd measure_temp command
        """
        host_out = self.client.run_command("vcgencmd measure_temp")
        for line in host_out.stdout:
            return line[5:9]

    def get_CPU_temp(self):
        """
        Obtains the CPU temperature
        """

        host_out = self.client.run_command("cat /sys/class/thermal/thermal_zone0/temp")
        for line in host_out.stdout:
            return (int(line) / 1000).__round__(1)

    def get_CPU_percentage(self, line):
        """
        Calculates the usage of a CPU based on the /proc/stat content
        :param line: line from /proc/stat for the CORE
        :return: Usage percentage for the CORE
        """

        fields = [float(column) for column in line.strip().split()[1:]]
        idle, total = fields[3], sum(fields)
        idle_delta, total_delta = idle - self.last_idle, total - self.last_total
        self.last_idle = idle
        self.last_total = total
        usage = 100.0 * (1.0 - (idle_delta / total_delta))
        return usage.__round__(2)

    def get_CPU_use(self):
        """
        Obtains the CPU usage
        """
        output = []
        host_out = self.client.run_command("cat /proc/stat")

        contline = 0
        for line in host_out.stdout:
            if contline == 1:
                break

            output.append(self.get_CPU_percentage(line))

            contline += 1

        return output[0]

    def get_status(self):
        """
        Returns the status of the system, indicating if there are under voltage warnings or any other events
        The string is already reversed, so byte 0 in documentation is position 0 of the string (easier parsing)
        """
        host_out = self.client.run_command("vcgencmd get_throttled")

        for line in host_out.stdout:
            """
            Bit Hex value 	Meaning
            0 	1           Under-voltage detected
            1 	2 	        Arm frequency capped
            2 	4 	        Currently throttled
            3 	8 	        Soft temperature limit active
            16 	10000 	    Under-voltage has occurred
            17 	20000 	    Arm frequency capping has occurred
            18 	40000 	    Throttling has occurred
            19 	80000 	    Soft temperature limit has occurred
            """
            # Convert the hexadecimal value into binary (filling with 0 up to 20 positions if needed) and reverse it
            return bin(int(line[10:], 16))[2:].zfill(20)[::-1]

    def get_codecs(self):
        """
        Returns a list of the codecs and its status (enable for HW of disabled for SW processing)
        """
        output = []

        for codec in utils.CODECS:
            host_out = self.client.run_command("vcgencmd codec_enabled " + codec)

            for line in host_out.stdout:
                output.append(line)

        return output

    def get_kernel_info(self, arch=False):
        """
        Returns kernel name, release and processor architecture (optional)
        :param arch: flag to  get the architecture
        """
        if arch:
            command = "uname -smr"
        else:
            command = "uname -sr"

        host_out = self.client.run_command(command)

        for line in host_out.stdout:
            return line

    def get_hostname(self):
        """
        Returns hostname
        """
        host_out = self.client.run_command("hostname")

        for line in host_out.stdout:
            return line

    def get_RAM_usage(self):
        """
        Returns % of RAM usage
        """
        host_out = self.client.run_command("free -m")

        aux2 = []
        for line in host_out.stdout:
            if str.startswith(line, "Mem"):
                aux2 = line.split(" ")
                break

        aux = []
        for elem in aux2:
            if elem != "":
                aux.append(elem)
        # Used RAM is the sum of Used and Shared columns
        value = (int(aux[2]) + int(aux[4]))/int(aux[1])
        return str((value * 100).__round__(2)) + " %"

    def get_CPU_freq(self):
        """
        Returns current CPU frequency
        """
        host_out = self.client.run_command("vcgencmd measure_clock arm")

        for line in host_out.stdout:
            return str(int(int(line[14:]) / 1000000))

    def get_disk_usage(self):
        """
        Returns mounted disks usage (excluding tmpfs)
        """
        if utils.HUMAN_DISK_INFO:
            host_out = self.client.run_command("df -mh")
        else:
            host_out = self.client.run_command("df -m")

        aux2 = []
        cont = 0
        for line in host_out.stdout:
            if cont == 0:
                cont += 1
                continue
            if str.startswith(line, "tmpfs") or str.startswith(line, "devtmpfs"):
                continue
            else:
                aux2.append(line)

        aux = []
        for elem in aux2:
            aux3 = elem.split(" ")
            for item in aux3:
                if item != "":
                    aux.append(item)
        output = "Mount\tTotal\tUsed\tFree\t% Used\n"
        for cont in range(0, len(aux) - 1, 6):
            output += str(aux[cont + 5]) + "\t" + str(aux[cont + 1]) + "\t" + str(aux[cont + 2]) + "\t" + \
                      str(aux[cont + 3]) + "\t" + str(aux[cont + 4]) + "\n"

        return output

    def get_avg_load(self):
        """
        Returns avg CPU load for the last 1, 5 and 15 minutes
        """
        host_out = self.client.run_command("cat /proc/loadavg")

        aux2 = []
        for line in host_out.stdout:
            aux2 = line.split(" ")

        aux = []
        for elem in aux2:
            if elem != "":
                aux.append(elem)

        return aux

    def get_uptime(self):
        """
        Returns the uptime in human readable format
        1 day, 5 hours, 5 minutes
        """
        host_out = self.client.run_command("uptime -p")
        for line in host_out.stdout:
            return line[3:]

    def get_governors(self):
        """
        Returns a list of the available governors as well as the current one
        """
        host_out = self.client.run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors")
        out = []
        for line in host_out.stdout:
            out = line.split(" ")

        host_out = self.client.run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
        governor = ""
        for line in host_out.stdout:
            governor = line

        return out, governor

    def get_GPU_memory(self):
        """
        Returns memory reserved for the GPU
        """
        host_out = self.client.run_command("vcgencmd get_mem gpu")

        for line in host_out.stdout:
            return line.split("=")[1]
