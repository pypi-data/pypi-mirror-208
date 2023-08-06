import sys
import os


def format_folder_drive_path_backslash(path):
    path = path.strip("'\"\\ ")
    if len(path) == 1:
        path = f"{path}:"
    return path


try:
    cfgfi = os.path.normpath(format_folder_drive_path_backslash(sys.argv[1]))
    from hackycfgparser import add_config, load_config_file_vars, config

    load_config_file_vars(cfgfile=cfgfi, onezeroasboolean=False)
except Exception as fe:
    from hackycfgparser import add_config, config

from collections import deque, defaultdict
from time import strftime

from get_file_type import guess_filetypes
from kthread_sleep import sleep
from a_pandas_ex_df_to_string import pd_add_to_string

from subprocesskiller import kill_subprocs
from touchtouch import touch
from tqdm import tqdm

pd_add_to_string()
from copytool import copyallfiles, copyfile, conf
from uffspd import list_all_files
import os
import pandas as pd
from a_pandas_ex_set import Setdf
from remtmp import delete_tmp_files

timest = lambda: strftime("%Y_%m_%d_%H_%M_%S")
uffsfilepath = conf.uffsfilepath
stop = False


def stop_loop():
    global stop
    stop = True


def flatcopy(rdir, output, sep="#"):
    if not os.path.exists(output):
        os.makedirs(output)
    tempflatcopy = []
    for sdirs, dirs, files in os.walk(rdir):
        [
            copyfile(g, gg, False, 1000 * 1024, False, False)
            for k in files
            if (
                gg := os.path.join(
                    output,
                    (g := os.path.join(sdirs, k)).replace(os.sep, sep).replace(":", ""),
                )
            )
            and not tempflatcopy.append(gg)
        ]
    return tempflatcopy


def guess_downloaded_filetypes(df, copyconfig):
    df2 = guess_filetypes(df.aa_copied.to_list(), pandas_dataframe=True)
    df2["aa_size_on_disk"] = (
        df.loc[df.aa_copied.isin(df2.aa_filename)].aa_size_on_disk.__array__().copy()
    )
    output = os.path.normpath(os.path.join(copyconfig.destination, "flat"))

    if not os.path.exists(output):
        os.makedirs(output)
    sep = copyconfig.flatcopy_sep
    copyresults = []
    howmanyvariants = 100
    for key, item in df2.iterrows():
        copyresults.append([])
        try:
            infile = item.aa_filename
            allfinames = item.aa_possible_filenames
            allext = item.aa_possible_extensions

            for ini, g in enumerate(allfinames):
                if ini >= howmanyvariants:
                    break
                breaknow = False
                if howmanyvariants == 1:
                    if "txt" in allext:
                        breaknow = True
                        g = [ba for ba in allfinames if ba.endswith(".txt")][0]
                size = item.aa_size_on_disk
                if size == 0:
                    continue
                outf = os.path.normpath(
                    os.path.join(output, g.replace(os.sep, sep).replace(":", ""))
                )
                result = copyfile(infile, outf, False, 1000 * 1024, False, False)
                if result:
                    copyresults[-1].append(outf)

                    if breaknow:
                        break

        except Exception as fe:
            print(fe)
        copyresults[-1] = tuple(copyresults[-1])
    return copyresults, df2


class Allresults:
    pass


