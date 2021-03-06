# import os, read_data, json, subprocess
import os, json, subprocess, time, datetime, queue, threading, smtplib
# from multiprocessing.dummy import Pool as ThreadPool
from email.mime.text import MIMEText

class runKlusta():

    def __init__(self):
        super(runKlusta, self).__init__()

    def klusta(self, expt, directory):
        cur_date = datetime.datetime.now().date()
        cur_time = datetime.datetime.now().time()
        folder_msg = ': Now analyzing files in the "' + expt + '" folder!'
        print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + folder_msg)

        dir_new = os.path.join(directory, expt)  # makes a new directory

        log_f_dir = os.path.join(dir_new, 'LogFiles')
        ini_f_dir = os.path.join(dir_new, 'IniFiles')

        proc_f_dir = os.path.join(directory, 'Processed')

        if not os.path.exists(proc_f_dir):
            os.makedirs(proc_f_dir)

        if not os.path.exists(log_f_dir):
            os.makedirs(log_f_dir)

        if not os.path.exists(ini_f_dir):
            os.makedirs(ini_f_dir)

        self.settings_fname = 'settings.json'

        with open(self.settings_fname, 'r+') as filename:
            self.settings = json.load(filename)

        f_list = os.listdir(dir_new)  # finds the files within that directory

        set_files = [file for file in f_list if '.set' in file]
        cur_date = datetime.datetime.now().date()
        cur_time = datetime.datetime.now().time()
        if len(set_files) > 1:
            set_msg = 'There are ' + str(len(set_files)) + " '.set' files in this directory"
        else:
            set_msg = 'There is ' + str(len(set_files)) + " '.set' file in this directory"
        print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']: ' + set_msg)

        skipped = 0
        experimenter = []
        error = []
        for i in range(len(set_files)):
            set_file = set_files[i][:-3]
            set_path = os.path.join(dir_new, set_file[:-1])
            cur_date = datetime.datetime.now().date()
            cur_time = datetime.datetime.now().time()
            cur_set_msg = 'Now analyzing tetrodes associated with the  ' + str(set_file[:-1]) + \
                          " '.set' file " + "(" + str(i+1) + "/" + str(len(set_files)) + ")."
            print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']: ' + cur_set_msg)

            tet_list = [file for file in f_list if file in ['%s%d' % (set_file, i)
                                                            for i in range(1, int(self.settings['NumTet']) + 1)]]

            if tet_list == []:
                cur_date = datetime.datetime.now().date()
                cur_time = datetime.datetime.now().time()
                no_files_msg = ': The ' + str(set_file[:-1]) + " '.set' file has no tetrodes to analyze!"
                error.append('\tThe ' + str(set_file[:-1]) + " '.set' file had no tetrodes to analyze, couldn't perform analysis.\n")
                associated_files = [file for file in f_list if str(set_file[:-1]) in file]
                missing_dir = os.path.join(dir_new, 'MissingAssociatedFiles')
                if not os.path.exists(missing_dir):
                    os.makedirs(missing_dir)

                for file in associated_files:
                    os.rename(os.path.join(dir_new, file), os.path.join(missing_dir, file))

                print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + no_files_msg)

            elif expt == 'Processed':
                continue

            elif str(set_file[:-1]) + '.eeg' not in f_list:

                associated_files = [file for file in f_list if str(set_file[:-1]) in file]
                missing_dir = os.path.join(dir_new, 'MissingAssociatedFiles')
                if not os.path.exists(missing_dir):
                    os.makedirs(missing_dir)

                for file in associated_files:
                    os.rename(os.path.join(dir_new, file), os.path.join(missing_dir, file))

                cur_date = datetime.datetime.now().date()
                cur_time = datetime.datetime.now().time()

                if str(set_file[:-1]) + '.pos' not in associated_files:
                    no_eeg_pos_msg = ': There is no "' + str(
                        set_file[:-1]) + '.eeg' + '" or ' + str(
                        set_file[:-1]) + '.pos' + '" file in this folder, skipping analysis!'
                    # skipped = 1

                    error.append('\tThe "' + str(set_file[:-1]) + '" \'.set\' file was not analyzed due to not having an \'.eeg\' and a \'.pos\' file.\n')

                    print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + no_eeg_pos_msg)
                else:
                    no_eeg_msg = ': There is no "' + str(set_file[:-1]) + '.eeg' '" file in this folder, skipping analysis!'
                    # skipped = 1
                    error.append('\tThe "' + str(set_file[
                                               :-1]) + '" \'.set\' file was not analyzed due to not having an \'.eeg\' file.\n')
                    print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + no_eeg_msg)
                continue

            elif str(set_file[:-1]) + '.pos' not in f_list:

                associated_files = [file for file in f_list if str(set_file[:-1]) in file]
                missing_dir = os.path.join(dir_new, 'MissingAssociatedFiles')
                if not os.path.exists(missing_dir):
                    os.makedirs(missing_dir)

                for file in associated_files:
                    os.rename(os.path.join(dir_new, file), os.path.join(missing_dir, file))

                cur_date = datetime.datetime.now().date()
                cur_time = datetime.datetime.now().time()

                if str(set_file[:-1]) + '.eeg' not in associated_files:
                    no_eeg_pos_msg = ': There is no "' + str(
                        set_file[:-1]) + '.pos' + '" or ' + str(
                        set_file[:-1]) + '.eeg' + '" file in this folder, skipping analysis!'
                    # skipped = 1
                    error.append('\tThe "' + str(set_file[
                                               :-1]) + '" \'.set\' file was not analyzed due to not having an \'.eeg\' and a \'.pos\' file.\n')
                    print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + no_eeg_pos_msg)
                else:
                    no_pos_msg = ': There is no "' + str(
                        set_file[:-1]) + '.pos' '" file in this folder, skipping analysis!'
                    # skipped = 1
                    error.append('\tThe "' + str(set_file[
                                               :-1]) + '" \'.set\' file was not analyzed due to not having a \'.pos\' file.\n')
                    print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + no_pos_msg)
                continue

            else:
                q = queue.Queue()
                for u in tet_list:
                    q.put(u)

                ThreadCount = int(self.settings['NumThreads'])

                if ThreadCount > len(tet_list):
                    ThreadCount = len(tet_list)
                skipped_mat = []

                with open(set_path + '.set', 'r+') as f:
                    for line in f:
                        if 'experimenter ' in line:
                            expter_line = line.split(' ', 1)
                            expter_line.remove('experimenter')
                            experimenter.append(' '.join(expter_line))
                            break


                while not q.empty():
                    Threads = []
                    for i in range(ThreadCount):
                        t = threading.Thread(target=runKlusta.analyze_tet, args=(self, q, experimenter, error, skipped_mat, i, set_path, set_file, f_list,
                                                                                 dir_new, log_f_dir, ini_f_dir))
                        time.sleep(0.5)
                        t.daemon = True
                        t.start()
                        Threads.append(t)

                    # q.join()

                    for t in Threads:
                        t.join()
                q.join()
        '''
        if 'skipped_mat' in locals():
            for k in range(len(skipped_mat)):
                if skipped_mat[k] == 1:
                    skipped = 1


        if skipped == 0:
        '''
        cur_date = datetime.datetime.now().date()
        cur_time = datetime.datetime.now().time()
        fin_msg = ': Analysis in the "' + expt + '" directory has been completed!'
        print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + fin_msg)

        smtpfile = 'smtp.json'
        with open(smtpfile, 'r+') as filename:
            smtp_data = json.load(filename)

            if smtp_data['Notification'] == 'On':

                expter_fname = 'experimenter.json'
                with open(expter_fname, 'r+') as f:
                    expters = json.load(f)

                toaddrs = []
                for key, value in expters.items():
                    if str(key).lower() in str(experimenter).lower():
                        if ',' in value and ', ' not in value:
                            addresses = value.split(', ', 1)
                            for address in addresses:
                                toaddrs.append(address)
                        elif ', ' in value:
                            addresses = value.split(', ', 1)
                            for address in addresses:
                                toaddrs.append(address)
                        else:
                            addresses = [value]
                            for address in addresses:
                                toaddrs.append(address)


                username = smtp_data['Username']
                password = smtp_data['Password']

                fromaddr = username

                if error == []:
                    error = ['\tNo errors to report on the processing of this folder!\n\n']

                subject = str(expt) + ' folder processed! [Automated Message]'

                text_list = ['Greetings from the Batch-TINTV2 automated messaging system!\n\n',
                                'The "' + expt + '" directory has finished processing and is now located in the "' + proc_f_dir +\
                                '" folder.\n\n',
                             'The errors that occurred during processing are the following:\n\n']

                for i in range(len(error)):
                    text_list.append(error[i])

                '''
                for i in range(len(error)):
                    for k in range(1, int(self.settings['NumTet']) + 1):
                        if '%s %d' % ('Tetrode', k) in error[i]:
                            while
                            text_list.append(error[i])
                '''
                text_list.append('\nHave a nice day,\n')
                text_list.append('Batch-TINTV2\n\n')
                text = ''.join(text_list)

                # Prepare actual message
                message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
                    """ % (fromaddr, ", ".join(toaddrs), subject, text)

                try:
                    # server = smtplib.SMTP('smtp.gmail.com:587')
                    server = smtplib.SMTP(str(smtp_data['ServerName']) + ':' + str(smtp_data['Port']))
                    server.ehlo()
                    server.starttls()
                    server.login(username, password)
                    server.sendmail(fromaddr, toaddrs, message)
                    server.close()
                    cur_date = datetime.datetime.now().date()
                    cur_time = datetime.datetime.now().time()
                    email_sent_msg = ': successfully sent e-mail!'
                    print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + email_sent_msg)
                except:
                    if toaddrs == []:
                        cur_date = datetime.datetime.now().date()
                        cur_time = datetime.datetime.now().time()
                        email_failed_msg = ': failed to send e-mail, could not establish an address to send the e-mail to!'
                        print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + email_failed_msg)
                    else:
                        cur_date = datetime.datetime.now().date()
                        cur_time = datetime.datetime.now().time()
                        email_failed_msg = ': failed to send e-mail, could be due to security settings of your e-mail!'
                        print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + email_failed_msg)

        proc_f_dir = os.path.join(directory, 'Processed')
        processing = 1
        while processing == 1:
            processing = 0
            try:
                # moves the entire folder to the processed folder
                os.rename(dir_new, os.path.join(proc_f_dir, expt))
            except PermissionError:
                processing = 1

        '''
        else:
        cur_date = datetime.datetime.now().date()
        cur_time = datetime.datetime.now().time()
        prob_fin_msg = ': There were some problems analyzing some files within this directory!'
        print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + prob_fin_msg)
        '''

    def analyze_tet(self, q, experimenter, error, skipped_mat, index, set_path, set_file, f_list, dir_new, log_f_dir, ini_f_dir):
        '''
        self.settings_fname = 'settings.json'

        with open(self.settings_fname, 'r+') as filename:
            self.settings = json.load(filename)
        '''
        # item = q.get()

        inactive_tet_dir = os.path.join(dir_new, 'InactiveTetrodeFiles')
        no_spike_dir = os.path.join(dir_new, 'NoSpikeFiles')

        if q.empty():
            try:
                q.task_done()
            except ValueError:
                pass
        else:
            tet_list = [q.get()]
            for tet_fname in tet_list:

                for i in range(1, int(self.settings['NumTet']) + 1):
                    if ['%s%d' % ('.', i) in tet_fname][0]:
                        tetrode = i
                cur_date = datetime.datetime.now().date()
                cur_time = datetime.datetime.now().time()
                file_analyze_msg = ': Now analyzing the following file: ' + tet_fname
                print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + file_analyze_msg)

                clu_name = set_path + '.clu.' + str(tetrode)
                cut_path = set_path + '_' + str(tetrode) + '.cut'
                cut_name = set_file[:-1] + '_' + str(tetrode) + '.cut'

                if cut_name in f_list:
                    cur_date = datetime.datetime.now().date()
                    cur_time = datetime.datetime.now().time()
                    already_done = 'The ' + tet_fname + ' file has already been analyzed!'
                    print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']: ' + already_done)
                    q.task_done()
                    continue

                tet_path = os.path.join(dir_new, tet_fname)

                ini_fpath = tet_path + '.ini'
                ini_fname = tet_fname + '.ini'

                parm_space = ' '
                kkparmstr = parm_space.join(['-MaxPossibleClusters', str(self.settings['MaxPos']),
                                             '-UseFeatures', str(self.settings['UseFeatures']),
                                             '-nStarts', str(self.settings['nStarts']),
                                             '-RandomSeed', str(self.settings['RandomSeed']),
                                             '-DistThresh', str(self.settings['DistThresh']),
                                             '-FullStepEvery', str(self.settings['FullStepEvery']),
                                             '-ChangedThresh', str(self.settings['ChangedThresh']),
                                             '-MaxIter', str(self.settings['MaxIter']),
                                             '-SplitEvery', str(self.settings['SplitEvery']),
                                             '-Subset', str(self.settings['Subset']),
                                             '-PenaltyK', str(self.settings['PenaltyK']),
                                             '-PenaltyKLogN', str(self.settings['PenaltyKLogN']),
                                             '-UseDistributional', '1',
                                             '-UseMaskedInitialConditions', '1',
                                             '-AssignToFirstClosestMask', '1',
                                             '-PriorPoint', '1',
                                             ])

                s = "\n"
                inc_channels = s.join(['[IncludeChannels]',
                                       '1=' + str(self.settings['1']),
                                       '2=' + str(self.settings['2']),
                                       '3=' + str(self.settings['3']),
                                       '4=' + str(self.settings['4'])
                                       ])

                with open(ini_fpath, 'w') as fname:

                    s = "\n"
                    main_seq = s.join(['[Main]',
                                       str('Filename=' + '"' + set_path + '"'),
                                       str('IDnumber=' + str(tetrode)),
                                       str('KKparamstr=' + kkparmstr),
                                       str(inc_channels)
                                       ])

                    clust_ft_seq = s.join(['\n[ClusteringFeatures]',
                                           str('PC1=' + str(self.settings['PC1'])),
                                           str('PC2=' + str(self.settings['PC2'])),
                                           str('PC3=' + str(self.settings['PC3'])),
                                           str('PC4=' + str(self.settings['PC4'])),
                                           str('A=' + str(self.settings['A'])),
                                           str('Vt=' + str(self.settings['Vt'])),
                                           str('P=' + str(self.settings['P'])),
                                           str('T=' + str(self.settings['T'])),
                                           str('tP=' + str(self.settings['tP'])),
                                           str('tT=' + str(self.settings['tT'])),
                                           str('En=' + str(self.settings['En'])),
                                           str('Ar=' + str(self.settings['Ar']))
                                           ])

                    report_seq = s.join(['\n[Reporting]',
                                         'Log=' + str(self.settings['Log File']),
                                         'Verbose=' + str(self.settings['Verbose']),
                                         'Screen=' + str(self.settings['Screen'])
                                         ])

                    for write_order in [main_seq, clust_ft_seq, report_seq]:
                        fname.seek(0, 2)  # seek the files end
                        fname.write(write_order)
                    fname.close()
                '''
                writing = 1

                while writing == 1:
                    new_cont = os.listdir(dir_new)
                    if ini_fname in new_cont:
                        writing = 0
                    else:
                        writing = 1
                '''

                log_fpath = tet_path + '_log.txt'
                log_fname = tet_fname + '_log.txt'

                cmdline = ["cmd", "/q", "/k", "echo off"]
                reading = 1
                with open(tet_path, 'rb') as f:
                    while reading == 1:
                        line = f.readline()
                        if 'experimenter ' in str(line):
                            expter_line = str(line).split(' ', 1)
                            expter_line.remove("b'experimenter")
                            experimenter.append(' '.join(expter_line))
                            reading = 0
                        elif 'data_start' in str(line):
                            reading = 0

                time.sleep(1)

                cmd = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

                if self.settings['Silent'] == 0:
                    batch = bytes(
                        'tint ' + '"' + set_path + '" ' + str(
                            tetrode) + ' "' + log_fpath + '" /runKK /KKoptions "' +
                        ini_fpath + '" /convertkk2cut /visible\n'
                        'exit\n', 'ascii')
                else:
                    batch = bytes(
                        'tint ' + '"' + set_path + '" ' + str(
                            tetrode) + ' "' + log_fpath + '" /runKK /KKoptions "' +
                        ini_fpath + '" /convertkk2cut\n'
                                    'exit\n', 'ascii')

                cmd.stdin.write(batch)
                cmd.stdin.flush()

                # result = cmd.stdout.read()
                # print(result.decode())

                processing = 1

                while processing == 1:
                    time.sleep(2)
                    new_cont = os.listdir(dir_new)

                    if cut_name in new_cont:
                        processing = 0
                        try:
                            try:
                                # moves the log files
                                try:
                                    os.rename(log_fpath, os.path.join(log_f_dir, tet_fname + '_log.txt'))
                                except FileNotFoundError:
                                    pass

                            except FileExistsError:
                                os.remove(os.path.join(log_f_dir, tet_fname + '_log.txt'))
                                os.rename(log_fpath, os.path.join(log_f_dir, tet_fname + '_log.txt'))
                            try:
                                # moves the .ini files
                                os.rename(ini_fpath, os.path.join(ini_f_dir, tet_fname + '.ini'))
                            except FileExistsError:
                                os.remove(os.path.join(ini_f_dir, tet_fname + '.ini'))
                                os.rename(ini_fpath, os.path.join(ini_f_dir, tet_fname + '.ini'))

                            cur_date = datetime.datetime.now().date()
                            cur_time = datetime.datetime.now().time()
                            finished_analysis = ': The analysis of the "' + tet_fname + '" file is finished!'
                            print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + finished_analysis)
                            pass

                        except PermissionError:
                            processing = 1

                    elif log_fname in new_cont:
                        active_tet = []
                        no_spike = []
                        with open(log_fpath, 'r') as f:
                            for line in f:
                                if 'list of active tetrodes:' in line:
                                    activ_tet = line
                                    if str(tetrode) not in str(line):

                                        if not os.path.exists(inactive_tet_dir):
                                            os.makedirs(inactive_tet_dir)

                                        cur_date = datetime.datetime.now().date()
                                        cur_time = datetime.datetime.now().time()
                                        not_active = ': Tetrode ' + str(tetrode) + ' is not active within the ' + \
                                                     str(set_file[:-1]) + ' set file!'
                                        error.append('\tTetrode ' + str(tetrode) + ' was not active within the ' + \
                                                     str(set_file[:-1]) + ' \'.set\' file, couldn\'t perform analysis.\n')
                                        print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + not_active)
                                        break
                                elif 'reading 0 spikes' in line:

                                    if not os.path.exists(no_spike_dir):
                                        os.makedirs(no_spike_dir)

                                    no_spike = 1
                                    # skipped_mat.append(1)
                                    cur_date = datetime.datetime.now().date()
                                    cur_time = datetime.datetime.now().time()
                                    not_spike = ': Tetrode ' + str(tetrode) + ' within the ' + \
                                                 str(set_file[:-1]) + ' \'.set\' file, has no spikes, skipping analysis!'

                                    error.append('\tTetrode ' + str(tetrode) + ' within the ' + \
                                                 str(set_file[:-1]) + ' \'.set\' file, had no spikes, couldn\'t perform analysis\n')

                                    print('[' + str(cur_date) + ' ' + str(cur_time)[:8] + ']' + not_spike)
                                    break

                                else:
                                    activ_tet = []

                        if 'activ_tet' in locals() and activ_tet != [] and str(tetrode) not in str(activ_tet):
                            x = 1
                            while x == 1:
                                try:
                                    try:
                                        # moves the log files
                                        try:
                                            os.rename(log_fpath,
                                                      os.path.join(log_f_dir, tet_fname + '_log.txt'))
                                        except FileNotFoundError:
                                            pass

                                    except FileExistsError:
                                        os.remove(os.path.join(log_f_dir, tet_fname + '_log.txt'))
                                        os.rename(log_fpath,
                                                  os.path.join(log_f_dir, tet_fname + '_log.txt'))
                                    try:
                                        # moves the .ini files
                                        os.rename(ini_fpath, os.path.join(ini_f_dir, tet_fname + '.ini'))
                                    except FileExistsError:
                                        os.remove(os.path.join(ini_f_dir, tet_fname + '.ini'))
                                        os.rename(ini_fpath, os.path.join(ini_f_dir, tet_fname + '.ini'))

                                    os.rename(tet_path, os.path.join(inactive_tet_dir, tet_fname))

                                    x = 0

                                except PermissionError:
                                    x = 1
                                processing = 0

                        if 'no_spike' in locals() and no_spike == 1:
                            x = 1
                            while x == 1:
                                try:
                                    try:
                                        # moves the log files
                                        try:
                                            os.rename(log_fpath,
                                                      os.path.join(log_f_dir, tet_fname + '_log.txt'))
                                        except FileNotFoundError:
                                            pass

                                    except FileExistsError:
                                        os.remove(os.path.join(log_f_dir, tet_fname + '_log.txt'))
                                        os.rename(log_fpath,
                                                  os.path.join(log_f_dir, tet_fname + '_log.txt'))
                                    try:
                                        # moves the .ini files
                                        os.rename(ini_fpath, os.path.join(ini_f_dir, tet_fname + '.ini'))
                                    except FileExistsError:
                                        os.remove(os.path.join(ini_f_dir, tet_fname + '.ini'))
                                        os.rename(ini_fpath, os.path.join(ini_f_dir, tet_fname + '.ini'))

                                    os.rename(tet_path, os.path.join(no_spike_dir, tet_fname))

                                    x = 0

                                except PermissionError:
                                    x = 1
                                processing = 0

                try:
                    q.task_done()
                except ValueError:
                    pass
        '''
        processing = 1
        while processing:
            processing = 0
            try:
                # moves the entire folder to the processed folder
                os.rename(dir_new, os.path.join(proc_f_dir, expt))
            except PermissionError:
                processing = 1
        '''