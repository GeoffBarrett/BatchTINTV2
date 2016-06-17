import sys, json, time, os, subprocess, functools, datetime, RunKlustaV2
# from RunKlustaV2.runKlusta import klusta, analyze_tet
from PyQt4 import QtGui, QtCore
from PIL import Image

'''Python 3.4, Libraries needed to install:
PyQt4 - needs .whl file since it has C++ backbone, can't do pip
H5Py - to interact with the HDF5 data (need .whl files for C dependicies)
NumPy - required for H5Py: pip install numpy'''

_author_ = "Geoffrey Barrett"  # defines myself as the author

Large_Font = ("Verdana", 12)  # defines two fonts for different purposes (might not be used
Small_Font = ("Verdana", 8)


def background(self):  # defines the background for each window
    """providing the background info for each window"""
    # Acquiring information about geometry
    self.setWindowIcon(QtGui.QIcon('cumc-crown.png'))  # declaring the icon image
    self.deskW, self.deskH = QtGui.QDesktopWidget().availableGeometry().getRect()[2:]  # gets the window resolution
    # self.setWindowState(QtCore.Qt.WindowMaximized) # will maximize the GUI
    self.setGeometry(0, 0, self.deskW/2, self.deskH/2)  # Sets the window size, 800x460 is the size of our window


