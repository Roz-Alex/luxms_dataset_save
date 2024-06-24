from typing import Any

import paramiko
import argparse
import re
import os


class Ds:

    def __init__(self):
        self.config = {
            'host': 'vr116.luxms.com',
            'port': 23144,
            'user': 'admin',
            'password': 'E5oHaTfmEXnakKZU'
        }
        self.ds = ''
        self.mode = ''
        self._path = ''

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:

        """
        creates parser of arguments from command line

        :return: parser
        """

        parser = argparse.ArgumentParser(
            prog='ds_save.py',
            description='Luxms BI Dataset saver. Saves specified dataset with all info from specified stand',
            epilog='Developed by Alex_R'
        )
        parser.add_argument(
            'ds_name',
            nargs='?',
            help='''name of dataset to dump. Is required'''
        )
        parser.add_argument(
            '-m', '--mode',
            default='save',
            choices=['save', 'restore'],
            required=False,
            nargs='?',
            help='''optional argument that sets basic program usage.
                        Can be save (default) or restore
                        If save - program makes a dump of specified dataset with additional meta info
                        If restore - program restores dataset from dump
                        '''
        )
        parser.add_argument(
            '-u', '--user',
            nargs='?',
            required=False,
            help='''
                    optional argument that specifies username for ssh connection.
                    is required if host and port are used
                    '''
        )
        parser.add_argument(
            '-H', '--host',
            nargs='?',
            required=False,
            help='''
                        optional argument that specifies host for ssh connection.
                        is required if user or port are used
                        '''
        )
        parser.add_argument(
            '-p', '--port',
            nargs='?',
            required=False,
            help='''
                        optional argument that specifies port for ssh connection.
                        is required if user or host are used
                        '''
        )

        parser.add_argument(
            '-P', '--path',
            nargs='?',
            required=False,
            help='''
                    optional argument that specifies local path where files will be saved
                    is required if user or host are used
                    '''
        )

        return parser

    def _parse_args(self) -> dict[str, Any]:

        """
        parsing of mode and path parameters

        :return: args - dict of arguments
        """

        parser = self.create_parser()
        # print('a', '\n')
        args = vars(parser.parse_args())
        self.mode = args['mode']
        if args['mode']:
            self._path = args['mode']

        return args

    def _main(self):

        _args = self._parse_args()

        if _args['mode'] == 'save':
            DsSave(_args)
        else:
            DsRestore(_args)


