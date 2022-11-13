import os
import zipfile as zipF

from PyQt6.QtCore import QMetaObject, Qt, Q_ARG


def extract(filename, should_d2j, is_mod, obj):
    curr_sys = os.uname().sysname
    prefix = 'org'
    if is_mod:
        prefix = 'mod'

    org_filepath = '../'+filename
    org_zipped_name = org_filepath.replace('.apk', '.zip')
    os.rename(org_filepath, org_zipped_name)

    org_zip = zipF.ZipFile(org_zipped_name)
    file_list = org_zip.namelist()
    dex_files = []
    for file in file_list:
        if '.dex' in file:
            dex_files.append(file)
            print(file)
    if not os.path.exists('{}_classes'.format(prefix)):
        os.mkdir(prefix + '_classes')
    if not os.path.exists(prefix + '_classes/jars'):
        os.mkdir(prefix + '_classes/jars')

    for dex in dex_files:
        org_zip.extract(dex, prefix + '_classes')

    classes_zip = []
    for dex in dex_files:
        name, x = dex.split('.dex')
        classes_zip.append(name + '.zip')
        if should_d2j:
            QMetaObject.invokeMethod(obj,
                                     "updateStatus", Qt.ConnectionType.QueuedConnection,
                                     Q_ARG(str, 'dex2jar file: {} from {} apk'.format(dex, prefix)), Q_ARG(bool, False))
            if curr_sys == 'Linux':
                os.system('bash ../d2j-dex2jar.sh --force {}_classes/{} -o {}_classes/jars/{}'.format(prefix, dex, prefix, name + '.zip'))
            elif curr_sys == 'Windows':
                os.system('..\\d2j-dex2jar.bat --force {}_classes\\{} -o {}_classes\\jars\\{}'.format(prefix, dex, prefix, name + '.zip'))

    QMetaObject.invokeMethod(obj,
                             "updateStatus", Qt.ConnectionType.QueuedConnection,
                             Q_ARG(str, 'DEX2JAR FINISHED FOR {} APK'.format(prefix)), Q_ARG(bool, True))


    if not os.path.exists(prefix + '_classes/all_classes'):
        os.mkdir(prefix + '_classes/all_classes')

    for zip_class in classes_zip:
        class_zip = prefix + '_classes/jars/' + zip_class
        QMetaObject.invokeMethod(obj,
                                 "updateStatus", Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(str, 'unzipping file: ' + zip_class), Q_ARG(bool, False))
        if curr_sys == 'Linux':
            os.system('unzip -o {} -d {}'.format(class_zip, prefix + '_classes/all_classes/'))
        elif curr_sys == 'Windows':
            #TODO check if usage is valid
            os.system('..\\unzip.exe {} -d {}'.format(class_zip, prefix + '_classes\\all_classes\\'))

    QMetaObject.invokeMethod(obj,
                             "updateStatus", Qt.ConnectionType.QueuedConnection,
                             Q_ARG(str, 'UNZIP FINISHED FOR {} APK'.format(prefix)), Q_ARG(bool, True))
    org_filepaths = open(prefix + '_filepaths.txt', 'w+')
    for root, dirs, files in os.walk(os.path.relpath(prefix + "_classes/all_classes")):
        for file in files:
            org_filepaths.write(root + '/' + file + '\n')

    os.rename(org_zipped_name, org_filepath)
    org_filepaths.close()


def compare(gran, mainfolder, obj):
    os.chdir(mainfolder)
    org_files = open('org_filepaths.txt', 'r')
    file_missing = open('missing.txt', 'w+')
    file_diff = open('diff.txt', 'w+')
    for file in org_files:
        org_size = os.stat(file.strip()).st_size
        if not os.path.exists(file.strip().replace('org_classes', 'mod_classes')):
            print('File doesnt exist in mod')
            file_missing.write(file)
            continue
        QMetaObject.invokeMethod(obj,
                                 "updateStatus", Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(str, 'comparing file: '+file.strip()), Q_ARG(bool, False))
        mod_size = os.stat(file.strip().replace('org_classes', 'mod_classes')).st_size
        if abs(org_size - mod_size) > gran:
            file_diff.write(file)
    org_files.close()
    file_missing.close()
    file_diff.close()
    QMetaObject.invokeMethod(obj,
                             "updateStatus", Qt.ConnectionType.QueuedConnection,
                             Q_ARG(str, 'COMPARING FINISHED'), Q_ARG(bool, True))


