# Guesses the file type/mime/encoding of files

## pip install get-file-type


```python
    Guesses the file type/mime/encoding of files. It uses the binaries from https://github.com/julian-r/file-windows/releases
    (File and Libmagic build with Visual Studio) - They are included in this package


    Args:
        files_folders (list or str): A list of file/folder paths or a single file/folder path.
        maxsubfolders (int, optional): Maximum number of subfolders to scan. Default is -1, which means no limit.
        pandas_dataframe (bool, optional): Determines if the results should be returned as a pandas DataFrame.
                                           Requires pandas to be installed. Default is False.
        verbose (bool, optional): Determines if verbose output should be displayed. Default is True.

    Returns:
        list or pd.DataFrame: A list of file type information for each file or a pandas DataFrame if pandas_dataframe is True.

    Raises:
        Exception: If pandas is not installed and pandas_dataframe is set to True.

    Example:
from get_file_type import guess_filetypes	
result_list = guess_filetypes(
    files_folders=[
        r"C:\Users\hansc\Pictures\fastcpy",  # png file without ending
        r"C:\Users\hansc\Pictures\fastcpy - Copy.png",  # an actual png file, to check if files with the correct ending are ignored
        r"C:\Users\hansc\Pictures\cppcomp.jpg",  # a .txt file with the wrong ending
        r"E:\destinationcopytemp5",  # internet cache files - whole folder will be scanned
    ],
    maxsubfolders=-1,  # if you want to limit the number of subfolders to scan, -1 means no limit
    pandas_dataframe=False,  # return the results as a pd.DataFrame (pandas must be installed)
    verbose=True,  # visual output
)

result_df = guess_filetypes(
    files_folders=[
        r"C:\Users\hansc\Pictures\fastcpy",  # png file without ending
        r"C:\Users\hansc\Pictures\fastcpy - Copy.png",  # an actual png file, to check if files with the correct ending are ignored
        r"C:\Users\hansc\Pictures\cppcomp.jpg",  # a .txt file with the wrong ending
        r"E:\destinationcopytemp5",  # internet cache files - whole folder will be scanned
    ],
    maxsubfolders=-1,
    pandas_dataframe=True,
    verbose=True,)
    output:
    [[['C:\\Users\\hansc\\Pictures\\fastcpy', 'image/png', 'charset=binary', ('png',), ('C:\\Users\\hansc\\Pictures\\fastcpy.png',)]]]
    [[['C:\\Users\\hansc\\Pictures\\fastcpy - Copy.png', 'image/png', 'charset=binary', ('png',), ('C:\\Users\\hansc\\Pictures\\fastcpy - Copy.png',)]]]
    [[['C:\\Users\\hansc\\Pictures\\cppcomp.jpg', 'text/plain', 'charset=us-ascii', ('conf', 'def', 'in', 'ini', 'list', 'log', 'text', 'txt'), ('C:\\Users\\hansc\\Pictures\\cppcomp.jpg.conf', 'C:\\Users\\hansc\\Pictures\\cppcomp.jpg.def', 'C:\\Users\\hansc\\Pictures\\cppcomp.jpg.in', 'C:\\Users\\hansc\\Pictures\\cppcomp.jpg.ini', 'C:\\Users\\hansc\\Pictures\\cppcomp.jpg.list', 'C:\\Users\\hansc\\Pictures\\cppcomp.jpg.log', 'C:\\Users\\hansc\\Pictures\\cppcomp.jpg.text', 'C:\\Users\\hansc\\Pictures\\cppcomp.jpg.txt')]]]
    [[['E:\\destinationcopytemp5\\00000000__2023_05_13_22_33_46\\Users\\hansc\\AppData\\Local\\Temp\\RBX-64BA6ED6.log', 'text/plain', 'charset=us-ascii', ('conf', 'def', 'in', 'ini', 'list', 'log', 'text', 'txt'), ('E:\\destinationcopytemp5\\00000000__2023_05_13_22_33_46\\Users\\hansc\\AppData\\Local\\Temp\\RBX-64BA6ED6.log',)]]]
    [[['E:\\destinationcopytemp5\\00000000__2023_05_13_22_33_46\\Users\\hansc\\AppData\\Local\\Temp\\RBX-DF39BC9A.log', 'text/plain', 'charset=us-ascii', ('conf', 'def', 'in', 'ini', 'list', 'log', 'text', 'txt'), ('E:\\destinationcopytemp5\\00000000__2023_05_13_22_33_46\\Users\\hansc\\AppData\\Local\\Temp\\RBX-DF39BC9A.log',)]]]


                                                                                                 aa_filename     aa_mime       aa_encoding                      aa_possible_extensions                                                                                                                                                                                                                                                                                                                       aa_possible_filenames
    0                                                                        C:\Users\hansc\Pictures\fastcpy   image/png    charset=binary                                      (png,)                                                                                                                                                                                                                                                                                                      (C:\Users\hansc\Pictures\fastcpy.png,)
    1                                                             C:\Users\hansc\Pictures\fastcpy - Copy.png   image/png    charset=binary                                      (png,)                                                                                                                                                                                                                                                                                               (C:\Users\hansc\Pictures\fastcpy - Copy.png,)
    2                                                                    C:\Users\hansc\Pictures\cppcomp.jpg  text/plain  charset=us-ascii  (conf, def, in, ini, list, log, text, txt)  (C:\Users\hansc\Pictures\cppcomp.jpg.conf, C:\Users\hansc\Pictures\cppcomp.jpg.def, C:\Users\hansc\Pictures\cppcomp.jpg.in, C:\Users\hansc\Pictures\cppcomp.jpg.ini, C:\Users\hansc\Pictures\cppcomp.jpg.list, C:\Users\hansc\Pictures\cppcomp.jpg.log, C:\Users\hansc\Pictures\cppcomp.jpg.text, C:\Users\hansc\Pictures\cppcomp.jpg.txt)
    3  E:\destinationcopytemp5\00000000__2023_05_13_22_33_46\Users\hansc\AppData\Local\Temp\RBX-64BA6ED6.log  text/plain  charset=us-ascii  (conf, def, in, ini, list, log, text, txt)                                                                                                                                                                                                                                    (E:\destinationcopytemp5\00000000__2023_05_13_22_33_46\Users\hansc\AppData\Local\Temp\RBX-64BA6ED6.log,)
    4  E:\destinationcopytemp5\00000000__2023_05_13_22_33_46\Users\hansc\AppData\Local\Temp\RBX-DF39BC9A.log  text/plain  charset=us-ascii  (conf, def, in, ini, list, log, text, txt)                                                                                                                                                                                                                                    (E:\destinationcopytemp5\00000000__2023_05_13_22_33_46\Users\hansc\AppData\Local\Temp\RBX-DF39BC9A.log,)




```