@add_config
def observe_folders(
    folders_to_scan: tuple | list = (),
    destination: str = "",
    create_flatcopy: int | bool = True,
    create_flatcopy_and_guess_img_type: int | bool = True,
    flatcopy_sep: str = "#",
    logfile: str = "",
    clean_tmp_files_before: int | bool = 0,
    verbose: int | bool = 0,
    copy_date: int | bool = 0,
    copy_permission: int | bool = 0,
    overwrite: int | bool = 1,
    use_tqdm: int | bool = 0,
    sleep_between_scans: int = 1,
    file_mb_limit: int | float = 100,
) -> pd.DataFrame:
    r"""
    The observe_folders function is useful for observing and analyzing folders, with various operations performed on the files within those folders. It offers several features that can be helpful in different scenarios.
    One use case is to identify and retrieve temporary files. By specifying the folders to scan, you can monitor and collect temporary files that might be created during software execution or system processes. This can be particularly useful for analyzing and managing temporary data, ensuring efficient use of disk space, or identifying potential security risks associated with leftover temporary files.
    Additionally, the function allows you to copy files from the observed folders to a destination folder. This can be helpful for creating backups or organizing files for further analysis or processing. You can choose to include additional information such as the file's last modified date or file permissions during the copying process.
    Furthermore, the function supports the creation of flat copies of files. Flat copies involve extracting files from nested folder structures and placing them all in a single destination folder, using a specified separator to differentiate the original file paths. This feature can simplify file organization and facilitate bulk processing or analysis of files.
    Moreover, the function provides the ability to guess the file types of downloaded files. By analyzing the file extension and content, it can make educated guesses about the file type. This can be useful when dealing with downloaded files that might have incorrect or missing file extensions, helping to identify the actual file type and enabling appropriate handling or processing.
    Overall, the observe_folders function offers a flexible and customizable approach to observing folders, performing operations on files within those folders, and extracting valuable insights from the observed data. It can be adapted to various use cases, including managing temporary files, organizing files, and analyzing downloaded files.


    The observe_folders function can be called in two different ways: through Python code and through the command-line interface (CLI).
    1) Calling the function in Python:

    Stop capturing by pressing ctrl+c
    from folderobserver import observe_folders

    df = observe_folders(
        folders_to_scan=(r"C:\Users\hansc\AppData\Local\Temp",),
        destination=r"C:\observer",
        create_flatcopy=0,
        create_flatcopy_and_guess_img_type=0,
        flatcopy_sep="#",
        logfile=r"C:\observerlog.csv",
        clean_tmp_files_before=0,
        verbose=0,
        copy_date=0,
        copy_permission=0,
        overwrite=1,
        use_tqdm=1,
        sleep_between_scans=1,
        file_mb_limit=50,
    )
    In this example, you import the observe_folders function from the folderobserver module. Then, you call the function with various parameters to configure its behavior. The function returns a DataFrame (df) containing the observed and processed data.


    Calling the function through the CLI:

    .\python.exe "..\__init__.py" config.ini

    In this example, you run the observe_folders function by executing a Python script through the CLI. The script (__init__.py) receives a configuration file (config.ini) as a command-line argument. The configuration file contains the parameters for the observe_folders function. The function reads the parameters from the configuration file and executes accordingly.

    Both methods allow you to customize the behavior of the observe_folders function by providing different parameters such as the folders to scan, destination folder, flat copy options, logging options, and more. Adjust these parameters according to your specific requirements.

    # example of config.ini

    [folders]
    folders_to_scan: ('C:\Users\hansc\AppData\Local\Temp',)
    destination: C:\observer
    create_flatcopy: 1
    create_flatcopy_and_guess_img_type: 1
    flatcopy_sep: #
    logfile: C:\observerlog.csv
    clean_tmp_files_before: 1
    verbose: 0
    copy_date: 0
    copy_permission: 0
    overwrite: 1
    use_tqdm: 1
    sleep_between_scans: 1
    file_mb_limit: 50

    Args:
        folders_to_scan (tuple | list, optional): List or tuple of folders to scan. Defaults to ().
        destination (str, optional): Destination folder for copied files. Defaults to "".
        create_flatcopy (int | bool, optional): Flag to create flat copies of the files. Defaults to True.
        create_flatcopy_and_guess_img_type (int | bool, optional): Flag to create flat copies and guess image types. Defaults to True.
        flatcopy_sep (str, optional): Separator for flat copies. Defaults to "#".
        logfile (str, optional): Path to the log file. Defaults to "".
        clean_tmp_files_before (int | bool, optional): Flag to clean temporary files before scanning. Defaults to 0.
        verbose (int | bool, optional): Flag to enable verbose output. Defaults to 0.
        copy_date (int | bool, optional): Flag to copy the last modified date of files. Defaults to 0.
        copy_permission (int | bool, optional): Flag to copy file permissions. Defaults to 0.
        overwrite (int | bool, optional): Flag to overwrite existing files. Defaults to 1.
        use_tqdm (int | bool, optional): Flag to use tqdm progress bar. Defaults to 0.
        sleep_between_scans (int, optional): Sleep duration between scans (in seconds). Defaults to 1.
        file_mb_limit (int | float, optional): Maximum file size limit (in MB). Defaults to 100.

    Returns:
        pd.DataFrame: Dataframe containing the results of the folder observation.

    Raises:
        None
    """
    if isinstance(folders_to_scan, str):
        folders_to_scan = [folders_to_scan]
    global stop
    stop = False

    lambdadeq = lambda: deque([], 2)
    copyconfig = Allresults()
    copyconfig.create_flatcopy = create_flatcopy
    copyconfig.create_flatcopy_and_guess_img_type = create_flatcopy_and_guess_img_type
    if copyconfig.create_flatcopy_and_guess_img_type:
        copyconfig.create_flatcopy = True
    copyconfig.flatcopy_sep = flatcopy_sep
    copyconfig.destination = os.path.normpath(destination)
    copyconfig.logfile = logfile
    if copyconfig.logfile:
        touch(copyconfig.logfile)
    copyconfig.searchresults = defaultdict()
    copyconfig.folders2scan_dict = {}
    copyconfig.folders2scan_list = []
    copyconfig.uffsfilepath = uffsfilepath
    copyconfig.sleepbetweenscans = sleep_between_scans
    if clean_tmp_files_before:
        delete_tmp_files()
    copyconfig.folders2scan_list = (
        [os.path.normpath(x) for x in folders_to_scan] if folders_to_scan else []
    )

    copyconfig.verbose = verbose
    if not copyconfig.folders2scan_list:
        copyconfig.folders2scan_list = [
            q
            for q in {os.environ.get("TEMP", ""), os.environ.get("TMP", "")}
            if os.path.exists(q)
        ]
    copyconfig.folders2scan_dict = defaultdict(lambdadeq)
    for folder in copyconfig.folders2scan_list:
        copyconfig.folders2scan_dict[os.path.normpath(folder)].append(pd.DataFrame())
    dfallresults = []

    allfiletresults = []
    condict = {k: -1 for k in list(copyconfig.folders2scan_dict.keys())}
    while True:
        if stop:
            break
        for i, q in enumerate(list(copyconfig.folders2scan_dict.keys())):
            print(f"Scanning folder: {q}")
            try:
                if copyconfig.sleepbetweenscans:
                    if condict[q] > -1:
                        sleep(copyconfig.sleepbetweenscans)

                tstamp = timest()
                dframetemp = list_all_files(
                    path2search=q,
                    file_extensions=None,
                    uffs_com_path=copyconfig.uffsfilepath,
                )
                if file_mb_limit:
                    dframetemp = (
                        dframetemp.loc[dframetemp.aa_size <= (file_mb_limit * 1024)]
                        .reset_index(drop=True)
                        .copy()
                    )
                dframetemp["aa_last_accessed"] = dframetemp[
                    "aa_last_accessed"
                ].ds_to_string()
                dframetemp["aa_timestamp"] = tstamp
                copyconfig.folders2scan_dict[q].append(dframetemp)
                dfallresults.append(dframetemp)
                if len(copyconfig.folders2scan_dict[q][0]) == 0:
                    sleep(sleep_between_scans)
                    continue
                setd = Setdf(
                    copyconfig.folders2scan_dict[q][0],
                    copyconfig.folders2scan_dict[q][1],
                )
                didis2 = setd.get_difference_of_all(
                    columns=[
                        "aa_path",
                        "aa_size_on_disk",
                        "aa_last_accessed",
                    ]
                )
                dframetemp = didis2[1].copy().reset_index(drop=True)
                dframetemp = dframetemp.loc[
                    ~dframetemp.aa_name.str.contains(r"^[\s.]*$")
                ]
                if dframetemp.empty:
                    if condict[q] == -1:
                        dframetemp = copyconfig.folders2scan_dict[q][-1].copy()
                        condict[q] += 1
                    else:
                        condict[q] += 1
                        sleep(sleep_between_scans)

                        continue

                condict[q] += 1

                dst = os.path.normpath(
                    os.path.join(
                        copyconfig.destination, str(i).zfill(8) + "__" + tstamp
                    )
                )
                print(f"Copying data to: {dst}")
                if not os.path.exists(dst):
                    os.makedirs(dst)
                if use_tqdm:
                    conf.tq = tqdm(total=len(didis2), unit="file")
                dframetemp["aa_copied"] = dframetemp.apply(
                    lambda fi: copyallfiles(
                        fi.aa_path,
                        fi.aa_archive,
                        dst,
                        fi.aa_size_on_disk,
                        copy_date,
                        copy_permission,
                        use_tqdm,
                        fi.aa_last_written,
                        fi.aa_last_accessed,
                        fi.aa_created,
                        fi.aa_attributes,
                        overwrite,
                    ),
                    axis=1,
                )
                dframetemp = (
                    dframetemp.dropna(subset="aa_copied").reset_index(drop=True).copy()
                )
                if dframetemp.empty:
                    sleep(sleep_between_scans)

                    continue
                dframetemp["aa_counter"] = condict[q]
                if copyconfig.create_flatcopy:
                    destflat = f"{dst}_f"
                    if not os.path.exists(destflat):
                        os.makedirs(destflat)
                    try:
                        _ = flatcopy(dst, destflat)
                    except Exception:
                        pass
                if copyconfig.verbose:
                    print(dframetemp)
                allfiletresults.append(dframetemp.copy())

                if use_tqdm:
                    conf.tq.close()
            except KeyboardInterrupt:
                print("Quitting ...")
                kill_subprocs()
                sleep(3)
                stop = True
                break
            except Exception as fa:
                print(fa)
                continue
    while True:
        try:
            kill_subprocs()
            sleep(2)
            break
        except KeyboardInterrupt:
            continue

    try:
        df = pd.concat(allfiletresults, ignore_index=True)
        df = df.loc[df.aa_copied.apply(lambda x: os.path.exists(x))].reset_index(
            drop=True
        )
    except Exception:
        df = pd.DataFrame()
    guessresults = []
    df2 = pd.DataFrame()
    try:
        if create_flatcopy_and_guess_img_type:
            guessresults, df2 = guess_downloaded_filetypes(df, copyconfig)
        if not df2.empty:
            df = pd.merge(
                df, df2, right_on="aa_filename", left_on="aa_copied", how="outer"
            ).reset_index(drop=True)
    except Exception as fe:
        print(fe)
    if guessresults:
        try:
            copypicdf = pd.DataFrame([guessresults])
            if copypicdf.shape[0] == 1:
                copypicdf = copypicdf.T.reset_index().copy()
            df = pd.concat([df, copypicdf], axis=1)
            df.columns = df.columns.to_list()[:-1] + ["aa_copied_types"]
        except Exception as fe:
            print(fe)
    if copyconfig.logfile:
        df.to_csv(copyconfig.logfile)
    return df


if __name__ == "__main__":
    if len(sys.argv) > 1:
        observe_folders()