def files_added():
    org_files = open('org_filepaths.txt', 'r')
    mod_files = open('mod_filepaths.txt', 'r')
    add_files = open('added_files.txt', 'w+')

    org_f = org_files.readlines()
    for file in mod_files:
        if file.replace('mod_classes', 'org_classes') not in org_f:
            add_files.write(file)
    org_files.close()
    mod_files.close()
    add_files.close()

# extract('spotify_org.apk', False, False)
# extract('spotify_mod.apk', False, True)
# compare(100)
# files_added()
def copy_diffs(mainfolder, obj):
    curr_sys = os.uname().sysname
    os.chdir(mainfolder)
    if not os.path.exists('diff'):
        os.mkdir('diff')
    if not os.path.exists('diff/org'):
        os.mkdir('diff/org')
    if not os.path.exists('diff/mod'):
        os.mkdir('diff/mod')
    if not os.path.exists('diff_files'):
        os.mkdir('diff_files')
    diff_org = open('diff.txt', 'r')
    for file in diff_org:
        QMetaObject.invokeMethod(obj,
                                 "updateStatus", Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(str, 'copying file: '+file.strip()), Q_ARG(bool, False))
        if curr_sys == 'Linux':
            os.system('cp {} diff/org/'.format("'"+file.strip()+"'"))
            os.system('cp {} diff/mod/'.format("'"+file.strip().replace('org_classes', 'mod_classes')+"'"))
        elif curr_sys == 'Windows':
            os.system('copy {} diff\\org\\'.format(("'" + file.strip() + "'").replace('/', '\\')))
            os.system('copy {} diff\\mod\\'.format(("'" + file.strip().replace('org_classes', 'mod_classes') + "'")).replace('/', '\\'))
    diff_org.close()
    QMetaObject.invokeMethod(obj,
                             "updateStatus", Qt.ConnectionType.QueuedConnection,
                             Q_ARG(str, 'COPY FINISHED'), Q_ARG(bool, True))


def decompile(mainfolder, obj):
    curr_sys = os.uname().sysname
    os.chdir(mainfolder)
    if not os.path.exists('diff/org/java'):
        os.makedirs('diff/org/java', exist_ok=True)
    if not os.path.exists('diff/mod/java'):
        os.makedirs('diff/mod/java',exist_ok=True)
    diff_org = open('diff.txt', 'r')
    for file in diff_org:
        QMetaObject.invokeMethod(obj,
                                 "updateStatus", Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(str, 'decompiling file: '+file.strip()), Q_ARG(bool, False))
        if curr_sys == 'Linux':
            os.system('java -jar ../jd-cli.jar -od {} {}'.format('diff/org/java', "'"+file.strip()+"'"))
            os.system('java -jar ../jd-cli.jar -od {} {}'.format('diff/mod/java',"'"+file.strip().replace('org_classes', 'mod_classes')+"'"))
            parts = (file.strip()).split("/")
            filename = parts[-1].replace(".class", ".java")
            os.system('diff -uN {} {} > diff_files/{}'.format('diff/org/java/' + "'"+filename+"'", 'diff/mod/java/' +"'"+ filename+"'", "'"+filename.replace(".java", ".diff")+"'"))
        elif curr_sys == 'Windows':
            os.system('java -jar ..\\jd-cli.jar -od {} {}'.format('diff\\org\\java', "'" + file.strip().replace('/', '\\') + "'"))
            os.system('java -jar ..\\jd-cli.jar -od {} {}'.format('diff\\mod\\java',
                                                                 "'" + (file.strip().replace('org_classes',
                                                                                            'mod_classes')).replace('/', '\\') + "'"))
    QMetaObject.invokeMethod(obj,
                             "updateStatus", Qt.ConnectionType.QueuedConnection,
                             Q_ARG(str, 'DECOMPILE FINISHED'), Q_ARG(bool, True))
    QMetaObject.invokeMethod(obj,
                             "showFiles", Qt.ConnectionType.QueuedConnection,)