class DsSave(Ds):

    def __init__(self, args):

        super().__init__()

        self.files_list = []

        self.main(args)

    @staticmethod
    def _is_def_host(_ars):

        """
        checks whether ssh info is specified or not

        :param: _ars - Namespace of args
        :return: bool
        """

        if _ars['user'] is not None and _ars['host'] is not None and _ars['port'] is not None:
            flag = True
        elif _ars['user'] is None and _ars['host'] is None and _ars['port'] is None:
            flag = False
        else:
            raise Exception(
                'You should specify all three args (-H, -p, -u) or none of them. for more information use -h')

        return flag

    def parse_args(self, _args):

        """
        parsing of arguments came from
        command (host, port, user, pass)

        :example:
        python ds_save.py ds_11
        python ds_save.py ds_11 -m save -h dev-arozanov.luxms.com -p 22 -u arozanov

        :param _args: list of arguments
        :return:
        """
        if self._is_def_host(_args):
            self.config['host'] = _args['host']
            self.config['port'] = _args['port']
            self.config['user'] = _args['user']
            self.config['password'] = input('enter the ssh password please:')

        if _args['ds_name'] is None:
            raise Exception('positional parameter ds_name must be specified, use -h for help')
        else:
            self.ds = _args['ds_name']
        # print(_args, self.ds)

    def dump_ds(self):

        """
        run pg_dump command on host
        through ssh tunnel

        :return:
        """

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(self.config['host'], port=self.config['port'], username=self.config['user'],
                        password=self.config['password'], timeout=3)

            stdin, stdout, stderr = ssh.exec_command(
                f'pg_dump --column-inserts -U bi -d mi --schema {self.ds} > auto_{self.ds}.dmp')
            stdin.write('bi\n')
            stdin.flush()

            err = stderr.read().decode()

            if err != 'Password: \n':
                raise Exception('Inner SSH Exception: ' + re.sub('Password: \n', '', err))

            ssh.close()

            self.files_list.append(f'auto_{self.ds}.dmp')

        except Exception as error:
            raise Exception(error)
        pass

    # todo: need to scp all auto files from files_list
    def scp_files(self):

        """
        copying dump from host to local through ssh tunel
        :return:
        """

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.config['host'], port=self.config['port'], username=self.config['user'],
                        password=self.config['password'], timeout=3)
            stdin, stdout, stderr = ssh.exec_command("ls")

            # print('stddin', stdout.readlines())

            sftp = ssh.open_sftp()

            if not self._path:
                # self._path = self.get_local_path()
                self._path = '/Users/alexr/Documents/work/sandbox_dumps' #just for work

            # todo: add function for directory making

            for fil in self.files_list:
                sftp.get(f'/home/{self.config["user"]}/{fil}', f'{self._path}/{fil}')

            sftp.close()
            ssh.close()
        except Exception as error:
            raise Exception(error)
        pass

    def remove_dump(self):

        """
        removing .dmp file from host through ssh
        :return:
        """

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh.connect(self.config['host'], port=self.config['port'], username=self.config['user'],
                        password=self.config['password'], timeout=3)

            stdin, stdout, stderr = ssh.exec_command(f"rm ~/auto1.dmp")

            stdout.channel.set_combine_stderr(True)
            # print(stdout.read().decode())

        except Exception as error:
            raise Exception(error)

    def get_file_names(self) -> list[str]:

        """

        :return:
        """

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(self.config['host'], port=self.config['port'], username=self.config['user'],
                    password=self.config['password'], timeout=3)

        stdin, stdout, stderr = ssh.exec_command(
            f"psql -U bi mi --csv -c 'COPY(select substring(sql_query, 7, 13) from {self.ds}._cubes) TO STDOUT'")
        stdin.write('bi\n')
        stdin.flush()
        stdout.channel.set_combine_stderr(True)

        table_name = stdout.readlines()[1:]

        ssh.close()
        # print('tbl name', table_name)
        return table_name

    def dump_excels(self, tables: list[str]):

        """

        :param tables: list with names of uploaded excel files
        :return:
        """

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        for i, tbl in enumerate(tables):

            tb_nm = re.search('"(.+?)"', tbl.strip()).group()[1:-1]

            # print('tb_nm', tb_nm)

            try:
                ssh.connect(self.config['host'], port=self.config['port'], username=self.config['user'],
                            password=self.config['password'], timeout=3)

                stdin, stdout, stderr = ssh.exec_command(
                    f'pg_dump --column-inserts -U bi -d mi --table xdds.{tb_nm} > auto_ist_{i}.dmp')
                stdin.write('bi\n')
                stdin.flush()

                err = stderr.read().decode()

                if err != 'Password: \n':
                    raise Exception('Inner SSH Exception: ' + re.sub('Password: \n', '', err))

                if f"auto_ist_{i}.dmp" not in self.files_list:
                    self.files_list.append(f"auto_ist_{i}.dmp")

                ssh.close()

            except Exception as error:
                raise Exception(error)
        pass

    def get_adm_insert(self):

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh.connect(self.config['host'], port=self.config['port'], username=self.config['user'],
                        password=self.config['password'], timeout=3)

            st = f"psql -U bi mi -c 'COPY(SELECT * from adm.datasets WHERE schema_name = $${self.ds}$$) to STDOUT csv'"

            stdin, stdout, stderr = ssh.exec_command(st)
            stdin.write('bi\n')
            stdin.flush()
            stdout.channel.set_combine_stderr(True)

            dss_line = stdout.readlines()[-1]

            ssh.close()

            _insert = self.parse_csv_out(dss_line.strip())

            local_path = self.get_local_path()

            try:
                f = open(f"{local_path}/ins.sql", 'x')
                f.close()
            except FileExistsError:
                pass

            with open(f"{local_path}/ins.sql", 'w') as file:
                file.write(_insert)

            # self.files_list.append("ins.sql")

        except Exception as error:
            raise error

    @staticmethod
    def parse_csv_out(st: str) -> str:

        """

        :param st:
        :return:
        """

        st_list = st.split(',')

        # print(st_list, '\n')

        new_st_list = []

        for ss in st_list:
            if ss.isdigit():
                new_st_list.append(ss)
            elif ss == '""':
                new_st_list.append('\'\'')
            elif ss == '':
                new_st_list.append('NULL')
            elif ss == '{}' or ss == '[]':
                new_st_list.append(f'\'{ss}\'::json')
            else:
                new_st_list.append(f'\'{ss}\'')

        out_st = "INSERT INTO adm.datasets VALUES(" + ','.join(new_st_list) + ");"
        # print(out_st)

        return out_st

    def add_info(self):

        file_names = self.get_file_names()
        self.dump_excels(file_names)
        self.get_adm_insert()

    @staticmethod
    def get_local_path() -> str:

        stream = os.popen('pwd')
        output = stream.read()

        return output.strip()

    def main(self, args):
        # todo: Maybe add handlers for exceptions, not just raising them into stderr
        # todo: Add verbose argument

        self.parse_args(args)
        tbls = self.get_file_names()
        self.dump_excels(tbls)
        self.dump_ds()
        self.add_info()
        print('\n------\n', self.files_list, '\n------\n')
        self.scp_files()

    # TO BE DONE
    def add_known_host(self):
        """
        todo: consider making list of known hosts, so that -h can be not ssh host, but name from known hosts
        :return:
        """
        pass

class DsRestore(Ds):
    # todo: write class for restoring
    def __init__(self, args):
        super().__init__(args)

        self.main(args)


if __name__ == "__main__":
    d = Ds()
    d._main()

    '''
    puthon ds_save.py ds_11 [ -m --mode <save/restore>
                                -u --user user, 
                                -h --host host, 
                                -p --port
    Если не указаны юзер, хост, порт, то используем дефолт - sandbox. 
    '''
