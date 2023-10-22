# Test for VfsPosix

try:
    import gc
    import os

    os.VfsPosix
except (ImportError, AttributeError):
    print("SKIP")
    raise SystemExit

# We need a directory for testing that doesn't already exist.
# Skip the test if it does exist.
temp_dir = "micropy_test_dir"
try:
    os.stat(temp_dir)
    print("SKIP")
    raise SystemExit
except OSError:
    pass

# getcwd and chdir
curdir = os.getcwd()
os.chdir("/")
print(os.getcwd())
os.chdir(curdir)
print(os.getcwd() == curdir)

# stat
print(type(os.stat("/")))

# listdir and ilistdir
print(type(os.listdir("/")))

# mkdir
os.mkdir(temp_dir)

# file create
f = open(temp_dir + "/test", "w")
f.write("hello")
f.close()

# close on a closed file should succeed
f.close()

# construct a file object with a raw fileno
f = open(2)
print(f)

# file read
f = open(temp_dir + "/test", "r")
print(f.read())
f.close()

# file finaliser, also see vfs_fat_finaliser.py
names = [temp_dir + "/x%d" % i for i in range(4)]
basefd = temp_dir + "/nextfd1"
nextfd = temp_dir + "/nextfd2"

with open(basefd, "w") as f:
    base_file_no = f.fileno()

for i in range(1024):  # move GC head forwards by allocating a lot of single blocks
    []


def write_files_without_closing():
    for n in names:
        open(n, "w").write(n)
    sorted(list(range(128)), key=lambda x: x)  # use up Python and C stack so f is really gone


write_files_without_closing()
gc.collect()

with open(nextfd, "w") as f:
    next_file_no = f.fileno()
    print("next_file_no <= base_file_no", next_file_no <= base_file_no)

for n in names + [basefd, nextfd]:
    os.remove(n)

# rename
os.rename(temp_dir + "/test", temp_dir + "/test2")
print(os.listdir(temp_dir))

# construct new VfsPosix with path argument
vfs = os.VfsPosix(temp_dir)
print(list(i[0] for i in vfs.ilistdir(".")))

# stat, statvfs (statvfs may not exist)
print(type(vfs.stat(".")))
if hasattr(vfs, "statvfs"):
    assert type(vfs.statvfs(".")) is tuple

# check types of ilistdir with str/bytes arguments
print(type(list(vfs.ilistdir("."))[0][0]))
print(type(list(vfs.ilistdir(b"."))[0][0]))

# remove
os.remove(temp_dir + "/test2")
print(os.listdir(temp_dir))

# remove with error
try:
    os.remove(temp_dir + "/test2")
except OSError:
    print("remove OSError")

# rmdir
os.rmdir(temp_dir)
print(temp_dir in os.listdir())

# rmdir with error
try:
    os.rmdir(temp_dir)
except OSError:
    print("rmdir OSError")
