
# Set the Delimeter character for separating fields in the workload file
DELIMITER = ','

# Set the data transfer rate in Hard Disk Drive, unit must be in MB/s
READ_DATA_TRANSFER_RATE_HDD = 156
WRITE_DATA_TRANSFER_RATE_HDD = 156

# Set the data transfer rate in Solid State Drive, unit must be in MB/s
READ_DATA_TRANSFER_RATE_SSD = 550
WRITE_DATA_TRANSFER_RATE_SSD = 530

# Set the default size files used in the simulation, it must be in MB
DEFAULT_SIZE_FILE = 128

# Set the size file unit abbreviation, the unit can be B (Byte), KB(Kilobyte), MB(MegaByte), GB(GigaByte)
# If there is no file size set the value to '-'.
SIZE_FILE_UNIT = 'B'

# Set the Data Transfer Rate Unit abbreviation  HAY Q VER Q TAN CONFIGURABLE ES ESTO
TRANSFER_RATE_UNIT = 'MB/s'

# ***** The columns fields positions are considered Starting in 0 (zero) *****
# Configure the number field position at Trace's file for column id filename
COLUMN_ID = 1

# Configure the number field position at Trace's file for column timestamp
COLUMN_TIMESTAMP = 0

# Configure the number field position at Trace's file for column size file.
# If there is no column file size set the value to '-'. By default in the simulation, the size file will be DEFAULT_SIZE_FILE
COLUMN_SIZE_FILE = 2

# Configure the number field position at Trace's file for column type of request, just supported Read or Write operations.
# If there is no type of request set the value to '-'. By default the simulation assumes only Read request operations
COLUMN_TYPE_REQUEST = 3

# Configure the timestamp unit second [s], millisecond [ms], microsecond [us] or nanosecond [ns] at Trace's file
TIMESTAMP_UNIT = 'ns'

# Configure the Replacement Policy to be used in the simulation
REPLACEMENT_POLICY = 'ssd_caching'

# Size used un replacement policy simulation
# Maximum number of Entries in Solid State Drive
SSD_CAPACITY = 1418
# Maximum number of Entries in Caching Layer
RAM_CAPACITY = 10

# Total of devices used in each layer to perform the simulation
NUMBER_SSD = 4146

NUMBER_HDD = 4146
