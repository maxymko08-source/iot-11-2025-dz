# iot-11-2025-dz
Develop a class for working with a file. The class should contain basic methods such as: reading and writing to a file, as well as the ability to append to a file (leaving the previous file contents). The path and name of the file must be passed through the class constructor. When creating an instance of the class, it is necessary to check whether the file exists. If such a file does not exist - generate an appropriate exception. When reading or writing to a file, if the file is damaged or writing is impossible - generate an appropriate exception. As exceptions, you need to create your own exceptions. Additionally, develop a decorator for logging write, read, and create file operations. Parameterized decorator logged, which accepts an exception and a mode as arguments. The mode can be "console" or "file". When an exception occurs in the decorated method, it is logged using the logging module. In console mode, logging occurs to the console, and in file mode, logging is written to a file.
Custom exceptions to clearly distinguish file-related problems:
File Not Found (FileNotFound).
File Corrupted (problems accessing or reading the file itself) (FileCorrupted).
File type for event logging - text
File type for reading the record - json
