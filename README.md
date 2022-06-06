# ModAnalyzer
This tool aims to help understand how APK files are modified, by showing the user a side by side comparison of original and modified code.

## How does it work?
A one to one comparison of .smali or .class files is often not feasible due to minor code changes
during decompilation and recompilation. Such an approach would have a very high rate of false positives
depending on the APK. Thus a different method is needed.

First we copy the dex files of both the original and the modified APK and obtain the jar files
through dex2jar. Then we extract the contents of these jar files. After that we compare the bytesize of the .class files
one by one. If the difference is higher than a chosen value of us, we determine the file to be modified.
These files deemed modified are then decompiled using the JD-Core decompiler and can be viewed by the user.