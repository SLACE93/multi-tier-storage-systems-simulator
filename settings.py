
# Set the Delimeter character for separating fields in the files
DELIMITER = ' '

# Set the data transfer rate in Hard Disk Drive, unit must be in MB/s
READ_DATA_TRANSFER_RATE_HDD = 120
WRITE_DATA_TRANSFER_RATE_HDD = 100

# Set the data transfer rate in Solid State Drive, unit must be in MB/s
READ_DATA_TRANSFER_RATE_SSD = 250
WRITE_DATA_TRANSFER_RATE_SSD = 230

# Set the default size files used in the simulation, it must be in MB
DEFAULT_SIZE_FILE = 128

# Set the size file unit abbreviation, the unit can be B (Byte), KB(Kilobyte), MB(MegaByte), GB(GigaByte), TB(TeraByte)
# If there is no file size set the value to '-'.
SIZE_FILE_UNIT = 'MB'

# Set the Data Transfer Rate Unit abbreviation  HAY Q VER Q TAN CONFIGURABLE ES ESTO
TRANSFER_RATE_UNIT = 'MB/s'

# ***** The columns fields positions are considered Starting in 0 (zero) *****
# Configure the number field position at Trace's file for column id filename
COLUMN_ID = 1

# Configure the number field position at Trace's file for column timestamp
COLUMN_TIMESTAMP = 0

# Configure the number field position at Trace's file for column size file.
# If there is no column file size set the value to '-'. By default in the simulation, the size file will be DEFAULT_SIZE_FILE
COLUMN_SIZE_FILE = '-'

# Configure the number field position at Trace's file for column type of request, just supported Read or Write operations.
# If there is no type of request set the value to '-'. By default the simulation assumes only Read request operations
COLUMN_TYPE_REQUEST = '-'

# Configure the timestamp unit second [s] or milliseconds [ms] at Trace's file
TIMESTAMP_UNIT = 'ms'

# Configure the Replacement Policy to be used in the simulation
REPLACEMENT_POLICY = 'hash'

# Size used un replamcement policy simulation
# Maximum number of Entries in Solid State Drive
SSD_CAPACITY = 10

RAM_CAPACITY = 10

NUMBER_SSD = 5

NUMBER_HDD = 5
