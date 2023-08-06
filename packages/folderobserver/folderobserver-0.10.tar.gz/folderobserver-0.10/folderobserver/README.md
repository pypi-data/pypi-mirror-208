# folderobserver

## pip install folderobserver

### Tested against Windows 10 / Python 3.10 / Anaconda

### observe_folders

The observe_folders function is useful for observing and analyzing folders, with various operations performed on the files within those folders. It offers several features that can be helpful in different scenarios.

One use case is to identify and retrieve temporary files. By specifying the folders to scan, you can monitor and collect temporary files that might be created during software execution or system processes. This can be particularly useful for analyzing and managing temporary data, ensuring efficient use of disk space, or identifying potential security risks associated with leftover temporary files.

Additionally, the function allows you to copy files from the observed folders to a destination folder. This can be helpful for creating backups or organizing files for further analysis or processing. You can choose to include additional information such as the file's last modified date or file permissions during the copying process.

Furthermore, the function supports the creation of flat copies of files. Flat copies involve extracting files from nested folder structures and placing them all in a single destination folder, using a specified separator to differentiate the original file paths. This feature can simplify file organization and facilitate bulk processing or analysis of files.

Moreover, the function provides the ability to guess the file types of downloaded files. By analyzing the file extension and content, it can make educated guesses about the file type. This can be useful when dealing with downloaded files that might have incorrect or missing file extensions, helping to identify the actual file type and enabling appropriate handling or processing.

Overall, the observe_folders function offers a flexible and customizable approach to observing folders, performing operations on files within those folders, and extracting valuable insights from the observed data. It can be adapted to various use cases, including managing temporary files, organizing files, and analyzing downloaded files.

Calling the function
The observe_folders function can be called in two different ways: through Python code and through the command-line interface (CLI).


### Calling the function in Python:


```python

# Stop capturing by pressing ctrl+c
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
```


### Calling the function through the CLI:

```python

In this example, you run the observe_folders function by executing a Python script through the CLI. The script (__init__.py) receives a configuration file (config.ini) as a command-line argument. The configuration file contains the parameters for the observe_folders function. The function reads the parameters from the configuration file and executes accordingly.

Both methods allow you to customize the behavior of the observe_folders function by providing different parameters such as the folders to scan, destination folder, flat copy options, logging options, and more. Adjust these parameters according to your specific requirements.

Configuration file example
Here's an example of a configuration file (config.ini) that can be used when calling the observe_folders function through the CLI:

# Stop capturing by pressing ctrl+c
.\python.exe "..\__init__.py" config.ini


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


In this example, the configuration file (config.ini) is structured using INI format. It consists of sections enclosed in square brackets ([]), followed by key-value pairs. The folders section contains the following key-value pairs:

folders_to_scan: Specifies the folders to scan. In this example, it scans the folder C:\Users\hansc\AppData\Local\Temp.
destination: Specifies the destination folder for copied files. In this example, it is set to C:\observer.
create_flatcopy: Determines whether to create flat copies of the files. Set to 1 (True) in this example.
create_flatcopy_and_guess_img_type: Determines whether to create flat copies and guess image types. Set to 1 (True) in this example.
flatcopy_sep: Specifies the separator for flat copies. In this example, it is set to #.
logfile: Specifies the path to the log file. In this example, it is set to C:\observerlog.csv.
clean_tmp_files_before: Determines whether to clean temporary files before scanning. Set to 1 (True) in this example.
verbose: Determines whether to enable verbose output. Set to 0 (False) in this example.
copy_date: Determines whether to copy the last modified date of files. Set to 0 (False) in this example.
copy_permission: Determines whether to copy file permissions. Set to 0 (False) in this example.
overwrite: Determines whether to overwrite existing files. Set to 1 (True) in this example.
use_tqdm: Determines whether to use tqdm progress bar. Set to 1 (True) in this example.
sleep_between_scans: Specifies the sleep duration between scans (in seconds). In this example, it is set to 1.
file_mb_limit: Specifies the maximum file size limit in megabytes (MB). In this example, it is set to 50.
You can modify the values in the configuration file according to your specific requirements before executing the observe_folders function through the CLI.

Please note that the INI configuration file format is commonly used for storing configuration settings and can be easily edited using a text editor.
```