class Window(QtGui.QWidget):  # defines the window class (main window)

    def __init__(self):  # intiializes the main window
        super(Window, self).__init__()
        # self.setGeometry(50, 50, 500, 300)
        background(self)  # acquires some features from the background function we defined earlier
        self.setWindowTitle("BatchTINT - Main Window")  # sets the title of the window
        self.home()  # runs the home function

    def home(self):  # defines the home funciton (the main window)

        # --- Reading in saved directory information ------
        self.dirfile = 'directory.json' # defining the filename that stores the directory information
        self.settings_fname = 'settings.json'

        try:  # attempts to run catches error if file not found
            # No saved directory's need to create file
            with open(self.dirfile, 'r+') as filename:  # opens the defined file
                dir_data = json.load(filename)  # loads the directory data from file
                cur_dir_name = dir_data['directory']  # defines the data
        except FileNotFoundError:  # runs if file not found
            with open(self.dirfile, 'w') as filename:  # opens a file
                cur_dir_name = 'No Directory Currently Chosen!'  # states that no directory was chosen
                dir_data = {'directory' : cur_dir_name} # creates a dictionary
                json.dump(dir_data, filename)  # writes the dictioary to the file

        # ---------------logo --------------------------------

        cumc_logo = QtGui.QLabel(self)  # defining the logo image
        logo_fname = os.getcwd() + "\\BatchKlustaLogo.png"  # defining logo pathname
        im2 = Image.open(logo_fname)  # opening the logo with PIL
        # im2 = im2.resize((self.deskW,self.deskH), PIL.Image.ANTIALIAS)
        # im2 = im2.resize((100,100), Image.ANTIALIAS)
        logowidth, logoheight = im2.size  # acquiring the logo width/height
        logo_pix = QtGui.QPixmap(logo_fname)  # getting the pixmap
        cumc_logo.setPixmap(logo_pix)  # setting the pixmap
        cumc_logo.setGeometry(0, 0, logowidth, logoheight)  # setting the geometry

        # ------buttons ------------------------------------------
        quitbtn = QtGui.QPushButton('Quit',self)  # making a quit button
        quitbtn.clicked.connect(self.close_app)  # defining the quit button functionality (once pressed)
        quitbtn.setShortcut("Ctrl+Q")  # creates shortcut for the quit button
        quitbtn.setToolTip('Click to quit Batch-Tint!')
        # quitbtn.move()

        self.setbtn = QtGui.QPushButton('Klusta Settings')  # Creates the settings pushbutton
        self.setbtn.setToolTip('Define the settings that KlustaKwik will use.')

        klustabtn = QtGui.QPushButton('Batch-TINT', self)  # creates the batch-klusta pushbutton
        klustabtn.setToolTip('Click to perform batch analysis via Tint and KlustaKwik!')

        self.choose_dir = QtGui.QPushButton('Choose Directory', self)  # creates the choose directory pushbutton

        self.cur_dir = QtGui.QLineEdit()  # creates a line edit to display the chosen directory (current)
        self.cur_dir.setText(cur_dir_name)  # sets the text to the current directory
        self.cur_dir.setAlignment(QtCore.Qt.AlignHCenter)  # centers the text
        self.cur_dir.setToolTip('The current directory that Batch-Tint will analyze.')
        self.cur_dir_name = cur_dir_name  # defines an attribute to exchange info between classes/modules

        klustabtn.clicked.connect(lambda: self.run_klusta(self.cur_dir_name))  # defines the button functionality once pressed

        # ------------------------------------ check box + Multithread ------------------------------------------------

        self.silent_cb = QtGui.QCheckBox('Run Silently')
        self.silent_cb.setToolTip("Check if you want Tint to run in the background.")

        self.Multithread_cb = QtGui.QCheckBox('Multiprocessing')
        self.Multithread_cb.setToolTip('Check if you want to run multiple tetrodes simultaneously')

        core_num_l = QtGui.QLabel('Cores (#):')
        core_num_l.setToolTip('Generally the number of processes that multiprocessing should use is \n'
                                   'equal to the number of cores your computer has.')

        self.core_num = QtGui.QLineEdit()

        Multithread_l = QtGui.QLabel('Simultaneous Tetrodes (#):')
        Multithread_l.setToolTip('Input the number of tetrodes you want to analyze simultaneously')

        self.Multithread = QtGui.QLineEdit()

        Multi_layout = QtGui.QHBoxLayout()

        for order in [self.Multithread_cb, core_num_l, self.core_num, Multithread_l, self.Multithread]:
            if 'Layout' in order.__str__():
                Multi_layout.addLayout(order)
                # Multi_layout.addStretch(1)
            else:
                Multi_layout.addWidget(order, 0, QtCore.Qt.AlignCenter)
                # Multi_layout.addWidget(order)
                # Multi_layout.addStretch(1)

        checkbox_layout = QtGui.QHBoxLayout()
        checkbox_layout.addStretch(1)
        checkbox_layout.addWidget(self.silent_cb)
        checkbox_layout.addStretch(1)
        checkbox_layout.addLayout(Multi_layout)
        checkbox_layout.addStretch(1)

        try:
            with open(self.settings_fname, 'r+') as filename:
                settings = json.load(filename)
                self.core_num.setText(settings['Cores'])
                self.Multithread.setText(settings['NumThreads'])
                if settings['Silent'] == 1:
                    self.silent_cb.toggle()
                if settings['Multi'] == 1:
                    self.Multithread_cb.toggle()
                if settings['Multi'] == 0:
                    self.core_num.setDisabled(1)


        except FileNotFoundError:
            self.silent_cb.toggle()
            self.core_num.setDisabled(1)
            self.core_num.setText('4')
            self.Multithread.setText('1')

        # ------------------------------------ version information -------------------------------------------------
        # finds the modifcation date of the program
        mod_date = time.ctime(os.path.getmtime(os.getcwd() + "\\BatchSort.py"))
        vers_label = QtGui.QLabel("BatchTINT V2.0 - Last Updated: " + mod_date)  # creates a label with that information

        # ------------------- page layout ----------------------------------------
        layout = QtGui.QVBoxLayout()  # setting the layout

        layout1 = QtGui.QHBoxLayout() # setting layout for the directory options
        layout1.addWidget(self.choose_dir)  # adding widgets to the first tab
        layout1.addWidget(self.cur_dir)

        # layout.addLayout(layout1)
        # layout.addWidget(quitbtn)

        btn_order = [klustabtn, self.setbtn, quitbtn]  # defining button order (left to right)
        btn_layout = QtGui.QHBoxLayout()  # creating a widget to align the buttons
        # btn_layout.addStretch(1)
        for butn in btn_order:  # adds the buttons in the proper order
            btn_layout.addWidget(butn)
            # btn_layout.addStretch(1)

        layout_order = [cumc_logo, layout1, checkbox_layout, btn_layout]  # creates the layout order for tab1

        layout.addStretch(1)  # adds the widgets/layouts according to the order
        for order in layout_order:
            if 'Layout' in order.__str__():
                layout.addLayout(order)
                layout.addStretch(1)
            else:
                layout.addWidget(order, 0, QtCore.Qt.AlignCenter)
                layout.addStretch(1)

        layout.addStretch(1)  # adds stretch to put the version info at the buttom
        layout.addWidget(vers_label)  # adds the date modification/version number
        self.setLayout(layout)  # sets the widget to the one we defined

        center(self)  # centers the widget on the screen

        self.show()  # shows the widget


    def run_klusta(self, directory):  # function that runs klustakwik
        klusta_ready = True
        with open(self.settings_fname, 'r+') as filename:
            self.settings = json.load(filename)
        self.settings['NumThreads'] = str(self.Multithread.text())
        self.settings['Cores'] = str(self.core_num.text())

        with open(self.settings_fname, 'w') as filename:
            json.dump(self.settings, filename)

        if self.settings['NumFet'] > 4:
            fet_msg = QtGui.QMessageBox.question(self, "No Chosen Directory: BatchTINT",
                                                "You have chosen more than four features,\n clustering will take a long time.\n"
                                                "Do you realy want to continue?",
                                                QtGui.QMessageBox.Yes,  QtGui.QMessageBox.No)
            if fet_msg == QtGui.QMessageBox.No:
                klusta_ready = False
            elif fet_msg == QtGui.QMessageBox.Yes:
                klusta_ready = True

        if directory == 'No Directory Currently Chosen!':
            directory_msg = QtGui.QMessageBox.question(self, "No Chosen Directory: BatchTINT",
                                                "You have not chosen a directory,\n please choose one to continue!",
                                                QtGui.QMessageBox.Ok )
            if directory_msg == QtGui.QMessageBox.Ok:
                pass
        elif 'Google Drive' in directory:
            directory_msg = QtGui.QMessageBox.question(self, "Google Drive Directory: BatchTINT",
                                                       "You have not chosen a directory within Google Drive,\n"
                                                       "be aware that during testing we have experienced\n"
                                                       "permissions errors while using Google Drive directories\n"
                                                       "that would result in BatchTINTV2 not being able to move\n"
                                                       "the files to the Processed folder (and stopping the GUI),\n"
                                                       "do you want to continue?",
                                                       QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if directory_msg == QtGui.QMessageBox.Yes:
                klusta_ready = True
            elif directory_msg == QtGui.QMessageBox.No:
                klusta_ready = False


        elif klusta_ready:
            self.hide()
            cur_time = datetime.datetime.now().time()
            dir_message = 'Analyzing the following direcotry: ' + directory  # display message
            print('[' + str(cur_time)[:8] + ']: ' + dir_message)  # prints the display message

            # ------------- find all files within directory -------------------------------------

            expt_list = os.listdir(directory)   # finds the files within the directory
            if len(expt_list) == 1 and expt_list[0] == 'Processed':
                cur_time = datetime.datetime.now().time()
                no_files_dir_msg = ': There are no files to analyze in this directory!'  # message that shows how many files were found
                print('[' + str(cur_time)[:8] + ']' + no_files_dir_msg)  # prints message
            else:
                cur_time = datetime.datetime.now().time()
                num_files_dir_msg = ': Found ' + str(len(expt_list)) + ' files in the directory!'  # message that shows how many files were found
                print('[' + str(cur_time)[:8] + ']' + num_files_dir_msg)  # prints message

            # ----------- cycle through each file and find the tetrode files ------------------------------------------

            for expt in expt_list:  # finding all the folders within the directory

                try:

                    dir_new = os.path.join(directory, expt) # sets a new filepath for the directory
                    f_list = os.listdir(dir_new)  # finds the files within that directory
                    set_file = [file for file in f_list if '.set' in file] # finds the set file
                    if expt == 'Processed':
                        continue
                    elif set_file == []: # if there is no set file it will return as an empty list
                        cur_time = datetime.datetime.now().time()
                        set_message = ': The following folder contains no .set file: ' + str(expt)  # message saying no .set file
                        print('[' + str(cur_time)[:8] + ']' + set_message)  # prints the message on the CMD
                        continue

                    RunKlustaV2.runKlusta.klusta(self, expt, directory)  # runs the function that will perform the klusta'ing

                except NotADirectoryError:
                    cur_time = datetime.datetime.now().time()
                    print('[' + str(cur_time)[:8] + ']: ' + expt + ' is not a directory, skipping analysis!')  # if the file is not a directory it prints this message
                    continue

            # --------------------------- makes a while loop that will check for new files to analyze -----------------
            contents = os.listdir(directory)  # lists the contents of the directory (folders)
            count = len(directory)  # counts the amount of files in the directory
            dirmtime = os.stat(directory).st_mtime  # finds the modification time of the file

            # creation of a while loop that will constantly check for new folders added to the directory
            while True:
                newmtime = os.stat(directory).st_mtime  # finds the new modification time
                if newmtime != dirmtime:  # only execute if the new mod time doens't equal the old mod time
                    dirmtime = newmtime  # sets the mod time to the new mod time for future iterations
                    newcontents = os.listdir(directory)  # lists the new contents of the directory including added folders
                    added = list(set(newcontents).difference(contents)) # finds the differences between the contents to state the files that were added
                    # added = list(added) #converts added to a list
                    if added:  # runs if added exists as a variable

                        for new_file in added: # cycles through the added files to analyze

                            if new_file == 'Processed':
                                continue

                            start_path = os.path.join(directory, new_file)
                            total_size = 0
                            total_size_old = 0
                            file_complete = 0
                            count_old = 0

                            while file_complete == 0:
                                total_size = 0
                                count_old = len(start_path)
                                # come up with way to have python wait until all the files have been transferred to the directory
                                for dirpath, dirnames, filenames in os.walk(start_path):
                                    for f in filenames:
                                        fp = os.path.join(dirpath, f)
                                        total_size += os.path.getsize(fp)
                                cur_time = datetime.datetime.now().time()
                                download_msg = new_file + ' is downloading... (' + str(total_size) +\
                                               ' bytes downloaded)!'
                                print('[' + str(cur_time)[:8] + ']: ' + download_msg)
                                # if total_size > total_size_old and len(start_path) > count_old:
                                if total_size > total_size_old:
                                    total_size_old = total_size
                                    time.sleep(45)  # waits x amount of seconds
                                elif total_size == total_size_old:
                                    cur_time = datetime.datetime.now().time()
                                    download_complete_msg = new_file + ' has finished downloading!'
                                    print('[' + str(cur_time)[:8] + ']: ' + download_complete_msg)
                                    file_complete = 1
                            try:
                                dir_new = os.path.join(directory, new_file)
                                f_list = os.listdir(dir_new)  # finds the files within that directory
                                set_file = [file for file in f_list if '.set' in file]

                                if set_file == []:
                                    set_message = "The following folder contains no '.set' file: " + str(new_file)
                                    print(set_message)
                                    continue

                                RunKlustaV2.runKlusta.klusta(self, new_file,
                                                             directory)  # runs the function that will perform the klusta'ing


                            except NotADirectoryError:
                                print(directory + ' is not a directory, skipping analysis!')
                                continue
                    '''
                    removed = set(contents).difference(newcontents)
                    if removed:
                        rem = "Files removed: %s" % (" ".join(removed))
                        print(rem)
                    '''
                    contents = newcontents  # defines the new contents of the folder

                '''
                    #case where the infinite while loop breaks
                elif :
                    return False
                '''
                # time.sleep(30) #checks every 30 seconds
                time.sleep(1)  # checks every 30 seconds

    def close_app(self):
        # pop up window that asks if you really want to exit the app ------------------------------------------------

        choice = QtGui.QMessageBox.question(self, "Quitting BatchTINT",
                                            "Do you really want to exit?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            sys.exit()  # tells the app to quit
        else:
            pass


class Settings_W(QtGui.QTabWidget):
    def __init__(self):
        super(Settings_W, self).__init__()

        self.set_adv = {}
        self.set_feats = {}
        self.set_chan_inc = {}
        self.position = {}
        self.reporting = {}

        self.default_adv = {'MaxPos': 30, 'nStarts': 1, 'RandomSeed': 1,
                       'DistThresh': 6.907755, 'PenaltyK': 1.0, 'PenaltyKLogN': 0.0,
                       'ChangedThresh': 0.05, 'MaxIter': 500, 'SplitEvery': 40,
                       'FullStepEvery': 20, 'Subset': 1}

         #self.settings_fname = 'settings.json'

        tab1 = QtGui.QWidget()  # creates the basic tab
        tab2 = QtGui.QWidget()  # creates the advanced tab

        background(self)
        # deskW, deskH = background.Background(self)
        self.setWindowTitle("BatchTINT - Settings Window")

        self.addTab(tab1, 'Basic')
        self.addTab(tab2, 'Advanced')
        # -------------------- number of tetrodes ---------------------

        num_tet_l = QtGui.QLabel('Number of Tetrodes')
        self.num_tet = QtGui.QLineEdit()
        self.num_tet.setToolTip('The maximum number of tetrodes in your directory folders.')

        num_tet_lay = QtGui.QHBoxLayout()
        num_tet_lay.addWidget(num_tet_l)
        # num_tet_lay.addStretch('1')
        num_tet_lay.addWidget(self.num_tet)

        # ------------------ clustering features --------------------------------
        clust_l = QtGui.QLabel('Clustering Features:')

        grid_ft = QtGui.QGridLayout()

        self.clust_ft_names = ['PC1', 'PC2', 'PC3', 'PC4',
                               'A', 'Vt', 'P', 'T',
                               'tP', 'tT', 'En', 'Ar']


        for feat in self.clust_ft_names:
            if feat != '':
                self.set_feats[feat] = 0

        self.clust_ft_cbs = {}

        positions = [(i, j) for i in range(4) for j in range(4)]

        for position, clust_ft_name in zip(positions, self.clust_ft_names):

            if clust_ft_name == '':
                continue
            self.position[clust_ft_name] = position
            self.clust_ft_cbs[position] = QtGui.QCheckBox(clust_ft_name)
            grid_ft.addWidget(self.clust_ft_cbs[position], *position)
            self.clust_ft_cbs[position].stateChanged.connect(
                functools.partial(self.channel_feats, clust_ft_name, position))

        # self.clust_ft_cbs.toggle()

        clust_feat_lay = QtGui.QHBoxLayout()
        clust_feat_lay.addWidget(clust_l)
        clust_feat_lay.addLayout(grid_ft)

        # -------------------------- reporting checkboxes ---------------------------------------

        report_l = QtGui.QLabel('Reporting Options:')

        self.report = ['Verbose', 'Screen', 'Log File']

        self.report_cbs = {}

        grid_report = QtGui.QGridLayout()

        positions = [(i, j) for i in range(1) for j in range(4)]

        for position, option in zip(positions, self.report):

            if option == '':
                continue
            self.position[option] = position
            self.report_cbs[position] = QtGui.QCheckBox(option)
            grid_report.addWidget(self.report_cbs[position], *position)
            self.report_cbs[position].stateChanged.connect(
                functools.partial(self.reporting_options, option, position))

        grid_lay = QtGui.QHBoxLayout()
        grid_lay.addWidget(report_l)
        grid_lay.addLayout(grid_report)

        # --------------------------Channels to Include-------------------------------------------

        chan_inc = QtGui.QLabel('Channels to Include:')

        grid_chan = QtGui.QGridLayout()
        self.chan_names = ['1', '2', '3', '4']

        for chan in self.chan_names:
            self.set_chan_inc[chan] = 0

        self.chan_inc_cbs = {}

        positions = [(i, j) for i in range(1) for j in range(4)]

        for position, chan_name in zip(positions, self.chan_names):

            if chan_name == '':
                continue
            self.position[chan_name] = position
            self.chan_inc_cbs[position] = QtGui.QCheckBox(chan_name)
            grid_chan.addWidget(self.chan_inc_cbs[position], *position)
            self.chan_inc_cbs[position].stateChanged.connect(
                functools.partial(self.channel_include, chan_name, position))
            self.chan_inc_cbs[position].setToolTip('Include channel ' + str(chan_name) + ' in the analysis.')

        chan_name_lay = QtGui.QHBoxLayout()
        chan_name_lay.addWidget(chan_inc)
        chan_name_lay.addLayout(grid_chan)

        # --------------------------basic lay doublespinbox------------------------------------------------
        '''
        max_clust_l = QtGui.QLabel('Maximum Clusters: ')
        min_clust_l = QtGui.QLabel('Minimum Clusters: ')
        max_clust = QtGui.QDoubleSpinBox()
        min_clust = QtGui.QDoubleSpinBox()

        clust_maxmin_order = [min_clust_l, min_clust, max_clust_l, max_clust]
        clust_maxmin_lay = QtGui.QHBoxLayout()

        for order in clust_maxmin_order:
            clust_maxmin_lay.addWidget(order, 0, QtCore.Qt.AlignCenter)
            clust_maxmin_lay.addStretch(1)
        '''
        # --------------------------adv lay doublespinbox------------------------------------------------

        row1 = QtGui.QHBoxLayout()
        row2 = QtGui.QHBoxLayout()
        row3 = QtGui.QHBoxLayout()
        row4 = QtGui.QHBoxLayout()
        row5 = QtGui.QHBoxLayout()
        row6 = QtGui.QHBoxLayout()

        maxposclust_l = QtGui.QLabel('MaxPossibleClusters: ')
        self.maxpos = QtGui.QLineEdit()

        chThresh_l = QtGui.QLabel('ChangedThresh: ')
        self.chThresh = QtGui.QLineEdit()

        nStarts_l = QtGui.QLabel('nStarts: ')
        self.nStarts = QtGui.QLineEdit()

        MaxIter_l = QtGui.QLabel('MaxIter: ')
        self.Maxiter = QtGui.QLineEdit()

        RandomSeed_l = QtGui.QLabel('RandomSeed: ')
        self.RandomSeed = QtGui.QLineEdit()

        SplitEvery_l = QtGui.QLabel('SplitEvery: ')
        self.SplitEvery = QtGui.QLineEdit()

        DistThresh_l = QtGui.QLabel('DistThresh: ')
        self.DistThresh = QtGui.QLineEdit()

        FullStepEvery_l  = QtGui.QLabel('FullStepEvery: ')
        self.FullStepEvery = QtGui.QLineEdit()

        PenaltyK_l = QtGui.QLabel('PenaltyK: ')
        self.PenaltyK = QtGui.QLineEdit()

        Subset_l = QtGui.QLabel('Subset: ')
        self.Subset = QtGui.QLineEdit()

        PenaltyKLogN_l = QtGui.QLabel('PenaltyKLogN: ')
        self.PenaltyKLogN = QtGui.QLineEdit()

        row1order = [maxposclust_l, self.maxpos, chThresh_l, self.chThresh]
        for order in row1order:
            row1.addWidget(order)
            # row1.addStretch(1)

        row2order = [nStarts_l, self.nStarts, MaxIter_l, self.Maxiter]
        for order in row2order:
            row2.addWidget(order)
            # row2.addStretch(1)

        row3order = [RandomSeed_l, self.RandomSeed, SplitEvery_l, self.SplitEvery]
        for order in row3order:
            row3.addWidget(order)
            # row3.addStretch(1)

        row4order = [DistThresh_l, self.DistThresh, FullStepEvery_l, self.FullStepEvery]
        for order in row4order:
            row4.addWidget(order)
            # row4.addStretch(1)

        row5order = [PenaltyK_l, self.PenaltyK, Subset_l, self.Subset]
        for order in row5order:
            row5.addWidget(order)
            # row5.addStretch(1)

        row6order = [PenaltyKLogN_l, self.PenaltyKLogN]
        for order in row6order:
            row6.addWidget(order)
            # row6.addStretch(1)

        # ------------------------ buttons ----------------------------------------------------
        self.basicdefaultbtn = QtGui.QPushButton("Default", tab1)
        self.basicdefaultbtn.clicked.connect(self.basic_default)
        self.advanceddefaultbtn = QtGui.QPushButton("Default", tab2)
        self.advanceddefaultbtn.clicked.connect(self.adv_default)

        self.backbtn = QtGui.QPushButton('Back', tab1)

        self.backbtn2 = QtGui.QPushButton('Back', tab2)

        self.apply_tab1btn = QtGui.QPushButton('Apply', tab1)
        self.apply_tab1btn.clicked.connect(self.apply_tab1)

        self.apply_tab2btn = QtGui.QPushButton('Apply',tab2)
        self.apply_tab2btn.clicked.connect(self.apply_tab2)


        basic_butn_order = [self.apply_tab1btn, self.basicdefaultbtn, self.backbtn]
        basic_butn_lay = QtGui.QHBoxLayout()
        for order in basic_butn_order:
            basic_butn_lay.addWidget(order, 0, QtCore.Qt.AlignCenter)
            # basic_butn_lay.addStretch(1)

        adv_butn_order = [self.apply_tab2btn, self.advanceddefaultbtn, self.backbtn2]
        adv_butn_lay = QtGui.QHBoxLayout()
        for order in adv_butn_order:
            adv_butn_lay.addWidget(order, 0, QtCore.Qt.AlignCenter)
            # adv_butn_lay.addStretch(1)

        # -------------------------- layouts ----------------------------------------------------

        # basic_lay_order = [chan_name_lay, clust_feat_lay, clust_maxmin_lay, basic_butn_lay]
        basic_lay_order = [num_tet_lay, chan_name_lay, clust_feat_lay, grid_lay, basic_butn_lay]
        basic_lay = QtGui.QVBoxLayout()

        # basic_lay.addStretch(1)
        for order in basic_lay_order:
            if 'Layout' in order.__str__():
                basic_lay.addLayout(order)
                basic_lay.addStretch(1)
            else:
                basic_lay.addWidget(order, 0, QtCore.Qt.AlignCenter)
                basic_lay.addStretch(1)

        tab1.setLayout(basic_lay)

        adv_lay_order = [row1, row2, row3, row4, row5, row6, adv_butn_lay]
        adv_lay = QtGui.QVBoxLayout()

        # basic_lay.addStretch(1)
        for order in adv_lay_order:
            if 'Layout' in order.__str__():
                adv_lay.addLayout(order)
                adv_lay.addStretch(1)
            else:
                adv_lay.addWidget(order, 0, QtCore.Qt.AlignCenter)
                adv_lay.addStretch(1)

        tab2.setLayout(adv_lay)

        self.settings_fname = 'settings.json'

        try:
            # No saved directory's need to create file
            with open(self.settings_fname, 'r+') as filename:
                self.settings = json.load(filename)
                self.maxpos.setText(str(self.settings['MaxPos']))
                self.chThresh.setText(str(self.settings['ChangedThresh']))
                self.nStarts.setText(str(self.settings['nStarts']))
                self.RandomSeed.setText(str(self.settings['RandomSeed']))
                self.DistThresh.setText(str(self.settings['DistThresh']))
                self.PenaltyK.setText(str(self.settings['PenaltyK']))
                self.PenaltyKLogN.setText(str(self.settings['PenaltyKLogN']))
                self.Maxiter.setText(str(self.settings['MaxIter']))
                self.SplitEvery.setText(str(self.settings['SplitEvery']))
                self.FullStepEvery.setText(str(self.settings['FullStepEvery']))
                self.Subset.setText(str(self.settings['Subset']))
                self.num_tet.setText(str(self.settings['NumTet']))

                for name in self.chan_names:
                    if int(self.settings[name]) == 1:
                        self.chan_inc_cbs[self.position[name]].toggle()

                for feat in self.clust_ft_names:
                    if feat != '':
                        if int(self.settings[feat]) == 1:
                            self.clust_ft_cbs[self.position[feat]].toggle()

                for option in self.report:
                    if int(self.settings[option]) == 1:
                        self.report_cbs[self.position[option]].toggle()

        except FileNotFoundError:

            with open(self.settings_fname, 'w') as filename:
                self.default_set_feats = self.set_feats
                self.default_set_feats['PC1'] = 1
                self.default_set_feats['PC2'] = 1
                self.default_set_feats['PC3'] = 1

                self.default_set_channels_inc = self.set_chan_inc
                self.default_set_channels_inc['1'] = 1
                self.default_set_channels_inc['2'] = 1
                self.default_set_channels_inc['3'] = 1
                self.default_set_channels_inc['4'] = 1

                self.default_reporting = self.reporting
                self.reporting['Verbose'] = 1
                self.reporting['Screen'] = 1
                self.reporting['Log File'] = 1

                self.settings = {}

                for dictionary in [self.default_adv, self.default_set_feats, self.default_set_channels_inc, self.default_reporting]:
                    self.settings.update(dictionary)

                default_set_feats = []
                default_reporting = []
                default_set_channels_inc = []

                self.settings['NumTet'] = '8'
                self.settings['NumFet'] = 3
                self.settings['Silent'] = 1
                self.settings['Multi'] = 0
                self.settings['UseFeatures'] = '1111111111111'
                self.settings['NumThreads'] = 1
                self.settings['Cores'] = 4

                json.dump(self.settings, filename)  # save the default values to this file

                self.maxpos.setText(str(self.settings['MaxPos']))
                self.chThresh.setText(str(self.settings['ChangedThresh']))
                self.nStarts.setText(str(self.settings['nStarts']))
                self.RandomSeed.setText(str(self.settings['RandomSeed']))
                self.DistThresh.setText(str(self.settings['DistThresh']))
                self.PenaltyK.setText(str(self.settings['PenaltyK']))
                self.PenaltyKLogN.setText(str(self.settings['PenaltyKLogN']))
                self.Maxiter.setText(str(self.settings['MaxIter']))
                self.SplitEvery.setText(str(self.settings['SplitEvery']))
                self.FullStepEvery.setText(str(self.settings['FullStepEvery']))
                self.Subset.setText(str(self.settings['Subset']))
                self.num_tet.setText(str(self.settings['NumTet']))

                for name in self.chan_names:
                    if self.settings[name] == 1:
                        self.chan_inc_cbs[self.position[name]].toggle()

                for feat in self.clust_ft_names:
                    if feat != '':
                        if self.settings[feat] == 1:
                            self.clust_ft_cbs[self.position[feat]].toggle()

                for option in self.report:
                    if int(self.settings[option]) == 1:
                        self.report_cbs[self.position[option]].toggle()
        center(self)
        # self.show()

    def reporting_options(self, option, position):
        if self.report_cbs[position].isChecked():
            self.reporting[option] = 1
        else:
            self.reporting[option] = 0

    def channel_feats(self, clust_ft_name, position):
        if self.clust_ft_cbs[position].isChecked():
            self.set_feats[clust_ft_name] = 1
        else:
            self.set_feats[clust_ft_name] = 0

    def channel_include(self,channel_name, position):
        if self.chan_inc_cbs[position].isChecked():
            self.set_chan_inc[channel_name] = 1
        else:
            self.set_chan_inc[channel_name] = 0

    def adv_default(self):

        self.maxpos.setText(str(self.default_adv['MaxPos']))
        self.chThresh.setText(str(self.default_adv['ChangedThresh']))
        self.nStarts.setText(str(self.default_adv['nStarts']))
        self.RandomSeed.setText(str(self.default_adv['RandomSeed']))
        self.DistThresh.setText(str(self.default_adv['DistThresh']))
        self.PenaltyK.setText(str(self.default_adv['PenaltyK']))
        self.PenaltyKLogN.setText(str(self.default_adv['PenaltyKLogN']))
        self.Maxiter.setText(str(self.default_adv['MaxIter']))
        self.SplitEvery.setText(str(self.default_adv['SplitEvery']))
        self.FullStepEvery.setText(str(self.default_adv['FullStepEvery']))
        self.Subset.setText(str(self.default_adv['Subset']))

        self.apply_tab2btn.animateClick()

    def basic_default(self):

        default_set_feats = {}
        default_set_feats['PC1'] = 1
        default_set_feats['PC2'] = 1
        default_set_feats['PC3'] = 1

        default_set_channels_inc = {}
        default_set_channels_inc['1'] = 1
        default_set_channels_inc['2'] = 1
        default_set_channels_inc['3'] = 1
        default_set_channels_inc['4'] = 1

        default_reporting = {}
        default_reporting['Verbose'] = 1
        default_reporting['Screen'] = 1
        default_reporting['Log File'] = 1

        for name in self.chan_names:
            default_keys = list(default_set_channels_inc.keys())
            if name in default_keys and self.chan_inc_cbs[self.position[name]].isChecked() == False:
                self.chan_inc_cbs[self.position[name]].toggle()
            elif name not in default_keys and self.chan_inc_cbs[self.position[name]].isChecked() == True:
                self.chan_inc_cbs[self.position[name]].toggle()

        for feat in self.clust_ft_names:
            if feat != '':
                default_keys = list(default_set_feats.keys())
                if feat in default_keys and self.clust_ft_cbs[self.position[feat]].isChecked() == False:
                    self.clust_ft_cbs[self.position[feat]].toggle()
                elif feat not in default_keys and self.clust_ft_cbs[self.position[feat]].isChecked() == True:
                    self.clust_ft_cbs[self.position[feat]].toggle()

        for option in self.report:
            default_keys = list(default_reporting.keys())
            if option in default_keys and self.report_cbs[self.position[option]].isChecked() == False:
                self.report_cbs[self.position[option]].toggle()
            elif option not in default_keys and self.report_cbs[self.position[option]].isChecked() == True:
                self.report_cbs[self.position[option]].toggle()

        self.num_tet.setText('8')

        self.apply_tab1btn.animateClick()

    def apply_tab1(self):
        with open(self.settings_fname, 'r+') as filename:

            for name, position in self.position.items():

                if name in self.chan_names:
                    if self.chan_inc_cbs[position].isChecked():
                        self.settings[name] = 1
                    else:
                        self.settings[name] = 0

                if name in self.clust_ft_names:
                    if self.clust_ft_cbs[position].isChecked():
                        self.settings[name] = 1
                    else:
                        self.settings[name] = 0

                if name in self.report:
                    if self.report_cbs[position].isChecked():
                        self.settings[name] = 1
                    else:
                        self.settings[name] = 0

            chan_inc = [chan for chan in self.chan_names if self.settings[chan] == 1]
            feat_inc = [feat for feat in self.clust_ft_names if self.settings[feat] == 1]

            UseFeat = ''
            # start_feat = 1
            for i in range(len(self.chan_names)):
                for j in range(len(feat_inc)):
                    if str(i+1) in chan_inc:
                        UseFeat += '1'
                    else:
                        UseFeat += '0'
            UseFeat += '1'

            self.settings['NumFet'] = len(feat_inc)
            self.settings['NumTet'] = str(self.num_tet.text())
            self.settings['UseFeatures'] = UseFeat

            self.backbtn.animateClick()

        with open(self.settings_fname, 'w') as filename:
            json.dump(self.settings, filename)  # save the default values to this file

    def apply_tab2(self):
        with open(self.settings_fname, 'r+') as filename:

            self.settings['MaxPos'] = self.maxpos.text()
            self.settings['nStarts'] = self.nStarts.text()
            self.settings['RandomSeed'] = self.RandomSeed.text()
            self.settings['DistThresh'] = self.DistThresh.text()
            self.settings['PenaltyK'] = self.PenaltyK.text()
            self.settings['PenaltyKLogN'] = self.PenaltyKLogN.text()
            self.settings['ChangedThresh'] = self.chThresh.text()
            self.settings['MaxIter'] = self.Maxiter.text()
            self.settings['SplitEvery'] = self.SplitEvery.text()
            self.settings['FullStepEvery'] = self.FullStepEvery.text()
            self.settings['Subset'] = self.Subset.text()

            self.backbtn2.animateClick()
        with open(self.settings_fname, 'w') as filename:
            json.dump(self.settings, filename)  # save the default values to this file


class Choose_Dir(QtGui.QWidget):
    def __init__(self):
        super(Choose_Dir, self).__init__()
        background(self)
        # deskW, deskH = background.Background(self)
        width = self.deskW / 5
        height = self.deskH / 5
        self.setGeometry(0, 0, width, height)

        self.dirfile = 'directory.json' # defining the directory filename

        with open(self.dirfile, 'r+') as filename:
            dir_data = json.load(filename)
            cur_dir_name = dir_data['directory']

        self.setWindowTitle("BatchTINT - Choose Directory")

        # ---------------- defining instructions -----------------
        instr = QtGui.QLabel("Choose the directory you are placing your TINT files to Batch-TINT")

        # ----------------- buttons ----------------------------
        self.dirbtn = QtGui.QPushButton('Choose Directory', self)
        self.dirbtn.setToolTip('Click to choose a directory!')
        # dirbtn.clicked.connect(self.new_dir)

        cur_dir_t = QtGui.QLabel('Current Directory:')  # the label saying Current Directory
        self.cur_dir_e = QtGui.QLineEdit() # the label that states the current directory
        self.cur_dir_e.setText(cur_dir_name)
        self.cur_dir_e.setAlignment(QtCore.Qt.AlignHCenter)
        self.cur_dir_name = cur_dir_name


        self.backbtn = QtGui.QPushButton('Back',self)
        applybtn = QtGui.QPushButton('Apply', self)
        applybtn.clicked.connect(self.apply_dir)

        # ---------------- save checkbox -----------------------
        self.save_cb = QtGui.QCheckBox('Leave Checked To Save Directory', self)
        self.save_cb.toggle()
        self.save_cb.stateChanged.connect(self.save_dir)

        # ----------------- setting layout -----------------------

        layout_dir = QtGui.QVBoxLayout()

        layout_h1 = QtGui.QHBoxLayout()
        layout_h1.addWidget(cur_dir_t)
        layout_h1.addWidget(self.cur_dir_e)

        layout_h2 = QtGui.QHBoxLayout()
        layout_h2.addWidget(self.save_cb)

        btn_layout = QtGui.QHBoxLayout()
        btn_order = [self.dirbtn, applybtn, self.backbtn]

        # btn_layout.addStretch(1)
        for butn in btn_order:
            btn_layout.addWidget(butn)
            # btn_layout.addStretch(1)

        layout_order = [instr, layout_h1, self.save_cb, btn_layout]

        for order in layout_order:
            if 'Layout' in order.__str__():
                layout_dir.addLayout(order)
            else:
                layout_dir.addWidget(order, 0, QtCore.Qt.AlignCenter)

        self.setLayout(layout_dir)

        center(self)
        # self.show()

    def save_dir(self,state):
        self.cur_dir_name = str(self.cur_dir_e.text())
        if state == QtCore.Qt.Checked:  # do this if the Check Box is checked
            # print('checked')
            with open(self.dirfile, 'w') as filename:
                dir_data = {'directory': self.cur_dir_name}
                json.dump(dir_data, filename)
        else:
            # print('unchecked')
            pass

    def apply_dir(self):
        self.cur_dir_name = str(self.cur_dir_e.text())
        self.save_cb.checkState()

        if self.save_cb.isChecked():  # do this if the Check Box is checked
            self.save_dir(self.save_cb.checkState())
        else:
            pass
        self.backbtn.animateClick()

@QtCore.pyqtSlot()
def raise_w(new_window, old_window):
    """ raise the current window"""
    new_window.raise_()
    new_window.show()
    time.sleep(0.1)
    old_window.hide()

def center(self):
    """centers the window on the screen"""
    frameGm = self.frameGeometry()
    screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
    centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
    frameGm.moveCenter(centerPoint)
    self.move(frameGm.topLeft())


def new_dir(self,main):
    cur_dir_name = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
    self.cur_dir_name = cur_dir_name
    self.cur_dir_e.setText(cur_dir_name)
    main.cur_dir.setText(cur_dir_name)
    main.cur_dir_name = cur_dir_name

def silent(self, state):
    with open(self.settings_fname, 'r+') as filename:
        settings = json.load(filename)
        if state == True:
            settings['Silent'] = 1
        else:
            settings['Silent'] = 0
    with open(self.settings_fname, 'w') as filename:
        json.dump(settings, filename)


def Multi(self, state):
    with open(self.settings_fname, 'r+') as filename:
        settings = json.load(filename)
        if state == True:
            settings['Multi'] = 1
            self.core_num.setEnabled(1)
        else:
            settings['Multi'] = 0
            self.core_num.setDisabled(1)
    with open(self.settings_fname, 'w') as filename:
        json.dump(settings, filename)

# ------- making a function that runs the entire GUI ----------
def run():
    app = QtGui.QApplication(sys.argv)

    main_w = Window() # calling the main window
    choose_dir_w = Choose_Dir()  # calling the Choose Directory Window
    settings_w = Settings_W()  # calling the settings window

    choose_dir_w.cur_dir_name = main_w.cur_dir_name # synchs the current directory on the main window

    main_w.raise_()  # making the main window on top

    main_w.silent_cb.stateChanged.connect(lambda: silent(main_w, main_w.silent_cb.isChecked()))
    main_w.Multithread_cb.stateChanged.connect(lambda: Multi(main_w, main_w.Multithread_cb.isChecked()))

    main_w.choose_dir.clicked.connect(lambda: raise_w(choose_dir_w,main_w)) # brings the directory window to the foreground
    #main_w.choose_dir.clicked.connect(lambda: raise_w(choose_dir_w))

    choose_dir_w.backbtn.clicked.connect(lambda: raise_w(main_w,choose_dir_w)) # brings the main window to the foreground
    #choose_dir_w.backbtn.clicked.connect(lambda: raise_w(main_w))  # brings the main window to the foreground

    main_w.setbtn.clicked.connect(lambda: raise_w(settings_w,main_w))
    #main_w.setbtn.clicked.connect(lambda: raise_w(settings_w))

    settings_w.backbtn.clicked.connect(lambda: raise_w(main_w, settings_w))
    #settings_w.backbtn.clicked.connect(lambda: raise_w(main_w))

    settings_w.backbtn2.clicked.connect(lambda: raise_w(main_w, settings_w))
    #settings_w.backbtn2.clicked.connect(lambda: raise_w(main_w))

    choose_dir_w.dirbtn.clicked.connect(lambda: new_dir(choose_dir_w,main_w)) # promps the user to choose a directory
    #choose_dir_w.dirbtn.clicked.connect(lambda: new_dir(choose_dir_w))  # promps the user to choose a directory

    sys.exit(app.exec_()) # prevents the window from immediatley exiting out

run() # the command that calls run()