# copytool
copytool copies files hell-bent for leather

### Tested+compiled against Windows 10 / Python 3.10 / Anaconda


TeraCopy needs 4 minutes, copytool does it 6 seconds
![](https://github.com/hansalemaos/copytool/blob/main/fastcopyscreenshot.png?raw=true)

## CLI
Compiled EXE: 
[](https://github.com/hansalemaos/copytool/raw/main/copytool.zip)
[](https://github.com/hansalemaos/copytool/raw/main/copytool.z01)

      Example: copytool --src "C:\ProgramData\anaconda3\envs" --dst "e:\envbackup" --use_tqdm 1 --copy_date 1 --copy_permission 0 --overwrite 1
      --src                     str         (source folder)
      --dst                     str         (destination folder)
      --log                     str  ""     (csv log)
      --copy_date               int  0      (copy date stats)
      --copy_permission         int  0      (copy permissions)
      --use_tqdm                int  1      (show progress bar)
      --overwrite               int  1      (overwrite existing files in dst)
      --use_uffs                int  1      (use uffs to get a list of files)


## Python

```python
# pip install copytool 
from copytool import get_all_files_on_hdd_and_copy
get_all_files_on_hdd_and_copy(
    src = r"C:\path",
    dst = r"e:\dest",
    log = "c:\\copylog.csv",
    copy_date= 0,
    copy_permission= 0,
    use_tqdm = 1,
    overwrite = 1,
    use_uffs = 1
)     

get_all_files_on_hdd_and_copy(
    src = r"C:\path",
    dst = r"e:\dest",
    log = "",
    copy_date= 0,
    copy_permission= 0,
    use_tqdm = 1,
    overwrite = 1,
    use_uffs = 0 # no logging without uffs 
)     
```
